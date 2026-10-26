# Hướng dẫn chạy K23 v2 — nghiệm thu iPhone 3 lượt (manual-only)

**Mục tiêu:** kiểm tra chức năng **bundled K14 reference verifier** đã
được user báo PASS một lượt (10 dòng). Thực hiện **ba lượt thao tác
riêng**, đối chiếu log với **chính IPA v2** macOS build. Chưa phải bảo vệ
mã thực thi trong RAM, anti-tamper, security root of trust, chứng thực
thiết bị hay Crane production.

## 1. Chọn đúng bản build K23 v2

- Mở repo GitHub branch `chore/reconstruction-build-ci`, vào
  **Actions → Kagura K23 - iOS Bundled Reference Runtime SHA Lab
  (Experimental) → Run workflow** (workflow_dispatch), chọn branch và
  chạy. Dùng ZIP artifact tên
  `DuoDash-Kagura-K23-IOS-RUNTIME-REFERENCE-LAB-EXPERIMENTAL` của
  **run thành công mới nhất có mã K23 v2**. Không dùng ZIP của K23 v1
  trước khi sửa SHA.
- Giải nén ZIP trên máy tính, tìm thư mục có **đúng ba tệp**:
  `KaguraK23RuntimeLab-TrollStore-arm64.ipa`,
  `Kagura-K23-RUNTIME-REFERENCE-IPA-REPORT.json`, `K23Expected.swift`.
  Đây là `--artifact-dir`; hãy giữ nguyên cùng thư mục.
- IPA bên trong phải có `CFBundleVersion=2` và resource
  `KaguraCSEBreakLab.reference.b64`. Test script kiểm tra cả hai;
  nếu thiếu, **không dùng artifact này**.
- IPA **unsigned**; chỉ cài trong môi trường thử nghiệm iPhone
  đã có phương thức cài IPA hợp pháp và tương thích (ví dụ TrollStore
  nếu thiết bị thực tế hỗ trợ). IPA không phải App Store build. Chưa có
  cam kết tương thích arm64e/PAC hay mọi phiên bản iOS. Không chỉnh
  cấu hình Crane hoặc các tweak production.

## 2. Ba lượt cần thực hiện trên iPhone

1. **Fresh install:** gỡ K23 lab cũ (không gỡ ứng dụng/tweak
   production), cài lại IPA v2, xác minh giao diện ghi `v2`, bấm
   **Verify + run tamper negative tests**. Chỉ khi hiển thị đầy đủ 10
   dòng và `DD_K23_COMPLETE=PASS` mới chuyển bước tiếp. Bấm
   **Share full diagnostic log** → lưu văn bản nguyên bản thành
   `01-fresh.txt`. Nếu FAIL, giữ nguyên log và dừng nghiệm thu.
2. **Relaunch:** đóng hẳn app K23 và mở lại, không cài lại. Bấm Verify,
   chia sẻ `02-relaunch.txt` đúng 10 dòng. Để ý không crash, treo,
   UI không phản hồi. Nếu FAIL dừng, không sửa log.
3. **Reinstall:** gỡ riêng K23 lab lần nữa, cài lại **cùng IPA v2**
   ở lượt 1, bấm Verify, chia sẻ `03-reinstall.txt`. Không ghi đè hai
   tệp log trước.

Có thể chạy thêm 5–10 lần nếu cần xem tính ổn định, nhưng **3 log
riêng theo ba bước** là tiêu chí tối thiểu cho bộ công cụ dưới đây.
Lưu file dạng UTF-8/ASCII **đầy đủ 10 dòng và dấu xuống dòng cuối**.
Không thêm thông tin máy, Apple ID, serial hoặc dữ liệu cá nhân.

## 3. Chạy bộ kiểm chứng từ Windows PowerShell

Tại thư mục gốc repository DuoDash, đặt 3 file log trong `k23-logs`.
Giải nén ZIP artifact v2 bằng PowerShell, ví dụ:

```powershell
Expand-Archive ".\DuoDash-Kagura-K23-IOS-RUNTIME-REFERENCE-LAB-EXPERIMENTAL.zip" -DestinationPath ".\k23-artifact" -Force
Get-ChildItem ".\k23-artifact" -Recurse -Filter "Kagura-K23-RUNTIME-REFERENCE-IPA-REPORT.json"
```

Nếu report nằm trực tiếp trong `k23-artifact`, chạy đúng lệnh:

```powershell
python scripts/custom_ollvm/kagura_k23/device_qa.py --artifact-dir ".\k23-artifact" --fresh-install ".\k23-logs\01-fresh.txt" --relaunch ".\k23-logs\02-relaunch.txt" --reinstall ".\k23-logs\03-reinstall.txt" --out ".\K23-QA-REVIEW.json"
```

Nếu report nằm ở thư mục con, thay `--artifact-dir` thành
**thư mục chứa report + IPA + K23Expected.swift**. Không truyền ZIP
trực tiếp thay cho đường dẫn thư mục.

Khi cả ba văn bản và artifact thống nhất, chương trình ghi
`K23-QA-REVIEW.json` và in:

`K23_V2_THREE_STAGE_USER_SHARED_LOG_CORRELATION_PASS`

Đó là **PASS việc so khớp file do người dùng gửi**, không chứng thực
ba lần chạy thực sự hay integrity của chính mã app. File JSON chứa
SHA-256 IPA và SHA của từng log cùng các flag chứng cứ hạn chế.

Nếu script báo lỗi: **không sửa flag thành PASS**, hãy gửi nguyên văn
cảnh báo, ZIP/report gốc và log K23 liên quan. Nếu bạn chỉ muốn kiểm một
log, có thể dùng công cụ `device_log_audit.py`:

```powershell
python scripts/custom_ollvm/kagura_k23/device_log_audit.py --log ".\k23-logs\01-fresh.txt" --ipa-report ".\k23-artifact\Kagura-K23-RUNTIME-REFERENCE-IPA-REPORT.json" --out ".\K23-SINGLE-REVIEW.json"
```

Phải dùng report **cùng IPA** để tránh nhầm SHA/UUID giữa các lượt build.
Không dùng file QA cũ khi thay artifact: script từ chối ghi đè report
đã tồn tại. Chỉ xoá/đổi tên sau khi đã lưu bản review cũ nếu muốn
nghiệm thu run khác.

## 4. Tiêu chí bước tiếp theo sau 3 lượt

- Toàn bộ 3 log đều đúng 10 dòng, SHA của IPA/report/transport/UUID
  consistent; không crash và không xảy ra FAIL sau reopen/reinstall.
- Ghi nhận tính năng bundled reference **ổn định theo báo cáo người
  dùng**. Vẫn giữ `running_app_self_integrity=False`, không hợp nhất
  BBCheck weak stub hoặc bật Crane production.
- Trước khi đi xa hơn về an toàn, phải thiết kế một **trust root riêng**
  và threat model rõ ràng, verifier thực sự đối chiếu executable/in-memory
  code, negative/adversarial tests, ký/cài/rollback, và QA iPhone/PAC
  trên thiết bị phù hợp. Đây là một mốc mới, không thể đánh dấu hoàn tất
  bằng 10 dòng K23 hiện tại.
