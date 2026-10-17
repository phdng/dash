# KaguraLab — iPhone arm64 IPA với 7 LLVM pass thật

Ngày triển khai: 2026-10-17. **Đã thêm source, CI build/IPA và regression
portable. Chưa có kết quả build KaguraLab trên macOS CI hay chạy thiết bị thật.**

## Ứng dụng thử nghiệm riêng

Có **hai** workflow manual-only để lấy IPA. Đường nhanh khuyến nghị là
**KaguraLab - Real LLVM19 arm64 TrollStore IPA (Experimental)**,
chỉ biên dịch plugin, hai object và iPhone app, không chạy lại K3 host
benchmark. Workflow nghiên cứu **Kagura MAX Candidate - LLVM19 Pass Lab
(Experimental)** vẫn tạo IPA cùng nội dung sau K0/K1/K2/K3.
Cả hai đều tạo:

`out/KaguraLab-TrollStore-arm64.ipa`

KaguraLab có bundle ID `com.duodash.research.kaguralab`, khác với
ProtectionLab (`com.duodash.research.protectionlab`). Có thể cài
**song song** với bản ProtectionLab đã thử ổn; không liên kết hoặc
tải bất cứ dylib/hook/daemon Crane nào. Không ký, không cài lên điện
thoại từ CI và không thu UDID, serial, định danh quảng cáo, tài khoản
hay dữ liệu người dùng.

KaguraLab chỉ nhắm **iPhone arm64 iOS 15+**. Với cấu hình hiện tại,
mục tiêu thực tế là thiết bị arm64 TrollStore; **arm64e Apple Clang
PAC ABI v2 chỉ build/audit ở pipeline riêng**, không yêu cầu runtime
A12+, không ép đổi subtype.

## Vì sao IPA chứa pass thật

Cùng một `critical.c` được LLVM 19 biên dịch thành **hai** bản
LLVM IR bằng macro chọn tên hàm `DD_KAGURA_ENTRY`:

1. `dd_kagura_plain`: baseline, cùng compiler/optimization,
   không gọi Kagura `opt`.
2. `dd_kagura_protected`: LLVM IR đầu vào giống cùng mã hàm,
   được chạy qua **7 pass Kagura thật** bằng `opt
   --load-pass-plugin` với seed cố định:
   **STR → FLA → BCF → SUB → CO → BBR → BBS**.

Cả hai được compile thành object `arm64-apple-ios15.0` bằng
LLVM19 rồi link với Apple Clang vào **cùng MH_EXECUTE** và cùng UIKit
app. CI kiểm tra symbol xuất hiện, protected object phải khác plain,
chuỗi marker công khai biến mất khỏi **protected object**, và
`package_ipa.py` kiểm tra layout, Mach-O arm64, LC_UUID,
SHA-256 IPA/binary. **Plain object cố ý còn public marker**, nên
không được nói toàn bộ IPA không còn plaintext.

Ngoài báo cáo IPA, CI xuất `KaguraLab-seven-pass-evidence.json`.
Công cụ `ios_pipeline_audit.py` kiểm tra byte thật của hai object
`MH_OBJECT` arm64, marker plaintext còn trong baseline nhưng biến mất
khỏi protected, và **bảy `-debug-pass-manager` trace** phải chứa lớp
pass Kagura tương ứng. Cuối cùng so SHA-256 + LC_UUID của executable
đã audit với nội dung IPA. Nếu thiếu pass hoặc binary sai thì CI FAIL.
Parser IPA một mình **không được dùng làm bằng chứng** pass LLVM đã chạy.

**Không dùng các object host benchmark**, không lấy source canary C
giả làm LLVM pass, không gộp Hikari/OLLVM/SLLVM thương mại,
không thêm VM/PAC/anti-debug, và không sửa Crane STRONG production.

## Thao tác trên iPhone

Sau khi workflow build **xanh và kiểm tra IPA**, với workflow nhanh,
tải artifact **`KaguraLab-TrollStore-arm64-LLVM19-SEVEN-PASSES`**;
hoặc với workflow đầy đủ, lấy artifact
`DuoDash-Kagura-MAX-CANDIDATE-LLVM19-EXPERIMENTAL`. Giải nén lấy
`KaguraLab-TrollStore-arm64.ipa` rồi import thủ công vào TrollStore.

Mở **Kagura Lab**, nhấn:

- **Run 8192 Kagura vectors** — so trực tiếp
  `dd_kagura_plain(x,salt)` với
  `dd_kagura_protected(x,salt)` trên cùng 8192 đầu vào có tính
  xác định. Chỉ hiển thị PASS nếu tất cả trùng.
- **Measure Kagura overhead (optional)** — chỉ bật sau PASS,
  đo năm cặp mẫu (4.096 calls/mẫu) có đảo thứ tự plain/protected,
  phát hiện sai checksum; kết quả ns/call chỉ là **quan sát trên máy
  hiện tại**, không phải điểm bảo mật hay đánh giá cold-start.
- **Share Kagura test logs** — xuất riêng báo cáo chức năng và,
  nếu đã đo, báo cáo hiệu năng. Kết quả có thể dùng để so sánh với
  host benchmark, không phải chứng thực mật mã của thiết bị.

Báo cáo PASS dự kiến có đúng 7 dòng:

```text
DD_KAGURA_SCHEMA=1
DD_KAGURA_CONTEXT=IOS_DEVICE
DD_KAGURA_ARCH=arm64:0x00000000
DD_KAGURA_PIPELINE=STR_FLA_BCF_SUB_CO_BBR_BBS
DD_KAGURA_VECTORS_PASS=8192
DD_KAGURA_CHECKSUM=<16 ký tự hex thực tế>
DD_KAGURA_COMPLETE=PASS
```

Ví dụ phía trên là **định dạng**, không phải log lấy từ iPhone. Để
đối chiếu text báo cáo do bạn thực sự chia sẻ (7 dòng chức năng, có thể
kèm 10 dòng hiệu năng), lưu nguyên văn rồi chạy:

```sh
python scripts/custom_ollvm/kagura_max/ios_report_audit.py \\
  --log kagura-iphone-log.txt --out kagura-iphone-log-review.json
```

Việc khớp định dạng là bằng chứng nhất quán của text được gửi,
**không chứng thực thực thi hoặc nguồn gốc thiết bị bằng mật mã**.
Nếu
một vector không trùng, app ghi `DD_KAGURA_ERROR=MISMATCH_AT_n`
và không xuất `DD_KAGURA_COMPLETE=PASS`.

## Giới hạn nghiệm thu

Giao diện và IPA chỉ có thể được xác nhận compile/link qua **macOS
Actions**; hồi quy Python trên workspace không thay thế runtime của
LLVM19/iPhone. Chưa có IPA mới từ CI trong lượt này nên không được
ghi `IOS_DEVICE_PASS` trong registry.

Sự tương đương kết quả trên hàm thử nghiệm không chứng minh hiệu quả
trên tất cả hàm Objective-C hoặc khả năng ngăn dịch ngược. Kagura
`kagura_decrypt_*` sinh ở cùng TU vẫn có thể chịu function passes.
Chỉ bảo vệ TU `critical.c` thử nghiệm; chưa có strict per-function
allowlist trong plugin. Trước khi bảo vệ hàm Crane thật còn cần số liệu
overhead iPhone, kiểm soát ABI, scope, rollback và đánh giá IDA/Ghidra.

Nếu bản Kagura full 7 pass gặp lỗi link hoặc crash trên thiết bị,
không đổi pipeline Crane production hoặc ép bỏ phép kiểm tra; dùng
log CI và log on-device để sửa trên app lab riêng.
