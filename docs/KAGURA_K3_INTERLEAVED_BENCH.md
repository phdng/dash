# Kagura K3 — benchmark đối chứng nhiều vòng, cân bằng thứ tự

Cập nhật: 2026-10-17 · **Mã K3 và regression portable đã triển khai; chưa có artifact macOS native K3.**

## Lý do

K2a đã có artifact native macOS xác minh 7/7 pass giữ parity, sentinel TU
không bị pass biến đổi và báo cáo 11 mẫu mỗi phiên bản. Nhưng **p95
nearest-rank với 11 mẫu chính là giá trị lớn nhất**, vì
`ceil(0,95 × 11) = 11`. Riêng BBR có outlier 144 ns/call khiến p95
từ một lượt CI khó diễn giải.

K3 tập trung vào **độ ổn định của phép đo**, không phải thêm một pass
hoặc tăng điểm bảo mật.

## Thiết kế phép đo

Workflow thủ công `Kagura MAX Candidate - LLVM19 Pass Lab
(Experimental)` sử dụng 8 executable K2a đã link từ cùng LLVM19 và
bench runner: **baseline, STR, FLA, BCF, SUB, CO, BBR, BBS**.

`interleaved_benchmark.py` chạy **16 vòng**:

- 8 vòng đầu: xoay thứ tự 8 executable; mỗi biến thể đứng ở mỗi vị trí
  từ đầu đến cuối **chính xác một lần**.
- 8 vòng sau: xoay theo chu kỳ thứ hai rồi **đảo chiều** thứ tự; mỗi
  biến thể lại đứng ở mỗi vị trí đúng một lần.
- Mỗi executable mỗi vòng: 2 warmups và **11 mẫu × 32.768 calls** như
  benchmark K2a. Tất cả biến thể đều phải có cùng checksum đầu ra.
- Tổng: **128 lượt khởi chạy executable** và **176 mẫu/biến thể**,
  tức 1.408 mẫu thời gian và 46.137.344 calls tổng cộng.
- Chỉ xét p95 gần nhất sau khi gộp đủ 176 mẫu/biến thể:
  `ceil(0,95 × 176) = 168`, **không còn là mẫu lớn nhất**.
- Ghi median/p95 pooled, tỷ lệ so pooled baseline và **median của 16
  tỷ lệ median theo vòng đã ghép cặp**, cùng phạm vi min/max median
  theo vòng và số vòng vượt tỷ lệ 5×.

Cách xoay và đảo chiều là **counterbalanced order** tất định, không
phải random double-blind. Những mẫu trong cùng executable invocation
có thể có tương quan; thời gian trên shared runner vẫn chịu nhiễu,
frequency scaling và tác động nhiệt độ. Chỉ nhìn kết quả như một
**microbenchmark host tương đối**, không khẳng định hiệu quả thống kê,
startup, iPhone hoặc mức độ khó dịch ngược.

## Giao thức và kiểm tra

Tài liệu đầu ra mới:

- `out/stages/interleaved/round01-baseline.log` và các log
  `roundNN-{str,fla,bcf,sub,co,bbr,bbs}.log` (tổng 128 log);
- `out/stages/kagura-k3-host-interleaved.json` (thống kê và chi tiết
  mỗi vòng, SHA-256 log, SHA-256 executable);
- `out/stages/kagura-k3-host-reverified.json` (đọc lại toàn bộ log
  mà **không chạy executable**, so nội dung với báo cáo trước).

Parser dùng giao thức `DD_KAGURA_BENCH_*` đang hoạt động, từ chối
thiếu/thừa log, sai `MACOS_HOST`, thiếu mẫu, checksum khác nhau,
điều kiện PASS sai, hoặc directory còn dữ liệu từ lần cũ.
Test `scripts/test_kagura_interleaved_bench.py` dùng mẫu giả và
negative cases **chỉ để xác minh logic**, không phải số đo CPU thực.

**Không đặt ngưỡng overhead mặc định để đánh FAIL compilation**:
những pass tốn thời gian cần được đánh giá theo hàm hot/cold, tần suất
gọi và mức chấp nhận chi phí của người dùng. Chỉ gate cứng sự toàn vẹn
dữ liệu và kết quả hàm.

## Ranh giới áp dụng

K3 **không thay đổi bất kỳ pass Kagura hay Crane OLLVM STRONG production**,
không thêm VM/PAC/anti-debug/hook. Sentinel TU vẫn không qua Kagura,
nhưng helper `kagura_decrypt_*` có thể nhận function passes; chưa có
allowlist strict bên trong Kagura.

Khi artifact K3 đạt PASS, so sánh với [K2a artifact](KAGURA_K2_ARTIFACT_REVIEW.md)
để nhận diện độ ổn định của BBR/BBS; sau đó mới xây IPA arm64 riêng để
kiểm thử Kagura thực trên iPhone TrollStore. `arm64e` chỉ Apple Clang
build/link/ABI/UUID, không yêu cầu A12+ runtime tại giai đoạn này.
