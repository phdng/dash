# K7 KaguraVMLab — real CI IPA artifact review

Ngày kiểm tra: **2026-10-17**. Người dùng gửi
`KaguraVMLab-K7-TrollStore-arm64-REAL-LLVM19-VM-EXPERIMENTAL.zip`
và xác nhận **toàn bộ kiểm thử trong ứng dụng trên iPhone PASS**.

## Những gì đã kiểm tra từ ZIP thực

- SHA-256 ZIP:
  `fdaed5005fd5b3ccefa5bd9db1bcb12cc27a411c586c0afc144ac1d42e5f5a9f`.
  Kích thước **25.808 byte**, **11 entry**, ZIP CRC PASS.
- IPA `KaguraVMLab-TrollStore-arm64.ipa` SHA-256
  `ab5a6d21bd676e06585e95f61f9295207c55679a89502d8f2198df6dc605f6e5`.
  Bên trong chỉ có
  `Payload/KaguraVMLab.app/Info.plist` và
  `Payload/KaguraVMLab.app/KaguraVMLab`; ZIP CRC PASS,
  executable mode `0755`.
- Bundle `com.duodash.research.kaguravmlab`, executable
  `KaguraVMLab`, iPhoneOS minimum iOS 15, riêng biệt với K5
  `com.duodash.research.kaguralab`.
- Executable **93.992 byte**, SHA-256
  `03d5aa93901cb03b5ffe7f8c3e754ee4bd21b13bb353bfb832d75e43bb40904d`.
  Mach-O `MH_MAGIC_64`/`CPU_TYPE_ARM64`/raw subtype `0`/
  `MH_EXECUTE` với **22 load command** hợp lệ, **một** `LC_UUID`
  `15a45d46-f0da-37ff-855d-5e6ea078be8e`.
  SHA/UUID khớp cả `KaguraVMLab-IPA-report.json` và
  `Kagura-K7-IPA-EVIDENCE.json`.
- `ios-vm.ll` chứa một VM bytecode global 171 byte
  `kagura_vm_bc_3768774349` và call thật tới
  `kagura_vm_execute`; `ios-plain.ll` không chứa VM trampoline.
  IR của `dd_vm_guard_plain` và `dd_vm_guard_protected` giữ
  nguyên cùng phép toán, không VM. Pass manager **được gọi** trên cả
  protected và guard, nhưng **chỉ protected thực sự được biến đổi**
  theo allowlist.
- `ipa-app-symbols.txt` khai báo năm symbol:
  `_dd_vm_plain`, `_dd_vm_protected`,
  `_dd_vm_guard_plain`, `_dd_vm_guard_protected`,
  `_kagura_vm_execute`, bên cạnh hàm UI parity/benchmark.
  Đây là dấu vết liên kết do macOS CI tạo, không phải bằng chứng
  các hàm đã chạy trên iPhone.
- Đối chiếu SHA-256 thực của `ios-vm.ll`, `ios-plain.ll`,
  `ios-vm-opt.log`, `vm-native.log` với K7/K6 evidence JSON;
  SHA-256 của toàn bộ K6 JSON cũng khớp K7 evidence.
  Chú ý: ba object `ios-{plain,vm,vm-interpreter}.o` không nằm
  trong artifact upload nên chỉ có checksum được báo cáo bởi CI,
  **không đối chiếu được bytes object độc lập từ ZIP này**.
- `vm-native.log` trong artifact K7 khẳng định **4.096 macOS
  baseline/VM parity PASS**, checksum
  `9625f13d712f59c3` và guard `09d9d53ddf189ce7`.
  Ba cặp ns/call trên **macOS runner**:
  baseline `[4,3,4]`, Kagura VM `[188,188,187]`,
  tỷ lệ lần lượt `47×`, `62,67×`, `46,75×`;
  median tỷ lệ ghép cặp **47×**. Đây không phải benchmark iPhone.

## Kết luận chính xác

**K7 CI_ARTIFACT_HASHES_VERIFIED**: có IPA arm64 hợp lệ về định dạng,
bằng chứng compiler LLVM19 Kagura VM thực và parity trên macOS nhất quán.

**K7 USER_SHARED_TEXT_PARITY_AND_PERF_VALIDATED_NOT_ATTESTED**:
người dùng cung cấp thêm tệp `a.txt` nguyên vẹn, SHA-256
`355ecf8be195c9c925ce8d56fe1b78dd63f9e1dc2aa7f543d67d4bfbfefbc763`.
Đã đối chiếu **9 dòng parity + 14 dòng benchmark**, UUID app với
executable arm64 MH_EXECUTE và hai JSON từ chính CI ZIP, checksum
4096 vector do Python độc lập tính lại, cùng ba cặp timing iPhone:
native `[46,32,30]` ns/call, VM `[3742,1918,2145]` ns/call;
**median paired ratio 71,5×**. Kết quả khớp văn bản do người dùng cung
cấp, **không phải chứng thực thực thi trên thiết bị bằng mật mã**.
Đoạn paste trước đó bị mất ký tự vẫn là dữ liệu **bị từ chối**; `a.txt`
mới không bị lỗi. Xem
[KAGURA_K7_DEVICE_LOG_REVIEW.md](KAGURA_K7_DEVICE_LOG_REVIEW.md).

Không tự động thêm VM vào production Crane, các callback Objective-C,
SpringBoard, arm64e/PAC hoặc thay thế IPA K5 đã PASS. K7 hiện là mốc
canary chức năng, **chưa chứng minh an toàn hiệu năng** cho hàm nóng.
Hàm VM nhỏ, hiếm gọi mới là hướng thí nghiệm được phép.

Nếu có text log iPhone, lưu thành `k7-iphone-log.txt` và chạy
`scripts/custom_ollvm/kagura_vm/ios_device_log_audit.py` với
`--ipa-report KaguraVMLab-IPA-report.json` và
`--evidence Kagura-K7-IPA-EVIDENCE.json` để so claimed LC_UUID và
checksum. Kết quả log chỉ là đối chiếu nhất quán, không phải attestation.
