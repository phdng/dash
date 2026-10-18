# DuoDash K14 — artifact IPA thực và log thiết bị được chia sẻ

Ngày đối chiếu: **18/10/2026**. Trạng thái:
**IPA_AND_USER_SHARED_LOG_UUID_CHECKSUM_VERIFIED_NOT_ATTESTED**.

Đây là báo cáo từ **ZIP K14 thực người dùng cung cấp và 8 dòng log
được chia sẻ**, không phải fixture giả lập hay log tự tạo bởi CI.
Đã đối chiếu bytes thật qua ZIP, IPA lồng trong ZIP, load commands /
`LC_UUID` và `LC_SYMTAB` của Mach-O, SHA-256, IR/object K13,
hai native runner logs, nguồn Kagura đã pin và UUID/checksum của log.
**Không có quan sát thiết bị trực tiếp hoặc chứng thực mật mã**.

## Artifact chính

- ZIP: `DuoDash-Kagura-K14-CSEBREAK-IOS-ARM64-IPA-EXPERIMENTAL.zip`
- SHA-256 ZIP: `0ffbace0a56457a517bded16aa92d1a2e1455982901af5f39644c9140c87da47`.
- **53 thành phần**, tên duy nhất, ZIP CRC32 hợp lệ, không path
  traversal, symlink hoặc thành phần mã hóa.
- Đối chiếu độc lập **103/103 điều kiện PASS** trên dữ liệu gốc.
  Quy tắc kiểm tra bao gồm nguồn PassRegistry/Licence, checksum các
  tệp `.bc`, `.ll`, `.o`, bản trace chạy pass, thực sự biến đổi
  IR/object, bằng chứng native parity, iOS `LC_UUID`, `LC_SYMTAB`,
  cấu trúc và SHA IPA. Không thay thế bằng cờ PASS từ report.
- IPA unsigned: `KaguraCSEBreakLab-TrollStore-arm64.ipa`.
- SHA-256 IPA: `8733e2f93001b6d1195581deea013688825a94aa1d4d29bbfb23814dd5f9716f`.
- Executable SHA-256:
  `584e9999d25a2642d818c0857a767173031868868df94d0e7de289176aa0cbd7`.
  Binary trong `Payload/KaguraCSEBreakLab.app/KaguraCSEBreakLab`
  **trùng byte-for-byte** executable cùng tên nằm ngoài IPA trong ZIP.
- Bundle ID chính xác:
  `com.duodash.research.kaguracsebreaklab`.
  IPA chỉ chứa `Info.plist` và `KaguraCSEBreakLab`; cấu trúc,
  permissions, CRC, nền tảng iPhoneOS, iOS tối thiểu 15.0 đều hợp lệ.

## Mach-O iOS arm64 và pass độc lập

Trực tiếp từ final executable nlist:
- Mach-O **arm64 subtype 0 `MH_EXECUTE`**, đúng một `LC_UUID`.
- UUID:
  `7c0cb853-77aa-3ccb-9f20-560e5f40e587`.
- **Defined external** symbols:
  `_main`, `_dd_k14_ios_parity`, `_dd_k8_evaluate`.
  Không tìm thấy `_kagura_*` unresolved trong final executable.
- `ios-cse-break.o`, `ios-probe.o`, `ios-app-main.o`
  đều là Mach-O **arm64 subtype0 `MH_OBJECT`**, có các external
  definitions tương ứng trong symbol table thật.
- SHA protected `ios-cse-break.o`:
  `a1dea3f6cdb66d4f62d40dcfa7d32608049082700b2c78f7f69854c6b864cc62`,
  khớp hoàn toàn đối chiếu object từ
  `Kagura-K13-REPORT.json` trong ZIP.
- Kagura upstream commit theo report
  `ac2136ee0408677cf7cdee55307e9b16edd5f4d5`;
  `pinned-registry.def` thật có SHA
  `6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa`.
- Traces `macos-pass-manager.log` và `ios-pass-manager.log` có
  `kagura::CSEBreakPass`, `VerifierPass`, `BitcodeWriterPass`
  trên `dd_k8_evaluate`, `dd_k8_internal`. Lệnh
  `cse.mask`, `cse.break`, `cse.unmask` xuất hiện sau
  pass, không có trước pass. Cả IR normalized và object SHA có delta.
- Log CI native macOS ở **cả baseline và protected** ghi 4096
  vector, checksum đúng `25a3318e3d7d6525`, `COMPLETE=PASS`.
  Kiểm toán không chạy lại executable macOS ở môi trường này.

## Log iPhone do người dùng cung cấp

```text
DD_K14_IOS_SCHEMA=1
DD_K14_IOS_CONTEXT=IOS_DEVICE
DD_K14_IOS_ARCH=arm64:0x00000000
DD_K14_IOS_APP_UUID=7c0cb853-77aa-3ccb-9f20-560e5f40e587
DD_K14_IOS_PASS=CSE_BREAK
DD_K14_IOS_VECTORS=4096
DD_K14_IOS_CHECKSUM=25a3318e3d7d6525
DD_K14_IOS_COMPLETE=PASS
```

Tất cả **8/8 dòng chính xác theo schema K14**. UUID log **trùng
đúng `LC_UUID` trực tiếp trong binary iOS**, đồng thời khớp
`Kagura-K14-IPA-report.json` và
`Kagura-K14-IPA-EVIDENCE.json`. Checksum **trùng oracle
native K13 4096 vector**; số vector và pass đúng yêu cầu.
SHA-256 của bản log được chuẩn hóa xuống dòng `LF`:
`a145013d104fc83b0369a9ff21175ec5f6e4097eb739de8b98601e9aea4360d6`.
Đây là hash văn bản tạo từ 8 dòng được cung cấp (không phải file
log gốc được trích trực tiếp từ điện thoại).

**Điều được xác minh:** cấu trúc/nguồn build IPA chính xác và
**văn bản log do người dùng chia sẻ nhất quán với đúng binary**.
**Điều chưa được xác minh độc lập:** điện thoại thực sự chạy
binary hay ai/tác vụ nào phát sinh dòng log; không có record signed
device attestation; CI cũng khai báo
`ios_device_execution=NOT_TESTED_BY_CI`. Không được viết
`DEVICE_CRYPTOGRAPHIC_ATTESTATION_PASS`.

## Những giới hạn vẫn giữ nguyên

K14 là single-pass CSEBreak trên canary C công khai, không
đo benchmark bảo mật hoặc độ khó reverse, không thử ghép K11
năm pass với K14, không chứng minh Objective-C hooks hoạt động,
không có arm64e/PAC, không sửa Crane production.
K11/K12/K13 được ghi nhận độc lập theo những tiêu chí trước đó.
