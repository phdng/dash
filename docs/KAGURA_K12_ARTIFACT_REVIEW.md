# DuoDash K12 — Đối chiếu artifact thật và log 23 pass còn lại

Ngày kiểm tra: **18/10/2026**. Trạng thái:
**K12_PINNED_REGISTRY_AND_OPT_ARTIFACT_REPLAY_VERIFIED_NOT_NATIVE**.

Báo cáo này được lập từ **ZIP thật do người dùng cung cấp**, không từ
fixture 16 tên tổng hợp dùng thử parser. Đây chỉ là **đối chiếu artifact
bitcode/LLVM IR và màn hình opt-only**. Không có native executable parity,
IPA K12, iPhone runtime, arm64e/PAC hay tích hợp Crane production.

## Artifact đã kiểm tra

- File: `DuoDash-Kagura-K12-PINNED-REMAINING-PASS-INVENTORY-EXPERIMENTAL.zip`
- SHA-256 ZIP: `6d827807db583c8581d218da2dfc41f7fe784ea607dddd83edd399a04718b0ca`
- **147 entry duy nhất**, CRC32 ZIP sạch, không path traversal và không
  encrypted entry; **2.029 điều kiện kiểm tra file-backed PASS**.
- Commit Kagura **theo report CI**:
  `ac2136ee0408677cf7cdee55307e9b16edd5f4d5`.
- File nguồn `Kagura-K12-PINNED-PASS-REGISTRY.def` nằm trong ZIP,
  SHA-256 `6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa`
  khớp report inventory; report inventory SHA-256 khớp report opt.
- **36** named registered Kagura passes; **13** tên đã có bằng chứng
  giới hạn phạm vi từ K1/K5, K6/K7, K8–K11; **23** pass còn lại.
  Không phải 36 pass đều có chứng cứ runtime/native hoặc đang bật trong app.

## Kết quả K12 theo loại và độ thay đổi LLVM IR

Đây là kết quả **trên fixture K8 hiện tại và 2 target compiler**, không
tuyên bố pass nào luôn biến đổi được mọi ứng dụng. File `.bc` và
`.ll` được đối chiếu SHA-256 trên đĩa; khi so IR đã loại **chỉ**
dòng `ModuleID` ghi tên file bởi `llvm-dis`.

| Nhóm | Pass | Số tên | Kết quả |
| --- | --- | ---: | --- |
| IR delta trên **cả macOS và iOS arm64** | `kagura-tamper`, `kagura-anti-debug`, `kagura-honey`, `kagura-sv`, `kagura-cse-break`, `kagura-dci`, `kagura-telemetry`, `kagura-bbcheck` | **8** | `OPT_EXECUTED_IR_DELTA_UNVERIFIED` trên hai target |
| Không thấy IR delta trên fixture | `kagura-pac`, `kagura-str-aes`, `kagura-wstr`, `kagura-string-split`, `kagura-objc`, `kagura-jni`, `kagura-lt`, `kagura-pe`, `kagura-elt` | **9** | `OPT_EXECUTED_NO_IR_DELTA_UNVERIFIED` trên hai target |
| Infrastructure | `kagura-autoselect`, `kagura-config`, `kagura-dwarf-control`, `kagura-symmap`, `kagura-vtp`, `kagura-audit` | **6** | `SKIPPED_INFRA_NOT_AUTO_RUN` |

Trong 23 tên: **10 MOD, 7 FN, 6 INFRA**.
Ở các lượt screen ứng viên non-INFRA, có tổng cộng
**16 IR-delta target runs, 18 no-delta target runs**;
không có lỗi `opt` được ghi trong 34 lượt này. Mọi pass vẫn
`REGISTERED_UNVERIFIED` ở tiêu chí native/iPhone, kể cả 8 pass
có delta. Pipeline chỉ screen **từng** ứng viên độc lập, không chạy
23 pass nối tiếp hay chứng minh có thể ghép vào K11.

## Nguyên nhân lỗi audit trước đây, nay xác nhận bằng bytes thật

`ios-arm64-build-only-baseline.bc` bắt đầu bằng 20-byte wrapper:

```text
de c0 17 0b | 00 00 00 00 | 14 00 00 00 | a0 10 00 00 | ff ff ff ff
BC c0 de ... (raw LLVM bitcode at offset 20)
```

Cả **macOS và iOS baseline lẫn output** đều có LLVM wrapper hợp lệ,
không phải file rác. Auditor cũ chỉ chấp nhận raw `BC c0 de`
nên dừng sai ngay khi quét target iOS. Bản sửa `audit.py` cho
phép wrapper đúng chuẩn, kiểm version/offset/size, embedded magic và
SHA-256; **68 lượt kiểm tra format bitcode** trong phép đối chiếu
trên ZIP thật đều là wrapped bitcode hợp lệ (các baseline được dùng
lặp lại theo ứng viên).

## Giới hạn và giai đoạn tiếp theo

- Báo cáo ZIP **không chứa LICENSE upstream nguyên gốc**; upstream
  commit trong JSON là dữ liệu CI tự khai, chưa xác thực lại toàn bộ
  Git checkout từ bên ngoài ZIP. Nguồn `PassRegistry.def` thật trong
  ZIP đã được băm và so với report.
- Việc bitcode/IR có delta không chứng minh checksum runtime đúng,
  liên kết được các helper/pass runtime, LLVM optimizer tương tác an toàn,
  hay khả năng cài và chạy IPA trên iPhone.
- Các pass `anti-debug`, `tamper`, `honey`, `telemetry`,
  `pac` và infrastructure cần đánh giá runtime, quyền riêng tư,
  ABI và thiết bị riêng; không tự bật vào app.
- **K13:** từ 8 ứng viên delta, ưu tiên thẩm định độc lập một pass
  chỉ ảnh hưởng chức năng ở mức thấp như `cse-break` hoặc
  `bbcheck` (kiểm tra đủ điều kiện + symbol dependencies), sau đó
  xác minh native oracle/checksum, Mach-O iOS object, cuối cùng mới
  cân nhắc IPA lab. **Đã triển khai K13 ở trạng thái staged**:
  [CSEBreak native lab](KAGURA_K13_CSE_BREAK_NATIVE_LAB.md)
  chọn riêng `kagura-cse-break` với gate native 4096-vector và
  iOS arm64 `MH_OBJECT`. **Artifact K13 đã có và được kiểm chứng**:
  [review K13](KAGURA_K13_ARTIFACT_REVIEW.md) có 41 entry,
  422/422 điều kiện PASS và native macOS checksum parity.
  Đây là **một pass K13 đã có chứng cứ native macOS ở phạm vi lab**,
  nhưng **vẫn không có iPhone K13 PASS**, không được nhập chung
  với trạng thái kiểm kê/opt-only K12 của 23 pass.
- K11 IPA thực đã đối chiếu 331/331 trước đó là scope **riêng**,
  không bị thay bởi K12 opt-only.

Đối chiếu quy trình: [K12 remaining pass inventory](KAGURA_K12_REMAINING_PASS_INVENTORY.md).
