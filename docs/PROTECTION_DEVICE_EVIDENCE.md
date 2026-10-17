# Protection Lab — đối chiếu Mach-O UUID và bằng chứng thiết bị

**Trạng thái:** Đã có mã nguồn, parser và workflow; người dùng xác nhận
**workflow UIKit benchmark phiên trước đã build xanh**, nhưng chưa đưa
log ứng dụng chạy thật trên A12+. Bước mới **chưa chạy macOS Actions**.

## Mục đích

Đối chiếu `LC_UUID` của file Mach-O thật được xây trên GitHub CI với
`LC_UUID` của **main executable đang được loader nạp** mà ứng dụng
UIKit tự đọc trên iPhone. UUID được kết hợp với:

- Báo cáo chức năng **7 dòng** `DD_RUNTIME_*` (4 x 8192 lượt);
- Báo cáo identity **7 dòng riêng** `DD_EVIDENCE_*`;
- Báo cáo benchmark **17 dòng riêng** `DD_PERF_*`, **tùy chọn**.

Đây là kiểm tra tính *nhất quán giữa các tài liệu do người dùng cung cấp*.
Mach-O UUID **không phải chữ ký số**. Log có thể bị chỉnh sửa/phát lại,
việc ký/provisioning có thể thay đổi binary, và khớp UUID không chứng
minh một thiết bị thật đã chạy app hoặc chứng minh bảo mật PAC.
Không biến các kết quả này thành cờ bật protection cho Crane.

## Artifact mới trên CI

Workflow **Protection Lab - iOS UIKit test app (Experimental)** vẫn chạy
thủ công. Sau khi tạo hai `.app` arm64/arm64e, lệnh
`scripts/protection_lab/device_evidence.py build`:

1. Đọc từng Mach-O `MH_EXECUTE` và ABI `arm64` / `arm64e`
   bằng `device_audit.inspect_executable`;
2. Duyệt `load_commands` có kiểm giới hạn, từ chối command lỗi hoặc
   thiếu/trùng `LC_UUID`;
3. Xuất `build-identity.json` gồm UUID, SHA-256 **của binary chưa
   ký**, kiến trúc và trạng thái `runtime_on_iphone=NOT_TESTED_BY_CI`.

Artifact cũ vẫn giữ nguyên; **không thêm bước ký hay cài lên thiết bị**.

## Xuất bằng chứng từ UIKit

Sau khi bấm **Run 4 suites × 8192** trên thiết bị thật và đạt PASS,
vào **Share result text**, chọn các mục riêng:

- **Share functional PASS/failure** — tệp `iphone-parity.txt`;
- **Share binary identity / OS model** — tệp `iphone-identity.txt`;
- **Share observational benchmark** — `iphone-perf.txt`, chỉ có nếu
  tự bấm nút đo tùy chọn.

Báo cáo identity 7 dòng ví dụ **giả lập** (KHÔNG phải log máy thật):

```text
DD_EVIDENCE_SCHEMA=1
DD_EVIDENCE_CONTEXT=IOS_DEVICE
DD_EVIDENCE_ABI=arm64e:0x80000002
DD_EVIDENCE_MACHO_UUID=7ee12c8d-8c2e-4329-a854-2d4e1bf0a73a
DD_EVIDENCE_DEVICE_MODEL=iPhone14,2
DD_EVIDENCE_IOS_VERSION=16.6.1
DD_EVIDENCE_NOTE=USER_SHARED_NOT_ATTESTED
```

Ứng dụng lấy `LC_UUID` từ `_dyld_get_image_header(0)` và phiên bản
hệ điều hành qua public `NSProcessInfo`, kiểu phần cứng qua `uname`.
**Không lấy serial, UDID, ID quảng cáo, tên cá nhân hoặc identifierForVendor.**
Không thu thập hay gửi lên dịch vụ; chỉ chia sẻ khi người thử bấm Share.

## Bản app được Xcode build và ký trên máy Mac

Nếu dùng project `ProtectionLab.xcodeproj` để ký/chạy arm64, Xcode sẽ
**link binary mới với LC_UUID riêng**, không nhất thiết khớp
`build-identity.json` của workflow CI unsigned. Khi đó dùng
`device_evidence.py verify-local --binary <file ProtectionLab trong
DerivedData> --arch arm64 --identity ... --parity ... --out ...` để đối
chiếu đúng binary local đã build với log chia sẻ. Chế độ này cũng không
chứng thực code signing hoặc tính xác thực log. Xem
[PROTECTION_XCODE_DEVICE_TEST.md](PROTECTION_XCODE_DEVICE_TEST.md).

## Đối chiếu trên máy tính

Từ root của repository (log phải giữ 7/7/17 dòng theo từng tệp UTF-8):

```sh
python scripts/protection_lab/device_evidence.py verify \
  --manifest build-identity.json \
  --arch arm64e \
  --identity iphone-identity.txt \
  --parity iphone-parity.txt \
  --performance iphone-perf.txt \
  --out iphone-evidence-review.json
```

Bỏ `--performance` khi không chạy benchmark. Thay `--arch arm64`
nếu kiểm thử iPhone 6s/A9, không ghi arm64e chỉ vì thiết bị A12+
**có khả năng** PAC. Parser từ chối nếu UUID không khớp slice của
artifact, sai ABI, thiếu dòng PASS, log host trá hình iOS, hoặc benchmark
không đúng định dạng. JSON trả về
`gate=REPORTED_IDENTITY_UUID_AND_PARITY_TEXT_CONSISTENT`, **không**
trả về trạng thái `on_device_attested=true`.

Giữ kèm ảnh màn hình, model, iOS, thời điểm chạy, chi tiết ký/provision
và SHA-256 binary **sau khi ký**. SHA-256 của binary CI chưa ký có thể
khác binary cài thực tế do quá trình ký; LC_UUID bình thường ổn định
nhưng không thay thế kiểm chứng code signature.

Trước khi cân nhắc bảo vệ helper CranePrefs thật, cần kết quả runtime
và overhead đáng tin cậy, ký/cài hợp lệ, cùng kế hoạch rollback rõ ràng.
Không sửa constructor/hook/daemon để giả lập bằng chứng thành công.
