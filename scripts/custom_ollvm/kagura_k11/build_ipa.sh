#!/usr/bin/env bash
# K11 standalone unsigned arm64 iPhone experiment; never Crane or K5/K7.
set -euo pipefail
llvm="$1"
src="$2"
out="$3"
dir="$(cd "$(dirname "$0")" && pwd)"
sdk="$(xcrun --sdk iphoneos --show-sdk-path)"
test -s "$out/Kagura-K10-METADATA-REPORT.json"
test -s "$out/Kagura-K9-COMPOSITION-REPORT.json"
test -s "$out/05-ci/ios.o"
test -s "$out/05-ci/ios.ll"
test -s "$out/05-ci/ios-opt.log"
test -s "$src/LICENSE"
python3 "$dir/../kagura_k10/pilot.py" --out "$out" --verify-report

# Upstream macOS libkagura_runtime.a is NOT an iOS library.
# Find exactly ONE upstream C translation unit defining the real CI
# runtime resolver, and cross-compile that pinned source for iOS arm64.
# Never replace the resolver with a dummy/shim and never link macOS .a.
resolver="$(python3 - "$src" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
files=sorted(path for path in (root/"runtime").rglob("*.c")
             if b"kagura_rtld_default_handle" in path.read_bytes())
if len(files)!=1:
    raise SystemExit("K11 requires exactly ONE pinned upstream C resolver source; found "+str(len(files)))
print(files[0])
PY
)"
test -f "$resolver"
python3 - "$src" "$resolver" "$out/ios-rtld-source.txt" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
source=Path(sys.argv[2]).resolve()
relative=source.relative_to(root).as_posix()
if not relative.startswith("runtime/") or not relative.endswith(".c"):
    raise SystemExit("K11 resolver source must be within upstream runtime/")
Path(sys.argv[3]).write_text(relative+"\n", encoding="utf-8")
PY
xcrun clang -std=c11 -O1 -Wall -Wextra -target arm64-apple-ios15.0 \
  -isysroot "$sdk" -I"$src/include" \
  -c "$resolver" -o "$out/ios-kagura-rtld.o"

xcrun clang -std=c11 -O1 -Wall -Wextra -Werror \
  -target arm64-apple-ios15.0 -isysroot "$sdk" \
  -c "$dir/ios_probe.c" -o "$out/ios-probe.o"
xcrun clang -fobjc-arc -fblocks -O1 -Wall -Wextra -Werror \
  -target arm64-apple-ios15.0 -isysroot "$sdk" \
  -c "$dir/ios_app_main.m" -o "$out/ios-app-main.o"

app="$out/KaguraFiveLab.app"
mkdir -p "$app"
cp "$dir/Info.plist" "$app/Info.plist"
xcrun clang -target arm64-apple-ios15.0 -isysroot "$sdk" \
  -Wl,-undefined,error \
  "$out/ios-app-main.o" "$out/ios-probe.o" \
  "$out/05-ci/ios.o" "$out/ios-kagura-rtld.o" \
  -framework Foundation -framework UIKit \
  -o "$app/KaguraFiveLab" > "$out/ipa-link.log" 2>&1

xcrun nm -gU "$app/KaguraFiveLab" > "$out/ipa-app-symbols.txt"
xcrun otool -hv "$app/KaguraFiveLab" > "$out/ipa-macho-arm64.txt"
python3 "$dir/package_ipa.py" \
  --app "$app" \
  --ipa "$out/KaguraFiveLab-TrollStore-arm64.ipa" \
  --report "$out/KaguraFiveLab-IPA-report.json"
python3 "$dir/ipa_evidence.py" --out "$out"
test -s "$out/Kagura-K11-IPA-EVIDENCE.json"
echo "K11 real CI five-pass iOS object linked to upstream iOS runtime: unsigned IPA structure only, iPhone not tested"
