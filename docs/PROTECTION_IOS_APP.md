# Protection Lab — ứng dụng UIKit để kiểm chứng trên iPhone thật

**Trạng thái:** ứng dụng nghiên cứu riêng; workflow tạo **IPA arm64 thử với TrollStore** cùng binary nghiên cứu arm64e **chỉ build/audit**. Không phải bản cập nhật Crane hay package jailbreak. IPA chưa được CI ký hoặc thử cài; build xanh không chứng minh ứng dụng chạy trên thiết bị. Xem [PROTECTION_TROLLSTORE_ARM64.md](PROTECTION_TROLLSTORE_ARM64.md).

## Thứ mới triển khai

- Giao diện UIKit có nút **Run 4 suites × 8192**, **Measure overhead
  (optional)** và **Share result text**; ban đầu hiển thị **NOT TESTED**,
  không tự chạy khi khởi động. Nút đo overhead **chỉ bật sau khi** bốn
  bộ kiểm tra chức năng PASS.
- Nút Run kiểm tra actual loaded Mach-O qua `_dyld_get_image_header(0)`,
  subtype `arm64=0` hoặc `arm64e=2` + ABI PAC phiên bản userspace;
  sau đó gọi đúng những hàm C đã có của VM / CE-ICALL / IGV-IBR
  và so sánh `NSString` ASCII + Unicode với ARC trong `@autoreleasepool`.
  Mỗi nhóm **8.192** vector. Nút Run chỉ báo `PASS` khi cả bốn nhóm
  đều thực sự chạy xong; lỗi trả về `DD_RUNTIME_ERROR=...`.
- Khi chia sẻ report, ứng dụng đưa ra đúng **7 dòng** sau, nếu toàn bộ
  check đều qua và binary thực là `arm64e`:

```text
DD_RUNTIME_CONTEXT=IOS_DEVICE
DD_RUNTIME_ABI=arm64e:0x80000002
DD_RUNTIME_VM_PASS=8192
DD_RUNTIME_CE_ICALL_PASS=8192
DD_RUNTIME_IGV_IBR_PASS=8192
DD_RUNTIME_OBJC_CE_PASS=8192
DD_RUNTIME_COMPLETE=PASS
```

Trên `arm64` dòng ABI phải là `arm64:0x00000000`. Kết quả
`MACOS_HOST` không được chấp nhận như kết quả iPhone.

Benchmark tùy chọn đo 5 cặp native/protected, mỗi cặp 20.000 lời gọi x
5 lần lặp, trung vị nanoseconds. Bản report benchmark **17 dòng** luôn
chia sẻ riêng, không gộp vào 7 dòng runtime. Chi tiết tại
[PROTECTION_PERFORMANCE.md](PROTECTION_PERFORMANCE.md).

**Sprint identity mới:** Sau khi chức năng PASS, nút Share có mục riêng
**Share binary identity / OS model**, tạo 7 dòng gồm UUID Mach-O đang
được loader nạp, ABI, model và phiên bản iOS. CI còn xuất
`build-identity.json` để so UUID arm64/arm64e đúng slice. UUID và log
không chứng thực mật mã nguồn gốc thiết bị. Xem
[PROTECTION_DEVICE_EVIDENCE.md](PROTECTION_DEVICE_EVIDENCE.md).

## Chạy trực tiếp với Xcode trên iPhone thật

Đã có project Xcode độc lập
`scripts/protection_lab/ios_xcode/ProtectionLab.xcodeproj`, scheme
`ProtectionLab`, **arm64** và automatic signing (chọn Apple Development
team của bạn trên Mac). Nó cho phép bấm Run trên iPhone dự phòng, không
cần thao tác ký thủ công bản ZIP unsigned. **arm64 chạy được trên A12+
không đồng nghĩa arm64e PAC runtime được xác nhận**. Chi tiết về ký/cài,
sinh header và lệnh kiểm tra UUID với binary Xcode *local*:
[PROTECTION_XCODE_DEVICE_TEST.md](PROTECTION_XCODE_DEVICE_TEST.md).

## GitHub Actions

