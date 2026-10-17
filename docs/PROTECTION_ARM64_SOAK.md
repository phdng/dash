# Protection Lab — kiểm thử ổn định 5 vòng trên arm64 TrollStore

## Khi nào dùng

Ứng dụng standalone Protection Lab đã được người dùng xác nhận cài
và chạy đủ bốn suite PASS trên iPhone arm64. Sau khi build/cài bản mới
có thêm chức năng soak, nút **Run stability test (5 rounds)** chỉ bật
khi đã nhấn **Run 4 suites × 8192** và nhận `Runtime: PASS (4/4)`.

Soak chỉ chạy khi người thử tự bấm nút, **không tự chạy lúc khởi động,
không chạy lặp vô hạn, không có background service**. Việc tính toán
chạy trên queue riêng để UIKit không bị khóa, còn trạng thái màn hình
cập nhật trên main queue.

Mỗi vòng chạy **bốn nhóm**, mỗi nhóm 8.192 vector:
VM, CE/ICALL, IGV/IBR và Objective-C/ARC (qua autoreleasepool).
Năm vòng thành công tương đương **163.840 phép kiểm tra** (đếm theo
nhóm/vector). Điều này khác với **thử 163.840 đường đi độc lập**: hàm
kiểm thử gốc dùng input deterministic và cùng vector seed trên mỗi vòng.
Đây là bài **stability/reentrancy repeatability**, không phải fuzz test
nhiều seed, benchmark hay kiểm thử bảo mật PAC.

Khi một nhóm thất bại, app dừng bài soak ngay, hiển thị
`DD_SOAK_ERROR=<suite>:ROUND_<n>`, và **không in dòng COMPLETE=PASS**.
Trạng thái PASS của vòng functional test trước vẫn là kết quả độc lập.

## Báo cáo mới, không ghép vào báo cáo cũ

Bấm **Share result text** rồi chọn **Share stability/soak result**.
Báo cáo khi đủ năm vòng PASS đúng **12 dòng**:

```text
DD_SOAK_SCHEMA=1
DD_SOAK_CONTEXT=IOS_DEVICE
DD_SOAK_ABI=arm64:0x00000000
DD_SOAK_ROUNDS=5
DD_SOAK_VECTORS_PER_SUITE_PER_ROUND=8192
DD_SOAK_VM_ROUNDS_PASS=5
DD_SOAK_CE_ICALL_ROUNDS_PASS=5
DD_SOAK_IGV_IBR_ROUNDS_PASS=5
DD_SOAK_OBJC_CE_ROUNDS_PASS=5
DD_SOAK_TOTAL_VECTOR_CHECKS=163840
DD_SOAK_NOTE=MANUAL_STRESS_NOT_SECURITY_ATTESTATION
DD_SOAK_COMPLETE=PASS
```

Đây là **ví dụ định dạng**, không phải log thu từ iPhone. Báo cáo
soak tách khỏi 7 dòng `DD_RUNTIME`, 7 dòng `DD_EVIDENCE`, và
17 dòng `DD_PERF`. Không thu UDID/serial/tài khoản.

Khi có log thật trên iPhone, lưu nội dung nguyên vẹn rồi kiểm tra:

```sh
python scripts/protection_lab/soak_audit.py verify \
  --log iphone-arm64-soak.txt --arch arm64 \
  --out iphone-arm64-soak-review.json
```

Parser từ chối log thiếu/thừa dòng, số vòng sai, thiếu suite PASS,
nhầm macOS host/iPhone, sai kiến trúc và tổng vector bị sửa.
Parser **không thể chứng thực** báo cáo thực sự được tạo trên thiết bị,
và không bao giờ tự đánh dấu `arm64e` runtime PASS.

## Artifact mới và trạng thái

Dùng workflow thủ công
`Protection Lab - iOS UIKit test app (Experimental)` để build IPA
`ProtectionLab-TrollStore-arm64.ipa` mới. CI chạy
`scripts/test_protection_soak.py` trước compile, tiếp tục kiểm tra
Mach-O/UUID/SHA của cả `arm64` và `arm64e`. Sau khi CI xanh, có thể
cập nhật IPA arm64 bằng TrollStore trên máy hiện tại.

**Cập nhật 17/10/2026:** người dùng đã gửi artifact CI mới `(4).zip`
chứa đúng mã soak và xác nhận **tất cả bài test trên iPhone PASS**.
Đã kiểm tra SHA-256/LC_UUID/ABI của binary thật trong ZIP. Soak được ghi
nhận là **USER_REPORTED_PASS**; chưa có log soak 12 dòng để xác minh nội
dung hoặc nguồn gốc độc lập. Xem
[PROTECTION_CI_ARTIFACT_REVIEW.md](PROTECTION_CI_ARTIFACT_REVIEW.md)
và [receipt không chứa UDID](PROTECTION_ARM64_USER_REPORTED_ACCEPTANCE_2026-10-17.json).
Cả hai workflow CI và soak này không sửa package/hook/daemon của Crane.

## Khi nào đủ điều kiện tiếp theo

Nếu soak PASS trên thiết bị hiện tại, xem thêm kết quả benchmark
native/protected và nhiệt độ/độ ổn định của máy (chỉ theo thông tin
người thử tình nguyện ghi lại, không tự thu nền). Sau đó mới cân nhắc
một helper **thử nghiệm, không trọng yếu và có thể rollback**, luôn
giữ pipeline Crane OLLVM STRONG production ổn định. Việc tích hợp
Crane cần sự cho phép rõ ràng, không suy ra từ PASS của app lab.

A12+ chưa có; `arm64e` **tiếp tục chỉ build + ABI/UUID audit**.
