# DuoDash K10 — kiểm chứng artifact LLVM19 strict target metadata (17/10/2026)

Đầu vào ZIP **nguyên bản người dùng gửi**:
`DuoDash-Kagura-K10-STRICT-LLVM-LINK-METADATA-LLVM19-EXPERIMENTAL.zip`.

- ZIP SHA-256: `3567fca73c11aaea0b30e50ca8eb9cda6491ff32cb7832893ffd104725f59383`.
- Kích thước: **136.361 byte**, **80 entry** không trùng; `ZipFile.testzip()` **CRC sạch**.
- Báo cáo thật trong ZIP: `Kagura-K10-METADATA-REPORT.json`
  và `Kagura-K9-COMPOSITION-REPORT.json`. Hai schema 1, pinned Kagura
  commit `ac2136ee0408677cf7cdee55307e9b16edd5f4d5`.
- **277/277 phép đối chiếu độc lập PASS** trên byte thật của `*.ll`,
  `*.o`, `*-opt.log`, `native.log`, hai `llvm-link.log`,
  hai `target-metadata.json`, báo cáo stage và SHA-256. Không chỉ
  tin nội dung status `PASS` trong JSON.
- Hai báo cáo nhất quán; SHA-256 bản K9 composition JSON được K10
  trích dẫn **khớp đúng bytes** trong ZIP.

## K10 giải quyết cả hai cảnh báo K9

**MacOS:**
- C `c.ll`, MVO `mvo-source.ll`, merged `merged.ll`
  đều có `target triple = "arm64-apple-macosx14.0.0"`.
- C, MVO, merged đều có datalayout
  `e-m:o-i64:64-i128:128-n32:64-S128-Fn32`.
- `macos/llvm-link.log` **0 byte**, không warning/error.

**iOS arm64:**
- C/MVO/merged đều có `target triple = "arm64-apple-ios15.0.0"`,
  cùng datalayout như macOS.
- `ios/llvm-link.log` **0 byte**, không warning/error.
- Các sidecar `macos/target-metadata.json` và
  `ios/target-metadata.json` khớp JSON cấp cao và SHA-256 của
  **IR thực** `c.ll`, `mvo-source.ll`, `merged.ll`.

**Từ K9 → K10:** MVO IR không còn thiếu datalayout; triple host
không còn khác C module. K8 `mvo.ll` nguồn **không thay đổi**,
chỉ IR được sinh ra cho từng target mang metadata Clang đã phát.

## Năm pass phối hợp thật: liên tiếp trên cùng module

| Stage | Pass | Trace LLVM / verifier | IR + object delta macOS | IR + object delta iOS |
|---|---|---|---|---|
| 01 | `mvo` `MemoryValueObfuscationPass` | PASS | PASS `%mixed.mvo`, `%value.mvo` | PASS |
| 02 | `genc` `GlobalEncryptionPass` | PASS | PASS `.dec` | PASS |
| 03 | `fsplit` `FunctionSplitPass` | PASS | PASS hàm `__kg_*` | PASS |
| 04 | `ibr` `IndirectBranchPass` | PASS | PASS `__kagura_fptr_*` | PASS |
| 05 | `ci` `CallIndirectionPass` | PASS | PASS `__kagura_thunk_table` | PASS |

Mỗi stage:
- có class đúng trong log `-debug-pass-manager` và
  `VerifierPass`, không chỉ `opt` exit=0;
- IR **và** object thực khác stage ngay trước, SHA-256 object trước
  và sau, SHA-256 IR/trace khớp báo cáo JSON; pass-specific markers
  xuất hiện, hai public ABI `dd_k8_evaluate` và
  `dd_k9_mvo_probe` còn tồn tại;
- macOS/iOS giữ triple và datalayout xuyên suốt; mọi
  object trước/sau là Mach-O `MH_MAGIC_64`, CPU arm64,
  subtype `0`, `MH_OBJECT` (filetype `1`).
  Đây là **cross-build object**, chưa chạy trên iPhone.

`plain-native.log` và cả năm `01-mvo/native.log` đến
`05-ci/native.log` **khớp từng byte** và có schema:

```text
DD_K9_SCHEMA=1
DD_K9_VECTORS_PER_FUNCTION=4096
DD_K9_C_CHECKSUM=25a3318e3d7d6525
DD_K9_MVO_CHECKSUM=64e61045bbc4a250
DD_K9_COMPLETE=PASS
```

Hai hàm độc lập × 4.096 vector mỗi stage; native executable Mac
`MH_EXECUTE` được kiểm ở baseline và sau cả năm stage.
K10 báo `MACOS_FIVE_COMPOSED_STAGES_STRICT_METADATA_NATIVE_PASS_IOS_BUILD_ONLY`.

## Provenance nguồn giữ nguyên

Hash mà K10 báo **được tính đối chiếu lại từ Workspace thực**:

- K8 `fixture.c`: `39e0b833ab8574bf2e8abb2a66dc440d06424a82d6a0f371297e313bc91992fc`
- K8 `runner.c`: `4c1929802af256c6a7130e8f010e26f517f887a5b8dcbaad53434c6eb5bc2d6e`
- K8 `mvo.ll`: `abbe02b364571b77fb94fff673111bf381f694211cca148d18a73650a8343e50`
- K9 `runner.c`: `b10fafa96bbe4e23aea2a5460fce86db8244a8b9a81314f2abe608b17e6afefc`

Nguồn Kagura được pin và ghi trong report, tuy nhiên kiểm chứng
artifact không tương đương chứng thực mật mã về binary compiler,
phần cứng hay khả năng chống reverse-engineering.

## Kết luận và giới hạn

**K10: MACOS_CI_ARTIFACT_VERIFIED_STRICT_LLVM_METADATA** — với
một thứ tự `mvo → genc → fsplit → ibr → ci`, module C+MVO IR,
zero `llvm-link` warnings, Mac 2×4096 native parity từng stage,
iOS arm64 object build-only. K9 lịch sử vẫn có cảnh báo link,
**không thay lịch sử K9**.

**Không có** K10 IPA, cài/chạy trên iPhone, arm64e/PAC runtime,
Objective-C selector/hook ABI, Crane production integration,
benchmark latency hay security-strength proof. K5/K7 và OLLVM
STRONG hiện hành không thay đổi.

Bước IPA lab kế tiếp **K11 đã có artifact macOS CI được kiểm chứng**
([review K11](KAGURA_K11_ARTIFACT_AND_DEVICE_REVIEW.md)):
119 ZIP entry, 331/331 kiểm tra PASS, IPA arm64 `MH_EXECUTE`,
object `05-ci/ios.o` sau cả năm pass và upstream Kagura iOS
runtime thật. Log iPhone **do người dùng chia sẻ** khớp UUID
IPA/2 checksum/4096 vector mỗi hàm; không phải chứng thực thiết bị.
K10 tự nó vẫn chỉ là giai đoạn `MH_OBJECT` build-only, không có
K10 IPA riêng. K11 không ghép vào Crane hay khẳng định PAC arm64e.