Chạy thủ công **Protection Lab - iOS UIKit test app (Experimental)**,
file `.github/workflows/protection-ios-app.yml`.

Workflow thực hiện:
1. Chạy kiểm tra cấu trúc app/UI và các hồi quy VM, CE/ICALL, IGV/IBR,
   NSString/ARC và device runtime trước;
2. Sinh các header thử nghiệm chứa **hằng/chuỗi công khai**, không có bí mật;
3. Biên dịch bằng Apple Clang, iPhoneOS SDK, tối thiểu iOS 15;
4. Tạo **hai bundle khác nhau** `ProtectionLab-arm64.app` và
   `ProtectionLab-arm64e.app`, đóng gói ZIP `UNSIGNED`;
5. Kiểm tra từng Mach-O `MH_EXECUTE` với CPU subtype và userspace PAC ABI,
   tạo checksum, thư viện liên kết và báo cáo JSON. Không gọi codesign,
   devicectl, SSH, dpkg hay tạo tweak.

Artifact: `ProtectionLab-UIKit-OnDevice-UNSIGNED-arm64-arm64e`, nay có thêm `ProtectionLab-TrollStore-arm64.ipa`, `TrollStore-IPA-report.json` và `build-gates.json`. **arm64e build/audit PASS là mục tiêu hiện tại; runtime A12+ được hoãn.**

## Thử trên iPhone dự phòng

1. Tải artifact, kiểm tra SHA-256 và hai phần `build-report.json`.
2. Chọn IPA `ProtectionLab-TrollStore-arm64.ipa` để thử trên thiết bị arm64 đang có. Hai ZIP `UNSIGNED` được giữ làm artifact nghiên cứu; binary arm64e chỉ dùng kiểm chứng biên dịch/Mach-O trong CI. **Không suy ra arm64e từ tên package roothide**.
3. **Với thiết bị hiện tại có TrollStore**, tải `ProtectionLab-TrollStore-arm64.ipa`, mở tệp bằng TrollStore rồi kiểm tra có cài/chạy được không; IPA chưa được ký ở CI và việc cài thực tế **chưa kiểm chứng**. Nếu lỗi, giữ log chính xác. Cần iOS 15+ do deployment target. **Không thử bản arm64e khi chưa có thiết bị A12+**. Quy trình Xcode với Apple Development team ở dưới là lựa chọn thay thế, không còn là điều kiện bắt buộc cho IPA arm64.
4. Mở ứng dụng, xem trạng thái **NOT TESTED**, nhấn Run, xác nhận bốn
   phép thử xong. Nhấn **Share result text**, sao chép **nguyên văn**
   vào tệp UTF-8 không kèm tiền tố timestamp/log của ứng dụng khác.
5. Xác minh report đã thu, ví dụ:

```sh
python scripts/protection_lab/device_audit.py verify-log \
  --log iphone-arm64e-ui.txt \
  --arch arm64e \
  --out iphone-arm64e-ui-check.json
```

Parser chỉ xác minh đúng cú pháp/nội dung 7 dòng; **không xác thực nguồn
gốc log**. Giữ kèm tên thiết bị, iOS, môi trường ký, bundle/binary hash,
ảnh màn hình kết quả và thông tin binary thực chạy. Trên A12+ cần xác
nhận app **arm64e** thực sự được loader chấp nhận, không chỉ `arm64`
được chạy trên A12+.

**Giới hạn:** không phải VMProtect thương mại/SLLVM compiler pass;
CE XOR canary không phải mã hóa bí mật; không chứng minh chống reverse
engineering hay an toàn của toàn bộ Crane. Không bật kỹ thuật này trong
hook, constructor, daemon, SpringBoard hoặc XPC khi thiếu device proof.

Tham khảo kế hoạch tổng quát tại [OLLVM_SLLVM_VMP_ROADMAP.md](OLLVM_SLLVM_VMP_ROADMAP.md)
và hướng dẫn CLI runtime tại
[PROTECTION_DEVICE_RUNTIME.md](PROTECTION_DEVICE_RUNTIME.md).
