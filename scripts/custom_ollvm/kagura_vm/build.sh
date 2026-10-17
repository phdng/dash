#!/usr/bin/env bash
# Kagura K6 REAL VM only on one public C function; independent manual workflow.
# No K5 IPA, Crane build, signing, PAC, hooks, network or device install.
set -euo pipefail
llvm="$1"
plugin="$2"
src="$3"
out="$4"
dir="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$out"
runtime="$(find "$src/../" -path '*/kagura-vm-build*/runtime/libkagura_runtime.a' -type f -print -quit)"
test -n "$runtime" && test -s "$runtime"
test -s "$src/runtime/core/vm_interpreter.c"
test -s "$src/include/kagura/VMOpcodes.def"
cp "$src/LICENSE" "$out/KAGURA-UPSTREAM-LICENSE"

# Same LLVM19 native target/compiler, one isolated translation unit, two
# variants; baseline never goes through the VM pass.
for variant in plain protected; do
  "$llvm/bin/clang" -O1 -std=c11 -Wall -Wextra -Werror \
    -DDD_VM_ENTRY=dd_vm_"$variant" \
    -DDD_VM_GUARD=dd_vm_guard_"$variant" \
    -emit-llvm -c "$dir/vm_canary.c" -o "$out/$variant-input.bc"
done
"$llvm/bin/opt" -S "$out/plain-input.bc" -o "$out/plain.ll"
"$llvm/bin/opt" --load-pass-plugin="$plugin" \
  -kagura-seed=46766 -kagura-vm -kagura-allow=dd_vm_protected \
  -debug-pass-manager -passes='function(kagura-vm),verify' \
  -S "$out/protected-input.bc" -o "$out/vm.ll" \
  2> "$out/vm-opt.log"
"$llvm/bin/clang" -O0 -c "$out/plain-input.bc" -o "$out/plain.o"
"$llvm/bin/clang" -O0 -c "$out/vm.ll" -o "$out/vm.o"
xcrun clang -O1 -std=c11 -Wall -Wextra -Werror \
  "$dir/vm_runner.c" "$out/plain.o" "$out/vm.o" "$runtime" \
  -o "$out/vm-host-runner"
"$out/vm-host-runner" > "$out/vm-native.log"

# Build-only iOS arm64 prototype. Uses the SAME Kagura VM pass, and compiles
# the pin's actual VM interpreter for iPhoneOS SDK. No iOS runtime PASS claim.
sdk="$(xcrun --sdk iphoneos --show-sdk-path)"
"$llvm/bin/clang" -O1 -std=c11 -Wall -Wextra -Werror \
  -target arm64-apple-ios15.0 -isysroot "$sdk" \
  -DDD_VM_ENTRY=dd_vm_protected -DDD_VM_GUARD=dd_vm_guard_protected \
  -emit-llvm -c "$dir/vm_canary.c" -o "$out/ios-input.bc"
"$llvm/bin/opt" --load-pass-plugin="$plugin" \
  -kagura-seed=46766 -kagura-vm -kagura-allow=dd_vm_protected \
  -debug-pass-manager -passes='function(kagura-vm),verify' \
  -S "$out/ios-input.bc" -o "$out/ios-vm.ll" \
  2> "$out/ios-vm-opt.log"
"$llvm/bin/clang" -O0 -target arm64-apple-ios15.0 -isysroot "$sdk" \
  -c "$out/ios-vm.ll" -o "$out/ios-vm.o"
xcrun clang -O1 -std=c11 -target arm64-apple-ios15.0 \
  -isysroot "$sdk" -I "$src/include" \
  -c "$src/runtime/core/vm_interpreter.c" -o "$out/ios-vm-interpreter.o"
xcrun clang -target arm64-apple-ios15.0 -isysroot "$sdk" -dynamiclib \
  "$out/ios-vm.o" "$out/ios-vm-interpreter.o" \
  -o "$out/KaguraVM-arm64-BUILD-ONLY.dylib"
xcrun nm -gU "$out/KaguraVM-arm64-BUILD-ONLY.dylib" > "$out/ios-symbols.txt"
grep -q '_dd_vm_protected$' "$out/ios-symbols.txt"
grep -q '_dd_vm_guard_protected$' "$out/ios-symbols.txt"
grep -q '_kagura_vm_execute$' "$out/ios-symbols.txt"

python3 "$dir/audit.py" \
  --plain-ir "$out/plain.ll" --candidate-ir "$out/vm.ll" \
  --ios-ir "$out/ios-vm.ll" --vm-trace "$out/vm-opt.log" \
  --ios-trace "$out/ios-vm-opt.log" \
  --native-log "$out/vm-native.log" \
  --vm-dylib "$out/KaguraVM-arm64-BUILD-ONLY.dylib" \
  --output "$out/Kagura-K6-VM-REPORT.json"
echo "K6 real Kagura VM selective: macOS host parity and arm64 build-only audited."
