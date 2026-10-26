# Kagura K23 — người dùng báo cáo PASS trên iPhone, chưa được attested

Ngày ghi nhận: **26/10/2026**.

Người dùng cung cấp trực tiếp log gồm **10 dòng** (dữ liệu trong hội
thoại, không phải app-log được chứng thực độc lập):

```text
DD_K23_SCHEMA=1
DD_K23_CONTEXT=IOS_DEVICE_USER_INITIATED
DD_K23_SCOPE=BUNDLED_REFERENCE_ONLY
DD_K23_REFERENCE_UUID=7c0cb853-77aa-3ccb-9f20-560e5f40e587
DD_K23_REFERENCE_SHA256=PASS
DD_K23_CODE_INTERVALS=2
DD_K23_MUTATED_CODE=REJECTED
DD_K23_TRUNCATED_REFERENCE=REJECTED
DD_K23_SELF_INTEGRITY=NOT_IMPLEMENTED
DD_K23_COMPLETE=PASS
```

**Kết quả:** 10/10 fields theo đúng thứ tự output của Swift K23.
UUID trùng với tham chiếu K14 từ artifact K23 gốc đã kiểm tra offline
(`docs/KAGURA_K23_ARTIFACT_DEVICE_FAILURE_REVIEW.md`). Lượt chạy
người dùng thông báo SHA mẫu tham chiếu PASS, hai vùng mã được kiểm
chứng, dữ liệu thử sửa/cắt cụt bị từ chối. Lỗi
`WHOLE_REFERENCE_SHA_MISMATCH` báo trước đây **không còn xuất hiện
trong log người dùng mới**.

**Cập nhật 26/10/2026:** người dùng báo 3 lượt test đều có đúng
chuỗi 10 dòng trên. Đã tiếp nhận ZIP K23 **v2 thực** và đối chiếu toàn
bộ IPA, reference Base64, K23Expected.swift, hash/UUID/2 vùng mã;
**65 entries CRC PASS**. Xem [KAGURA_K23_V2_THREE_RUN_ARTIFACT_REVIEW.md](KAGURA_K23_V2_THREE_RUN_ARTIFACT_REVIEW.md)
để biết SHA-256 và bằng chứng chi tiết.

**Giới hạn bằng chứng:** ZIP có IPA/report/build logs, **không có ba file
log thực từ ba lần chạy**. Người dùng dán một chuỗi 10 dòng rồi báo cả
ba lượt giống nhau, nên đây là **3/3 user-reported functional PASS**, không
phải 3 log độc lập đã được script nghiệm thu hay device attestation.
Không thể xác nhận device type, OS, thời điểm, attested executable hay
chống đóng gói lại. Các flag security/self-integrity vẫn false.

Các flag `k23_running_executable_integrity_verified`,
`k23_runtime_self_integrity_implemented`,
`k23_security_anti_tamper_proven`, `k23_arm64e_pac_tested`,
`k23_production_merge` bắt buộc **false**. K15 BBCheck weak always-pass
vẫn blocked. K18 không bị tự động đánh dấu PASS. Không thay đổi Crane
production.

**Nghiệm thu tiếp theo:** hướng dẫn trong
[KAGURA_K23_IPHONE_QA_RUNBOOK.md](KAGURA_K23_IPHONE_QA_RUNBOOK.md).
Ba log riêng kèm IPA/report v2, công cụ tự động xác minh strict
`scripts/custom_ollvm/kagura_k23/device_qa.py`; ba tên file chỉ
đại diện cho nhãn người dùng cung cấp, không chứng thực hành động.
