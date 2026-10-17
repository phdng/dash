#!/usr/bin/env bash
# K7 isolated VM IPA. Run only after K6 real host/arm64 build.sh passed.
set -euo pipefail
llvm="$1"
out="$2"
dir="$(cd "$(dirname "$0")" && pwd)"
sdk="$(xcrun --sdk iphoneos --show-sdk-path)"
test -s "$out/Kagura-K6-VM-REPORT.json"
test -s "$out/ios-vm.ll"
test -s "$out/ios-vm-opt.log"
test -s "$out/ios-vm.o"
test -s "$out/ios-vm-interpreter.o"
test -s "$out/vm-native.log"

# The baseline uses SAME pure C TU, same iOS target and compiler flags;
# only protected input goes through the actual K6 VM pass.
"$llvm/bin/clang" -O1 -std=c11 -Wall -Wextra -Werror \
  -target arm64-apple-ios15.0 -isysroot "$sdk" \
  -DDD_VM_ENTRY=dd_vm_plain -DDD_VM_GUARD=dd_vm_guard_plain \
  -emit-llvm -c "$dir/vm_canary.c" -o "$out/ios-plain-input.bc"
"$llvm/bin/opt" -S "$out/ios-plain-input.bc" -o "$out/ios-plain.ll"
"$llvm/bin/clang" -O0 -target arm64-apple-ios15.0 -isysroot "$sdk" \
  -c "$out/ios-plain-input.bc" -o "$out/ios-plain.o"

app="$out/KaguraVMLab.app"
mkdir -p "$app"
cp "$dir/ios_app_Info.plist" "$app/Info.plist"

xcrun clang -O1 -std=c11 -Wall -Wextra -Werror \
  -target arm64-apple-ios15.0 -isysroot "$sdk" \
  -c "$dir/ios_probe.c" -o "$out/ios-probe.o"
xcrun clang -fobjc-arc -fblocks -O1 -Wall -Wextra -Werror \
  -target arm64-apple-ios15.0 -isysroot "$sdk" \
  -c "$dir/ios_app_main.m" -o "$out/ios-app-main.o"
xcrun clang -target arm64-apple-ios15.0 -isysroot "$sdk" \
  "$out/ios-app-main.o" "$out/ios-probe.o" \
  "$out/ios-plain.o" "$out/ios-vm.o" "$out/ios-vm-interpreter.o" \
  -framework Foundation -framework UIKit \
  -o "$app/KaguraVMLab"
xcrun nm -gU "$app/KaguraVMLab" > "$out/ipa-app-symbols.txt"
xcrun otool -hv "$app/KaguraVMLab" > "$out/ipa-macho-arm64.txt"

python3 "$dir/package_ipa.py" \
  --app "$app" \
  --ipa "$out/KaguraVMLab-TrollStore-arm64.ipa" \
  --report "$out/KaguraVMLab-IPA-report.json"
python3 "$dir/ipa_evidence.py" \
  --ipa "$out/KaguraVMLab-TrollStore-arm64.ipa" \
  --ipa-report "$out/KaguraVMLab-IPA-report.json" \
  --k6-report "$out/Kagura-K6-VM-REPORT.json" \
  --ios-plain-ir "$out/ios-plain.ll" \
  --ios-vm-ir "$out/ios-vm.ll" \
  --ios-vm-trace "$out/ios-vm-opt.log" \
  --symbols "$out/ipa-app-symbols.txt" \
  --ios-vm-obj "$out/ios-vm.o" \
  --ios-plain-obj "$out/ios-plain.o" \
  --vm-interpreter-obj "$out/ios-vm-interpreter.o" \
  --output "$out/Kagura-K7-IPA-EVIDENCE.json"
echo "K7 standalone VM arm64 IPA: exact Mach-O+pass+runtime audit complete; device NOT TESTED"
