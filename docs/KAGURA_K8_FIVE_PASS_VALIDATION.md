# Kagura K8 — xác minh 5 pass bổ sung trước khi đánh giá hiệu năng

Ngày tạo: **2026-10-17**. Trạng thái hiện tại:
**MACOS_CI_ARTIFACT_VERIFIED_ISOLATED_FIVE_PASS**. Đã đối chiếu độc lập
ZIP CI LLVM19 macOS: 5/5 pass riêng có thay đổi IR/object thật và
4.096 native vector khớp baseline, 92/92 bằng chứng kiểm tra PASS.
**Chưa chạy K8 trên iPhone hoặc kết hợp năm pass**. Xem
[KAGURA_K8_ARTIFACT_REVIEW.md](KAGURA_K8_ARTIFACT_REVIEW.md).
K0/K1/K5 (7 structural passes) và K6/K7 (VM pass) có
bằng chứng CI/thiết bị riêng, không tự động chứng minh K8 trên Crane.

## Mục tiêu

Theo ưu tiên của người dùng: xác minh trước **build được → pass thực sự
đổi LLVM IR + object → chương trình giữ nguyên hành vi → arm64 object ABI
hợp lệ**. Chưa áp đặt ngưỡng hiệu năng; đo sau khi có chức năng đúng.
Điều kiện "pass được gọi" không đủ — pass no-op phải FAIL.

Năm ứng viên này được đối chiếu với **nguồn Kagura chính xác tại commit**
`ac2136ee0408677cf7cdee55307e9b16edd5f4d5`
(`include/kagura/PassRegistry.def` và triển khai C++ tương ứng);
không trộn với tên/semantics proprietary SLLVM:

| Pass | Registry upstream | Điều kiện fixture | Kỳ vọng |
| --- | --- | --- | --- |
| `kagura-ibr` | function / `IndirectBranchPass` | gọi trực tiếp hàm **định nghĩa trong cùng module** | private `__kagura_fptr_*`, chuyển sang indirect call |
| `kagura-mvo` | function / `MemoryValueObfuscationPass` | **fixture LLVM IR riêng** `mvo.ll` có direct `alloca i64`, volatile store/load, không escape | XOR quanh store/load, biến `.mvo` |
| `kagura-genc` | module / `GlobalEncryptionPass` | constant integer array private/internal được load bằng chỉ số runtime | initializer bị mã hóa và load decode `.dec` |
| `kagura-fsplit` | module / `FunctionSplitPass` | hàm có ít nhất 5 basic block, có block không phải exit an toàn để tách | hàm helper mới, IR/object thay đổi |
| `kagura-ci` | module / `CallIndirectionPass` | gọi external `strlen` (không để Clang thay built-in) | global thunk table, constructor, `kagura_rtld_default_handle` |

Lưu ý: IBR Kagura **không đồng nghĩa** nhánh indirect-branch của SLLVM:
trong nguồn đã pin nó chuyển **direct same-module function call** sang
global function pointer. CI Kagura tác động external call và phải
liên kết **`libkagura_runtime.a`** (bao gồm runtime resolver); không
thử trên hook, Objective-C selector, callback, constructors của Crane.

## K8 CI được triển khai

Workflow thủ công, **không có push/PR**:
`.github/workflows/kagura-k8-pass-coverage.yml`,
`Kagura K8 - Five Remaining LLVM19 Passes (Experimental)`.

- macOS-14: tải/checkout đúng Kagura MIT commit pin, LLVM19, build plugin
  và native runtime; so `PassRegistry.def` với 5 kiểu module/function.
- `fixture.c` thuần C dùng cho IBR/GENC/FSPLIT/CI; `mvo.ll` là
  **IR riêng cho MVO**, tránh việc Clang tự tạo hoặc loại bỏ alloca.
  Hai fixture chỉ chứa public canary, không có key/secret, PAC, hook,
  Objective-C hay dữ liệu của Crane. `runner.c` chạy **4.096 vector
  riêng cho mỗi baseline** và candidate theo cùng ABI.
