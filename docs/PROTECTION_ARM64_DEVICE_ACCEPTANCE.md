# Protection Lab — nghiệm thu thực tế arm64 qua TrollStore

Ngày ghi nhận: **2026-10-17**.

## Kết quả do người dùng xác nhận

- Đã cài và mở được ứng dụng Protection Lab trên thiết bị hiện tại qua TrollStore.
- Người dùng xác nhận **tất cả các phép thử đều PASS khi thao tác trên thiết bị**.
  Bộ app hiện có bốn nhóm VM, CE/ICALL, IGV/IBR, Objective-C/ARC,
  mỗi nhóm **8.192 vector** khi bấm Run.
- Người dùng xác nhận **UDID được nhận diện đúng** trong quá trình thử.
  Đây là thông tin người dùng báo; **Protection Lab không yêu cầu, ghi
  lại hay xuất giá trị UDID**. Không commit UDID, serial hoặc tệp chứa
  thông tin nhận dạng cá nhân vào repository.
- Chưa nhận được **log 7 dòng** DD_RUNTIME, log 7 dòng DD_EVIDENCE,
  `build-identity.json` hay thời gian benchmark từ lần chạy thực,
  vì vậy **chưa có đối chiếu log/LC_UUID độc lập trong workspace**.
- Chưa có máy A12+. **arm64e chỉ cần build, link, Mach-O ABI/PAC
  subtype, UUID audit PASS** ở CI; arm64e runtime vẫn
  `DEFERRED_NO_DEVICE`.

## Artifact đã kiểm tra và bước ổn định tiếp theo

Người dùng cũng gửi ZIP artifact CI. Đã soát binary arm64 và arm64e,
đối chiếu hash/UUID với báo cáo build: arm64 IPA structure PASS;
arm64e versioned PAC ABI **build/audit-only PASS**. Đây là kiểm tra
binary CI, không phải log runtime từ thiết bị. Xem
[PROTECTION_CI_ARTIFACT_REVIEW.md](PROTECTION_CI_ARTIFACT_REVIEW.md).

Đã tạo soak test **5 vòng x 4 nhóm x 8192** tự chọn sau functional
PASS, có báo cáo 12 dòng riêng. Chưa có kết quả soak on-device của bản
mới: [PROTECTION_ARM64_SOAK.md](PROTECTION_ARM64_SOAK.md).

## Bản IPA cập nhật và xác nhận soak trên thiết bị

Đã kiểm tra artifact `(4).zip` mới: binary arm64 có mã soak 5 vòng;
SHA-256, LC_UUID và subtype của hai binary khớp báo cáo CI. Người dùng
xác nhận **tất cả bài test trên bản này đều PASS trên thiết bị thật**.
Do chưa gửi log 12 dòng `DD_SOAK_*`, trạng thái được ghi nhận là
`soak.status=USER_REPORTED_PASS` và
`soak.evidence_validation=NOT_PERFORMED_NO_LOGS`, không giả lập bằng
chứng. Xem [kết quả soát artifact](PROTECTION_CI_ARTIFACT_REVIEW.md)
và [receipt 2026-10-17](PROTECTION_ARM64_USER_REPORTED_ACCEPTANCE_2026-10-17.json).

Dùng `device_acceptance.py --user-confirmed-pass --user-confirmed-soak-pass`
để tạo receipt tương đương; thêm `--soak iphone-arm64-soak.txt` **chỉ khi
đã xuất log thật** để kiểm tra định dạng/kiến trúc, không chứng thực
mật mã hay định danh thiết bị. UDID không được lưu.

## Hai mức nghiệm thu minh bạch

`scripts/protection_lab/device_acceptance.py` tạo receipt JSON
**không chứa UDID**:

1. **USER_REPORTED_PASS** (trạng thái hiện tại): tin vào lời xác nhận
   của người thử; `evidence_validation=NOT_PERFORMED_NO_LOGS`.
2. **SHARED_LOG_TEXT_AND_CI_UUID_CONSISTENT**: nếu người dùng sau này
   cung cấp đúng bộ log parity, identity và CI build identity; kiểm tra
   lại 7 dòng chức năng/7 dòng UUID/ABI và tùy chọn 17 dòng benchmark.
   Đây là kiểm tra nhất quán dữ liệu do người dùng cung cấp,
   **không phải chứng thực cryptographic** hoặc kiểm tra PAC A12+.

Để xuất receipt mức 1:

```sh
python scripts/protection_lab/device_acceptance.py \
  --user-confirmed-pass \
  --out arm64-device-acceptance.json
```

Để nâng lên mức 2 **chỉ khi có log thật**:

```sh
python scripts/protection_lab/device_acceptance.py \
  --user-confirmed-pass \
  --manifest build-identity.json \
  --parity iphone-parity.txt \
  --identity iphone-identity.txt \
  --out arm64-device-acceptance.json
```

Có thể thêm `--performance iphone-perf.txt` nếu đã bấm benchmark trên
iPhone và đã xuất log 17 dòng. Nếu nhầm log host, sai kiến trúc, thiếu
suite hay UUID không khớp CI, công cụ sẽ lỗi thay vì nâng mức PASS.
Receipt không lưu model/iOS hoặc UDID; chỉ giữ checksum log và Mach-O
LC_UUID (là định danh binary nghiên cứu, không phải định danh thiết bị).

**Cảnh báo phạm vi:** nghiệm thu này chỉ áp dụng ứng dụng lab riêng,
**không chứng minh Crane production đã được bảo vệ bằng VM/SLLVM/IGV/IBR**
hoặc các kỹ thuật thương mại. Crane OLLVM STRONG production vẫn giữ
nguyên; mọi thử nghiệm tích hợp về sau cần opt-in, rollback và CI riêng.

Xem [PROTECTION_TROLLSTORE_ARM64.md](PROTECTION_TROLLSTORE_ARM64.md)
và [PROTECTION_DEVICE_EVIDENCE.md](PROTECTION_DEVICE_EVIDENCE.md).
