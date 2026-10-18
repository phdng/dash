# DuoDash Kagura K12 — kiểm kê các pass còn lại (chưa nghiệm thu native)

Ngày khởi tạo: **17/10/2026**. Trạng thái:
`PINNED_REGISTRY_INVENTORY_STAGED_NOT_MACOS_VERIFIED`.

## Kết quả hiện đã có trước K12

Không được đếm nhầm những phép kiểm trùng nhau thành pass mới:

- K1/K5: bảy Kagura LLVM pass cấu trúc **STR, FLA, BCF, SUB, CO, BBR, BBS** (bằng chứng CI/native phạm vi riêng).
- K8: năm pass Kagura LLVM bổ sung **IBR, MVO, GENC, FSPLIT, CI**. K9/K10 ghép đủ năm pass này trên cùng module C+MVO, mỗi stage đổi IR/object, native macOS 4096 vector/mỗi hàm, iOS arm64 object. K11 có IPA arm64 thực, ZIP 119 entry, 331/331 checks PASS và log iPhone 9 dòng do người dùng chia sẻ khớp UUID/chksum; không phải chứng thực thiết bị mật mã. Xem [K11 artifact+device review](KAGURA_K11_ARTIFACT_AND_DEVICE_REVIEW.md).
- K6/K7: **VM** Kagura là pass thử nghiệm **riêng**, có bằng chứng CI iOS IPA/log người dùng; không được tự nhập vào pipeline K11 hoặc Crane production.

Như vậy **13 tên pass Kagura riêng biệt đã có bằng chứng thực ở những phạm vi khác nhau**, nhưng KHÔNG phải 13 pass đều đang bật trong Crane, cũng không chứng minh rằng chạy kết hợp 13 pass là an toàn. Ngoài ra plugin `Obfuscator` production đang dùng bốn pass SPLIT/BCF/FLA/SUB của upstream khác (`lich4/ollvm-pass`), Hikari STRCRY/CONSTENC là plugin thử nghiệm tách biệt.

## Vì sao cần kiểm kê đúng upstream pin

Nguồn Kagura mới trên Internet có thể đã thêm hoặc thay tên pass. K12 **không dùng README hiện hành để quyết định số lượng**. Chỉ file:

`include/kagura/PassRegistry.def` của commit cố định
`ac2136ee0408677cf7cdee55307e9b16edd5f4d5`

mới là nguồn thẩm quyền của workflow K12. K12 scan mọi
`KAGURA_FN_PASS`, `KAGURA_MOD_PASS`,
`KAGURA_INFRA_PASS` có tên `kagura-*`; xử lý macro nhiều dòng,
nested constructor, comment và tên trùng. Kiểm tra sự hiện diện của 13 pass
cũ và exact type của năm pass K8, fail nếu thiếu/đổi loại.

Phân loại file JSON thực: `historically_evidenced` (13 pass, không tự
mở rộng phạm vi proof) và `remaining_registered_unverified`
(mọi pass nguồn upstream mà K1/K8/VM chưa xác minh). Tên/đếm **thực tế**
phải lấy từ artifact macOS CI trước khi lập danh sách chuẩn.

Một vài nhóm cần lưu ý gồm AES string, protected-value,
anti-debug, tamper, ObjC, PAC; tại đây **chưa khẳng định chúng tồn
tại hay hoạt động trong đúng commit pin** khi chưa có inventory artifact.
Infrastructure passes `INFRA` chỉ được liệt kê, không tự gọi.

## K12 đã triển khai

Workflow chỉ chạy khi người dùng kích hoạt:
`.github/workflows/kagura-k12-remaining-inventory.yml`
(`Kagura K12 - Remaining Pinned Pass Inventory and Opt-Only Screen
(Experimental)`), runner `macos-14`, LLVM19, Kagura nguồn và
plugin build từ đúng commit đã pin.

1. Portable fail-closed test `scripts/test_kagura_k12_remaining_inventory.py`.
2. `scripts/custom_ollvm/kagura_k12/inventory.py` ghi file nguồn
   `Kagura-K12-PINNED-PASS-REGISTRY.def` byte-for-byte,
   `Kagura-K12-REMAINING-PASS-INVENTORY.json`, SHA-256 registry và
   LICENSE. Tự đọc lại để chống thay đổi report hoặc nới `PASS`.
