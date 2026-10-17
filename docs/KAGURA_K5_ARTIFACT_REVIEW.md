# KaguraLab K5 — review of real CI artifact, 2026-10-17

This review uses the user-provided file
`KaguraLab-TrollStore-arm64-LLVM19-SEVEN-PASSES (1).zip` (24,575 bytes).
The ZIP CRC check passed, it contains 19 entries, and its SHA-256 is
`64ec7131642356638340eefff58b54a70f906dd9e9270de63a83336e6f99157a`.

**Verified from actual ZIP bytes**, rather than from a green Actions badge:

- `KaguraLab-TrollStore-arm64.ipa` SHA-256
  `7233235c60c9843c8e342c81f63dff326f2bdbfdfc39197db4d07d5c398d9ccd`,
  equals both `KaguraLab-TrollStore-report.json` and the seven-pass evidence JSON.
- Embedded `Payload/KaguraLab.app/KaguraLab` (94,128 B) SHA-256
  `003b85756b914e3e722668c249d7a3f00c4ec27b1487797e9ab194b2d940eb6a`.
  Exact SHA matches both reports; Mach-O magic `0xfeedfacf`, arm64 CPU,
  raw subtype `0`, filetype `MH_EXECUTE`. Executable UUID
  `199de9bc-9006-3d40-9e75-86b85a5d958d` matches both reports.
- IPA has exactly two files (Info.plist and executable) under the correct
  `Payload/KaguraLab.app` path, with bundle ID
  `com.duodash.research.kaguralab` and iOS 15 minimum.
- `plain.o` and `protected.o` SHA-256 match the actual seven-pass
  evidence JSON; public marker remains in plain and is absent from protected.
- All seven `pass-{str,fla,bcf,sub,co,bbr,bbs}.log` SHA-256 hashes match their
  corresponding evidence records. Logs report the respective Kagura LLVM
  pass running, and the linked binary exports both `_dd_kagura_plain` and
  `_dd_kagura_protected`.
- Native-host reference log matches the independent Python oracle:
  parity `fa194ad0bc2c9f28` for 8,192 vectors and benchmark
  `1664c1fc632776a0` for 4,096 calls.
  `KaguraLab-runtime-reference.json` confirms the native-host
  reference step ran in CI (`native_host_reference_checked: true`).
- Separate Apple Clang arm64e dylib is **build-only**. No claim that VM,
  PAC, or the seven Kagura passes executed on arm64e hardware.

**Device status:** User independently reported that the K5 IPA ran and all
their device checks PASS. The uploaded CI artifact does not include a
user-shared eight-line parity / eleven-line timing schema-2 log. No
cryptographic device execution attestation, exact installed executable
comparison, or reproducible on-device performance figure was available to
this review. Therefore label this **USER_REPORTED_PASS**, not
`DEVICE_LOG_ATTESTED`.

**Scope:** Proven compiler pipeline and IPA artifacts apply only to the
standalone KaguraLab C canary. There is no inference about Crane runtime,
per-function protection of arbitrary Objective-C methods, or prevention
of reverse engineering.

Next: keep this K5 IPA as the known-good rollback; start separate
`Kagura K6 - Selective Real VM Canary (Experimental)` as a **manual-only**
native host + iOS arm64 build experiment. Do not co-apply VM to the known-good
K5 IPA or production Crane.
