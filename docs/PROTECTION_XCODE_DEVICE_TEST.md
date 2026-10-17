# Protection Lab — chạy iPhone trực tiếp bằng Xcode (arm64)

**Trạng thái:** Project Xcode độc lập đã được tạo trong workspace; workflow
kiểm tra project bằng `xcodebuild` được bổ sung nhưng **chưa chạy trên
macOS trong lượt này**. Người dùng xác nhận workflow UIKit/UUID trước
build xanh, **chưa cung cấp log thiết bị A12+ chạy thực**.

## Lý do có project riêng

Các artifact trước là bundle `UNSIGNED` tạo bằng Apple Clang, không thể
bấm Run trực tiếp từ Xcode. Project mới cho phép nhà phát triển **chọn
Apple Development team của mình trong Signing & Capabilities** rồi
build/run app test trên một iPhone dự phòng. Không có tài khoản, certificate,
provisioning profile, UDID hoặc private key nào được ghi trong repository.

Đường dẫn:

`scripts/protection_lab/ios_xcode/ProtectionLab.xcodeproj`

Scheme: **ProtectionLab** — iPhoneOS, tối thiểu iOS 15, **arm64**,
UIKit/Foundation/ARC. Dùng lại 12 tệp C/Objective-C của các pilot trước;
build phase tạo **3 header canary từ dữ liệu công khai** vào Xcode
`DERIVED_FILE_DIR` (không chép đè source hoặc sinh file trong Crane).

## Chạy thực tế trên iPhone dự phòng

1. Trên Mac có Xcode, mở `ProtectionLab.xcodeproj`.
2. Chọn target **ProtectionLab** → **Signing & Capabilities** → chọn
   Apple Development team bạn có quyền sử dụng. Giữ **Automatically manage
   signing**. Nếu Xcode báo bundle identifier đã được dùng hoặc không
   thuộc team, đặt một identifier duy nhất của bạn ở target **và**
   `ios_app_Info.plist` (hiện cùng là
   `com.duodash.research.protectionlab`). Không commit Apple team ID,
   provisioning profile hoặc private key.
3. Chọn đúng iPhone đã kết nối trong destination (không phải Simulator),
   đảm bảo có quyền chạy ứng dụng phát triển. Bấm **Run**.
   Nếu ký/cài bị từ chối, đọc thông báo Xcode, **không sửa Mach-O
   subtype, không strip PAC, không tắt code-signing** để ép chạy.
4. Trong app, bấm **Run 4 suites × 8192**. Nếu PASS, tùy ý bấm
   **Measure overhead** rồi chia sẻ riêng 7 dòng chức năng,
   7 dòng binary identity, 17 dòng benchmark (tùy chọn).
5. Với log identity và parity vừa xuất, đối chiếu với đúng **binary
   local Xcode đã build/cài** (không dùng `build-identity.json` của
   workflow Apple Clang, vì linker có thể sinh một LC_UUID khác):

```sh
python scripts/protection_lab/device_evidence.py verify-local \
  --binary "/path/to/DerivedData/Build/Products/Debug-iphoneos/ProtectionLab.app/ProtectionLab" \
  --arch arm64 \
  --identity iphone-identity.txt \
  --parity iphone-parity.txt \
  --out iphone-local-xcode-review.json
```

Thêm `--performance iphone-perf.txt` nếu có kết quả benchmark.
`verify-local` đọc CPU subtype, Mach-O `LC_UUID` và SHA-256 của
binary local, kiểm tra các log và xuất JSON. Kiểm tra này xác nhận
**nội dung tài liệu khớp nhau**, không chứng thực cryptographic rằng
ứng dụng thực sự chạy trên máy đó.

## Khác biệt arm64 và arm64e

Project Xcode này **cố ý nhắm arm64**, cấu hình phổ biến để Xcode quản
lý ký/cài cho ứng dụng developer. Trên iPhone A12+ một binary arm64
có thể chạy thành công, nhưng đó **không phải bằng chứng thực thi bản
arm64e/PAC**. Không đổi `ARCHS=arm64e` hoặc patch header để lấy một
PASS giả.

Để nghiên cứu Apple Clang **arm64e versioned PAC ABI**, tiếp tục dùng
cặp binary riêng từ workflow thủ công
`.github/workflows/protection-ios-app.yml`. Việc ký và thực thi
`arm64e` còn phụ thuộc iPhone, iOS, toolchain và môi trường ký phù hợp;
nếu không chạy được thì ghi `NOT_TESTED`, không suy luận từ arm64.

## Kiểm thử trong GitHub CI

Workflow **Protection Lab - iOS UIKit test app (Experimental)**:
chạy `plutil -lint` trên project, gọi

```sh
xcodebuild -project scripts/protection_lab/ios_xcode/ProtectionLab.xcodeproj \
  -scheme ProtectionLab -configuration Debug \
  -destination 'generic/platform=iOS' -sdk iphoneos \
  CODE_SIGNING_ALLOWED=NO build
```

và kiểm tra Mach-O arm64 thực; job này **không ký/cài ứng dụng**. Mục
tiêu là phát hiện lỗi project, build phase sinh headers, ObjC/ARC và
liên kết UIKit. Mã arm64e vẫn build/audit trong nhánh riêng của workflow.

## Giới hạn

App này là test fixture, không phải tweak Crane và không tích hợp plugin
SLLVM hoặc VMProtect thương mại. Chỉ cân nhắc triển khai helper production
sau khi có dữ liệu runtime thiết bị thực, overhead và rollback đủ rõ.
Không đụng vào SpringBoard, daemon, securityd, Substrate, hooks hay bootstrap.
