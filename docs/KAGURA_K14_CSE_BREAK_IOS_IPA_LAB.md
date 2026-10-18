# DuoDash Kagura K14 — CSEBreakPass iOS arm64 IPA lab độc lập

Ngày triển khai và nhận kết quả: **18/10/2026**. Trạng thái:
**IPA_AND_USER_SHARED_LOG_UUID_CHECKSUM_VERIFIED_NOT_ATTESTED**.

K14 **đã có artifact IPA macOS CI thực** và **8 dòng log iPhone do
người dùng chia sẻ**: [review K14](KAGURA_K14_ARTIFACT_AND_DEVICE_REVIEW.md).
ZIP 53 thành phần CRC sạch, **103/103 điều kiện file-backed PASS**,
IPA executable Mach-O UUID/SHA và native K13 oracle khớp toàn bộ;
UUID log thiết bị trùng đúng UUID trong LC_UUID thật. Nhưng
**không có quan sát thiết bị độc lập hoặc device attestation**.
Không sửa Crane production, Objective-C hooks, arm64e/PAC,
K5/K7/K11 hoặc các giai đoạn khác.

## Vì sao chọn K14 sau K13

[K13 artifact review](KAGURA_K13_ARTIFACT_REVIEW.md) đã xác minh
422/422 điều kiện trên ZIP thật: Kagura pinned commit
`ac2136ee0408677cf7cdee55307e9b16edd5f4d5`,
source registry SHA
`6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa`,
exact **`kagura::CSEBreakPass`** chạy ở macOS/iOS LLVM19,
IR+Mach-O object delta thực, hai native macOS executable chạy
**4096 vector**, cùng checksum `25a3318e3d7d6525`.
Object iOS subtype0 **`ios-cse-break.o`** có external symbol
`_dd_k8_evaluate`, undefined `_strlen` và không có
`_kagura_*` runtime dependency.

K13 có bằng chứng native macOS/object iOS; **K14 đã build
và audit thành công IPA thực** từ object đó, theo [review K14](KAGURA_K14_ARTIFACT_AND_DEVICE_REVIEW.md).
K14 đóng gói duy nhất object này vào bundle mới, không nhúng
K11 `05-ci/ios.o` hay thư viện macOS/Kagura giả, không ghép 5 pass.

## Workflow thủ công

`.github/workflows/kagura-k14-cse-break-ios-ipa.yml`

**Kagura K14 - Isolated CSEBreak iOS arm64 IPA Lab (Experimental)**,
runner `macos-14`, LLVM19.

1. Chạy `scripts/test_kagura_k14_ios_ipa.py` cùng các hồi quy
   K13/K12/K11, pass matrix.
2. Fetch đúng commit Kagura đã pin; kiểm SHA-256 chính xác của
   `include/kagura/PassRegistry.def`, build plugin LLVM19.
3. Chạy lại nguyên `scripts/custom_ollvm/kagura_k13/pilot.py`
   với baseline/protected IR/object, hai native macOS 4096-vector
   parity checksums. `kagura_k13/audit.py` phải replay PASS
   trước khi có quyền link IPA.
4. `kagura_k14/build_ipa.sh` cross-compile `ios_probe.c` và
   UIKit `ios_app_main.m` bằng SDK iphoneos đúng kiến trúc
   `arm64-apple-ios15.0`. Link **chính**
   `ios-cse-break.o` từ K13 với hai object K14 vào
   `KaguraCSEBreakLab.app/KaguraCSEBreakLab`. Thất bại linker
   phải để nguyên lỗi kèm stage log, không thêm shim/fake symbol.
5. Bộ đóng gói `package_ipa.py` yêu cầu Mach-O
   `MH_EXECUTE` ARM64 subtype0 (không phải arm64e), một
   `LC_UUID`, bundle đúng
   `com.duodash.research.kaguracsebreaklab`,
   đúng hai file trong `Payload/KaguraCSEBreakLab.app/`,
   CRC ZIP sạch, SHA-256 executable trong IPA trùng app vừa link.
   IPA **unsigned**, định dạng phục vụ thử nghiệm riêng khi
   thiết bị hỗ trợ phương pháp cài tương ứng.
