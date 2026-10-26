# Kagura K23 — artifact IPA thực, báo cáo FAIL từ iPhone và bản sửa chẩn đoán

Ngày review: **25/10/2026**. Người dùng đã cài và mở ứng dụng unsigned
`KaguraK23RuntimeLab-TrollStore-arm64.ipa`, nhưng thao tác Verify hiển thị
**FAIL với hai dòng không chỉ rõ nguyên nhân**. Đây là báo cáo người dùng,
**không phải log thiết bị được quan sát độc lập**. Không ghi runtime PASS.

Artifact ZIP người dùng gửi:
`DuoDash-Kagura-K23-IOS-RUNTIME-REFERENCE-LAB-EXPERIMENTAL.zip`.
SHA-256: `eba93a0b5e2f965c4addec02e06262e3ca5db550bf6b23a61496b42b7a844f06`.
Dung lượng ZIP 184800 byte, 65 entries tên duy nhất, CRC sạch.
Bản K23 unsigned IPA trong ZIP có SHA-256
`337b4144678558ef6067b6c602b3b92b56f5c1f241ed47fefffa925f86819a37`.

**Đối chiếu trực tiếp:** IPA gồm đúng 3 tệp: K23 executable, Info.plist,
`KaguraCSEBreakLab.reference`. IPA SHA khớp report, executable K23
SHA `67aaa2f64a7059ba71ca95fbf5b442fb3eec81b03c629db3cb83d10dfbf8ad8b`.
Tệp tham chiếu K14 có SHA
`584e9999d25a2642d818c0857a767173031868868df94d0e7de289176aa0cbd7`
và UUID `7c0cb853-77aa-3ccb-9f20-560e5f40e587`, đúng
`K23Expected.swift` trong artifact. Hai khoảng mã (offset/length/SHA)
đối chiếu bằng byte thực: 21588/484 với SHA
`10b05c44f7e87b150a453fe7dc7c64b2fd00ff672c0f747c709650d4271f1e0a`,
22072/544 với SHA
`81cba0a6201a018c0b48198aa3331ba0a265e45e3c12206b62ea9a5bec98ba97`.
Nlist/LC_FUNCTION_STARTS trong bản K21 trước đó nhất quán. Mach-O
K14 có 22 load commands, tổng 2976 byte, toàn bộ command size chia hết 8,
LC_UUID đúng 24 byte. Các số liệu này **không giải thích được lý do
iPhone FAIL**; bản IPA trên iPhone có thể có vấn đề lúc đọc asset hoặc
lúc chạy, không suy ra từ bản ZIP.

## Nguyên nhân kỹ thuật đã xác nhận và bản sửa

Mã K23 cũ gộp **mọi exception** thành:
`DD_K23_COMPLETE=FAIL` và
`DD_K23_ERROR=REFERENCE_RUNTIME_VERIFICATION_FAILED`.
Đây là khiếm khuyết chẩn đoán **đã xác nhận**, không phải bằng chứng
rằng CryptoKit, UUID hay hash đã sai.

Mã K23 cập nhật:
- kiểm tra CryptoKit SHA-256 vector `abc` trước khi đọc file;
- tìm resource bằng `Bundle.main.url`, có dự phòng file đúng tên trong
  bundle root nếu lookup thông thường không trả về URL;
- yêu cầu tài nguyên là regular file, không symlink;
- đọc với lỗi riêng, rồi **giữ nguyên toàn bộ đối chiếu SHA-256, UUID,
  hai code intervals, mutation/truncation negative controls**;
- xuất `DD_K23_ERROR=<stable-code>` ở trường hợp FAIL; không đặt PASS
  trên bất kỳ lỗi nào. Mã FAIL không tạo security/attestation claims.

**Bước cần kiểm chứng tiếp:** build IPA K23 sau bản sửa trên macOS,
gỡ ứng dụng K23 cũ, cài IPA mới, chạm Verify và chia sẻ nguyên văn 3
dòng FAIL nếu còn lỗi; nếu PASS thì xuất đầy đủ 10 dòng. Không yêu cầu
cài đặt K18, không bật BBCheck weak stub hoặc Crane production. Build
macOS đã có artifact thực; iPhone user-reported FAIL vẫn chưa được khắc
phục bằng bằng chứng thiết bị.
