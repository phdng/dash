# Kagura K1 — xác minh artifact CI thực (17/10/2026)

Đầu vào: ZIP tải lên `DuoDash-Kagura-MAX-CANDIDATE-LLVM19-EXPERIMENTAL (1).zip`.
Đã đọc trực tiếp 68 entry; ZIP CRC `testzip()` không báo lỗi. SHA-256
của ZIP: `e4edb1c1b8d1907be82208e9e472d09522210d90226916d9d74eccf3b0d33d3e`.

## K1: kết quả 7 pass trên LLVM19 thật

`stages/kagura-k1-stage-report.json` được đối chiếu với chính bảy
`stageNN-*.ll`, `stageNN-*.o`, `stageNN-*.log` và
`stageNN-*-opt.log` trong ZIP, kiểm lại SHA-256 độc lập.

| Giai đoạn | Basic blocks trong hàm chính | Object size | Phân loại đóng góp |
|---|---:|---:|---|
| Baseline | 5 | 1008 B | Không bảo vệ |
| STR | 7 | 1600 B | `IR_AND_OBJECT_DELTA` |
| FLA | 11 | 1872 B | `IR_AND_OBJECT_DELTA` |
| BCF | 19 | 1984 B | `IR_AND_OBJECT_DELTA` |
| SUB | 19 | 2192 B | `IR_AND_OBJECT_DELTA` |
| CO | 19 | 2208 B | `IR_AND_OBJECT_DELTA` |
| BBR | 19 | 2200 B | `IR_AND_OBJECT_DELTA` |
| BBS | 38 | 2744 B | `IR_AND_OBJECT_DELTA` |

**Tất cả bảy giai đoạn** đều có IR và object byte khác giai đoạn
ngay trước. BBR không làm tăng số BB nhưng có thay đổi IR/object;
object nhỏ hơn 8 B, không được suy luận là yếu hơn/mạnh hơn chỉ dựa
trên số byte. BBS tăng BB của hàm chính từ 19 lên 38.
Object cuối dài 2744 B (baseline 1008 B), tăng ~2,72 lần;
đây là *code-size proxy*, không phải điểm bảo mật.

Bảy log kết quả mỗi cái 180249 byte và **giống hệt**
`host-plain.log`, tổng cộng **7 × 8192 = 57344 lần đối chiếu
vector theo giai đoạn**. Cùng 8192 đầu vào deterministic được chạy
lại ở mỗi giai đoạn, **không phải 57344 đầu vào độc lập**.
Tất cả object sau STR đều không chứa plaintext marker
`DD_KAGURA_PUBLIC_CANARY_CE_STRING_V1`. CRC, SHA object,
SHA IR, SHA debug log và output parity đã được kiểm lại từ ZIP,
khớp JSON.

`-debug-pass-manager` xác nhận:

- `kagura::StringEncryptionPass` chạy ở **module**;
- `ControlFlowFlatteningPass`, `BogusControlFlowPass`,
  `SubstitutionPass`, `ConstantObfuscationPass`,
  `BasicBlockReorderingPass`, `BasicBlockSplittingPass`
  chạy trên hàm `dd_kagura_critical`;
- function passes **cũng được gọi trên helper**
  `kagura_decrypt_3068888805` do STR tạo ra.

Điểm cuối quan trọng: **K1 đã chứng minh pass tạo delta và giữ
parity trên fixture đã thử, nhưng không chứng minh scope pass được
giới hạn riêng một hàm production**. `opt -passes=function(...)`
chạy trên tất cả hàm phù hợp trong module; cần function selection
/ allowlist có kiểm chứng trước khi đụng Crane. Log pass execution
không chứng minh một pass cải thiện chống reverse engineering bao
nhiêu, hay có thể chặn phân tích tĩnh tuyệt đối.

## K2a: bước tiếp theo đã triển khai

Đã bổ sung [KAGURA_K2_SCOPE_BENCH.md](KAGURA_K2_SCOPE_BENCH.md):
TU `critical.c` đi qua Kagura, object sentinel độc lập không đi qua pass;
công cụ kiểm tra scope cho từng stage và benchmark native 11 mẫu × 32.768
calls, xuất median/p95 và ratio so baseline. **Đây không phải xác minh
function allowlist nghiêm ngặt** vì `kagura_decrypt_*` có thể nhận pass.
Bộ kiểm thử K2a hiện mới PASS cục bộ, chưa có kết quả macOS CI.

## ABI và thiết bị

`audit.json` K0 vẫn báo:
- iOS arm64 candidate: `MH_DYLIB`, binary khác baseline, build-only;
- Apple Clang arm64e: versioned user-space PAC ABI
  `0x80000002`, **không được bảo vệ bằng Kagura**;
- K1: **đối chiếu native trên macOS**, chưa có Kagura K1 on-device
  parity, latencies p50/p95, bộ nhớ, startup hoặc dữ liệu IDA/Ghidra.

Người dùng đã thử và xác nhận các phiên bản Protection Lab khác
trên TrollStore arm64; đó **không tự động xác nhận Kagura K1**.

## Quyết định kỹ thuật

**K1 build+native per-pass parity: VERIFIED_FROM_USER_CI_ARTIFACT.**
Cả STR/FLA/BCF/SUB/CO/BBR/BBS đều có `IR_AND_OBJECT_DELTA`.
Không loại BBR/BBS chỉ vì số basic block, cũng không tăng độ mạnh
chỉ dựa vào số BB.

Trước khi xét `MAX_STRUCTURAL` cho helper thật: (1) chặn pass trên
hàm ngoài allowlist (bao gồm helper giải mã, callback/selector
nhạy cảm); (2) chạy benchmark native/timing distribution và so
baseline cùng compiler; (3) kiểm thử iOS arm64 trên IPA lab mới;
(4) đánh giá IDA/Ghidra; (5) cung cấp rollback tách khỏi Crane.
**Không triển khai VM Kagura vào production tại mốc này.**

Crane OLLVM STRONG tiếp tục giữ nguyên; A12+ arm64e runtime
`DEFERRED_NO_DEVICE`.
