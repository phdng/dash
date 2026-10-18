# K13 — thử nghiệm riêng Kagura CSEBreakPass trên LLVM19

Ngày chuẩn bị: **18/10/2026**. Trạng thái:
**STAGED_MANUAL_MACOS_LLVM19_NATIVE_NOT_VERIFIED**.

Không được đọc trạng thái này thành native compiler PASS:
K13 hiện chỉ triển khai mã, workflow và portable negative gates;
**chưa có kết quả chạy workflow K13 macOS thật**.

## Nguồn chọn pass

Từ [K12 artifact đã kiểm chứng](KAGURA_K12_ARTIFACT_REVIEW.md),
registry thực của pinned Kagura
`ac2136ee0408677cf7cdee55307e9b16edd5f4d5`
có 36 tên, 23 chưa xác minh native. K12 opt-only ghi nhận
`kagura-cse-break` là **FN**, enable flag `CSEBreak`,
actual trace `kagura::CSEBreakPass`, pipeline
`function(kagura-cse-break),verify`, LLVM IR delta trên
hai target macOS và iOS arm64. Điều đó chỉ xác minh được
**opt-only**, không chứng minh native parity, liên kết runtime hay IPA.

Registry nguồn thật từ K12 trong ZIP có SHA-256:
`6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa`.
K13 **phải khớp exact hash** của file
`include/kagura/PassRegistry.def` từ commit này. Không
chấp nhận tải HEAD mới hoặc registry khác thay thế.

## Workflow manual K13

`.github/workflows/kagura-k13-cse-break-native.yml`

**Kagura K13 - Isolated CSEBreak Native and iOS Arm64 Object (Experimental)**,
GitHub Actions `macos-14`, LLVM19, mã Kagura pin, plugin riêng
`KaguraObfuscator.dylib`.

1. Chạy `scripts/test_kagura_k13_native.py` (portable negative),
   K12 opt audit, K12 inventory, K11 portable IPA và pass matrix.
2. Fetch exact pin, hash-check registry theo bằng chứng K12, build
   Kagura LLVM19 plugin. Lưu pinned `PassRegistry.def` và LICENSE
   **nguyên bytes** vào artifact.
3. Dùng canary C K8 `dd_k8_evaluate` công khai, không liên quan
   Crane/hook/PAC hoặc dữ liệu riêng. Compiler Clang O1 sinh
   bitcode baseline macOS và iOS arm64. Chạy **một**
   `CSEBreakPass`, yêu cầu `-debug-pass-manager` chứng minh class
   được chạy trên hàm canary, `VerifierPass` và `BitcodeWriterPass`.
4. LLVM `llvm-dis` sinh IR hai biến thể, so normalized IR SHA
   (chỉ bỏ ModuleID); yêu cầu **IR delta** và còn external symbol
   `dd_k8_evaluate`. Clang biên dịch `MH_OBJECT`, so SHA
   object baseline/protected thực, không chỉ log opt.
5. Trên **macOS** link native executable với **cùng runner C K8**,
   chạy baseline/protected **4096 vector trên mỗi biến thể**;
   kiểm strict `DD_K8_SCHEMA=1`, `DD_K8_VECTORS=4096`,
   checksum 16 hex và `DD_K8_COMPLETE=PASS`; checksum phải
   **bằng nhau**, không được nới gate khi khác.
6. Trên **iPhoneOS arm64** chỉ **biên dịch object**, kiểm Mach-O
   `MH_MAGIC_64`, CPU ARM64, subtype0, `MH_OBJECT`,
   `xcrun nm -gU` có definition thật `_dd_k8_evaluate`,
   `nm -u -j` không phát sinh Kagura runtime dependency chưa link.
   Đây là build-only; **không tạo IPA, không chạy iPhone**.
7. `scripts/custom_ollvm/kagura_k13/audit.py` đọc lại bản
   `Kagura-K13-REPORT.json` và **mọi file bằng chứng gốc**:
   pinned source SHA, raw IR/object SHA, normalized IR delta,
   exact `CSEBreakPass` trace, Mach-O/nm arm64,
   hai native 4096 checksum từ actual executable stdout, từ chối
   khai báo iPhone/arm64e/PAC/Crane PASS.

Artifact (kể cả khi fail):
`DuoDash-Kagura-K13-CSEBREAK-NATIVE-IOS-ARM64-OBJECT-EXPERIMENTAL`.

## Điều kiện đạt

`K13_MACOS_CSE_BREAK_4096_PARITY_AND_IOS_ARM64_OBJECT_PASS`
chỉ hợp lệ khi CI macOS đã chạy đủ bước và `audit.py` replay PASS.
Ngay cả như vậy: iOS arm64 **MH_OBJECT build-only**, không chứng
minh có thể link app/IPA, kiểm nghiệm iPhone, arm64e PAC hoặc
khả năng tương thích với pass khác. Nếu link runtime của CSEBreak
yêu cầu module khác, phải fail và thu log; không bịa shim
hoặc dùng thư viện macOS để link vào iOS.

## Không thay đổi production

Không chỉnh `Makefile`, `policy.json`,
`obfuscator/Obfuscator`, Crane hooks, Objective-C ABI,
mã arm64e/PAC hoặc K11 đã xác minh. Không tự tích hợp các pass
rủi ro cao từ K12 như `anti-debug`, `tamper`, `honey`,
`telemetry`, `PAC` hoặc 6 pass INFRA.

Bản portable test dùng Mach-O/IR/log **giả lập và cố ý kiểm tra
negative gates**. PASS trên Windows chỉ chứng minh luật kiểm
chứng hoạt động, không chứng minh công cụ LLVM19 trên macOS.
