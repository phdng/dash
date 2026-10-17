# Protection Lab — kiểm thử runtime độc lập trên thiết bị iOS

Trạng thái: **workflow runtime CLI đã được người dùng xác nhận build xanh;
chưa có chứng cứ chạy trực tiếp trên iPhone trong phiên này**.
Để thử bằng giao diện UIKit thay cho terminal CLI, xem
[PROTECTION_IOS_APP.md](PROTECTION_IOS_APP.md).
Người dùng xác nhận các workflow Protection Lab trước đã build xanh; điều đó
**không chứng minh** arm64e/PAC đã được thực thi trên iPhone A12+.

## Workflow

Actions → **Protection Lab - iOS device runtime canary (Experimental)**
(`.github/workflows/protection-device-runtime.yml`) → Run workflow.

Workflow mới chỉ chạy thủ công, độc lập pipeline Crane. Nó:
1. Chạy kiểm tra Python cục bộ và các pilot trước;
2. Sinh 3 header từ *chuỗi công khai* và VM bytecode;
3. Biên dịch **10 module** C/Objective-C cho macOS host, chạy thực tế
   4 nhóm x **8.192 vector**, xác minh log `host-runtime.log`;
4. Biên dịch Apple Clang **hai iOS MH_EXECUTE riêng biệt**:
   `protection-device-arm64` và `protection-device-arm64e`;
5. Đọc Mach-O header, từ chối `arm64e.old`, ABI kernel/non-versioned;
   ghi SHA-256, các thư viện liên kết, build-report.json; upload artifact
   `ProtectionLab-iOS-DeviceRuntime-arm64-arm64e-EXPERIMENTAL`.

Bộ test **không** sign/provision/ssh/cài package/launch vào iPhone,
không tạo `.deb`, không thay đổi tweak Crane. Artifact **không phải ứng dụng
iOS đã ký/được phân phối**, và yêu cầu chuẩn bị riêng trên máy thử.

## Các nhóm test chạy trên iOS khi người dùng tự khởi động executable

- **VM:** cùng hàm C baseline/VM static bytecode/typed function pointer;
- **CE/ICALL:** so sánh hash trên public string và typed pointer dispatch;
- **IGV/IBR-inspired:** đối chiếu hai tầng global + state handler;
- **Objective-C NSString CE:** ARC, `NSString` equality, Unicode/UTF-8,
  autoreleasepool và vòng đời object.

Mỗi nhóm 8.192 vector. Nếu bất cứ vector nào sai, binary in
`DD_RUNTIME_ERROR=...` vào stderr và trả exit code khác 0. Chỉ khi
tất cả nhóm qua mới in `DD_RUNTIME_COMPLETE=PASS`.

Executable iOS tự đọc Mach-O của **main executable đã được nạp** qua
`_dyld_get_image_header(0)`, so CPU/subtype với kiến trúc lúc compile.
Với `arm64e`, bắt buộc subtype versioned PAC userspace. Điều này là
**kiểm tra ABI + thực thi logic**, không phải kiểm tra chống tấn công PAC
hay chứng minh mã sản phẩm Crane đã được bảo vệ.

## Hướng dẫn chạy thủ công (chỉ trên máy dự phòng)

1. Tải artifact, xác nhận `binary-sha256.txt` và `build-report.json`.
2. Chọn đúng binary: iPhone 6s (A9) dùng `arm64`; để xác nhận
   `arm64e` chọn iPhone A12+ và binary `arm64e` (không dùng tên
   package `iphoneos-arm64e` để suy ra CPU).
3. Dùng **cơ chế ký/trusted execution tương thích bootstrap đang có
   trên máy dự phòng**, cấp quyền chạy riêng cho canary, không thay thế
   bất kỳ file Crane hoặc tweak/dylib đang sử dụng. Nếu môi trường không
   cho chạy CLI executable đã ký, dừng và ghi lại lỗi code sign. Không
   tắt code signing, không patch subtype hay PAC chỉ để cho PASS.
4. Chạy executable từ terminal thiết bị bằng tài khoản có quyền phù hợp,
   lưu **stdout nguyên vẹn** và **exit code**. Không trộn stderr vào log
   thành công; ghi lỗi riêng. Đảm bảo `DD_RUNTIME_CONTEXT=IOS_DEVICE`,
   không phải `MACOS_HOST`. Sao chép `stdout` vào máy tính kiểm thử.
5. Với log thu trực tiếp, chạy:

```sh
python scripts/protection_lab/device_audit.py verify-log \
  --log iphone-arm64e-stdout.txt \
  --arch arm64e \
  --out iphone-arm64e-validation.json
```

Thay `--arch arm64` cho iPhone 6s. Parser đòi **đúng 7 dòng** theo
thứ tự: context, ABI, 4 test groups, COMPLETE. Ví dụ log arm64e:

```text
DD_RUNTIME_CONTEXT=IOS_DEVICE
DD_RUNTIME_ABI=arm64e:0x80000002
DD_RUNTIME_VM_PASS=8192
DD_RUNTIME_CE_ICALL_PASS=8192
DD_RUNTIME_IGV_IBR_PASS=8192
DD_RUNTIME_OBJC_CE_PASS=8192
DD_RUNTIME_COMPLETE=PASS
```

**Lưu ý:** Parser chỉ xác nhận *nội dung log được cung cấp* đúng định
dạng; không thể chứng thực log đến từ thiết bị thật. Bản runtime vẫn cần
lưu loại máy, OS, bootstrap, binary SHA và cách ký/execution riêng.
Kết quả host macOS không thay thế iOS PAC runtime.

## Điều kiện chuyển sang bảo vệ Crane thật

Chỉ cân nhắc tích hợp helper không quan trọng khi có các kết quả
đối chứng độc lập cho hai kiến trúc, không lỗi Objective-C lifetime/PAC,
không crash, có benchmark và rollback. Không tích hợp VM hay CE vào
constructor, hook runtime, daemon, securityd/XPC hoặc logic container
chính của Crane khi chưa có dữ liệu này.
