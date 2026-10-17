# Protection Lab — soát artifact CI người dùng gửi (17/10/2026)

## Nguồn và phạm vi

Người dùng gửi artifact `ProtectionLab-UIKit-OnDevice-UNSIGNED-arm64-arm64e (3).zip`
từ workflow `Protection Lab - iOS UIKit test app (Experimental)`.
Đã đọc **nội dung thật** của ZIP (gồm IPA và hai app ZIP lồng nhau), kiểm
tra Mach-O headers và tính SHA-256, so với `build-report.json`,
`build-identity.json` và `build-gates.json` trong cùng artifact.
Việc đối chiếu này độc lập với lời xác nhận app đã chạy tốt trên máy thật.

| Chứng cứ từ artifact | arm64 | arm64e |
|---|---|---|
| Mach-O | `MH_EXECUTE` | `MH_EXECUTE` |
| CPU subtype (raw) | `0x00000000` | `0x80000002` |
| Kích thước binary | 98.824 bytes | 115.208 bytes |
| Mach-O LC_UUID | `7ba6c16a-93ea-3ce7-af07-d8be36524382` | `469ac542-524e-3a53-a556-f3356f1cac94` |
| SHA-256 | `a6ff35df8793ec93a472c698dc5f4bbb4a1f580a5275daff7d134dd1dfdea058` | `da62cebc40ee593e6d63a1f82791d5501b085bbf7d4dffadd334e40e709acd89` |
| Phạm vi xác nhận | IPA chứa binary đúng hash | Apple-Clang build, versioned PAC subtype/UUID |

IPA `ProtectionLab-TrollStore-arm64.ipa` chứa đúng hai entry:
`Payload/ProtectionLab.app/Info.plist` và
`Payload/ProtectionLab.app/ProtectionLab`. SHA-256 IPA trong báo cáo là
`25cc953e40f060aa67089aab52c7a048cf12f156eda84d9ba60013ba55a4d975`;
hash binary trong IPA khớp binary `arm64` và báo cáo build.
`macho-arm64e.txt` cũng nhận dạng **ARM64 E USR00**, phù hợp raw
`0x80000002` (kiểm tra ABI userspace, **không phải chạy thử PAC**).

`host-performance-report.json` chỉ là kết quả benchmark
`MACOS_HOST`, không phải kết quả đo hiệu năng iPhone.

Người dùng đã xác nhận IPA arm64 cài được bằng TrollStore và toàn bộ
bốn nhóm test PASS trên thiết bị thật. Chưa có raw
`DD_RUNTIME`/`DD_EVIDENCE` được chia sẻ nên trạng thái kiểm thử thiết bị
ở mức **USER_REPORTED_PASS**, không phải independently attested.
Không ghi lại hoặc yêu cầu UDID.

**Chính sách:** arm64e hiện đã đạt điều kiện **build + Mach-O ABI +
UUID** trong artifact được gửi. A12+ runtime là
`DEFERRED_NO_DEVICE`; Crane OLLVM STRONG production không bị thay đổi.


## Artifact CI mới `(4).zip` và kết quả soak do người dùng xác nhận

Đã kiểm tra trực tiếp ZIP người dùng gửi ngày 17/10/2026,
`ProtectionLab-UIKit-OnDevice-UNSIGNED-arm64-arm64e (4).zip`.
Nó chứa 17 mục gồm IPA arm64, hai app ZIP, log `xcodebuild`, ba báo
cáo ABI/UUID/gate, report IPA và host performance. Trong
`xcode-arm64-build.log` có `** BUILD SUCCEEDED **`; **cả hai binary
đều chứa mã soak test mới** (marker `DD_SOAK_SCHEMA=1`,
`DD_SOAK_COMPLETE=PASS` và nút chạy 5 vòng).

| Kiểm tra thật trong artifact mới | arm64 | arm64e |
|---|---|---|
| Mach-O filetype | `MH_EXECUTE` | `MH_EXECUTE` |
| Raw CPU subtype | `0x00000000` | `0x80000002` |
| Kích thước binary | 116.336 bytes | 116.336 bytes |
| SHA-256 binary | `e082d29608779b6beb1b18fa14ca1908a839fed62c3bcb66adcfb1554cb5eb02` | `f6d58930c788216e1417576b91d3528ee97d0a11ad0c0dc2052bf6f9981dcd9f` |
| LC_UUID | `919f30eb-1629-3658-86fc-cc7da188a483` | `29654d8f-ab31-39fc-9a14-2eecc618e851` |

SHA-256 của IPA arm64 là
`5be6197265883db48575a93ba93f6d64e752c9ed9a3be204b1349aa2bcadcfa2`
và SHA-256 của ZIP tổng là
`99b0be3c56cf0186d9c1d522890844a436b72c96976febee8b975624521d7eb8`.
Binary arm64 trong IPA trùng byte với binary trong
`ProtectionLab-UNSIGNED-arm64.zip`, hash khớp
`build-report.json`, `build-identity.json`, `build-gates.json`.
`macho-arm64e.txt` cho `ARM64 E USR00`.

**Người dùng xác nhận tất cả bài test trong bản mới PASS trên iPhone.**
Điều này được lưu dưới dạng **USER_REPORTED_PASS** cho functional
suite và soak 5 vòng; chưa có tệp log `DD_SOAK_*` 12 dòng hoặc
`DD_RUNTIME_*` từ iPhone trong artifact để kiểm tra độc lập.
Không ghi UDID hoặc thông tin định danh thiết bị.

Receipt không chứa UDID:
[PROTECTION_ARM64_USER_REPORTED_ACCEPTANCE_2026-10-17.json](PROTECTION_ARM64_USER_REPORTED_ACCEPTANCE_2026-10-17.json).
**Soak runtime chưa được chứng thực bằng log**, và **arm64e chỉ
BUILD/AUDIT PASS, không có A12+ runtime**. Crane OLLVM STRONG
production giữ nguyên.

## Sprint kế tiếp

Đã bổ sung bài **soak thủ công** trong Protection Lab: 5 vòng liên
tiếp × 4 nhóm × 8.192 vector = **163.840 phép kiểm tra tổng cộng**,
chỉ bật khi lần chạy bình thường đã PASS. Nếu một nhóm sai, dừng ngay
và xuất lỗi có tên nhóm/vòng. Log 12 dòng `DD_SOAK_*` được chia sẻ
riêng, dùng `soak_audit.py` để kiểm tra nội dung.

Xem [PROTECTION_ARM64_SOAK.md](PROTECTION_ARM64_SOAK.md). Bước soak là
chức năng **mới** và chưa có kết quả chạy thật trên iPhone từ artifact
đính kèm; các PASS cũ không được dùng để suy ra soak PASS.