3. `scripts/custom_ollvm/kagura_k12/smoke.py` screen bằng `opt`
   LLVM19 **từng** pass FN/MOD còn lại độc lập trên K8 C fixture,
   với cả macOS và iOS arm64 bitcode. LLVM19 `llvm-dis` chuyển
   **cả trước và sau** thành file `.ll`. Lọc **chỉ dòng
   `; ModuleID = '...'`** do `llvm-dis` gắn theo đường dẫn
   file, còn giữ nguyên toàn bộ phần IR thật (kể cả attributes
   và metadata). Chỉ khi SHA-256 phần **LLVM IR đã chuẩn hóa**
   khác nhau thì mới ghi `OPT_EXECUTED_IR_DELTA_UNVERIFIED`;
   bitcode bytes hoặc ModuleID khác nhau nhưng nội dung IR
   không đổi thì chỉ là
   `OPT_EXECUTED_NO_IR_DELTA_UNVERIFIED`. Lưu
   `*-opt.log`, `*-llvm-dis.log`, `*-post-opt.bc`,
   `*-post-opt.ll`, SHA của đầu vào/đầu ra, ghi
   `OPT_FAILED_UNVERIFIED` hoặc `OPT_INVALID_BITCODE_UNVERIFIED`
   nếu thật sự gặp lỗi. Không đọc lại output cũ sau lần chạy fail.
   Tất cả đều **UNVERIFIED** về native parity và iPhone;
   dù có IR delta, cũng KHÔNG phải pass validation. Pass `INFRA`
   là `SKIPPED_INFRA_NOT_AUTO_RUN`.
4. `scripts/custom_ollvm/kagura_k12/audit.py` kiểm tra độc lập
   các raw file trên đĩa: magic LLVM bitcode, SHA-256 IR gốc
   **và** chuẩn hóa (độc lập loại trừ ModuleID),
   `dd_k8_evaluate` ABI, iOS triple, số ứng viên, opt status,
   không có artifact kết quả do lần chạy trước lọt vào và **bắt
   buộc** không có native/device PASS trong report. CI fail-closed
   nếu bị sửa tráo JSON hoặc không có IR/object gốc.
5. Artifact luôn lưu khi FAIL:
   `DuoDash-Kagura-K12-PINNED-REMAINING-PASS-INVENTORY-EXPERIMENTAL`.

K12 không link iOS IPA, không có signing/install, không test runtime
Objective-C/PAC, không cấu hình Crane, không sửa Makefile,
`policy.json`, plugin `Obfuscator` hoặc workflow production.

## Gate nghiệm thu mỗi pass mới sau khi có K12 artifact

Chỉ chọn *một* ứng viên rõ ràng có trong pinned registry, xác định
fixture hội đủ điều kiện và runtime đúng nguồn, rồi thực thi quy trình
tách biệt giống K8/K11: opt thực xác nhận pass class, **IR+Mach-O
object delta trên cùng input**, native 4096 hoặc 8192+ parity với
oracle độc lập, iOS arm64 object ABI, tiếp sau đó mới xét IPA lab
manual riêng và log UUID/checksum. Chỉ có pass name hoặc opt parse
success **không được** nâng status thành `PASS`.

K12 không đặt performance/security claim. Nhóm VM trước đây có
overhead thiết bị quan sát rất cao ở K7, không auto-enable vào hot path.
Các pass infrastructure/anti-debug/tamper/PAC đòi đánh giá riêng để
không làm sai ABI/runtime hoặc hành vi kiểm thử iOS.

## Kiểm thử cục bộ

```sh
python scripts/test_kagura_k12_remaining_inventory.py
python scripts/test_kagura_k12_opt_audit.py
python scripts/test_custom_ollvm_pass_matrix.py
python scripts/custom_ollvm/audit_passes.py
python scripts/verify_reconstruction.py
```

Portable K12 test dùng upstream `PassRegistry.def` tổng hợp (16 tên
trong fixture: 13 cũ và 3 pass *giả lập*, **không phải upstream thật**)
để kiểm tra parser, chặn trùng/missing/tamper và scope CI.
Kiểm thử audit dùng file bitcode/IR giả lập và chứng minh rằng
**bitcode hoặc ModuleID khác nhưng IR không đổi không tạo IR PASS**,
đồng thời từ chối sai SHA, thiếu tệp, report giả claim device.
Không được
đọc dòng `registered=16` của fixture như kết quả pinned Kagura CI.
Chưa có macOS K12 artifact, nên **chưa đếm được số pass còn lại thật**
và `k12_new_native_validated=0` cho đến khi nhận và audit CI.
