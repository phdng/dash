# Kagura K6 — selective real LLVM19 VM canary

Status: **real Kagura K6 LLVM19 VM macOS CI artifact independently verified; 4,096 host native parity PASS, iOS arm64 MH_DYLIB build-only PASS; iPhone VM runtime NOT TESTED** (2026-10-17). See [K6 artifact review](KAGURA_K6_ARTIFACT_REVIEW.md). This is a **separate**
research workflow and does **not** change the K5 iPhone IPA already reported
PASS by the user, nor Crane OLLVM STRONG production.

## Manual experiment

Trigger `Kagura K6 - Selective Real VM Canary (Experimental)` in Actions.
It uses the exact MIT Kagura upstream SHA
`ac2136ee0408677cf7cdee55307e9b16edd5f4d5` and LLVM19.
Real plugin pass: `opt --load-pass-plugin -kagura-vm
-kagura-allow=dd_vm_protected
-passes=function(kagura-vm),verify`. The pass must *materially* virtualize
`dd_vm_protected`, not merely announce its invocation.
No custom bytecode pretending to be an upstream Kagura pass.

- Standalone `vm_canary.c` contains exactly two public, pure C functions.
  `dd_vm_protected` is explicitly annotated `kagura_vm` and allowlisted.
  `dd_vm_guard_protected` is a deliberate *same-translation-unit* guard.
- Compile the exact same source separately as `dd_vm_plain` and
  `dd_vm_protected` with LLVM19 `-O1` IR; only protected IR is passed to the
  actual pinned Kagura VM plugin. Both variants and a native runner are linked
  on macOS with the real `libkagura_runtime.a`.
- Compiler audit requires a bytecode global `kagura_vm_bc_*`, a VM key,
  a native trampoline calling `kagura_vm_execute`, debug-pass-manager
  evidence on the intended function, *and a byte-identical unprotected guard
  IR body* plus real 4,096-vector host parity.
- A standalone Python model independently computes the expected host
  parity checksum `9625f13d712f59c3` and guard checksum
  `09d9d53ddf189ce7`. Three alternating measurement pairs of 1,024 calls
  report observed macOS ns/call. No fabricated speedup/security score and no
  hard overhead threshold from an uncontrolled shared runner.
- Separately compile the actual VM-transformed iOS arm64 bitcode and
  upstream `runtime/core/vm_interpreter.c` with Apple Clang/iPhoneOS SDK;
  link an arm64 `MH_DYLIB` and reject any fake/arm64e subtype. This is
  **iOS ABI build-only**, not an installable IPA or physical runtime test.

Expected artifact:
`DuoDash-Kagura-K6-VM-SELECTIVE-LLVM19-EXPERIMENTAL`, including native
proof log, LLVM IR, actual pass logs, arm64 dylib, audit JSON and upstream
LICENSE. A failure in compiler, host parity, VM effect or iOS link is a **real
failure** to diagnose, not a reason to downgrade a strict check.

## Isolation and exit conditions

Never add VM to `policy.json`, root `Makefile`, Crane hook/daemon,
Objective-C callbacks, iOS launch lifecycle, arm64e PAC or the existing
`KaguraLab-TrollStore-arm64.ipa` production-style acceptance lab.
The actual K6 macOS artifact has been inspected; all required host/ABI
gates match. A distinct K7 manual-only VM IPA workflow is now staged at
[KAGURA_K7_VM_TROLLSTORE.md](KAGURA_K7_VM_TROLLSTORE.md) to validate on
iPhone while preserving the K5 application as a rollback. K7 has not yet
been built or executed on a device. Upstream VM performance guidance is an estimate,
not project evidence.

`scripts/test_kagura_vm_selective.py` currently uses *synthetic*
Mach-O/LLVM IR solely to test fail-closed parsing and workflow contracts;
it must never be called actual LLVM VM execution or device PASS.
