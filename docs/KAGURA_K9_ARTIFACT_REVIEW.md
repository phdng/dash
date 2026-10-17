# DuoDash K9 — xác minh 5 pass Kagura phối hợp (17/10/2026)

Nguồn chứng cứ: ZIP người dùng gửi
`DuoDash-Kagura-K9-FIVE-PASS-COMPOSED-LLVM19-EXPERIMENTAL.zip`.

- SHA-256 ZIP: `9925f6ae0f95f2ec52ae53e7416723cd134de2e2e6fafc2ce6a3b58db5f96cf5`
- 129.771 byte, **75 entry**, `zipfile.testzip()` xác nhận CRC sạch.
- **179/179 phép đối chiếu độc lập PASS**, chạy trên nội dung thực các
  `*.ll`, `*.o`, `*-opt.log`, `native.log` và JSON báo cáo; không
  chấp nhận riêng tuyên bố `status: PASS`.
- Báo cáo: `Kagura-K9-COMPOSITION-REPORT.json`, schema 1,
  `K9_PINNED_KAGURA_FIVE_PASS_ONE_MODULE_COMPOSITION`,
  Kagura upstream pin `ac2136ee0408677cf7cdee55307e9b16edd5f4d5`.
- SHA-256 của các fixture thật trong Workspace khớp provenance của
  JSON: K8 C `39e0b833ab8574bf2e8abb2a66dc440d06424a82d6a0f371297e313bc91992fc`,
  K8 MVO IR `abbe02b364571b77fb94fff673111bf381f694211cca148d18a73650a8343e50`,
  K8 runner `4c1929802af256c6a7130e8f010e26f517f887a5b8dcbaad53434c6eb5bc2d6e`,
  K9 runner `b10fafa96bbe4e23aea2a5460fce86db8244a8b9a81314f2abe608b17e6afefc`.

## Thực thi *nối tiếp* trên cùng module

Module `macos/merged.ll` có đủ hai hàm
`dd_k8_evaluate` (từ C `-O1`) và
`dd_k9_mvo_probe` (từ MVO LLVM IR trực tiếp).
Tất cả năm bước áp dụng lên **output của bước trước**, không phải
năm lần chạy độc lập từ input đầu tiên.

| Stage thực | Pass upstream | macOS IR+object delta | iOS arm64 IR+object delta | Native hai hàm |
|---|---|---|---|---|
| 01 | MVO / `MemoryValueObfuscationPass` | PASS, `%mixed.mvo` / `%value.mvo` | PASS | PASS |
| 02 | GENC / `GlobalEncryptionPass` | PASS, `.dec` | PASS | PASS |
| 03 | FSPLIT / `FunctionSplitPass` | PASS, outline thành các hàm `__kg_*` | PASS | PASS |
| 04 | IBR / `IndirectBranchPass` | PASS, `__kagura_fptr_*` | PASS | PASS |
| 05 | CI / `CallIndirectionPass` | PASS, `__kagura_thunk_table`, runtime resolver | PASS | PASS |

Mỗi stage có trace đúng class, `VerifierPass`, hai public ABI còn,
IR thực khác bước trước và Mach-O object thực khác bước trước,
SHA-256 của `*.ll`, `*.o`, `*-opt.log`, `native.log`
khớp trường tương ứng trong JSON. Đã kiểm cả hash `previous_object`
của *stage trước* chứ không chỉ so hash bất kỳ.
Mọi `ios/*.o` và `xx-pass/ios.o` đều có header
`MH_MAGIC_64`, `CPU_TYPE_ARM64` raw subtype `0`,
`MH_OBJECT`, **build-only không thực thi trên iPhone**.

## Native parity

Log `plain-native.log` và cả năm `01-mvo/native.log` ...
`05-ci/native.log` **khớp từng byte**, có schema 1,
`4096` vector mỗi hàm, kết thúc `DD_K9_COMPLETE=PASS`:

```text
DD_K9_SCHEMA=1
DD_K9_VECTORS_PER_FUNCTION=4096
DD_K9_C_CHECKSUM=25a3318e3d7d6525
DD_K9_MVO_CHECKSUM=64e61045bbc4a250
DD_K9_COMPLETE=PASS
```

Checksum MVO khớp oracle Python độc lập từ K8.
CI giai đoạn cuối liên kết với đúng Kagura runtime archive.
K9 native đã hoàn thành; lỗi hậu kiểm JSON từng xuất hiện trước đó
chỉ do `json.dumps(sort_keys=True)` thay đổi thứ tự khóa,
không thay trình tự pass; artifact này có `stage_order` và
`stages[name].index` đúng 1..5.

## Cảnh báo thực tế từ `llvm-link` — chưa chặn native canary

`macos/llvm-link.log` ghi hai cảnh báo:

1. MVO module `mvo.bc` thiếu `target datalayout`; C module có
   `e-m:o-i64:64-i128:128-n32:64-S128-Fn32`.
2. Triple MVO host là `arm64-apple-darwin23.6.0` còn module C là
   `arm64-apple-macosx14.0.0`.

`ios/llvm-link.log` cũng cảnh báo `target datalayout` bị thiếu
trong MVO IR. Các cảnh báo này **không làm CI dừng và không gây
mismatch trên hai hàm/4096 vector của lần thử này**, nhưng cần
chuẩn hóa triple/data layout cùng module C trước khi thử ABI
phức tạp hoặc đóng gói IPA. Không được xóa cảnh báo bằng cách
lờ đi nguy cơ không tương thích.

## Phạm vi kết luận

**K9: MACOS_CI_ARTIFACT_VERIFIED_FIVE_COMPOSED_STAGES**. Đây là
một thứ tự cụ thể `mvo → genc → fsplit → ibr → ci`,
trên một module có hai hàm C/IR canary và 5 biến đổi thật;
**không** bao hàm mọi thứ tự, Objective-C runtime, Apple PAC,
Crane production hay sức chống reverse-engineering. iOS mới
cross-compile `arm64 MH_OBJECT`, **không** IPA/on-device runtime.
Chưa benchmark/đánh giá slowdown K9. K5/K7 và OLLVM STRONG hiện
hành được giữ nguyên.

Bước tiếp theo đã triển khai **riêng dưới dạng K10 staged**:
[KAGURA_K10_LINK_METADATA.md](KAGURA_K10_LINK_METADATA.md) đọc
`target datalayout` và `target triple` trực tiếp từ C bitcode
do Clang19 phát, gắn vào IR MVO tạm, rồi yêu cầu `llvm-link`
**không có cảnh báo** và chạy lại cả năm stage 2×4096 native.
Chưa có K10 macOS CI artifact, **không đổi kết quả K9 đã xác minh**;
sau đó mới xét ma trận thứ tự hoặc IPA lab riêng.
