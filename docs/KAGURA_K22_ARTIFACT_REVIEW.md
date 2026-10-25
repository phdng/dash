# K22 — kết quả xác minh ZIP hai lượt build macOS thực

Ngày review: **25/10/2026**. Trạng thái:
**REAL_MACOS_TWO_BUILD_OFFLINE_CODE_ARTIFACT_VERIFIED_NOT_RUNTIME_SECURITY**.

Artifact người dùng cung cấp:
`DuoDash-Kagura-K22-TWO-BUILD-REPRODUCIBILITY-OFFLINE-EXPERIMENTAL.zip`.

SHA-256: `f7f449e3929f78f42650c46925e37e884c8a4612713abd67bf604c8ce8b01c82`.
115 entries tên duy nhất, CRC hợp lệ: 57 tệp trong `build-a/`,
57 trong `build-b/`, 1 `Kagura-K22-REPRODUCIBILITY.json`.
**388/388 đối chiếu file-backed PASS** từ raw Mach-O, LC_UUID, text hashes,
K19 nlist, K20 function starts, K21 histogram và K22 manifest.

Bốn target intervals trùng chính xác code SHA-256:
macOS baseline `_dd_k8_evaluate` 460 byte / 115 words;
macOS protected `_dd_k8_evaluate` 544 / 136;
iOS protected `_dd_k8_evaluate` 544 / 136;
iOS `_dd_k14_ios_parity` 484 / 121.
Cả **ba executable Mach-O** (macOS baseline, macOS protected và iOS lab)
trùng byte giữa A/B, cũng như unsigned IPA K14. Bốn log native
(A/B baseline/CSEBreak) ghi 4096 vectors, checksum
`25a3318e3d7d6525`, `DD_K8_COMPLETE=PASS`.
Đây là hai chuỗi compile/link trên **cùng runner**, không phải hai runner
được attested. JSON/LLVM IR phụ thuộc đường dẫn có thể khác mà code
liên kết không khác.

**Đã đóng mốc nghiên cứu offline K13–K22**. Không có bằng chứng
từ ZIP về iPhone K22 runtime, anti-tamper, secure signer/trust root,
per-basic-block integrity, PAC hay Crane production. ZIP không chứa full
GitHub Actions run id/console state. K18 user-skipped (không giả PASS),
BBCheck K15 weak always-return-1 vẫn blocked.
