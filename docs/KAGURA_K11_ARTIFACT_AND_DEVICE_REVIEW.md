# K11 — Review IPA CI và log iPhone do người dùng chia sẻ (17/10/2026)

**Kết luận:** ZIP macOS CI K11 **119 entry, CRC sạch, 331/331 kiểm tra độc lập PASS**; IPA iOS arm64 `MH_EXECUTE` có UUID/SHA-256 khớp đúng binary thật và log iPhone 9 dòng do người dùng cung cấp. Đây là **xác minh tính nhất quán của văn bản log với IPA đã build**, không phải device attestation có chữ ký, không kiểm chứng PAC arm64e, benchmark hoặc Crane production.

## Artifact kiểm tra trực tiếp

- ZIP: `DuoDash-Kagura-K11-FIVE-COMPOSED-PASSES-IOS-ARM64-IPA-EXPERIMENTAL.zip`
- SHA-256 ZIP: `e004ea806724659afc9c7fe77efdfe954e8083e1fef10fd75275992405ad45a9`
- Tổng 119 entry duy nhất; ZIP CRC **PASS**; không có path traversal hoặc file mã hóa.
- IPA lồng bên trong: `KaguraFiveLab-TrollStore-arm64.ipa`; đúng 2 file trong `Payload/KaguraFiveLab.app/` (binary và `Info.plist`); CRC IPA **PASS**.
- SHA-256 IPA: `57fe287ee04503c9bf5b64e8f7ed2589ec0b22a5c80fdcb035855b8781fa31d4`
- SHA-256 binary app: `a6b01f4df5c1128e2e8f24f13cde786557b354fd9c07b8ed6a8c8a5103899692`
- Mach-O gốc trong IPA: `MH_MAGIC_64`, CPU `ARM64`, subtype `0`, `MH_EXECUTE`, duy nhất **một LC_UUID** `580390ef-6ba0-357c-a1d7-a0678e3d27ff`. SHA binary trong IPA trùng byte-for-byte với `KaguraFiveLab.app/KaguraFiveLab` của artifact.
- Bundle `com.duodash.research.kagurafivelab`, iPhoneOS min 15.0; IPA unsigned theo CI manifest. Không kết luận TrollStore hoặc cài đặt được trên các thiết bị khác.

## Bằng chứng compiler/runtime

- K10 native metadata và K9 composition report được băm SHA-256 lại, đúng tham chiếu của K11; hai `llvm-link.log` rỗng, datalayout/triple đồng nhất trong C/MVO/merged IR trên macOS/iOS.
- LLVM19 Kagura upstream pinned commit `ac2136ee0408677cf7cdee55307e9b16edd5f4d5`. Cùng một module C+MVO qua **MVO → GENC → FSPLIT → IBR → CI**. Với cả macOS/iOS, từng pass có `-debug-pass-manager` của lớp Kagura đúng, `VerifierPass`, IR SHA và object SHA đúng report, IR/object đổi so với stage liền trước, hai symbol C/MVO còn hiện diện.
- Baseline native macOS và năm stage: log `DD_K9_COMPLETE=PASS`, 4096 vector cho **mỗi** hàm, checksum C `25a3318e3d7d6525`, checksum MVO `64e61045bbc4a250`. Đây là log CI, không chạy lại binary macOS trên host kiểm tra.
- Final `05-ci/ios.o` thực là Mach-O arm64 subtype0 `MH_OBJECT`, hash `087ad94d637a8e4ac4f58b878517069fa755750088ef4fdcabd7436f4b86c682`, khớp hash được nhúng trong K11 evidence.
- `runtime/anti_debug/anti_debug.c` là nguồn resolver Kagura pin được báo cáo, object `ios-kagura-rtld.o` **thực sự định nghĩa** `_kagura_rtld_default_handle`, đồng thời **tham chiếu chưa giải** `_kagura_image_list_contains` và `_kagura_suspicious_image_patterns`.
- `ios-kagura-dependency-01.o` arm64 `MH_OBJECT` từ báo cáo source `runtime/core/imagelist.c` có SHA `d026148dac9995954c61160d5864e94176e3eb712f4b027cb26a7c4d2b582530`. Nlist thực của object **định nghĩa cả hai symbol**; binary IPA cuối cũng định nghĩa cả hai và resolver; không còn Kagura dependency trong closure report, `ipa-link.log` rỗng. `_kagura_init_thunk_table` cũng tồn tại trong final executable, là **symbol local**, không phải export.
- Bản ZIP **không chứa** các tệp `.c` upstream của Kagura; SHA nguồn C chỉ được đối chiếu giữa các JSON report/manifest, không tái băm độc lập từ upstream source. Object, Mach-O nlist và SHA trong ZIP đã được đọc trực tiếp.

## Log iPhone do người dùng cung cấp

```text
DD_K11_IOS_SCHEMA=1
DD_K11_IOS_CONTEXT=IOS_DEVICE
DD_K11_IOS_ARCH=arm64:0x00000000
DD_K11_IOS_APP_UUID=580390ef-6ba0-357c-a1d7-a0678e3d27ff
DD_K11_IOS_PIPELINE=MVO_GENC_FSPLIT_IBR_CI
DD_K11_IOS_VECTORS_PER_FUNCTION=4096
DD_K11_IOS_C_CHECKSUM=25a3318e3d7d6525
DD_K11_IOS_MVO_CHECKSUM=64e61045bbc4a250
DD_K11_IOS_COMPLETE=PASS
```

- Log đúng 9 dòng, schema và thứ tự field đầy đủ; hai checksum bằng native CI và đúng 4096 vector/mỗi hàm. UUID so trực tiếp với `LC_UUID` trong file executable của **IPA thật**, không chỉ so hai JSON.
- SHA-256 của **log đã chuẩn hóa chín dòng UTF-8 với LF cuối**: `b61d53c870a7553564a85eb769bcbcb6717b714590fa9ef691738e618b38987b`. Văn bản gốc gửi qua chat có thể dùng dấu gạch chéo xuôi ngược/định dạng khác; đây chỉ là hash của dạng chuẩn hóa dùng để audit.
- Trạng thái chính xác: `USER_SHARED_TEXT_PARITY_AND_UUID_VALIDATED_NOT_ATTESTED`. User reported actual iPhone execution; verification supports correlation to this precise CI IPA, **không có chứng thực mật mã từ thiết bị, không tự chứng thực thao tác cài/launch, không đo hiệu năng, không thử PAC/arm64e/Crane hooks**.
- `NOT_TESTED_BY_CI` trong build report là **đúng**: runner GitHub không chạy ứng dụng trên iPhone, log người dùng được cung cấp **sau** khi artifact được build.

## Ranh giới nghiêm ngặt

K11 là **lab độc lập** của năm Kagura pass. Không chuyển trạng thái OLLVM/Crane production, không suy rộng sang ObjC hook PAC ABI, không khẳng định anti-tamper hoặc bảo vệ mã mạnh. Năm pass được xác minh về hiện diện IR/object và tính đúng đầu ra kiểm thử canary, không phải bằng chứng bảo mật chống đảo ngược.

Tài liệu nền: [KAGURA_K11_IOS_IPA_LAB.md](KAGURA_K11_IOS_IPA_LAB.md), [KAGURA_K10_ARTIFACT_REVIEW.md](KAGURA_K10_ARTIFACT_REVIEW.md).