6. `ipa_evidence.py` đọc lại K13 chứng cứ gốc, SHA của
   `ios-cse-break.o`, iOS probe/entry object và IPA;
   chạy lại `xcrun nm -gU` trên executable và yêu cầu
   external definitions thật `_dd_k8_evaluate`,
   `_dd_k14_ios_parity`, `_main`; không chấp nhận
   Kagura runtime undefined. Đối chiếu UUID và hash
   `Kagura-K14-IPA-report.json` + app nhúng.
   Báo cáo CI luôn giữ `ios_device_execution=NOT_TESTED_BY_CI`.

Artifact xuất ngay cả khi thất bại:
`DuoDash-Kagura-K14-CSEBREAK-IOS-ARM64-IPA-EXPERIMENTAL`.
IPA bên trong:
`KaguraCSEBreakLab-TrollStore-arm64.ipa`.

## Nếu chạy trên iPhone (sau khi IPA macOS đã xác minh)

K14 UIKit lấy **UUID của app image từ LC_UUID ở Mach-O thật**
qua `_dyld_get_image_header(0)`, từ chối simulator và arm64e
tại compile guard. Nút Run chạy đúng **4096 vector K8** qua
`dd_k8_evaluate` CSEBreak đã link và so oracle native
`25a3318e3d7d6525`. Nếu sai checksum, chỉ in
`DD_K14_IOS_ERROR=NATIVE_CHECKSUM_MISMATCH`, **không
in `COMPLETE=PASS`**.

Tám dòng thiết bị khi thành công:

```text
DD_K14_IOS_SCHEMA=1
DD_K14_IOS_CONTEXT=IOS_DEVICE
DD_K14_IOS_ARCH=arm64:0x00000000
DD_K14_IOS_APP_UUID=<uuid trong LC_UUID thật>
DD_K14_IOS_PASS=CSE_BREAK
DD_K14_IOS_VECTORS=4096
DD_K14_IOS_CHECKSUM=25a3318e3d7d6525
DD_K14_IOS_COMPLETE=PASS
```

`device_log_audit.py` kiểm tra **đúng 8 dòng** và UUID khớp
`Kagura-K14-IPA-report.json` + `Kagura-K14-IPA-EVIDENCE.json`
sau khi có artifact thực; không sử dụng log K11/K13 thay thế,
không tự tạo chứng thực mật mã từ một văn bản chia sẻ.

## Giới hạn và điều kiện nâng trạng thái

Trạng thái trước artifact là `STAGED_MANUAL_IOS_ARM64_IPA_CI_NOT_VERIFIED`.
**Nay đã có artifact thực**: SHA/LC_UUID Mach-O, CRC IPA, symbol,
object protected K13 và native 4096 parity được replay PASS.
**Log do người dùng chia sẻ** có đúng 8 dòng, UUID và checksum
khớp IPA/oracle nên đạt `USER_SHARED_TEXT_PARITY_UUID_VALIDATED_NOT_ATTESTED`.
CI **không chạy trên iPhone** và không có chứng thực thiết bị độc lập.
Không tuyên bố device attestation, PAC, Objective-C hook safety,
bảo vệ chống reverse, hoặc hợp nhất Crane.

## Kiểm thử portable

```sh
python scripts/test_kagura_k14_ios_ipa.py
python scripts/test_kagura_k13_native.py
python scripts/test_custom_ollvm_pass_matrix.py
python scripts/custom_ollvm/audit_passes.py
python scripts/verify_reconstruction.py
```

Những test chạy trên Windows có thể dùng Mach-O **giả lập chỉ để
thử các điều kiện bị từ chối**. Không được coi log
`KAGURA_K14_PORTABLE_IPA_PASS` là thành công macOS/iPhone.
