# DuoDash K9 — ghép 5 pass Kagura thật vào một LLVM module (chưa có native CI)

Ngày triển khai: **17/10/2026**. Trạng thái:
**STAGED_MANUAL_COMPOSED_CI_NOT_VERIFIED**.

## Lý do phát triển K9

Artifact K8 đã xác minh **5/5 LLVM19 Kagura pass chạy riêng lẻ** trên
macOS: IBR, MVO, GENC, FSPLIT, CI, IR/object delta thực,
4.096-vector native parity mỗi pass; iOS arm64 object build-only.
Xem [KAGURA_K8_ARTIFACT_REVIEW.md](KAGURA_K8_ARTIFACT_REVIEW.md).
K8 **chưa chứng minh** năm pass phối hợp trên cùng một module,
hay có thể dùng lên Crane/Objective-C/PAC.

**MVO** K8 đòi hỏi `alloca` nguyên thủy bằng LLVM IR riêng:
không ghép hai fixture bằng cách so sánh hàm khác nhau (PASS giả).
K9 tạo một module với **hai hàm public riêng**:

- `dd_k8_evaluate`: từ `scripts/custom_ollvm/kagura_k8/fixture.c`
  qua LLVM19 clang `-O1 -fno-builtin-strlen`; chứa phép gọi nội bộ,
  global constant và external `strlen`.
- `dd_k9_mvo_probe`: từ *đúng* `mvo.ll` K8, chỉ thay tên định
  nghĩa `dd_k8_evaluate` và host/iOS target triple. `llvm-as`
  tạo BC để đảm bảo một `alloca i64` có load/store trực tiếp.
- `llvm-link` ghép **cả hai** vào một LLVM module, yêu cầu hai ABI
  tồn tại, MVO IR có eligible alloca, GENC có global const/direct load.
  Hash của 3 nguồn K8 phải khớp artifact đã xác minh; sai hash FAIL.

Chạy 2 oracle trong **cùng binary mỗi stage**:
`dd_k8_evaluate` kỳ vọng checksum `25a3318e3d7d6525` và
`dd_k9_mvo_probe` kỳ vọng `64e61045bbc4a250`, mỗi hàm
**4.096 vectors**. Nếu checksum khác hai giá trị K8 đã được xác minh,
hoặc stage khác log baseline dù cả hai ghi PASS → **CI FAIL**.

## Thứ tự pipeline nghiên cứu K9

```text
K8 verified C fixture (-O1) ---+
                              +-- llvm-link --> merged.bc
K8 verified MVO IR (llvm-as) -+
             |
             v
   01 mvo (function)
   02 genc (module)
   03 fsplit (module)
   04 ibr (function)
   05 ci (module + Kagura native resolver)
```

Thứ tự trên giữ MVO trên đầu vào chưa bị pass khác biến đổi;
GENC thực hiện trước các lần tách/đổi lời gọi; FSPLIT trước IBR
để tránh việc IBR chuyển direct call thành indirect khiến
FSPLIT mất điều kiện. CI cuối cùng cần link
**`libkagura_runtime.a`** cùng đúng SHA Kagura pin.

K9 **không tự tuyên bố mọi thứ tự pass đều tương thích**.
Nếu một stage no-op hoặc parity FAIL thì dừng và lưu trạng thái
`INCOMPLETE_UNTIL_ALL_STAGES_PASS`, không tự ý bỏ pass hoặc sửa
checker cho xanh.

## Workflow thủ công mới

`.github/workflows/kagura-k9-composition.yml`
— **Kagura K9 - Five Pass Single Module Composition (Experimental)**.

1. Chạy portable regressions fail-closed, kiểm SHA K8 và đúng commit
   Kagura `ac2136ee0408677cf7cdee55307e9b16edd5f4d5`.
2. macOS-14: build Kagura real LLVM19 New Pass Manager plugin,
   dùng đúng thư viện native runtime Kagura.
3. Sau **mỗi pass** riêng trên module *đã qua các pass trước đó*:
   yêu cầu exact class `-debug-pass-manager`, `-passes=...,verify`,
   pass-specific marker, IR+Mach-O object changed, giữ cả hai
   `dd_k8_evaluate`/`dd_k9_mvo_probe`, 4.096 native parity cho
   mỗi hàm và log giống từng byte baseline.
4. Kiểm tra iOS15 arm64 **MH_OBJECT** ở baseline và sau mỗi stage,
   cả IR/object cũng phải thay đổi với từng stage; không thực thi
   iOS, không cài IPA, không gọi arm64e là protected.
5. Upload **artifact kể cả khi fail**:
   `DuoDash-Kagura-K9-FIVE-PASS-COMPOSED-LLVM19-EXPERIMENTAL`,
   bao gồm `Kagura-K9-COMPOSITION-REPORT.json`,
   các `*.ll`, `*.bc`, `*.o`, `*-opt.log`,
   `native.log`, linker logs và pinned MIT license.

Chỉ khi báo cáo đủ 5 stage và tất cả gates native + object thành công
mới xuất `MACOS_NATIVE_ALL_FIVE_COMPOSED_STAGES_PASS_IOS_BUILD_ONLY`.
Trước khi chạy CI, **không được** đổi trạng thái lên PASS.

## Giới hạn cố ý

- K9 mới chứng minh **một thứ tự hợp nhất** trên C + LLVM IR canary,
  không bao phủ tất cả tương tác/biến thể/ABI hay toàn bộ Kagura/SLLVM.
- Thử nghiệm đúng chức năng **trước**, không benchmark/đặt ngưỡng
  slowdown ở giai đoạn này. VM Kagura vẫn disabled trong Crane production.
- Không thay `policy.json`, `Makefile`, workflow build sản phẩm,
  Objective-C hook, PAC trên arm64e hoặc IPA K5/K7. K9 cần CI thật
  trước khi lên K10 kiểm tra thứ tự khác/IPA thử riêng.

Kiểm tra portable (không phải native LLVM19 run):

```sh
python3 scripts/test_kagura_k9_composition.py
python3 scripts/test_kagura_k8_passes.py
python3 scripts/test_custom_ollvm_pass_matrix.py
python3 scripts/verify_reconstruction.py
```
