# K7 — KaguraVMLab real Kagura VM iPhone arm64 IPA pilot

State on 2026-10-17: **real K7 macOS CI IPA independently inspected and original device text attachment `a.txt` now strictly validated against exact executable UUID, 4096-vector checksums and 3 iPhone timing pairs**. Earlier pasted text was truncated/rejected, but the new 809-byte attachment has complete 9+14 canonical lines. Device text is user-shared evidence, **not cryptographic device attestation**. The observed median paired VM overhead is **71.5×** on this single iPhone fixture; no VM production rollout. See [K7 artifact review](KAGURA_K7_ARTIFACT_REVIEW.md) and [device text review](KAGURA_K7_DEVICE_LOG_REVIEW.md).

## Rationale and isolation

K6 host and iOS build-only evidence is verified from the user-shared ZIP:
[K6 artifact review](KAGURA_K6_ARTIFACT_REVIEW.md). Because VM overhead
averaged about 48× in a small 3-pair macOS microbenchmark, K7 tests
**exactly one pure C function** through a true upstream Kagura LLVM19 VM.
No production Crane tweak, Objective-C method, hook, app identifiers, device
identifiers, license key, PAC-sensitive pointer or user data are accessed.

New standalone arm64 UIKit app:
- Executable `KaguraVMLab`; bundle ID
  `com.duodash.research.kaguravmlab`.
- Separate from K5 `com.duodash.research.kaguralab` (existing K5
  remains known-good and installable side-by-side).
- Pin `qusamulab/kagura` commit
  `ac2136ee0408677cf7cdee55307e9b16edd5f4d5` with MIT LICENSE,
  build LLVM19 plugin from source on macOS-14 CI.
- Compile same `vm_canary.c` to two iOS arm64 objects using the same
  LLVM19 clang and `-O1` input IR: `dd_vm_plain` (no VM pass) versus
  `dd_vm_protected` (real
  `-kagura-vm -kagura-allow=dd_vm_protected
  -passes=function(kagura-vm),verify`). Guard symbols are native in
  both objects. Actual `vm_interpreter.c` is compiled with Apple Clang
  for arm64 and **linked into the app executable**, with no runtime
  library dependency shipped separately.
- CI must rerun K6 native parity on macOS before packaging. App evidence
  requires VM bytecode/trampoline and host K6 proof, same-TU guard
  unchanged, exact arm64 `MH_EXECUTE`, LC_UUID, binary/IPA SHA-256 and
  required exported VM/runtime function symbols; rejects arm64e and
  malformed/extra IPA ZIP files.
- No CI signing, automatic install, device execution, root Theos
  Makefile change or merging with other plugins. No claim of cryptographic
  execution attestation or reverse-engineering immunity.

## Build and device trial

From the GitHub Actions **Actions** tab, manually run

`Kagura K7 - Real VM iPhone arm64 TrollStore IPA (Experimental)`

Artifact thực đã được cung cấp và đối chiếu:
`KaguraVMLab-K7-TrollStore-arm64-REAL-LLVM19-VM-EXPERIMENTAL`.
Kết quả device PASS do người dùng báo: trước đây không có log trong CI ZIP và đoạn text dán bị lỗi, nhưng sau đó đã nhận tệp `a.txt` nguyên vẹn, UUID/checksum và benchmark 3 cặp đều qua kiểm tra. Đây là kiểm chứng tính nhất quán từ text người dùng chia sẻ, không phải attestation thiết bị. Xem [kiểm tra log](KAGURA_K7_DEVICE_LOG_REVIEW.md).

Only if the job is green and the artifact contains exact evidence JSON,
download `KaguraVMLab-TrollStore-arm64.ipa`. Import through TrollStore
on a spare physical iPhone arm64 running iOS 15+, keeping K5 installed
separately as rollback. UI will offer:

1. **Run 4096 VM vectors**. This compares actual baseline/VM and native
   guard and checks independent fixed reference checksums.
2. **Measure VM overhead (optional)** only after parity PASS. Three
   alternating pairs of 1,024 calls, observational on that iPhone.
3. **Share K7 VM test log**. The text includes the *executing*
   `LC_UUID`, parity/guard results, and optional per-pair timings.
   No UDID, persistence, telemetry or network export.

Parity report has **9 lines**, optional benchmark **14 lines**.
Expected parity checksum `9625f13d712f59c3` and guard checksum
`09d9d53ddf189ce7`. If the VM result mismatches or app crashes,
report FAIL, don't relabel CI as iPhone PASS. The C app fails closed on
unexpected UUID, checksum, ABI and sample mismatches.

After sharing the text, save it as `k7-iphone-log.txt` and copy the two
matching CI JSON files. Check:

```sh
python3 scripts/custom_ollvm/kagura_vm/ios_device_log_audit.py \
  --log k7-iphone-log.txt \
  --ipa-report KaguraVMLab-IPA-report.json \
  --evidence Kagura-K7-IPA-EVIDENCE.json \
  --out k7-iphone-log-review.json
```

This verifies checksum and **claimed** executable UUID against the IPA
and CI evidence. It cannot prove the sender's device or code execution
cryptographically. iOS arm64e/PAC execution stays untested.

K7 is an opt-in research app; do not replace the stable K5 IPA or deploy
VM into Crane production based only on this pilot.
