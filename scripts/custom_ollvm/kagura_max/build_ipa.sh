#!/usr/bin/env bash
# Real LLVM19 Kagura seven-pass KaguraLab IPA; no Crane production changes.
# macOS only, no signing/install/arm64e PAC runtime or Mach-O relabel.
set -euo pipefail
llvm="$1"
plugin="$2"
out="$3"
dir="$(cd "$(dirname "$0")" && pwd)"
sdk="$(xcrun --sdk iphoneos --show-sdk-path)"
mkdir -p "$out/KaguraLab.app"
cp "$dir/ios_app_Info.plist" "$out/KaguraLab.app/Info.plist"
plutil -lint "$out/KaguraLab.app/Info.plist"
for variant in plain protected; do
  "$llvm/bin/clang" -O1 -std=c11 -Wall -Wextra -Werror \
    -target arm64-apple-ios15.0 -isysroot "$sdk" \
    -DDD_KAGURA_ENTRY=dd_kagura_"$variant" \
    -emit-llvm -c "$dir/critical.c" -o "$out/$variant-input.bc"
done
"$llvm/bin/clang" -O0 -target arm64-apple-ios15.0 -isysroot "$sdk" \
  -c "$out/plain-input.bc" -o "$out/plain.o"
current="$out/protected-input.bc"
for pass in str fla bcf sub co bbr bbs; do
  if [ "$pass" = str ]; then
    pipeline=kagura-str
  else
    pipeline="function(kagura-$pass)"
  fi
  "$llvm/bin/opt" --load-pass-plugin="$plugin" \
    -kagura-seed=1234567 -debug-pass-manager \
    -passes="$pipeline" "$current" \
    -o "$out/protected-$pass.bc" 2> "$out/pass-$pass.log"
  test -s "$out/protected-$pass.bc"
  grep -q 'Running pass:' "$out/pass-$pass.log"
  current="$out/protected-$pass.bc"
done
"$llvm/bin/clang" -O0 -target arm64-apple-ios15.0 -isysroot "$sdk" \
  -c "$current" -o "$out/protected.o"
python3 - "$out/plain.o" "$out/protected.o" <<'PY'
import sys
from pathlib import Path
baseline, candidate = [Path(x).read_bytes() for x in sys.argv[1:]]
marker = b"DD_KAGURA_PUBLIC_CANARY_CE_STRING_V1"
assert marker in baseline
assert marker not in candidate
assert baseline != candidate
PY
xcrun clang -std=c11 -O1 -Wall -Wextra -Werror \
  -target arm64-apple-ios15.0 -isysroot "$sdk" \
  -c "$dir/ios_canary.c" -o "$out/ios_canary.o"
xcrun clang -O1 -fobjc-arc -fblocks -Wall -Wextra -Werror \
  -target arm64-apple-ios15.0 -isysroot "$sdk" \
  -c "$dir/ios_app_main.m" -o "$out/ios_app_main.o"
xcrun clang -target arm64-apple-ios15.0 -isysroot "$sdk" \
  "$out/plain.o" "$out/protected.o" \
  "$out/ios_canary.o" "$out/ios_app_main.o" \
  -framework UIKit -framework Foundation \
  -o "$out/KaguraLab.app/KaguraLab"
xcrun nm -gU "$out/KaguraLab.app/KaguraLab" > "$out/app-symbols.txt"
grep -q '_dd_kagura_plain$' "$out/app-symbols.txt"
grep -q '_dd_kagura_protected$' "$out/app-symbols.txt"
xcrun otool -hv "$out/KaguraLab.app/KaguraLab" > "$out/macho-arm64.txt"
python3 "$dir/package_ipa.py" \
  --app "$out/KaguraLab.app" \
  --ipa "$out/KaguraLab-TrollStore-arm64.ipa" \
  --report "$out/KaguraLab-TrollStore-report.json"
python3 "$dir/ios_pipeline_audit.py" \
  --plain "$out/plain.o" --protected "$out/protected.o" \
  --app "$out/KaguraLab.app/KaguraLab" \
  --ipa "$out/KaguraLab-TrollStore-arm64.ipa" \
  --logs "$out" \
  --out "$out/KaguraLab-seven-pass-evidence.json"
shasum -a 256 "$out/plain.o" "$out/protected.o" \
  "$out/KaguraLab.app/KaguraLab" > "$out/object-binary-sha256.txt"
echo "KaguraLab arm64 real LLVM pass IPA build/audit PASS; runtime NOT TESTED."
