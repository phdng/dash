# Kagura K22 — cổng nghiệm thu tính tái lập của code interval (hai build)

Triển khai mã: **25/10/2026**. Trạng thái sau đối chiếu ZIP thật:
**REAL_MACOS_TWO_BUILD_OFFLINE_CODE_ARTIFACT_VERIFIED_NOT_RUNTIME_SECURITY**.
Artifact SHA-256 `f7f449e3929f78f42650c46925e37e884c8a4612713abd67bf604c8ce8b01c82`, **115 entries, 388/388 đối chiếu PASS**; xem
[KAGURA_K22_ARTIFACT_REVIEW.md](KAGURA_K22_ARTIFACT_REVIEW.md).

## Vì sao K22 là chặng kết thúc nghiên cứu offline

Đã có bằng chứng **artifact K21 macOS thực** (57 entries, 785/785 checks file-backed); K13 có native parity 4.096 vector, K14 có IPA unsigned, K16/K19/K20/K21 kiểm chứng lại source Mach-O liên kết. Chuỗi offline này không cần thêm parser metadata chỉ để kéo dài K-series. Vấn đề còn lại đối với tính tái lập nghiên cứu: bốn vùng code sau compiler/linker có giữ đúng byte giữa **hai lần build macOS độc lập** trong cùng môi trường pin nguồn và toolchain hay không?

## Cơ chế K22 và giới hạn

- Workflow thủ công `.github/workflows/kagura-k22-reproducibility.yml` dùng một Kagura plugin build từ commit `ac2136ee0408677cf7cdee55307e9b16edd5f4d5` với LLVM19, sau đó thực thi **hai chuỗi compile + link** tách biệt, mỗi chuỗi chạy K13 native/IR/object, K14 unsigned IPA, K16 text, K19 symbol, K20 LC_FUNCTION_STARTS và K21 opcode histogram; mỗi bước `--verify` tính lại byte nguồn thật.
- `scripts/custom_ollvm/kagura_k22/reproducibility.py` yêu cầu hai thư mục nguồn khác nhau và gọi `k21.verify` trên cả hai. Phải trùng đúng raw SHA-256, chiều dài, word count, word đầu/cuối và histogram của bốn *symbol intervals* K19/K20. Chênh lệch code bytes bất kỳ **FAIL**.
- Chấp nhận khác `LC_UUID`, whole-executable SHA-256 giữa hai build (linker metadata có thể không tái lập). Lưu hai digest và UUID vào report để kiểm toán. Điều này **không phải reproducible binary toàn phần**.
- Báo cáo `Kagura-K22-REPRODUCIBILITY.json`, `--verify` tái tính từ raw sources; không cho ghi đè và chặn JSON giả/byte bị sửa. Vì hai folder có thể do bất kỳ ai copy, **không có chứng thực hai CI runs độc lập**; workflow chỉ tạo hai compile/link passes riêng trong một runner.
- Artifact dự kiến: `DuoDash-Kagura-K22-TWO-BUILD-REPRODUCIBILITY-OFFLINE-EXPERIMENTAL`, upload dù fail, gồm cả hai thư mục để truy xuất nguyên nhân. Đã có artifact K22 macOS thực được kiểm chứng độc lập offline; **không đánh đồng artifact PASS với runtime/device/security PASS**.

## Tiêu chí kết thúc và số vòng test dự kiến

**Mốc A — nghiên cứu offline hoàn tất:** K22 macOS CI tạo ZIP thật và kiểm tra độc lập 4 interval, native baseline/protected 4.096-vector đều PASS, hai build có cùng code bytes và báo cáo phù hợp. ZIP K22 đã được người dùng cung cấp và review; **0 vòng bổ sung bắt buộc cho phạm vi nghiên cứu offline K13–K22**. Đây là kết quả đã quan sát, không phải dự báo.

**Mốc B — IPA thử nghiệm trên iPhone:** cần riêng quy trình signing/cài sạch, chạy parity + negative cases (không dùng test synthetic làm bằng chứng), soak/stability và rollback, bao gồm kiến trúc thiết bị thực. Ước lượng kế hoạch **3–5 vòng tích hợp/test**, không phải số vòng đã chứng thực đủ.

**Mốc C — production bảo vệ integrity:** **KHÔNG THỂ CHỐT SỐ VÒNG TEST** vì còn công việc phát triển chưa thực hiện:
1. BBCheck K15 đang dùng weak always-return-1; phải có verifier thực sự và fail-closed path.
2. Cần trust root/quy trình ký và threat model, đối chiếu artifact immutable, xử lý adversarial tampering, tránh ký lộ key K17 và phụ thuộc K18 user-skipped.
3. Xác minh trên thiết bị/threat model thực, tương thích arm64e/PAC cho thiết bị tương ứng và Crane hooks lifecycle, có rollback/safe mode.
4. Đánh giá hiệu năng, crash/soak, QA và review dữ liệu production trước khi mở rollout.

Đây là điều kiện chất lượng, không đồng nghĩa chỉ cần nhiều ZIP PASS.

**Ranh giới bắt buộc:** K18 user-skipped, BBCheck K15 weak-stub vẫn blocked; không có security/in-memory attestation, device K22, PAC/Crane production. Không chỉnh Makefile, không trộn compiler plugins.
