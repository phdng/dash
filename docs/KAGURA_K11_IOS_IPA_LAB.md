# DuoDash K11 — IPA lab 5 Kagura LLVM19 pass ghép nối tiếp (staged)

Ngày triển khai: 17/10/2026. **Trạng thái: STAGED_MANUAL_IOS_IPA_CI_NOT_VERIFIED**.
Chưa có K11 macOS GitHub Actions artifact, chưa có IPA K11 xác minh thực,
**chưa có log iPhone K11**. Không diễn giải các bài test synthetic portable
thành native/IPA/device PASS.

## Vì sao tách K11 khỏi K10

K10 đã được kiểm chứng **277/277 từ artifact macOS CI** cho
`mvo → genc → fsplit → ibr → ci` trên cùng LLVM19 C+MVO module:
metadata `target triple`/`datalayout` đồng nhất macOS/iOS,
không warning từ hai `llvm-link.log`, IR/object thật sự đổi sau từng
pass, macOS native hai hàm ×4096 vector PASS. K10 **chưa link thành
iOS IPA** và không chứng minh runtime iPhone. Xem
[KAGURA_K10_ARTIFACT_REVIEW.md](KAGURA_K10_ARTIFACT_REVIEW.md).

K11 tạo **ứng dụng UIKit nghiên cứu riêng**:
`com.duodash.research.kagurafivelab`, tên
`KaguraFiveLab-TrollStore-arm64.ipa`. Không thay Crane,
K5/K7, app bundle thực tế hoặc hook Objective-C của sản phẩm.

## Kiến trúc IPA và nguồn pass thực

Workflow riêng: `.github/workflows/kagura-k11-ios-ipa.yml`
(`Kagura K11 - Five Composed Passes iOS arm64 Lab IPA (Experimental)`).

1. Manual `workflow_dispatch`, runner `macos-14`, LLVM19 real
   New Pass Manager, Kagura source pinned đúng commit
   `ac2136ee0408677cf7cdee55307e9b16edd5f4d5`.
2. Chạy lại `scripts/custom_ollvm/kagura_k10/pilot.py` đầy đủ;
   xác thực báo cáo `Kagura-K10-METADATA-REPORT.json` trên file
   thực; hai hàm `dd_k8_evaluate` và `dd_k9_mvo_probe`,
   MVO→GENC→FSPLIT→IBR→CI với IR/object delta, macOS native 2×4096
   baseline parity, iOS arm64 `MH_OBJECT` subtype 0.
3. **Chỉ link** object iOS của stage cuối `05-ci/ios.o` (đã qua
   cả năm pass), **không** dùng host `libkagura_runtime.a`,
   không link baseline `ios/merged.o` cùng lúc (sẽ tạo symbol trùng).
   Kagura `ci` yêu cầu runtime thật `kagura_rtld_default_handle`
   và hệ thống `dlsym`. Script tìm chính xác **một upstream C
   source** dưới `runtime/` định nghĩa/tồn tại symbol ấy tại commit
   pin; cross-compile source đó bằng `xcrun clang -target
   arm64-apple-ios15.0` và iPhoneOS SDK vào `ios-kagura-rtld.o`.
   Nếu có 0 hoặc nhiều hơn 1 nguồn, hoặc lỗi compile/link symbol,
   **CI FAIL**. Tuyệt đối không dùng shim giả, host library hay
   bỏ pass CI để tránh lỗi.

   **Gia cố hậu kiểm cho lần build K11 bị exit=1 sau K10 PASS:**
   trước đây runner đếm bất kỳ `.c` có **chuỗi**
   `kagura_rtld_default_handle`, gồm cả khai báo, lời gọi hoặc
   comment. Đã thay bằng `ci_runtime_resolver.py`, chỉ chọn đúng
   **một định nghĩa hàm C** thật, giữ `ios-rtld-discovery.json`
   (cả các source chỉ nhắc tên, hash source được chọn) và xác minh
   `xcrun nm -gU` cho symbol **được định nghĩa** trong object iOS.
   Workflow thực hiện preflight trước khi chạy lại K10.
   Script ghi `Kagura-K11-BUILD-FAILURE.txt` với stage, dòng và
   lệnh bị lỗi; stderr compile/link giữ tại
   `ios-kagura-rtld-compile.log`,
   `ios-probe-compile.log`, `ios-app-main-compile.log`,
   `ipa-link.log`. Các file này được upload `if: always()`.
   **Log mới (17/10/2026) đã định vị đúng lỗi thực:**
   `KAGURA_K10_SERIALIZED_METADATA_AND_NATIVE_EVIDENCE_PASS`;
   `K11_UPSTREAM_CI_RESOLVER_SOURCE_DEFINED=runtime/anti_debug/anti_debug.c`;
   iOS linker báo thiếu **hai external Kagura symbol**
   `_kagura_image_list_contains` và
   `_kagura_suspicious_image_patterns` khi
   `kagura_check_loaded_dylibs` trong `ios-kagura-rtld.o`
   tham chiếu. Đây là lỗi **thiếu transitive runtime objects** ở
   `K11_LINK_REAL_FIVE_PASS_IOS_EXECUTABLE`, không phải lỗi K10.

   **Sửa K11 tiếp theo:** script mới
   `ci_runtime_closure.py` dùng `xcrun nm -u` đọc các Kagura
   symbols thật chưa được giải trên object iOS đầu vào; tìm ứng
   viên chỉ trong C `runtime/` của Kagura pinned, compile bằng
   `xcrun clang -target arm64-apple-ios15.0`, rồi đòi hỏi đúng
   **một object định nghĩa symbol bằng `nm -gU`**. Nếu tệp
   nguồn ấy tạo ra Kagura unresolved khác thì tiếp tục giải đệ quy
   có giới hạn; nếu không tìm được hoặc phát hiện trùng symbol,
   CI FAIL. `ios-runtime-closure.json` và
   `ios-runtime-extra-objects.txt` ghi các source object, SHA256,
   tên symbol, log build; mỗi object được đưa vào lệnh link iOS
   chỉ khi nó chứa **định nghĩa Kagura thực**. Không dùng
   macOS `libkagura_runtime.a`, không thêm stub. Bỏ tùy chọn
   linker macOS đã deprecated `-Wl,-undefined,error`;
   Apple linker vẫn bắt undefined `MH_EXECUTE` mặc định.

   **Chưa có kết quả run workflow sau sửa này**; giữ
   `k11_ios_ipa_status=STAGED_MANUAL_IOS_IPA_CI_NOT_VERIFIED`
   cho đến khi ZIP artifact thật qua kiểm chứng. Nếu lỗi tái hiện,
   thu `Kagura-K11-BUILD-FAILURE.txt`,
   `ios-runtime-closure.json` và `ipa-link.log`
   để truy tiếp theo tên symbol chứ không nới kiểm tra.
