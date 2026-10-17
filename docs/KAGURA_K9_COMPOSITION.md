# DuoDash K9 — ghép 5 pass Kagura thật vào một LLVM module

Ngày triển khai: **17/10/2026**. Trạng thái sau khi kiểm ZIP thực:
**MACOS_CI_ARTIFACT_VERIFIED_FIVE_COMPOSED_STAGES**. Đã đối chiếu
179/179 bằng chứng độc lập; xem
[KAGURA_K9_ARTIFACT_REVIEW.md](KAGURA_K9_ARTIFACT_REVIEW.md).
iOS arm64 mới object build-only, chưa có runtime iPhone.

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

## Sửa lỗi hậu kiểm JSON sau native PASS (17/10/2026)

GitHub Actions được người dùng báo đã in
`KAGURA_K9_COMPOSED_FIVE_STAGE_MACOS_NATIVE_AND_ARM64_OBJECTS_PASS`,
sau đó **thất bại ở lệnh Python ngắn trong workflow**, cụ thể
`<stdin>` dòng 4 với `AssertionError`. Đó là dòng cũ:

```python
assert list(r["stages"]) == ["mvo", "genc", "fsplit", "ibr", "ci"]
```

Trong `pilot.py`, report được xuất bằng `json.dumps(...,
sort_keys=True)`: trường `stages` bị sắp xếp tên alphabet
`ci,fsplit,genc,ibr,mvo` khi đọc lại JSON. **Trình tự thực thi
không bị thay đổi**; `report["stage_order"]` và
`stages[name]["index"]` vẫn ghi đúng thứ tự. Đây là lỗi giả định
thứ tự dictionary trong hậu kiểm, không phải bằng chứng no-op hay
native checksum sai.

Đã sửa workflow để chạy
`python3 scripts/custom_ollvm/kagura_k9/pilot.py --verify-report <JSON>`
trên **bản JSON đã serialize ra đĩa**. Hàm kiểm tra nghiêm ngặt
`validate_composition_report()` yêu cầu:

- `stage_order` đúng `mvo,genc,fsplit,ibr,ci`, đủ năm khóa không
  thiếu/thừa, mỗi `pass` + `index` chính xác (1..5); không
  sử dụng thứ tự `dict` của JSON để suy ra thứ tự thực thi;
- mỗi stage phải có `macos_native_4096_per_function=PASS`;
  dấu chứng IR/object delta cho cả `macos` và `ios`, pass class,
  SHA-256 object trước/sau khác nhau và SHA-256 log hợp lệ;
- hai checksum độc lập theo K8 (`25a3318e3d7d6525`,
  `64e61045bbc4a250`), `4096` vector mỗi hàm, không có
  claim iOS runtime/arm64e/Crane production/performance.

Regression tạo report `sort_keys=True` để **tái hiện lỗi cũ**,
xác minh parser mới nhận đúng; đồng thời thử trường hợp sai index,
thiếu stage, fake object, sai checksum và native FAIL đều bị từ chối.

**Bổ sung bằng chứng sau đó:** người dùng đã gửi ZIP K9 đầy đủ;
đối chiếu trực tiếp **75 entry CRC sạch, 179/179 phép kiểm tra PASS**,
cả năm stage thực hiện nối tiếp đúng thứ tự và hai checksum native
khớp từng byte ở mọi bước. Vì vậy **giai đoạn chức năng K9 macOS
đã xác minh từ artifact**; xem
[KAGURA_K9_ARTIFACT_REVIEW.md](KAGURA_K9_ARTIFACT_REVIEW.md).
Cảnh báo `llvm-link` về `target datalayout` thiếu và host triple
không đồng nhất không ảnh hưởng parity canary đã kiểm. **K10**
đang xử lý bằng metadata lấy trực tiếp từ C module LLVM19, có
workflow manual-only mới, chưa có CI macOS thật:
[KAGURA_K10_LINK_METADATA.md](KAGURA_K10_LINK_METADATA.md).

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
