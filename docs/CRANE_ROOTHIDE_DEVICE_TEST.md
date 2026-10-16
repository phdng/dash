# Crane Demo – kiểm thử runtime trên iPhone 6s / iOS 15.8.8 (roothide)

## Trạng thái được xác nhận

- **Build CI / package:** PASS theo báo cáo CI của người dùng, scheme `roothide`,
  Debian Architecture `iphoneos-arm64e`.
- **Cài đặt:** người dùng xác nhận cài đặt được trên iPhone 6s iOS 15.8.8.
- **Biến đổi mã tại lúc biên dịch:** OLLVM ghi đúng 8 sự kiện: 4 pass
  (SPLIT / BCF / FLA / SUB) cho mỗi hàm
  `CRCreditsOpenTwitter` và `CRCreditsLocalizedRows`.
- **Phạm vi:** chỉ `arm64` của `CRCredits.m` được LLVM19 + OLLVM;
  `arm64e` của cùng file dùng Apple Clang. iPhone 6s (A9) là thiết bị
  arm64; metadata package `iphoneos-arm64e` của roothide không phải CPU.
- **Runtime người dùng báo (16/10/2026):** bản OLLVM roothide trước khi
  tăng cấu hình đã **hoạt động bình thường trên iPhone 6s**. Đây là xác nhận
  tổng quát, chưa điền riêng kết quả D02–D09, chưa có crash/benchmark log.
- **OLLVM STRONG mới (16/10/2026):** người dùng xác nhận build PASS,
  ứng dụng vẫn hoạt động đúng chức năng, IDA đã quan sát thấy làm rối mã
  trên binary. Đây là đánh giá tổng quát người dùng báo, **chưa phân tích
  riêng D01–D09, chưa benchmark hoặc thử arm64e/PAC trên A12+**.
- **Chưa xác minh:** từng kịch bản UI cụ thể, runtime trực tiếp của từng
  helper, daemon/hook/container data và thử nghiệm PAC/arm64e thực.

SHA-256 báo cáo (CranePrefs, cùng kích thước 494960 byte):
- Baseline: `0310754a4a3635f8315b453eea9b5b7575a6cf682cca9d8978786b91331177e4`
- OLLVM: `41443b0d7fab918582aa17ac813cd155147af9ad5c586b8030a3b1cfd8fbf48c`

**Khác SHA-256 không tự chứng minh mã chạy hay độ an toàn/hiệu quả bảo vệ.**
Cũng không đồng nghĩa tất cả chức năng reconstruction đã hoàn chỉnh.

## Bài test ưu tiên — không sửa dữ liệu ứng dụng

Chỉ dùng thiết bị dự phòng đã sao lưu và giữ bản đã chạy ổn định trước
để rollback khi kiểm thử các profile mới hơn STRONG. Không cài đồng thời
baseline/OLLVM hoặc các biến thể cùng Package ID. Người dùng báo STRONG hoạt
động đúng tổng thể, nhưng **D02–D07 vẫn cần ghi PASS theo từng tình huống**;
không tự điền khi chưa có kết quả cụ thể.

| ID | Thao tác | Kết quả mong đợi | Kết quả thực tế |
| --- | --- | --- | --- |
| D01 | Xác nhận thiết bị và dpkg, không sửa cấu hình | iPhone 6s / 15.8.8 / roothide; package đã ở trạng thái installed | CHƯA TEST |
| D02 | Mở Settings, tìm mục Crane | Có mục Preferences, không thoát đột ngột | CHƯA TEST |
| D03 | Mở trang Crane / Credits & Licenses | Hiển thị tiêu đề, specifier và nhãn đã bản địa hóa; không treo | CHƯA TEST |
| D04 | Mở trang ZipArchive License rồi quay lại | Chi tiết giấy phép hiển thị, nút Back hoạt động | CHƯA TEST |
| D05 | Mở trang MiniZip License rồi quay lại | Nội dung hiển thị, nút Back hoạt động | CHƯA TEST |
| D06 | Thử liên kết GitHub/author công khai, nếu muốn | Mở URL hợp lệ hoặc fallback web; không crash Settings | CHƯA TEST |
| D07 | Vào/ra Credits 3 lần, chuyển app rồi quay lại | Không treo, không mất Settings entry, không phát sinh lỗi rõ ràng | CHƯA TEST |
| D08 | So sánh với **baseline roothide** cùng thiết bị | Khác biệt giao diện/crash/lỗi chỉ có trên bản OLLVM được ghi nhận | CHƯA TEST |
| D09 | Kiểm tra daemon, switch container, hook riêng | Chưa dùng để kết luận OLLVM ổn định; reconstruction có phần chưa hoàn thiện | CHƯA TEST |

Các thao tác kiểm tra thông tin có thể chạy trong terminal của **đúng
bootstrap roothide**, không dùng để sửa system hoặc khởi chạy daemon:

```sh
uname -m
sysctl -n hw.machine
dpkg --print-architecture
dpkg-query -W -f='${Package} ${Status} ${Architecture} ${Version}\n' com.opa334.cranereconstruction
```

Nếu câu lệnh `dpkg-query` không có trên môi trường cụ thể, dùng
`dpkg -s com.opa334.cranereconstruction` để đọc metadata; không cần cài
thêm công cụ. Thông tin dpkg phải được đọc từ cùng bootstrap đã cài demo.

## Cách ghi nhận lỗi

Ghi lại mã test (ví dụ D04), thao tác vừa làm, màn hình trước/sau, kết quả,
nếu Settings tự thoát thì ghi crash time và tên process. Nếu có log, **xóa
tokens, danh tính tài khoản, thông tin container và dữ liệu cá nhân trước
khi chia sẻ**. Đừng thử chuyển container/xóa ứng dụng để chứng minh OLLVM
khi chưa có baseline runtime khỏe và bản sao lưu.

## Kết luận có thể đưa ra

- **Installation PASS**: chỉ khi package manager báo cài thành công; hiện
  là kết quả người dùng trực tiếp xác nhận, không phải kiểm tra tự động.
- **Build/pass audit PASS**: đã có báo cáo CI với 33 đường dẫn trùng và 8
  lượt pass, mã trên arm64 đã qua LLVM19.
- **Runtime người dùng báo**: bản OLLVM cũ hoạt động bình thường;
  chưa xác minh riêng từng tình huống D02–D07.
- **Runtime Credits STRONG PASS**: chỉ sau khi D02–D07 đạt trên bản STRONG.
- **OLLVM runtime parity PASS**: chỉ sau so sánh D02–D08 trên baseline và
  bản OLLVM ở cùng bootstrap/thiết bị.
- **Full Crane reconstruction PASS**: không thể kết luận từ bộ thử Credits.

Không đưa package thử nghiệm lên môi trường chính hay công bố là bản production.