- Từng pass chạy **riêng** bằng
  `opt --load-pass-plugin ... -kagura-[name]`,
  `-debug-pass-manager -passes=[correct-kind],verify`, so IR/object
  candidate với **baseline của chính fixture đó**, không nhận
  chênh lệch giữa hai fixture khác nhau là biến đổi pass.
  Kiểm tra exact pass class, thật sự đổi IR **và** object, dấu vết
  cấu trúc đặc thù như bảng fptr/thunk/alloca/global/decode/outline,
  và native executable chạy ra chính xác log 4096 vector như baseline.
  `ci` native linker bắt buộc có pinned Kagura runtime archive.
- Cross-compile iOS15 `arm64` bằng LLVM19 trên đúng fixture của từng pass
  và audit Mach-O `MH_OBJECT`/raw subtype 0. **Không có link/install/IPA/
  thực thi iOS hay kiểm thử arm64e**, và không được gọi iPhone PASS.
- Log native, `opt` của từng pass, IR, object và
  `Kagura-K8-PASS-REPORT.json` được lưu vào artifact
  `DuoDash-Kagura-K8-FIVE-ISOLATED-PASSES-LLVM19-EXPERIMENTAL`,
  kể cả failure diagnostics. Report chỉ hoàn thành đủ 5 nếu mọi pass
  có IR+object delta, native parity PASS và arm64 object pass.
- Chưa bật pipeline **kết hợp 5 pass**: trước tiên phải có proof từng
  pass vì thứ tự ảnh hưởng trực tiếp (ví dụ IBR có thể làm block
  không còn đủ điều kiện cho FSPLIT), rồi mới thử matrix với
  giai đoạn/điều kiện rõ ràng.

## Sửa lỗi CI K8 MVO no-op (2026-10-17)

GitHub Actions báo:
`AssertionError: K8 mvo: invoked pass but no real IR/object delta`.
Đây là lỗi **fixture MVO không tạo được bằng chứng biến đổi**, không
được gọi là MVO PASS. Mã nguồn Kagura upstream MVO chỉ chọn các
`alloca i8/i16/i32/i64` có sử dụng trực tiếp trong `load/store`,
không escape qua `llvm.lifetime`, call, GEP hoặc alias. Trong lần CI
đã báo lỗi, `-O1` chưa cung cấp đầu vào MVO có tác dụng. Không
có artifact `plain.ll` và `mvo/opt.log` riêng được gửi để xác
định chính xác biến nào bị optimizer loại bỏ; nguyên nhân cụ thể
trong LLVM IR cần quan sát ở lần CI kế tiếp.

**Lần chạy GitHub Actions kế tiếp cũng FAIL** tại
`validate_mvo_input_ir(mvo_text)` (dòng 260): baseline C ở
`-O0 -Xclang -disable-O0-optnone` không đáp ứng preflight
nonescaping i64 alloca. Không có `mvo-plain.ll` gốc trong yêu cầu
để xác định chi tiết cách Clang phát IR; không khẳng định upstream
MVO bị lỗi. Do đó **không tiếp tục đoán cờ Clang**.

**Cách sửa hiện tại:** bổ sung `scripts/custom_ollvm/kagura_k8/mvo.ll`
là **fixture LLVM IR độc lập**, chứa một `alloca i64` có direct
`store volatile i64` và `load volatile i64`, không có lifetime
intrinsic, alias hay pointer escape. Chỉ `target triple` được thay
theo macOS host/ios arm64; `llvm-as` LLVM19 assemble trực tiếp thành
`mvo-plain.bc` và `mvo-ios-plain.bc`, không đi qua Clang
frontend optimization. Chính văn bản IR sau `llvm-dis` vẫn phải qua
`validate_mvo_input_ir()` nghiêm ngặt.

