# Kagura K6 real selective VM — macOS CI artifact review

Date: 2026-10-17. User uploaded
`DuoDash-Kagura-K6-VM-SELECTIVE-LLVM19-EXPERIMENTAL.zip` and reported
GitHub Actions build PASS.

Independent inspection of **real ZIP bytes** (not green badge alone):

- Artifact: 12,064 bytes, **11 entries**, ZIP CRC clean; SHA-256
  `93117aa780b1032e8951b157a29ee63265cb7850016e87c90cdaf93fd448e582`.
- `Kagura-K6-VM-REPORT.json` independently matched SHA-256 for host
  `plain.ll`, `vm.ll`, `vm-opt.log`, `vm-native.log` and iOS
  `ios-vm.ll` and `ios-vm-opt.log`. Audit report matches real files.
- LLVM19 on macOS produced a **171-byte VM bytecode blob**
  `kagura_vm_bc_3040747483`, key global and exact trampoline call
  `@kagura_vm_execute` for `dd_vm_protected`. iOS arm64 IR has a separate
  real 171-byte blob `kagura_vm_bc_3768774349` and same trampoline shape.
  `dd_vm_guard_protected` remains direct native arithmetic (not virtualized).
- Important scope nuance: the **pass manager invokes VMObfuscationPass on
  both functions** (visible in both opt logs). The guard is excluded from
  transformation by Kagura's allowlist; don't misstate that it wasn't visited.
- Real host execution finished `DD_VM_COMPLETE=PASS` for **4,096**
  baseline/VM vector comparisons and the guard. Strict independent Python
  checksum: protected/baseline `9625f13d712f59c3`, guard
  `09d9d53ddf189ce7`.
- Three **observational macOS host** ns/call paired measurements were:
  baseline `[4,4,3]`, VM `[192,192,193]`. Per-pair ratios approximately
  `[48.0,48.0,64.33]` ×; median-of-paired measurements `48.0×`.
  With just three samples, no claim of stable p95 or device performance.
- The iOS `KaguraVM-arm64-BUILD-ONLY.dylib` is 49,712 bytes,
  SHA-256 `eb3b7e260d3fc896b2c5cb67f41f10b9c16a5be839116199b9a10a425eb5a005`,
  Mach-O `0xfeedfacf` / arm64 CPU / raw subtype `0` /
  `MH_DYLIB`; LC_UUID
  `4d4fc6fa-c713-3c4e-a659-6690ab336fad`. Exports target,
  native guard and `_kagura_vm_execute`.
- Kagura pinned SHA `ac2136ee0408677cf7cdee55307e9b16edd5f4d5`,
  MIT license text retained in artifact.

**Conclusion:** K6 `MACOS_CI_ARTIFACT_VERIFIED_HOST_ONLY` and iOS arm64
`BUILD_ONLY`, not an installable IPA or device VM runtime PASS. The VM incurs
material overhead on this fixture. No code or execution evidence from Crane
production, Objective-C callbacks, arm64e/PAC device, or iPhone.

Next step is a **separate K7 KaguraVMLab IPA** manual CI experiment with a
distinct bundle ID from KaguraLab K5 and independent device parity gates.
Do not modify or overwrite the K5 IPA reported PASS by the user.
