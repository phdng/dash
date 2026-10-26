# K23 — thử nghiệm iOS runtime kiểm tra tham chiếu Mach-O K14 trong bundle

Ngày tạo: **25/10/2026**. Trạng thái sau khi người dùng cài IPA:
**REAL_MACOS_UNSIGNED_IPA_ARTIFACT_VERIFIED_USER_REPORTED_DEVICE_VERIFY_FAIL**.
ZIP macOS K23 thực đã được kiểm tra raw bytes, nhưng trên iPhone
người dùng báo bấm Verify nhận 2 dòng FAIL chung. Đã sửa để phát mã lỗi
cụ thể trong lần build tiếp theo, **chưa có bằng chứng on-device PASS**.
Xem [KAGURA_K23_ARTIFACT_DEVICE_FAILURE_REVIEW.md](KAGURA_K23_ARTIFACT_DEVICE_FAILURE_REVIEW.md).
Tách riêng hẳn khỏi K18 user-skipped, K15 BBCheck weak-stub và Crane production.

## K22 đã đóng nghiên cứu offline

Artifact K22 thật đã được đối chiếu:
[KAGURA_K22_ARTIFACT_REVIEW.md](KAGURA_K22_ARTIFACT_REVIEW.md),
SHA-256 `f7f449e3929f78f42650c46925e37e884c8a4612713abd67bf604c8ce8b01c82`,
115 mục, 388/388 đối chiếu từ raw bytes. Bốn code intervals tái lập,
cả ba executable và IPA K14 trùng byte A/B. Đây **không** phải xác nhận
chống can thiệp trên thiết bị hay trust anchor.

## K23 làm gì khi iPhone chạy app

K23 tạo IPA **standalone unsigned** `KaguraK23RuntimeLab-TrollStore-arm64.ipa`;
không ghi đè IPA K14 và không thay đổi tweak, Theos, hooks, Makefile
hoặc OLLVM production. iOS 15+, arm64 subtype 0; không thử arm64e/PAC.
Không có ký/cài app tự động từ CI, user thực hiện test trên thiết bị
phù hợp theo quy trình riêng.

Trong workflow manual-only
`.github/workflows/kagura-k23-runtime-reference-lab.yml`, build lại K13
canary native + K14 IPA thật; replay K16/K19/K20/K21. Python
`scripts/custom_ollvm/kagura_k23/package.py prepare` rút SHA-256 toàn
executable K14, UUID và SHA của `_dd_k8_evaluate`,
`_dd_k14_ios_parity` từ `k21.verify` (không tin JSON ghi PASS). Nó
đóng `KaguraCSEBreakLab.reference` nguyên bản vào ứng dụng K23, tạo
`K23Expected.swift` có expected digest/offset/length biên dịch **vào
K23 executable** rồi Swift CryptoKit code thực hiện khi người dùng bấm nút.

Mỗi lần bấm **Verify + run tamper negative tests**:
- đọc K14 reference từ bundle, đối chiếu SHA-256 toàn file;
- kiểm tra Mach-O thin arm64 MH_EXECUTE và LC_UUID đúng;
- so SHA-256 từng vùng mã trong đúng offset/length đã được K21 đo;
- tạo bản copy trong RAM, flip byte đầu của một vùng mã rồi bắt buộc
  verifier **từ chối**;
- tạo bản copy bị cắt 1 byte, bắt buộc verifier **từ chối**;
- chỉ in `DD_K23_COMPLETE=PASS` nếu mọi positive và negative case đều
  đạt. Mất file/lỗi decode/mismatch đều in `DD_K23_COMPLETE=FAIL`.

Mẫu log dự kiến **10 dòng**, chỉ là kiểm chứng văn bản tự báo cáo, chưa
có independent attestation:

```text
DD_K23_SCHEMA=1
DD_K23_CONTEXT=IOS_DEVICE_USER_INITIATED
DD_K23_SCOPE=BUNDLED_REFERENCE_ONLY
DD_K23_REFERENCE_UUID=<real-K14-uuid>
DD_K23_REFERENCE_SHA256=PASS
DD_K23_CODE_INTERVALS=2
DD_K23_MUTATED_CODE=REJECTED
DD_K23_TRUNCATED_REFERENCE=REJECTED
DD_K23_SELF_INTEGRITY=NOT_IMPLEMENTED
DD_K23_COMPLETE=PASS
```

## Giới hạn cần giữ nguyên

**Đây là verifier *tham chiếu trong bundle*, KHÔNG phải runtime
self-integrity của executable K23/K14 đang chạy trong RAM.**
`K23Expected.swift` và K14 reference nằm trong cùng IPA unsigned; một
đối thủ sửa đồng thời app và dữ liệu có thể dựng lại hash. Hash compile
time không phải root of trust bất biến, không phải code signing, không
phải security anti-tamper hoặc kiểm chứng bất kỳ BBCheck production.
Không kiểm tra code sau ASLR/dyld, không quét trang thực thi, không có
independent on-device observation, PAC/arm64e/Crane protection.

**Tiêu chí nghiệm thu vòng sắp tới:** macOS CI cần build **lại K23
với mã đã sửa**, kiểm tra IPA/UUID/reference SHA. Người dùng gỡ K23 cũ,
cài IPA mới, bấm Verify: nếu còn FAIL, chia sẻ chính xác 3 dòng
`DD_K23_SCHEMA=1`, `DD_K23_COMPLETE=FAIL`,
`DD_K23_ERROR=<mã lỗi cụ thể>`; nếu PASS, chia sẻ đủ 10 dòng để đối
chiếu với artifact. Chưa được bỏ bất kỳ kiểm tra SHA/UUID/negative case
chỉ để ép PASS; khi có log hợp lệ, tiếp tục thử reinstall/rollback. CI PASS một
mình không đủ chứng minh runtime; nếu không có log thiết bị, giữ
`k23_iphone_runtime=NOT_TESTED`. Không mang cơ chế tham chiếu yếu này
vào Crane production.

Tiếp theo, để thực sự tiến đến production: cần thiết kế trust anchor
ngoài quyền kiểm soát của attacker, verifier có khả năng đối chiếu chính
executable/in-memory code và kiểm thử đối kháng + thiết bị, thay cho K15
weak always-return-1. **Chưa đạt những điều kiện đó ở K23.**