4. Build UIKit `ios_app_main.m` riêng và `ios_probe.c`. Link
   `05-ci/ios.o`, iOS resolver, probe và app bằng Apple iOS linker
   với undefined-symbol error. Lưu `ipa-link.log`,
   `ipa-app-symbols.txt` và `ipa-macho-arm64.txt`.
5. `package_ipa.py` chỉ cho IPA unsigned với đúng hai entry
   `Payload/KaguraFiveLab.app/Info.plist` và
   `Payload/KaguraFiveLab.app/KaguraFiveLab`; xác minh bundle,
   `MH_EXECUTE` arm64 subtype0, `LC_UUID` đúng một, executable
   SHA256 và IPA SHA256. Không codesign, cài/launch thiết bị hay
   khai báo tương thích arm64e/PAC.
6. `ipa_evidence.py` xác minh lại **toàn bộ** K10 bằng chứng thực,
   hash `05-ci/ios.o` khớp JSON, đúng upstream CI source,
   symbol `_dd_k8_evaluate`, `_dd_k9_mvo_probe`,
   `_kagura_rtld_default_handle`, `_dd_k11_ios_parity`
   trong binary và UUID/SHA binary bên trong IPA trùng app
   tạm. Ghi `Kagura-K11-IPA-EVIDENCE.json`; trạng thái device
   `NOT_TESTED_BY_CI`.

Artifact tự upload kể cả khi FAIL:
`DuoDash-Kagura-K11-FIVE-COMPOSED-PASSES-IOS-ARM64-IPA-EXPERIMENTAL`.
Nếu link runtime upstream cho iOS không khả thi, không được bỏ
CI hoặc nới điều kiện pass để giả xanh; đọc artifact tìm nguyên nhân.

## Test thử trên iPhone sau khi có IPA thật

Chỉ import IPA vào TrollStore **theo thao tác của người dùng**, nếu
thiết bị/hệ thống hỗ trợ. Ứng dụng hiện nút chạy 4096 vector cho
mỗi hàm sau 5 pass; log hiển thị để copy/share. Hai checksum
độc lập giữ từ K8/K9/K10:

- C: `25a3318e3d7d6525`
- MVO: `64e61045bbc4a250`

Log K11 PASS **phải có đúng chín dòng**:

```text
DD_K11_IOS_SCHEMA=1
DD_K11_IOS_CONTEXT=IOS_DEVICE
DD_K11_IOS_ARCH=arm64:0x00000000
DD_K11_IOS_APP_UUID=<actual-lowercase-LC_UUID>
DD_K11_IOS_PIPELINE=MVO_GENC_FSPLIT_IBR_CI
DD_K11_IOS_VECTORS_PER_FUNCTION=4096
DD_K11_IOS_C_CHECKSUM=25a3318e3d7d6525
DD_K11_IOS_MVO_CHECKSUM=64e61045bbc4a250
DD_K11_IOS_COMPLETE=PASS
```

`device_log_audit.py` từ chối log thiếu, cắt/đứt checksum, sai
ABI/UUID, thiếu stage hoặc thêm text; có thể so với chính xác
`KaguraFiveLab-IPA-report.json` và
`Kagura-K11-IPA-EVIDENCE.json`. Đây là **tính nhất quán giữa
text người dùng chia sẻ và IPA CI**, không phải chứng thực mật mã,
không khẳng định iPhone đã chạy nếu chưa nhận log tương ứng.

## Phạm vi và nghiệm thu

Portable regression `scripts/test_kagura_k11_ios_ipa.py` kiểm tra
các fixture Mach-O/IPA/UUID giả và log âm tính; không có Apple SDK
trong workspace Windows. CI macOS sẽ tạo và kiểm object/IPA thật.
K11 khác K5 và K7: **không** dùng VM Kagura, không hòa Kagura/Hikari
vào OLLVM production và không đo benchmark ở pha này.

Muốn nâng `k11_ios_ipa_status`, trước tiên phải nhận ZIP artifact
thật và kiểm SHA/CRC, linker+resolver, final `ios.o`, Mach-O UUID,
IPA embedding, K10 full native parity. Chỉ sau đó mới xem xét
`k11_device_runtime` từ log iPhone đúng dạng. Cấm nhảy từ
`IPA_ARTIFACT_VERIFIED` sang `DEVICE_VERIFIED` vì chữ PASS in ở CI.
