# Kagura K2 — scope isolation và benchmark trên macOS

Cập nhật: 2026-10-17. **Trạng thái: mã và kiểm thử portable đã PASS,
native macOS CI của K2 CHƯA ĐƯỢC CHẠY.**

## Lý do phải có bước này

Artifact K1 đã được kiểm chứng: cả STR, FLA, BCF, SUB, CO, BBR và
BBS sinh LLVM IR/native-object delta và giữ đúng 8.192 output vector
trên macOS. Nhưng `-debug-pass-manager` cho thấy các function passes
cũng chạy trên helper `kagura_decrypt_*` do STR tạo ra. Không thể coi
`-passes=function(...)` là **hàm allowlist một-mình**.

K2 xác định **biên translation unit (TU)** độc lập, không tuyên bố
plugin Kagura đã có bộ lọc function nào cả.

## Cách ly bản thử nghiệm

`critical.c` là TU duy nhất được chuyển sang LLVM19 IR và chạy
Kagura `opt`. `sentinel.c` định nghĩa
`dd_kagura_unprotected_sentinel`, biên dịch thành object riêng
**không qua Kagura** và link nguyên trạng vào baseline và mọi
bản candidate. `stage_pipeline.py` FAIL nếu IR đầu vào có bất cứ
function definition nào ngoài `dd_kagura_critical`, hoặc sau pass xuất
hiện function ngoài `dd_kagura_critical` và helpers có prefix
`kagura_decrypt_`. SHA-256 object sentinel được đối chiếu sau từng
stage. Debug log không được chứa symbol sentinel.

Đây chỉ là **cách ly theo TU**, không bảo đảm chỉ mỗi
`dd_kagura_critical` bị pass biến đổi. Helper được sinh ở trong
TU Kagura **vẫn có thể bị biến đổi** và report ghi rõ
`strict_single_function_pass_filter_verified=false`. Nếu một helper
mới không được nhận diện, CI FAIL để xem xét trước khi nới danh sách.

Không dùng kỹ thuật này để tự động biến đổi các TU Objective-C lớn
chứa `objc_msgSend`, class constructor, hook hoặc callback của Crane.

## Benchmark mới: native, cùng compiler

`bench_runner.c` chỉ chạy trên macOS host. Mỗi executable ghép
**cùng bench runner, cùng sentinel object và một Kagura object**
(stage0 baseline hoặc stage1–7). Mỗi bản chạy:

- 2 lượt warmup;
- 11 mẫu đo `CLOCK_MONOTONIC`, **32.768 calls/mẫu**;
- kiểm tra checksum đầu ra của phép tính qua biến `volatile` để
  ngăn lược bỏ lời gọi;
- viết log `DD_KAGURA_BENCH_*` có checksum 16 hex và marker PASS.

`benchmark_audit.py` từ chối log sai schema/context/số mẫu,
negative/zero timing, checksum lệch, PASS giả, dữ liệu thừa.
Kết quả `kagura-k1-host-benchmark.json` ghi **median ns/call**,
**p95 nearest-rank ns/call** và ratio so baseline ở từng stage.
Nó không đưa ra điểm bảo mật, không đo *cold start* và không phản ánh
hiệu năng máy iPhone. Chạy benchmark trên macOS shared runner có thể
chịu ảnh hưởng turbo boost/throttle/nhiệt độ; số đo chỉ là tham khảo
để phát hiện regressions lớn, không phải kết luận cuối.

## CI mới

Workflow thủ công `Kagura MAX Candidate - LLVM19 Pass Lab
(Experimental)` đã bổ sung:

```text
LLVM19 isolated critical.c → K1 7 stages
LLVM19 original sentinel.c → 1 unprotected object
Apple Clang bench_runner.c → 1 bench object
    baseline + 7 stage native binaries
    → 8192 vector parity từng stage
    → TU scope evidence
    → 11 timing samples × 32768 calls
    → JSON p50/p95 relative overhead
```

Output nằm trong `out/stages/kagura-k1-stage-report.json`,
`out/stages/kagura-k1-host-benchmark.json`, các tệp
`stageNN-*-bench.log`, `.ll`, `.o`, `*-opt.log`.
Có regression portable `scripts/test_kagura_scope_bench.py`
được chạy trước native build.

**Chưa có bằng chứng macOS native của bước K2**, cũng chưa thử Kagura
trên iPhone. Nếu các bước trên PASS, bước tiếp theo là so sánh
code size/startup chi tiết và tạo **app lab arm64 dùng TrollStore**
để thử Kagura thực tế trên thiết bị hiện tại. `arm64e` chỉ
AppleClang build+ABI v2, không có thiết bị A12+ và không giả lập
PAC runtime.

Crane OLLVM STRONG production không sửa, chưa bật Kagura VM/CI/PAC,
không cam kết hàm quan trọng không thể phân tích tĩnh.
