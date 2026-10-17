# Kagura K0 — xác minh artifact LLVM19 đã build xanh (17/10/2026)

Nguồn được kiểm tra: ZIP CI người dùng gửi có tên
`DuoDash-Kagura-MAX-CANDIDATE-LLVM19-EXPERIMENTAL.zip`.
Đã mở **23 thành phần thật** gồm `audit.json`, `.ll`, `.bc`,
Mach-O, log so sánh 8.192 vector; không suy diễn chỉ từ lời báo
“build xanh”.

| Bằng chứng | Baseline | Kagura K0 |
|---|---:|---:|
| Native host object | 1.008 bytes | 2.104 bytes |
| Native LLVM IR (.ll) | 3.357 bytes | 10.063 bytes |
| iOS arm64 MH_DYLIB | 32.944 bytes | 49.344 bytes |
| SHA-256 host object | `ffa3b05f67b3050ddeb0b36bc19e252a4bd2fcf5fa7a58cd8e13285b5f9cb8e2` | `cef17e374b997ddac03bd464fdcef6caed2948bff5f7b478eed3879709d69425` |
| SHA-256 iOS arm64 dylib | `dcd313dc2a451479d4922c2626a8dd1a6e2906bfb708a4c13de6703669b8c3c2` | `2e604d92eb954be583f693667dd22148636cf60fc75cbb8b65ab88ba0581dc2f` |
| Public marker ASCII | Có | Không thấy |
| Host parity | 8.192 vector | Trùng 8.192/8.192 |

Đã so `host-plain.log` và `host-candidate.log`: giống byte,
180.249 bytes mỗi tệp, SHA-256 chung
`3b93079621fb51626a6bf8be36adb290558d7d48a3c33475ac897ef7116db491`.
Mỗi log có 8.192 dòng vector và `DD_KAGURA_HOST_PASS=8192` cuối tệp.
Hai `*-pass.log` K0 rỗng; **không có trace riêng chứng minh từng
pass có đóng góp ở mức native**. Tuy nhiên `host-candidate.ll` chứa
`kagura.sw`, `kagura.preloop`, `kagura_enc_*`,
`kagura_decrypt_*`, `bcf.pred`, `sub.*`, `co.*`.
Đây là dấu vết biến đổi tổng hợp, không chứng minh từng pass khó
phân tích đến mức nào.

`ios-arm64e.dylib` 32.944 bytes, SHA-256
`0e716d4a943b0164eee12ea1586baaa358dfc75058668081ae3a797e1ab13356`,
CPU raw subtype `0x80000002` (versioned userspace PAC ABI);
**Apple Clang build-only** — không được Kagura bảo vệ, chưa chạy
trên iPhone A12+. Người dùng chưa có A12+ nên điều này không chặn K1.

## Tiếp theo — K1: đóng góp của từng pass thật

Đã tạo `stage_pipeline.py` trong `scripts/custom_ollvm/kagura_max/`.
Chạy incrementally từ **cùng LLVM19 baseline**:

```text
LLVM19 -O1 .bc
 → kagura-str
 → kagura-fla
 → kagura-bcf
 → kagura-sub
 → kagura-co
 → kagura-bbr
 → kagura-bbs
```

Mỗi bước gọi một **LLVM pass thực bằng `opt`**, lấy output bước
trước làm input; chạy native 8.192 vector sau mỗi lần, ghi sha256 object
và `.ll`, số BB của `dd_kagura_critical` trước/sau và
`-debug-pass-manager` log. Nếu một pass chạy mà không làm thay đổi
LLVM IR của hàm này thì report `NO_OBSERVED_IR_DELTA`; nếu IR
khác nhưng object chưa khác thì `IR_ONLY_DELTA`. Không cộng lớp
bảo vệ “ảo” và không đánh giá bảo mật bằng code-size.

**K1 hiện mới có workflow và regression nguồn trên Windows, chưa có
kết quả native LLVM19 macOS sau 7 bước.** BBR/BBS là hai pass mới chỉ
đang thử, chưa kích hoạt production. Chưa bật VM, CI, PAC,
anti-debug, SLLVM proprietary hoặc phối hợp runtime hook.

Quy trình: chạy lại GitHub Actions workflow thủ công
**Kagura MAX Candidate - LLVM19 Pass Lab (Experimental)**;
artifact cũ vẫn giữ trong `out/` và có thêm
`out/stages/kagura-k1-stage-report.json`, 7 bộ `.ll`, object,
vector log và pass debug log. Đọc `classification` của từng stage
trước khi quyết định pass nào thực sự hữu ích.

Không thay đổi Crane OLLVM STRONG production hay quy tắc
`arm64e` build/audit-only. Không có tuyên bố “không thể phân tích
tĩnh” — so sánh IDA/Ghidra và chi phí chạy cần thực hiện sau khi K1
native CI PASS.
