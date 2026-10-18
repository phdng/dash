# K15 — Kagura BBCheckPass: điều tra runtime gốc, không tự chạy tamper

Ngày triển khai: **18/10/2026**. Trạng thái:
**STAGED_BBCHECK_PINNED_RUNTIME_PROVIDER_DISCOVERY_NOT_NATIVE**.

Đây là workflow thử nghiệm khác K14. K14 đã có IPA CSEBreak thực
và văn bản log iPhone 8 dòng khớp UUID/checksum, nhưng kết quả đó
**không áp dụng** cho BBCheck. K15 chưa có artifact CI macOS, chưa
có native parity, iOS IPA hoặc iPhone BBCheck.

## Dấu vết chính xác từ K12 thật

Trong ZIP K12 được người dùng cung cấp (registry SHA:
`6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa`),
pass có khai báo thật:

`KAGURA_FN_PASS(BBCheck, "kagura-bbcheck", "Basic block opcode checksum guards", BasicBlockChecksumPass())`

- Loại: **FN**, enable flag `BBCheck`.
- LLVM New Pass Manager:
  `function(kagura-bbcheck),verify`.
- Log opt thực ở cả macOS và iOS:
  `Running pass: kagura::BasicBlockChecksumPass on dd_k8_evaluate`
  và trên `dd_k8_internal`.
- `llvm-dis` IR sau pass có lời gọi **thật**:
  `@kagura_bb_check(i32, i32)`,
  `@kagura_on_tamper_detected()`, vốn **không có trước pass**.
- K12 xác nhận IR delta trên hai target, **không phải native checksum
  hoặc khả năng link iOS**.

**Điểm chặn quan trọng:** hai symbol nói trên điều khiển kiểm tra
basic block và nhánh tamper. Không thể suy luận rằng runtime an toàn,
không có overhead hoặc callback tamper sẽ không terminate. K15
**không sinh shim, stub, override hay bypass** các callback này;
đồng thời **không chạy chúng** khi chưa thẩm định mã nguồn và
dependency closure.

## Workflow thử nghiệm

`.github/workflows/kagura-k15-bbcheck-runtime-audit.yml`

Tên: **Kagura K15 - BBCheck Runtime Provider Research (Experimental)**.
Chỉ `workflow_dispatch`, runner `macos-14`, LLVM19 và source Kagura
commit **`ac2136ee0408677cf7cdee55307e9b16edd5f4d5`**
kèm SHA registry bắt buộc trùng bằng chứng K12.

Quy trình:
1. Chạy các portable negative gates K15/K14/K13/K12, matrix/audit.
2. Build plugin Kagura thật từ commit pin.
3. Compiler LLVM19 Clang O1 biên dịch fixture C công khai K8,
   chạy **riêng** `kagura::BasicBlockChecksumPass`.
   Cả macOS và iOS arm64 phải thấy trace class đúng,
   normalized `.ll` IR delta, **hai lời gọi runtime** và
   Mach-O `MH_OBJECT` delta. `xcrun nm -u -j` xác minh hai
   unresolved symbol đúng trong object; `nm -gU` còn definition
   `_dd_k8_evaluate`.
4. Liệt kê mọi `runtime/**/*.c` từ pinned upstream có nhắc hai
   symbol. Lưu **nguyên bytes source C** và SHA; compile từng
   ứng viên bằng target macOS/iOS arm64, giữ log lỗi nếu compile
   thất bại. Provider chỉ có giá trị nếu Mach-O object
   thật có `nm -gU` definition chính xác, không tính comment,
   prototype hoặc chỉ có lời gọi.
5. Phân loại **mỗi target**: thiếu/duplicate provider,
   có provider nhưng thiếu dependency Kagura phát sinh thêm,
   hay đủ provider trực tiếp nhưng **chưa thực thi runtime**.
   Không tự động link app, chạy tamper callback hoặc tạo IPA.
   Trong report `native_4096_parity` luôn
   `NOT_TESTED_GUARD_HAS_TAMPER_CALLBACK`,
   `ios_ipa_built=false`, `ios_device_executed=false`.
6. `scripts/custom_ollvm/kagura_k15/audit.py` replay
   nguyên file nguồn, source SHA, IR, Mach-O objects,
   `nm` original/undefined, status và graph provider,
   không tin vào cờ `PASS` của JSON.

Artifact GitHub Actions:
`DuoDash-Kagura-K15-BBCHECK-RUNTIME-PROVIDER-RESEARCH-EXPERIMENTAL`.
Luôn upload artifact khi lỗi, bao gồm `Kagura-K15-REPORT.json`,
raw `.ll`, `.bc`, `.o`, nm và compile logs/source C.

## Tiêu chuẩn cho K16 nếu K15 chứng minh closure

Chỉ khi cả macOS và iOS có provider gốc duy nhất, không
thiếu dependency runtime Kagura, đã đọc/đánh giá nhánh tamper
và bảo đảm xử lý error/termination trong lab **không bị bypass**,
mới thiết kế native 4096-vector pilot trên môi trường thử nghiệm
có cách rollback. K15 **không tự nâng trạng thái Native PASS** ngay
cả khi bước scan provider có kết quả tốt.

Không thay Crane production, hooks Objective-C, K5/K7,
K11–K14, arm64e/PAC. Không đưa ra tuyên bố tăng cường bảo mật,
anti-reverse hay benchmark runtime chỉ từ IR delta.
