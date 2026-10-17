# Protection Lab — TrollStore trên arm64; arm64e chỉ build/audit

**Phạm vi đã thống nhất:** thiết bị hiện tại có TrollStore và chưa có
thiết bị A12+. Vì vậy, **arm64 được phép thử cài IPA bằng TrollStore**;
**arm64e chỉ cần Apple Clang compile/link PASS và kiểm tra Mach-O/UUID**
trong CI. Không có điều kiện chạy thật trên A12+ cho workflow này.

## IPA cho thiết bị hiện tại

GitHub Actions → **Protection Lab - iOS UIKit test app (Experimental)**
(`.github/workflows/protection-ios-app.yml`) → Run workflow.

Sau khi CI xanh, trong artifact
`ProtectionLab-UIKit-OnDevice-UNSIGNED-arm64-arm64e` có:

- **`ProtectionLab-TrollStore-arm64.ipa`** — cấu trúc chuẩn
  `Payload/ProtectionLab.app/Info.plist` và binary `ProtectionLab`.
  Không có certificate hay private key Apple trong repository, không có
  bước signing ở CI. Bộ đóng gói kiểm tra `arm64 MH_EXECUTE`, bundle ID,
  phiên bản iOS tối thiểu, executable bit, CRC và hash binary.
- `TrollStore-IPA-report.json` — trạng thái **structure PASS**,
  `trollstore_installation=NOT_TESTED`.
- `build-gates.json` — trạng thái tách biệt `arm64` IPA structure
  và `arm64e` compile/link/Mach-O/UUID gate.
- `build-report.json`, `build-identity.json`, `macho-*.txt`,
  `binary-sha256.txt`, 2 file ZIP nghiên cứu trước đây, log host.

Cách thử thủ công: tải `ProtectionLab-TrollStore-arm64.ipa` trên
iPhone đang có TrollStore, mở/Share tệp IPA bằng **TrollStore** rồi
cài ứng dụng lab độc lập. App này không yêu cầu đặc quyền, không đụng
tweak hoặc file Crane. Nếu TrollStore báo lỗi khi nhập IPA hay app không
mở, ghi **nguyên văn lỗi**, phiên bản iOS và TrollStore để sửa chính xác;
**IPA hợp lệ về cấu trúc không bảo đảm cài/chạy thành công**. Không
cần ép quyền truy cập hệ thống, thay đổi PAC, hoặc cài gói daemon.

**Tương thích:** IPA build với `MinimumOSVersion=15.0`; thiết bị hiện
tại phải chạy iOS 15 trở lên, và TrollStore phải tương thích đúng phiên
bản iOS đang dùng. Nếu bạn sử dụng iOS 14, bản IPA này chưa phù hợp
deployment target; không tự nhận là tương thích.

Sau khi app mở, có thể bấm **Run 4 suites × 8192** để thử các hàm
VM/CE/ICALL/IGV/IBR/ObjC trên `arm64`, và xuất ba báo cáo riêng
(7 dòng chức năng, 7 dòng LC_UUID/model/iOS, tùy chọn 17 dòng benchmark).
Các báo cáo chỉ có giá trị trên đúng thiết bị, binary và iOS được thử.
Nếu chưa cài/chạy, trạng thái vẫn là `NOT_TESTED`.

## Chính sách arm64e khi chưa có A12+

CI phải thực hiện đủ các bước kiểm tra kỹ thuật **không cần thiết bị**:

1. Apple Clang tạo/link `ProtectionLab-arm64e.app/ProtectionLab`.
2. Kiểm tra `MH_EXECUTE`, CPU ARM64, subtype `0x80000002`
   (versioned userspace arm64e PAC ABI); từ chối `arm64e.old`, kernel ABI
   và nhãn kiến trúc giả.
3. Đọc đúng một `LC_UUID`, SHA-256, dependencies và đối chiếu với
   `build-report.json` và `build-identity.json`.
4. **Chỉ khi toàn bộ bước trên PASS** mới ghi
   `arm64e.compiler_link_macho_abi_uuid=PASS` trong `build-gates.json`.

Không cần chạy binary `arm64e` trong TrollStore, không chờ iPhone A12+,
không sửa kiểm tra ABI để CI xanh. Report vẫn ghi:
`arm64e.a12_plus_device_runtime=DEFERRED_NO_DEVICE` và
`arm64e.pac_runtime_validation=NOT_TESTED`. Đó là trạng thái **đạt mục
tiêu build hiện tại**, không phải kết luận PAC runtime đã hoạt động.

Khi có máy A12+, mở lại [PROTECTION_IOS_APP.md](PROTECTION_IOS_APP.md)
và [PROTECTION_DEVICE_EVIDENCE.md](PROTECTION_DEVICE_EVIDENCE.md).
Đến lúc đó mới thử việc ký/cài/chạy `arm64e` và thu log thật.

## Phạm vi bảo vệ

Đây là Protection Lab, không tích hợp SLLVM proprietary, VMProtect
thương mại hoặc đổi đường OLLVM STRONG của Crane. Chưa commit/push
hay cài ứng dụng bằng tool trong phiên này.
