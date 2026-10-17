# DuoDash K10 — sửa metadata LLVM linker trên pipeline K9

Ngày triển khai **17/10/2026**. Trạng thái: **STAGED_MANUAL_STRICT_LLVM_LINK_CI_NOT_VERIFIED**.

## Bằng chứng K9 và lỗi metadata cần giải quyết

[K9 artifact review](KAGURA_K9_ARTIFACT_REVIEW.md) đã kiểm 75 tệp/179 phép kiểm tra PASS: năm pass `mvo → genc → fsplit → ibr → ci` nối tiếp trên một LLVM module, hai hàm đều giữ 4096-vector native parity sau mọi stage. Đây **không phải** kết quả K10.

K9 `llvm-link` vẫn cảnh báo: MVO IR thiếu `target datalayout` (module C có `e-m:o-i64:64-i128:128-n32:64-S128-Fn32`); host MVO triple `arm64-apple-darwin23.6.0` khác C triple `arm64-apple-macosx14.0.0`; iOS cũng thiếu MVO data layout. K9 vẫn native parity PASS, nhưng phải giải quyết trước khi mở rộng ABI/IPA.

## Cách sửa strict trên IR tạm, không thay nguồn K8

K10 gọi lại K9 runner với `strict_link_metadata=True`; **đường chạy K9 mặc định không thay đổi**. Với cả macOS và iOS arm64:

1. LLVM19 Clang compile fixture C K8 `-O1`, `llvm-dis` ra `c.ll`, rồi đọc đúng `target datalayout` và `target triple` Clang đã phát. **Không** dùng `clang -print-target-triple` để dự đoán deployment triple.
2. Từ đúng **K8 `mvo.ll` đã pin hash** sinh IR MVO tạm, đổi tên hàm thành `dd_k9_mvo_probe`, chèn triple/layout lấy trực tiếp từ C. Không sửa body, volatile load/store hoặc file `mvo.ll` nguồn.
3. `llvm-as` rồi `llvm-link`; fail nếu C/MVO/merged khác layout hoặc triple, thiếu/lặp metadata hay `llvm-link.log` còn **warning/error**.
4. Lưu `target-metadata.json` từng target: triple, datalayout, hash SHA-256 của `c.ll`, `mvo-source.ll`, `merged.ll`, số warning bằng 0.
5. Chạy **đúng năm stage K9** trên output liên tiếp, yêu cầu mỗi pass thực sự thay đổi IR/object, exact pass class log, giữ hai hàm, baseline native checksum **C `25a3318e3d7d6525` và MVO `64e61045bbc4a250`**, 4096 vector cho từng hàm sau **mỗi stage**; iOS arm64 `MH_OBJECT` subtype 0 chỉ build, không chạy.

K10 `--verify-report` **đọc lại file thực**: so hash C/MVO/merged IR, `llvm-link.log`, stage IR/objects/logs, exact metadata xuyên suốt từng stage, và byte-for-byte native parity. PASS chỉ khi output `Kagura-K10-METADATA-REPORT.json` có status `MACOS_FIVE_COMPOSED_STAGES_STRICT_METADATA_NATIVE_PASS_IOS_BUILD_ONLY` cùng bản K9 composition report.

## Workflow và nghiệm thu

Workflow thủ công **Kagura K10 - Strict LLVM Link Target Metadata (Experimental)** ở `.github/workflows/kagura-k10-link-metadata.yml`; build Kagura MIT đúng SHA `ac2136ee0408677cf7cdee55307e9b16edd5f4d5` bằng LLVM19/macOS-14. Upload artifact **kể cả khi FAIL**: `DuoDash-Kagura-K10-STRICT-LLVM-LINK-METADATA-LLVM19-EXPERIMENTAL`.

Portable test `scripts/test_kagura_k10_link_metadata.py` phải từ chối C/MVO triple/layout sai, metadata thiếu/lặp, warning `llvm-link` và sai CPU. Các kiểm thử local không chứng minh macOS native K10. Chỉ khi **CI artifact thật** có zero warning và audit raw IR/object/native sau tất cả stage thì mới nâng status K10.

**Ranh giới:** K9 đã verified nhưng giữ nguyên lịch sử cảnh báo cũ. K10 chưa thử iPhone IPA/runtime, Objective-C hooks, arm64e PAC, benchmark hoặc Crane production. K5/K7, `policy.json`, `Makefile`, production workflow không đổi.