**Chống PASS giả:** MVO baseline riêng chạy 4.096 vector trên macOS,
bắt buộc bằng **checksum oracle Python độc lập**
`64e61045bbc4a250` và qua schema kiểm tra log. MVO protected phải
(1) gọi đúng `MemoryValueObfuscationPass`, (2) thay đổi IR **và**
object so với chính `mvo.ll` baseline, (3) chứa XOR `.mvo`,
(4) trả chính xác 4.096 kết quả baseline. iOS arm64 build-only cũng
phải có IR/object delta với baseline cùng fixture. **Không được so
hai hàm C và IR khác thuật toán để tạo ra PASS giả.** IBR/GENC/FSPLIT/CI
vẫn giữ nguyên `-O1` và oracle/parity riêng. **Bản GitHub Actions
mới đã chạy và xác minh độc lập:** MVO IR thực chứa XOR cả store/load,
object macOS+iOS có delta, 4.096 vector/native checksum đúng. Chi tiết
[artifact review K8](KAGURA_K8_ARTIFACT_REVIEW.md).

**Gia cố thêm GENC sau khi rà upstream:** cùng phiên bản Kagura,
`GlobalEncryptionPass::collectEligibleGlobals()` chỉ nhận private/
internal constant có `LoadInst` trực tiếp (hoặc qua một số
`ConstantExpr`). Một constant array truy cập bằng **GEP runtime**
trong fixture `-O1` không đảm bảo có direct load của chính global.
Vì vậy K8 bổ sung **`dd_k8_genc_scalar`** private constant và truy
cập qua volatile-qualified lvalue để giữ một direct load có thể
được pass biến đổi, không giảm `-O1` cho GENC. Bộ kiểm tra yêu cầu
IR macOS và iOS đều chứa `internal/private constant i64` và
`load volatile i64, ptr @dd_k8_genc_scalar`; chỉ gọi pass mà không
mã hóa/thêm decode XOR hoặc không đổi object vẫn FAIL.

Lưu ý: đây là **phòng lỗi no-op theo mã upstream**, không phải lỗi GENC
trong log lần trước. **Artifact K8 mới đã chứng minh** GENC thay đổi
IR/object macOS+iOS và giữ đúng 4.096 native vector trên canary; chưa
thử iPhone runtime.

## Lệnh kiểm tra cục bộ

```sh
python3 scripts/test_kagura_k8_passes.py
python3 scripts/test_custom_ollvm_pass_matrix.py
python3 scripts/verify_reconstruction.py
```

**Đầu ra local portable không phải build LLVM native**.

## Điều kiện nghiệm thu

Điều kiện xác minh **5 pass riêng** đã đạt theo ZIP K8 vừa đối chiếu:
`MACOS_CI_ARTIFACT_VERIFIED_ISOLATED_FIVE_PASS`, hash nguồn của ba
fixture khớp báo cáo, 74 entry/CRC sạch, 92/92 checks PASS.
Bước tiếp theo phải duy trì đúng chuẩn: thử tương tác/từng thứ tự
pipeline trước rồi mới cân nhắc IPA iPhone riêng. Nếu phép thử phối hợp
FAIL, **không thay đổi** trạng thái 5 pass riêng thành
`COMBINED_PASS` hay hạ điều kiện parity/IR/object.

**Không đổi** `policy.json`, `Makefile`, `.github/workflows/build.yml`,
Hikari/Kagura K5/K7, Objective-C hooks, dylibs/debs Crane. Giữ
`vm_state=PRODUCTION_DISABLED_K6_K7_ISOLATED_VALIDATION_ONLY`;
đặc biệt VM K7 có median overhead iPhone 71,5× trên canary nên
không đưa vào các hàm hot-path. Performance và tương thích ABIs/hook
thực được đánh giá ở pha sau, không suy ra từ một canary.
