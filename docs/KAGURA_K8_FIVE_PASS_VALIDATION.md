# Kagura K8 — xác minh 5 pass bổ sung trước khi đánh giá hiệu năng

Ngày tạo: **2026-10-17**. Trạng thái:
**STAGED_MACOS_CI_NOT_VERIFIED**. Bộ kiểm thử portable/negative cục bộ có thể
PASS trên Windows, nhưng **chưa chứng minh** Kagura LLVM19 thực sự chạy
đủ 5 pass K8 trên macOS hoặc iPhone. K0/K1/K5 (7 structural passes) và
K6/K7 (VM pass) vẫn là bằng chứng riêng đã có từ artifact/log thật.

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
| `kagura-mvo` | function / `MemoryValueObfuscationPass` | volatile integer local alloca/load/store (không escape) | XOR quanh store/load, biến `.mvo` |
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
- `fixture.c` thuần C, không có dữ liệu cá nhân, key/secret, PAC,
  objc_msgSend, hooks, Crane/TrollStore identifiers; `runner.c` dùng
  4096 vector đầu vào xác định và digest; baseline dùng **cùng LLVM19**.
- Mỗi pass chạy **riêng** từ cùng `plain.bc` bằng
  `opt --load-pass-plugin ... -kagura-[name]`,
  `-debug-pass-manager -passes=[correct-kind],verify`.
  Kiểm tra exact pass class, thật sự đổi IR **và** object, dấu vết
  cấu trúc đặc thù như bảng fptr/thunk/alloca/global/decode/outline,
  và native executable chạy ra chính xác log 4096 vector như baseline.
  `ci` native linker bắt buộc có pinned Kagura runtime archive.
- Cross-compile iOS15 `arm64` bằng LLVM19 trên cùng fixture cho từng pass
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

Cập nhật `pilot.py`: chỉ với **MVO**, biên dịch lại **cùng fixture**
bằng LLVM19 `-O0 -Xclang -disable-O0-optnone`; xác minh một
`alloca i64` có `store volatile` + `load volatile` trực tiếp,
không có pointer use khác trên chính alloca đó. Nếu thiếu fixture
đủ điều kiện, audit FAIL **trước khi chạy pass**. Các lifetime
intrinsics của alloca *khác* không gây kết luận sai.

**Chống PASS giả**: tạo và thực thi một baseline MVO riêng ở `-O0`,
bắt buộc 4.096 vector giống hệt baseline `-O1`; sau đó so sánh
**MVO transformed IR/object với chính baseline MVO `-O0`** trên
cả macOS và iOS arm64. Bắt buộc MVO thay IR, object, có chỉ dấu
XOR `.mvo`, giữ nguyên 4.096 kết quả; toàn bộ 4 pass còn lại
không đổi baseline `-O1`. Không hạ mức audit, không bỏ pass.
Đây là **bản sửa đã qua kiểm thử portable, chờ rerun macOS CI**;
không tự nhận đã khắc phục xong trên LLVM19 native.

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

Lưu ý: đây là **phòng lỗi no-op kế tiếp theo mã upstream**, không
phải một lỗi GENC đã được quan sát trong log người dùng vừa gửi.
Chỉ bản chạy mới của GitHub Actions mới xác nhận kết quả native thực.

## Lệnh kiểm tra cục bộ

```sh
python3 scripts/test_kagura_k8_passes.py
python3 scripts/test_custom_ollvm_pass_matrix.py
python3 scripts/verify_reconstruction.py
```

**Đầu ra local portable không phải build LLVM native**.

## Điều kiện nghiệm thu

Sau khi commit/push K8 và run thủ công, chỉ đổi state lên
`MACOS_CI_ARTIFACT_VERIFIED` sau khi đọc trực tiếp ZIP, xác minh từng
`*.ll`, `*.o`, `opt.log`, `native.log` so với báo cáo và
không có bản no-op. Nếu fail, giữ `STAGED...` và khắc phục nguyên nhân
thực, không giảm yêu cầu audit để làm xanh CI.

**Không đổi** `policy.json`, `Makefile`, `.github/workflows/build.yml`,
Hikari/Kagura K5/K7, Objective-C hooks, dylibs/debs Crane. Giữ
`vm_state=PRODUCTION_DISABLED_K6_K7_ISOLATED_VALIDATION_ONLY`;
đặc biệt VM K7 có median overhead iPhone 71,5× trên canary nên
không đưa vào các hàm hot-path. Performance và tương thích ABIs/hook
thực được đánh giá ở pha sau, không suy ra từ một canary.
