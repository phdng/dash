# DuoDash Hikari — thử nghiệm string/constant obfuscation

**Trạng thái: các pilot Hikari C và Objective-C đã PASS theo xác nhận của người dùng. Đã bổ sung tùy chọn build dylib Hikari-only thử nghiệm, chưa được kiểm chứng trên iPhone.**

Kỹ thuật gợi ý từ SLLVM được thử thông qua module **Hikari có mã nguồn**
trong [lich4/ollvm-pass](https://github.com/lich4/ollvm-pass), **không phải**
trình biên dịch SLLVM. Nguồn và phiên bản được pin cùng commit đang dùng cho
workflow OLLVM: `592f215f852e3957da01b2b15024dc63713a462e`.
SLLVM trên GitHub hiện không có mã nguồn compiler/pass để tích hợp trực tiếp.

## Chạy trên GitHub Actions

1. Đẩy các file workflow/fixture lên nhánh muốn kiểm thử.
2. Vào **Actions → Evaluate Hikari Obfuscation (Experimental) → Run workflow**.
3. Xem Job Summary và artifact `DuoDash-Hikari-Evaluation-Diagnostics` (chứa log/báo cáo). Mặc định `build_tweak` tắt; bật tùy chọn này khi muốn thử tạo một dylib Hikari-only riêng, không dành cho production.
4. Nếu thất bại, xem step và các log `hikari-native.log`, `hikari-ios.log`.

Workflow này **chỉ có `workflow_dispatch`**, không chạy trên push/PR, không
sửa hoặc phụ thuộc thành công của `.github/workflows/build.yml`. Vì vậy
`DuoDashReconstruction` và `DuoDashReconstruction-OLLVM` không thay đổi.

## Phạm vi và cách kiểm tra

`scripts/hikari_eval/policy.json` là policy **riêng** (do Hikari đọc
`policy.json` từ current working directory), không dùng chung với policy
OLLVM tại root. Hikari được biên dịch bằng Homebrew LLVM 19 từ mã nguồn đã
pin. Hai hàm trong `probe.c` được chọn như sau:

- `dd_hikari_probe_string`: `enable-strcry = true`, `strcry_prob = 100`.
  Thử với chuỗi đánh dấu vô hại trong object C. Không đưa key/license thật
  vào fixture.
- `dd_hikari_probe_const`: `enable-constenc = true`,
  `constenc_subxor = true`, `constenc_subxor_prob = 100`,
  `constenc_times = 1`. `constenc_togv` được tắt ở vòng thử đầu tiên.

CI sẽ FAIL nếu thiếu một trong hai log `>>>> run strenc on
dd_hikari_probe_string` hoặc `>>>> run constenc on
dd_hikari_probe_const`, nếu chuỗi đánh dấu không tồn tại ở object chuẩn,
nếu chuỗi đó vẫn tồn tại nguyên dạng trong object Hikari hoặc executable
native được liên kết, hoặc nếu hai bản chạy macOS không trả cùng kết quả
trên 513 đầu vào từ -256 đến 256.

Với iOS arm64, cả hai object cũng được biên dịch bằng cùng SDK và audit,
nhưng **không thể xác nhận hành vi runtime iOS** chỉ bằng compile.

Báo cáo hiển thị dung lượng và tiền tố SHA-256 của object bình thường/Hikari
riêng cho native macOS và iOS. Kiểm tra byte chỉ chứng minh một test marker
không còn nguyên dạng; không xác nhận mọi string của app đều được mã hóa.
Log chạy pass cũng không chứng minh biến đổi luôn đúng cho Objective-C.

## Pilot trên hai helper Objective-C thật (chỉ trong workflow thử nghiệm)

Bên cạnh fixture C đã pass, workflow mới **trích đúng hai function body từ**
`re/RECONSTRUCTION/VersionDeviceHelpers.m` bằng
`scripts/hikari_eval/extract_pilot.py` để biên dịch thành translation unit
`pilot.m` trong `$RUNNER_TEMP`:

- `DDVersionDeviceSanitizeMachineModel`: thử Hikari `enable-strcry` trên
  chuỗi whitelist hiện có của hàm.
- `DDVersionDeviceFormatClientVersion`: thử `enable-constenc` trên các
  nhánh định dạng/version và hằng số hiện có.

Policy nằm tại `scripts/hikari_eval/pilot_policy.json`, được copy sang
`$RUNNER_TEMP/hikari-objc-pilot/policy.json` trước khi biên dịch. Compiler
nạp plugin Hikari trong **thư mục riêng**, không nạp chung với OLLVM.
Không sửa file `.m` production, `Makefile`, hoặc workflow build tweak.

Runner macOS `pilot_runner.m` thử các case chuẩn và biên (model hợp lệ,
whitespace, ký tự bị loại, độ dài vượt 32, phiên bản lỗi, chuỗi Unicode),
đồng thời quét printable ASCII. Bước audit mới yêu cầu **213 vector** chạy
bản chuẩn và bản Hikari giống hệt, có log **strenc** và **constenc** cho
đúng hai hàm và kiểm tra whitelist có mặt trong object chuẩn nhưng không
còn dưới dạng plaintext trong object/binary Hikari. Cũng biên dịch
hai hàm này thành object Objective-C cho iOS arm64 và xác thực pass +
plaintext; không tuyên bố đã kiểm tra runtime trên iPhone.

Nếu pilot Objective-C thất bại, kết quả phải được xem là lỗi hoặc giới hạn
của Hikari khi xử lý Objective-C, **không tự động vô hiệu hoá bài audit**.
Kiểm tra string marker không chứng minh toàn bộ chuỗi đã được bảo vệ; những
selector và symbol cần thiết cho runtime Objective-C vẫn phải được giữ lại.

## Tweak Hikari thử nghiệm (opt-in)

Người dùng đã xác nhận pilot Objective-C trên GitHub Actions PASS. Workflow
thêm checkbox **build_tweak** mặc định **false**. Khi tắt, không build dylib.

Khi bật tại **Actions → Evaluate Hikari Obfuscation (Experimental) → Run workflow**,
CI vẫn chạy đầy đủ fixture C và 213 case Objective-C, rồi thực hiện:

- Tạo sandbox trong RUNNER_TEMP và copy Makefile, control, filter plist và source
  re/RECONSTRUCTION. Không thay đổi mã nguồn production hoặc root policy.json.
- Build Theos bình thường trước để lưu bản chuẩn so sánh.
- Build Hikari riêng với LLVM19 và policy tweak_policy.json trong sandbox;
  chỉ hai helper VersionDeviceHelpers.m được chọn. Không nạp cùng OLLVM.
- Kiểm tra arm64, log đúng hai pass/hàm, symbol bắt buộc, dấu vết plaintext
  trong baseline so với bản Hikari, SHA-256 và kích thước dylib.
- Chỉ upload **DuoDashReconstruction-Hikari-EXPERIMENTAL** khi toàn bộ
  kiểm tra PASS. Artifact có dylib, plist và file cảnh báo.

Workflow Build Reconstruction thông thường không thay đổi; hai artifact
DuoDashReconstruction và DuoDashReconstruction-OLLVM vẫn độc lập.

**Quan trọng:** Đây là bản thử nghiệm chưa được xác nhận chạy đúng trên iPhone.
Không cài trên thiết bị chính hoặc phân phối như bản phát hành. Cần kiểm
tra launch, SpringBoard/CarPlay, license, preferences, crash, rollback và
nguồn gốc/giấy phép Hikari trước khi phát hành rộng rãi.

## Kiểm tra cục bộ

```sh
python3 scripts/test_hikari_integration.py
python3 scripts/test_ollvm_integration.py
python3 scripts/verify_reconstruction.py
```

Thử nghiệm thực tế Hikari trên macOS + LLVM 19 chỉ được xác nhận khi GitHub
Actions mới chạy xanh. Không có trình biên dịch macOS/LLVM 19 trong workspace
Windows thì không thể kết luận tương thích dựa trên static tests.

## Giới hạn an toàn và phát hành

- Hai hàm thật đã được **kiểm tra riêng**; có thể bật Hikari trong dylib thử nghiệm opt-in, nhưng **không trong pipeline production** hoặc Makefile gốc.
- Chưa kiểm chứng Hikari + Obfuscator khi cùng nạp trong một compilation.
- Không bật `enable-fco`, `enable-indibran`, `enable-funcwra` hoặc
  anti-debug/anti-hook. Các pass đó cần một vòng thí nghiệm riêng.
- Pilot Objective-C có thử mã hóa hằng `NSString` trong `DDVersionDeviceSanitizeMachineModel`; chỉ khi macOS CI pass mới kết luận thí nghiệm này tương thích trên các vector đã thử. Objective-C selectors, lớp/runtime và symbol dùng bởi Substrate phải được giữ nguyên.
- Kiểm tra license/provenance của các thành phần Hikari trước khi đóng gói,
  phân phối hoặc tái sử dụng ngoài hoạt động thử nghiệm.
- Không nên lưu secret trong client chỉ vì phép thử mã hóa chuỗi thành công.

Khi bản dylib Hikari thử nghiệm build xanh, bước tiếp theo là kiểm tra runtime trên thiết bị dự phòng, chuẩn bị phương án rollback, rồi mới nghiên cứu FCO/indirect-branch/function-wrapper.
