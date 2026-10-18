#!/usr/bin/env bash
# K14 research-only unsigned iPhoneOS arm64 IPA. Link actual K13 CSEBreak.
set -Eeuo pipefail
llvm="$1"
src="$2"
out="$3"
dir="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$out"
stage="K14_PRECHECK"
error() {
  local code=$?
  trap - ERR
  {
    printf 'K14_FAILURE_STAGE=%s\n' "$stage"
    printf 'K14_EXIT_CODE=%s\n' "$code"
    printf 'K14_FAILED_LINE=%s\n' "$1"
    printf 'K14_FAILED_COMMAND=%s\n' "$2"
  } > "$out/Kagura-K14-BUILD-FAILURE.txt"
  echo "::error::K14 stage=$stage line=$1 exit=$code; see per-step logs" >&2
  exit "$code"
}
trap 'error "$LINENO" "$BASH_COMMAND"' ERR
sdk="$(xcrun --sdk iphoneos --show-sdk-path)"
test -s "$out/Kagura-K13-REPORT.json"
test -s "$out/ios-cse-break.o"
test -s "$out/ios-cse-break.ll"
test -s "$out/ios-pass-manager.log"
test -s "$src/LICENSE"
stage="K14_REPLAY_K13_REAL_NATIVE_AND_IOS_OBJECT"
python3 "$dir/../kagura_k13/audit.py" --out "$out"

stage="K14_COMPILE_PUBLIC_DATA_IOS_PARITY"
if ! xcrun clang -std=c11 -O1 -Wall -Wextra -Werror \
    -target arm64-apple-ios15.0 -isysroot "$sdk" \
    -c "$dir/ios_probe.c" -o "$out/ios-probe.o" \
    > "$out/ios-probe-compile.log" 2>&1; then
  cat "$out/ios-probe-compile.log" >&2; false
fi
stage="K14_COMPILE_ISOLATED_UIKIT"
if ! xcrun clang -fobjc-arc -fblocks -O1 -Wall -Wextra -Werror \
    -target arm64-apple-ios15.0 -isysroot "$sdk" \
    -c "$dir/ios_app_main.m" -o "$out/ios-app-main.o" \
    > "$out/ios-app-main-compile.log" 2>&1; then
  cat "$out/ios-app-main-compile.log" >&2; false
fi

stage="K14_LINK_ACTUAL_PROTECTED_ARM64_OBJECT"
app="$out/KaguraCSEBreakLab.app"
mkdir -p "$app"
cp "$dir/Info.plist" "$app/Info.plist"
# No K11 five-pass object, shim, macOS archive, or Crane production linkage.
if ! xcrun clang -target arm64-apple-ios15.0 -isysroot "$sdk" \
    "$out/ios-app-main.o" "$out/ios-probe.o" \
    "$out/ios-cse-break.o" \
    -framework Foundation -framework UIKit \
    -o "$app/KaguraCSEBreakLab" > "$out/ipa-link.log" 2>&1; then
  cat "$out/ipa-link.log" >&2; false
fi

stage="K14_CAPTURE_REAL_EXECUTABLE_SYMBOLS"
xcrun nm -gU "$app/KaguraCSEBreakLab" > "$out/ipa-app-defined-symbols.txt"
xcrun otool -hv "$app/KaguraCSEBreakLab" > "$out/ipa-macho-arm64.txt"
stage="K14_PACK_UNSIGNED_RESEARCH_IPA"
python3 "$dir/package_ipa.py" \
  --app "$app" \
  --ipa "$out/KaguraCSEBreakLab-TrollStore-arm64.ipa" \
  --report "$out/Kagura-K14-IPA-report.json"

stage="K14_REPLAY_REAL_EMBEDDED_BINARY_AND_K13_PASS"
python3 "$dir/ipa_evidence.py" --out "$out"
test -s "$out/Kagura-K14-IPA-EVIDENCE.json"
echo "K14_CSEBREAK_UNSIGNED_IPA_REAL_BUILD_EVIDENCE_PASS"
echo "K14 arm64 lab IPA built and SHA/UUID verified; no iPhone execution, no PAC/Crane."
