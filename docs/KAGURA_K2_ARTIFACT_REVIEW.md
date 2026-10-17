# Kagura K2a — kiểm tra artifact CI và overhead macOS (17/10/2026)

Artifact do người dùng cung cấp:
`DuoDash-Kagura-MAX-CANDIDATE-LLVM19-EXPERIMENTAL (2).zip`.
Đã kiểm tra trực tiếp **87 thành phần**, ZIP CRC sạch,
SHA-256 tổng `051498435b7201beac3c0895b7ed9cc15fd795228232b6896da260b0f588e11c`.
Đây là artifact chạy K2a mới, không phải kết quả runtime từ iPhone.

## Kiểm chứng từ byte thật trong ZIP

- `stages/kagura-k1-stage-report.json`: 7 pass incremental (STR, FLA,
  BCF, SUB, CO, BBR, BBS) đều `IR_AND_OBJECT_DELTA`.
- Mỗi stage có log 8.192 vector khớp byte với baseline, tức **57.344
  lượt đối chiếu trên cùng 8.192 input deterministic**, không phải
  57.344 input độc lập.
- SHA-256 thực của từng `.ll`, `.o`, `-opt.log`, `-bench.log`
  trùng JSON từng giai đoạn, không thấy public plaintext canary trong
  các protected objects.
- Object `sentinel-plain.o` là **576 bytes**, SHA-256
  `e5641276de04bb8d81234aec4c5923645d39758087ebda63ef2841a9e53ee555`;
  cả 7 stage đều tham chiếu đúng hash nguyên vẹn. IR vào module chỉ
  định nghĩa `dd_kagura_critical`, IR sau transform thêm helper
  `kagura_decrypt_3068888805`. `unprotected_sentinel_pass_invoked=false`.
- **TU isolation = PASS**, nhưng `strict_single_function_pass_filter_verified=false`.
  Các function pass có thể chạy trên helper giải mã. Không được coi đây
  là allowlist strict bên trong Kagura.

## Benchmark host native thực

11 mẫu × 32.768 calls/sample cho mỗi bản, CLOCK_MONOTONIC, 2 warmups.
Checksum đều `0b35fe5c6831527a`, log từng stage có schema, PASS và
SHA-256 khớp `stages/kagura-k1-host-benchmark.json`.

| Pipeline tích lũy | Median ns/call | p95 nearest-rank ns/call | Median / baseline | p95 / baseline |
|---|---:|---:|---:|---:|
| Baseline | 15 | 17 | 1,000x | 1,000x |
| STR | 24 | 51 | 1,600x | 3,000x |
| + FLA | 39 | 41 | 2,600x | 2,412x |
| + BCF | 45 | 48 | 3,000x | 2,824x |
| + SUB | 50 | 55 | 3,333x | 3,235x |
| + CO | 46 | 47 | 3,067x | 2,765x |
| + BBR | 52 | 144 | 3,467x | 8,471x |
| + BBS | 82 | 92 | 5,467x | 5,412x |

**Số đo đã lấy từ artifact và kiểm lại các log thô**.
Đáng chú ý:
- BBR có 11 mẫu `45,45,46,82,144,79,60,52,54,52,52`. Có nhiễu
  hoặc biến động rõ rệt, không đủ cơ sở kết luận BBR làm p95 gấp
  8,471 lần một cách ổn định.
- Với đúng 11 mẫu, **p95 nearest-rank = mẫu lớn nhất** (ceil(0,95 × 11)
  = 11). Vì vậy p95 cực kỳ nhạy với outlier.
- +CO giảm median từ 50 xuống 46 ns dù có thêm transform; con số
  có thể do thay đổi native code layout/caching hoặc nhiễu benchmark,
  không có nghĩa CO luôn làm mã chạy nhanh hơn.
- +BBS có median cao nhất, 82 ns/call và object 2.744 bytes so với
  baseline 1.008 bytes. Đây không phải thước đo mức chống phân tích tĩnh.

## Tiếp tục phát triển — K3 chưa có native artifact

Đã có pipeline 16 vòng, thứ tự cân bằng và đảo chiều của 8 biến thể
baseline/STR/FLA/BCF/SUB/CO/BBR/BBS; mục tiêu đo 176 mẫu/biến thể,
đối chiếu checksum trong từng vòng và báo cáo median/p95 mới. Test
parser portable mới PASS, **số đo K3 native chưa có**, xem
[KAGURA_K3_INTERLEAVED_BENCH.md](KAGURA_K3_INTERLEAVED_BENCH.md).

## Đánh giá cổng kỹ thuật

- **K2a MACOS_NATIVE_PARITY_AND_SCOPE_BENCH_ARTIFACT_VERIFIED**:
  đủ bằng chứng build, TU isolation và timing logs của hàm thử nghiệm.
- **Chưa VERIFIED**: kiểm soát strict per-function bên trong Kagura,
  cold start, hiệu năng iPhone arm64, PAC runtime A12+ arm64e,
  IDA/Ghidra mức chi phí phân tích, hay custom MAX production.
- **Không tự bật BBR/BBS/VM** trên các hàm hot, constructor, selector,
  Substrate hook, PAC callback hoặc Crane production.
- **Cổng kế tiếp:** benchmark interleaved nhiều lượt (đảo thứ tự,
  môi trường máy cố định), kết quả median/p95 trên từng đợt và
  native iPhone arm64 với mẫu độc lập. Đánh giá mức khó đọc tĩnh
  bằng IDA/Ghidra phải tách khỏi hiệu năng.

Crane OLLVM STRONG vẫn giữ nguyên; arm64e dùng Apple Clang build-only
với Mach-O PAC userspace ABI `0x80000002`, A12+ runtime hoãn.
