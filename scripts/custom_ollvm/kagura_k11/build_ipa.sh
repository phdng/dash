#!/usr/bin/env bash
# K11 standalone unsigned arm64 iPhone experiment; never Crane or K5/K7.
set -Eeuo pipefail
llvm="$1"
src="$2"
out="$3"
dir="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$out"
stage="K11_PRECHECK"
# Always leave a precise failure-stage marker inside the uploaded CI artifact.
k11_error() {
  local status=$?
  trap - ERR
  {
    printf 'K11_FAILURE_STAGE=%s\n' "$stage"
    printf 'K11_EXIT_CODE=%s\n' "$status"
    printf 'K11_FAILED_LINE=%s\n' "$1"
    printf 'K11_FAILED_COMMAND=%s\n' "$2"
  } > "$out/Kagura-K11-BUILD-FAILURE.txt"
  echo "::error::K11 stage=$stage line=$1 exit=$status; see Kagura-K11-BUILD-FAILURE.txt and per-step logs" >&2
  exit "$status"
}
trap 'k11_error "$LINENO" "$BASH_COMMAND"' ERR
sdk="$(xcrun --sdk iphoneos --show-sdk-path)"
test -s "$out/Kagura-K10-METADATA-REPORT.json"
test -s "$out/Kagura-K9-COMPOSITION-REPORT.json"
test -s "$out/05-ci/ios.o"
test -s "$out/05-ci/ios.ll"
test -s "$out/05-ci/ios-opt.log"
test -s "$src/LICENSE"
python3 "$dir/../kagura_k10/pilot.py" --out "$out" --verify-report

# The macOS libkagura_runtime.a is NOT an iOS library.
# Strictly find one ACTUAL upstream function definition (not a comment,
# prototype or call). Preserve all mentions in a JSON for postmortem.
stage="K11_FIND_REAL_UPSTREAM_CI_RESOLVER"
python3 "$dir/ci_runtime_resolver.py" \
  --src "$src" \
  --report "$out/ios-rtld-discovery.json" \
  --selected-path "$out/ios-rtld-source.txt"
resolver="$src/$(cat "$out/ios-rtld-source.txt")"
test -s "$resolver"
stage="K11_COMPILE_UPSTREAM_IOS_RESOLVER"
if ! xcrun clang -std=c11 -O1 -Wall -Wextra -target arm64-apple-ios15.0 \
   -isysroot "$sdk" -I"$src/include" \
   -c "$resolver" -o "$out/ios-kagura-rtld.o" \
   > "$out/ios-kagura-rtld-compile.log" 2>&1; then
  cat "$out/ios-kagura-rtld-compile.log" >&2
  false
fi
# No fake substitute: confirm the cross-compiled arm64 Mach-O object has
# a real external DEFINITION of the exact Kagura resolver before linking.
xcrun nm -gU "$out/ios-kagura-rtld.o" > "$out/ios-kagura-rtld-symbols.txt"
if ! grep -Eq ' [Tt] _kagura_rtld_default_handle$' \
  "$out/ios-kagura-rtld-symbols.txt"; then
  echo "K11 pinned upstream C did not define real _kagura_rtld_default_handle" >&2
  false
fi

stage="K11_COMPILE_IOS_PROBE"
if ! xcrun clang -std=c11 -O1 -Wall -Wextra -Werror \
   -target arm64-apple-ios15.0 -isysroot "$sdk" \
   -c "$dir/ios_probe.c" -o "$out/ios-probe.o" \
   > "$out/ios-probe-compile.log" 2>&1; then
  cat "$out/ios-probe-compile.log" >&2
  false
fi
stage="K11_COMPILE_UIKIT"
if ! xcrun clang -fobjc-arc -fblocks -O1 -Wall -Wextra -Werror \
   -target arm64-apple-ios15.0 -isysroot "$sdk" \
   -c "$dir/ios_app_main.m" -o "$out/ios-app-main.o" \
   > "$out/ios-app-main-compile.log" 2>&1; then
  cat "$out/ios-app-main-compile.log" >&2
  false
fi

# anti_debug.c contains the genuine resolver, but also calls other
# Kagura runtime functions. Discover the complete iOS arm64 C source/object
# symbol closure with nm, never inject fake stubs or a host-built archive.
stage="K11_RESOLVE_PINNED_IOS_RUNTIME_C_DEPENDENCY_CLOSURE"
python3 "$dir/ci_runtime_closure.py" \
  --src "$src" --out "$out" --sdk "$sdk"
test -s "$out/ios-runtime-closure.json"
test -s "$out/ios-runtime-extra-objects.txt"
# macos-14 /bin/bash is 3.2: do not use Bash 4 'mapfile'.
runtime_extra_objects=()
while IFS= read -r object_path; do
  test -s "$object_path"
  runtime_extra_objects+=("$object_path")
done < "$out/ios-runtime-extra-objects.txt"
if (( ${#runtime_extra_objects[@]} < 1 )); then
  echo "K11 expected nonempty real pinned iOS Kagura dependency objects" >&2
  false
fi

stage="K11_LINK_REAL_FIVE_PASS_IOS_EXECUTABLE"
app="$out/KaguraFiveLab.app"
mkdir -p "$app"
cp "$dir/Info.plist" "$app/Info.plist"
# Apple ld defaults to rejecting unresolved MH_EXECUTE symbols;
# avoid obsolete undefined-symbol linker option (warning on Xcode).
if ! xcrun clang -target arm64-apple-ios15.0 -isysroot "$sdk" \
   "$out/ios-app-main.o" "$out/ios-probe.o" \
   "$out/05-ci/ios.o" "$out/ios-kagura-rtld.o" \
   "${runtime_extra_objects[@]}" \
   -framework Foundation -framework UIKit \
   -o "$app/KaguraFiveLab" > "$out/ipa-link.log" 2>&1; then
  cat "$out/ipa-link.log" >&2
  false
fi

stage="K11_VERIFY_EXPORTED_FUNCTIONS"
xcrun nm -gU "$app/KaguraFiveLab" > "$out/ipa-app-symbols.txt"
xcrun otool -hv "$app/KaguraFiveLab" > "$out/ipa-macho-arm64.txt"
stage="K11_PACKAGE_UNSIGNED_IPA"
python3 "$dir/package_ipa.py" \
  --app "$app" \
  --ipa "$out/KaguraFiveLab-TrollStore-arm64.ipa" \
  --report "$out/KaguraFiveLab-IPA-report.json"
stage="K11_AUDIT_EMBEDDED_IPA_AND_K10_EVIDENCE"
python3 "$dir/ipa_evidence.py" --out "$out"
test -s "$out/Kagura-K11-IPA-EVIDENCE.json"
echo "K11_IPA_BUILD_AND_EVIDENCE_PASS"
echo "K11 real CI five-pass iOS object linked to upstream iOS runtime: unsigned IPA structure only, iPhone not tested"
