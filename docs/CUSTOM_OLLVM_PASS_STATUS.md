# DuoDash — trạng thái pass thực trong custom OLLVM

Cập nhật: 2026-10-17 · Áp dụng cho nhánh nghiên cứu `chore/reconstruction-build-ci`.

## Phân biệt các phạm vi thực thi

**Không có compiler pass mới được nhập vào plugin `Obfuscator` ở thời
điểm lập báo cáo này.** `scripts/protection_lab` chứa các mẫu C/ObjC
được biến đổi ở mức **source**, không thể tự động trở thành LLVM IR pass.
Các bài kiểm thử TrollStore arm64 (functional/soak) được người dùng xác
nhận PASS, nhưng chúng chạy **ProtectionLab**, không phải chứng cứ
plugin compiler đã thêm CE/ICALL/IGV/IBR.

| Nhóm | Tên cụ thể | Đã được compiler thực thi trong phạm vi nào? |
|---|---|---|
| **Custom OLLVM đang dùng** | SPLIT, BCF, FLA, SUB | LLVM 19 + `obfuscator/Obfuscator`; có log pass trên probe/CranePrefs arm64 |
| **LLVM pass thật nhưng plugin riêng** | Hikari `strcry`, `constenc` | Pilot Hikari độc lập, mã nguồn có ở cùng repo upstream; không gộp `Obfuscator` |
| **Mã thử nghiệm, không phải LLVM pass** | CE, ICALL, IGV, IBR, ObjC CE, VM | `scripts/protection_lab/` (C/ObjC, static bytecode); app arm64 đã PASS theo báo cáo người dùng |
| **Đề xuất pass mới chưa triển khai** | string CE, constant encoding, indirect branch, indirect call, global indirection, virtualization | Chưa có code LLVM pass tương ứng trong custom `Obfuscator` của DuoDash |

Đọc chính xác machine-readable:
`scripts/custom_ollvm/pass_registry.json`.

## Kagura × SLLVM: thử nghiệm MAX_CANDIDATE mới

Đã triển khai [KAGURA_SLLVM_CUSTOM_MAX.md](KAGURA_SLLVM_CUSTOM_MAX.md)
và workflow manual-only `.github/workflows/kagura-max-candidate.yml`:
mã C++ **Kagura LLVM IR pass thật** được tải ở SHA cố định, build
LLVM19 trên macOS, chạy pipeline thử `str,fla,bcf,sub,co` qua
`opt --load-pass-plugin` trên một hàm C synthetic, so native 8.192
vector, quan sát IR/object/Mach-O và compile-only iOS arm64/arm64e.
K0 đã có **artifact CI macOS thực** (8.192 vector native parity, IR/object
thay đổi, marker biến mất), được đối chiếu tại
[KAGURA_K0_ARTIFACT_REVIEW.md](KAGURA_K0_ARTIFACT_REVIEW.md). K1 đã chạy CI macOS và có artifact đã đối chiếu: cả 7 pass sinh IR/object
khác biệt, mỗi giai đoạn giữ 8.192 vector native parity; xem
[KAGURA_K1_ARTIFACT_REVIEW.md](KAGURA_K1_ARTIFACT_REVIEW.md).
**Chưa kiểm thử Kagura K1 runtime iPhone hay tích hợp Crane**.

K2a đã thêm **TU scope isolation** và benchmark native 11 mẫu × 32.768
calls theo từng stage; **artifact macOS CI mới đã được kiểm chứng:** baseline 15 ns/call, K1+BBS 82 ns/call (median 5,467×); BBR p95 dao động lớn và chưa có máy iPhone Kagura runtime. Chi tiết [KAGURA_K2_ARTIFACT_REVIEW.md](KAGURA_K2_ARTIFACT_REVIEW.md).

K3 đã bổ sung benchmark **16 vòng cân bằng thứ tự**, 8 biến thể,
176 mẫu/biến thể và parser kiểm tra log toàn vẹn; **chưa có native macOS
artifact K3**. Xem [KAGURA_K3_INTERLEAVED_BENCH.md](KAGURA_K3_INTERLEAVED_BENCH.md).

Đã thêm app **KaguraLab IPA arm64**, chứa một hàm baseline và một
hàm có 7 pass Kagura thực, UI chạy 8192 parity trên iPhone và benchmark
tùy chọn. Workflow có kiểm tra native pass trace/Object/IPA, nhưng
**chưa có macOS build IPA hoặc on-device Kagura runtime PASS**.
[Hướng dẫn KaguraLab/TrollStore](KAGURA_IOS_TROLLSTORE_PILOT.md).

**K8 (đã có macOS LLVM19 CI artifact, đối chiếu độc lập):** workflow
manual-only `.github/workflows/kagura-k8-pass-coverage.yml` đã thực
thi đủ 5 pass Kagura `ibr/mvo/genc/fsplit/ci` (2 function + 3 module).
IR/object đều có delta thật, native parity 4096 vector từng pass PASS,
iOS arm64 MH_OBJECT build-only (chưa chạy trên iPhone). ZIP 74 entry
CRC sạch, SHA và 92/92 phép kiểm chứng độc lập PASS. Chưa kiểm thử
pipeline kết hợp, Crane/arm64e PAC runtime hoặc hiệu năng K8.
Xem [KAGURA_K8_ARTIFACT_REVIEW.md](KAGURA_K8_ARTIFACT_REVIEW.md) và
[KAGURA_K8_FIVE_PASS_VALIDATION.md](KAGURA_K8_FIVE_PASS_VALIDATION.md).
**K9 (đã xác minh ZIP macOS LLVM19 phối hợp 5 pass):**
workflow manual-only
[KAGURA_K9_COMPOSITION.md](KAGURA_K9_COMPOSITION.md)
ghép C + MVO IR vào **một LLVM19 module**, chạy nối tiếp
`mvo,genc,fsplit,ibr,ci`; từng stage có IR/object delta thật,
hai hàm × 4096 native parity và iOS arm64 object build-only.
Artifact 75 entry CRC sạch, **179/179 kiểm tra độc lập PASS**.
Lưu ý `llvm-link` cảnh báo datalayout MVO thiếu và host triple
khác C module; chưa có IPA/runtime iPhone/arm64e/Crane production.
Xem [KAGURA_K9_ARTIFACT_REVIEW.md](KAGURA_K9_ARTIFACT_REVIEW.md).
**K10 (artifact macOS LLVM19 đã xác minh độc lập):**
[KAGURA_K10_ARTIFACT_REVIEW.md](KAGURA_K10_ARTIFACT_REVIEW.md):
ZIP 80 entry, CRC sạch, **277/277 PASS**. C/MVO/merged có
target datalayout+triple trùng nhau cả macOS và iOS,
`llvm-link` **0 warning**, sau từng stage năm pass IR/object
đổi thật và native hai checksum ×4096 vector giữ nguyên.
iOS arm64 object build-only; chưa chạy trên iPhone/arm64e/PAC,
không sửa Crane, K5/K7 hoặc ObjC hooks.
**K11 IPA lab đã xác minh artifact ZIP (331/331 kiểm tra PASS):**
[KAGURA_K11_ARTIFACT_AND_DEVICE_REVIEW.md](KAGURA_K11_ARTIFACT_AND_DEVICE_REVIEW.md)
cho thấy IPA iOS arm64 `MH_EXECUTE`, ZIP 119 entry, CRC sạch,
UUID `580390ef-6ba0-357c-a1d7-a0678e3d27ff`, liên kết object
`05-ci/ios.o` K10 với resolver Kagura thật + imagelist runtime.
**Log iPhone 9 dòng do người dùng chia sẻ khớp UUID IPA thật,
2 checksum ×4096 vector**, chưa phải chứng thực thiết bị mật mã.
Không xác minh PAC arm64e, ObjC hooks hay Crane production.
Thiết kế workflow: [KAGURA_K11_IOS_IPA_LAB.md](KAGURA_K11_IOS_IPA_LAB.md).
K7 VM đã có log `a.txt` xác minh UUID/checksum với IPA thực, median
paired iPhone overhead 71,5× (3 cặp, chưa phải chứng thực mật mã).

**K12 — artifact registry và opt-only đã được đối chiếu độc lập:**
[KAGURA_K12_ARTIFACT_REVIEW.md](KAGURA_K12_ARTIFACT_REVIEW.md).
ZIP 147 entry CRC sạch, **2.029 file-backed checks PASS**. Registry
CI cho thấy **36 tên Kagura**: K1/K5 (7) + K8–K11 (5) +
VM K6/K7 (1) = **13 tên từng có bằng chứng riêng** và **23 tên
chưa được nghiệm thu native** (8 IR delta ở cả macOS/iOS,
9 no-delta trên fixture, 6 INFRA không tự chạy).
Bitcode iOS thật dùng LLVM wrapper, bản audit đã xử lý đúng.
K12 opt-only **không phải native/IPA/iPhone PASS** và không có pass
mới nào được tích hợp vào `Obfuscator`. Quy trình:
[KAGURA_K12_REMAINING_PASS_INVENTORY.md](KAGURA_K12_REMAINING_PASS_INVENTORY.md).

**K13 — CSEBreak native macOS + iOS object artifact đã xác minh:**
[KAGURA_K13_ARTIFACT_REVIEW.md](KAGURA_K13_ARTIFACT_REVIEW.md).
ZIP K13 41 entry CRC sạch, **422/422 kiểm tra độc lập PASS**;
trace LLVM19 thực `CSEBreakPass`, IR/object Mach-O delta,
hai executable macOS arm64 có 4096-vector checksum bằng
`25a3318e3d7d6525`, iOS arm64 subtype0 `MH_OBJECT`.
**Không có IPA/iPhone K13**; không bật pass K13 trong Crane production.
Quy trình: [KAGURA_K13_CSE_BREAK_NATIVE_LAB.md](KAGURA_K13_CSE_BREAK_NATIVE_LAB.md).

**K14 — IPA CSEBreak và văn bản log thiết bị đã được đối chiếu:**
[KAGURA_K14_ARTIFACT_AND_DEVICE_REVIEW.md](KAGURA_K14_ARTIFACT_AND_DEVICE_REVIEW.md).
ZIP K14 thật gồm **53 thành phần, 103/103 checks PASS**, IPA unsigned
arm64 MH_EXECUTE, executable SHA/LC_UUID và object CSEBreak đúng
nguồn K13. Log iPhone 8 dòng do người dùng chia sẻ có UUID
`7c0cb853-77aa-3ccb-9f20-560e5f40e587` trùng binary và
checksum `25a3318e3d7d6525` trùng oracle K13 **4096 vector**.
Đây là **user-shared text parity, không phải device attestation**;
CI cũng không chạy iPhone. Quy trình:
[KAGURA_K14_CSE_BREAK_IOS_IPA_LAB.md](KAGURA_K14_CSE_BREAK_IOS_IPA_LAB.md).
Crane production, K11 và arm64e/PAC không thay đổi.

**K15 — BBCheck: provider đã xác minh nhưng runtime không kiểm tra integrity:**
[KAGURA_K15_ARTIFACT_REVIEW.md](KAGURA_K15_ARTIFACT_REVIEW.md).
ZIP thật 231 files, 2.609/2.609 checks; 22 candidate C nguồn thật
được compile trên mỗi target, tìm đúng provider duy nhất cho
`_kagura_bb_check` và `_kagura_on_tamper_detected`, không còn
Kagura transitive deps trong hai provider được chọn. **Vấn đề:**
`runtime/core/bb_check.c` là weak stub **luôn return 1**, bỏ qua
`block_id/expected` nên **không có code integrity check thực**;
callback tamper weak mặc định gọi `abort()` trên macOS/iOS.
Không native 4096/IPA/iPhone/security PASS, không tự link/execute
hoặc merge vào Crane. Quy trình:
[KAGURA_K15_BBCHECK_RUNTIME_RESEARCH.md](KAGURA_K15_BBCHECK_RUNTIME_RESEARCH.md).

**K16 — đo Mach-O code section offline từ CI thực đã xác minh:**
[KAGURA_K16_ARTIFACT_REVIEW.md](KAGURA_K16_ARTIFACT_REVIEW.md).
ZIP K16 thật **54 thành phần, 276/276 checks PASS**. Ba Mach-O arm64
macOS K13 baseline/CSEBreak và iOS K14 CSEBreak có byte
`__TEXT,__text` thực, offset/size/SHA-256 trùng manifest.
UUID executable iOS trùng IPA K14 và log K14 người dùng chia sẻ;
đó **không phải device execution K16**. Manifest **không ký,
không có trust anchor**, không có runtime verifier và không đo
per-basic-block. Không coi K16 là integrity/security PASS,
không chạy BBCheck stub hoặc thay đổi iPhone/Crane/PAC.
Quy trình: [KAGURA_K16_OFFLINE_MACHO_TEXT.md](KAGURA_K16_OFFLINE_MACHO_TEXT.md).

**K17 — đã kiểm chứng chữ ký Ed25519 TEST trên ZIP CI thực:**
[KAGURA_K17_ARTIFACT_REVIEW.md](KAGURA_K17_ARTIFACT_REVIEW.md).
ZIP gồm **56 tệp, 446/446 kiểm tra file-backed PASS**. Chữ ký detached
Ed25519 64 bytes hợp lệ cho byte gốc manifest K16; public-key SPKI
SHA-256 khớp khóa TEST ngoài ZIP, receipt được tính lại và ba
executable Mach-O/IPA/IR/object K13–K14 đều replay đúng.
**Tuy nhiên private key TEST từng bị công khai trong cuộc trò chuyện,**
không thể coi chữ ký là secure trust anchor độc lập. Người dùng báo
ứng dụng cài và chạy trên thiết bị, chưa có signed device attestation
hoặc runtime verifier K17. Không có chứng cứ sửa BBCheck, tăng
integrity security, arm64e/PAC hoặc thay đổi Crane production.
Hướng dẫn ký/verify:
[KAGURA_K17_ED25519_OFFLINE_REFERENCE.md](KAGURA_K17_ED25519_OFFLINE_REFERENCE.md).

**K18 — người dùng bỏ qua, không đánh dấu CI/device PASS:**
[KAGURA_K18_ROTATED_IOS_REFERENCE_LAB.md](KAGURA_K18_ROTATED_IOS_REFERENCE_LAB.md).
Workflow macOS thủ công dùng cặp Ed25519 mới **khác khóa TEST K17
đã công khai**, rebuild K13/K14 và K16 raw manifest, tạo chữ ký
K17 v1 bằng signer mới, đóng app Swift CryptoKit riêng và IPA unsigned.
Trong app, người dùng bấm Verify để đối chiếu chữ ký, SHA, UUID và
`__TEXT,__text` của **file mẫu K14 được đóng kèm**, không phải code
K18 đang chạy. **SKIPPED_BY_USER_NO_MACOS_OR_DEVICE_VERIFICATION**. Chưa có K18 macOS Swift build hay log device thật;
không có trust root bất biến, code-signing/attestation,
self-integrity/PAC/Crane production. K15 weak stub vẫn bị chặn.

**K19 — nghiên cứu nlist symbol-address intervals trên Mach-O sau linker (staged):**
[KAGURA_K19_SYMBOL_BOUNDED_OFFLINE.md](KAGURA_K19_SYMBOL_BOUNDED_OFFLINE.md).
Workflow thủ công từ K13 native/K14 IPA/K16 section SHA, **không phụ
thuộc K18 hay các khóa K18**. Parse thật `LC_SYMTAB`/nlist arm64,
đo byte từ địa chỉ symbol `_dd_k8_evaluate`/`_dd_k14_ios_parity`
đến địa chỉ symbol cao hơn gần nhất hoặc cuối `__TEXT,__text`.
**Không phải function-size chính xác**, không hash từng basic block,
không có runtime verifier, on-device hay security/PAC/Crane PASS.

Nhánh này **không hợp nhất Hikari, Obfuscator, Kagura thành một plugin**,
và `VM` Kagura chưa bật. Chỉ sau CI và runtime evidence mới xét bản
custom merged/derived. Chưa được gọi là MAX production.

## OLLVM STRONG hiện có

`policy.json` và `scripts/demo_ollvm/policy.json` hiện chỉ có
`enable_split`, `enable_bcf`, `enable_fla`, `enable_sub` với các
tham số lặp/xác suất; không có `enable_ce` hoặc các SLLVM flags.

Profile demo STRONG: **SPLIT4 + BCF100% × 2 + FLA + SUB × 3** chỉ áp
dụng cho `CRCreditsOpenTwitter` và `CRCreditsLocalizedRows` của
`CRCredits.m`. Trong build DuoDash Reconstruction, các hàm helper
allowlist nhận cùng tập bốn pass; `scripts/verify_ollvm_log.py`
kiểm tra log `>>>> run <pass> on <function>` chính xác.

Nguồn plugin: `lich4/ollvm-pass`,
commit `592f215f852e3957da01b2b15024dc63713a462e`;
compiler: **LLVM 19**. Xác minh qua
`.github/workflows/build.yml` và
`.github/workflows/demo-ollvm-evaluation.yml`.

**Giới hạn**: phiên bản hiện tại chỉ đưa Obfuscator lên **Mach-O arm64**.
Apple-Clang riêng được dùng cho `arm64e` để giữ versioned user-space PAC
ABI; không gọi bản arm64e là OLLVM protected, không đổi subtype.
`iphoneos-arm64e` là kiến trúc gói roothide, không tương đương CPU
Mach-O `arm64e`.

## Các pass mới cần triển khai thật

Đây là lộ trình ưu tiên **chứ không phải danh sách đã có trong
Obfuscator**:

| Ưu tiên | Pass mục tiêu | Bài kiểm tra bắt buộc |
|---|---|---|
| P1 | **String CE** | Native LLVM19 plaintext-marker baseline/after, NSString/ARC lifetime, 8.192 vector, iPhone arm64 |
| P2 | **Constant Encoding** | Chứng minh object/IR sau `-O1` biến đổi; native parity và kiểm soát optimizer folding |
| P3 | **Indirect Branch** | C-only function, branch target type, parity, không đụng hook/ObjC selector |
| P4 | **Indirect Call** | Typed function pointers, bảo toàn ABI/PAC, kiểm tra điều hướng |
| P5 | **Global Indirection** | Native parity, thread-safety và lifetime |
| P6 | **IR Virtualization** | Compiler chuyển LLVM IR thật sang VM model, không chỉ interpreter được viết thủ công; overhead và rollback |

Các pass như **FW / ECF** có thể xếp sau các thử nghiệm trên.
**FCC / SVC / SEC / anti-debug** không tự bật cho Objective-C
constructor, SpringBoard, Substrate callback, securityd hoặc CarPlay;
cần điều kiện ABI và vận hành riêng. Đặc biệt không nhận tính tương
đương với pass proprietary SLLVM chỉ vì cùng tên.

## Quy trình đưa một pass mới thành tính năng thật

1. **LLVM IR pass source thực**: có `.cpp`/plugin biên dịch bằng LLVM
   19, policy và callback pass pipeline hoạt động. Không dùng
   `source_canary_not_llvm_pass` làm bằng chứng triển khai.
2. **CI isolated manual-only**: build plugin từ source đã pin/kiểm giấy
   phép, compile **cùng Clang19/cùng flags** baseline và candidate; log
   đúng pass/hàm, kiểm tra IR/object native thật sự biến đổi. Thiếu
   invocation hoặc không khác biệt phải FAIL.
3. **Parity & overhead**: host native vectors trước, iOS arm64 build
   + ký/cài trên thiết bị thử qua quy trình hiện có, test chức năng và
   soak; chỉ kết luận runtime theo log thiết bị. Không ghi UDID.
4. **Đánh giá bằng IDA/Ghidra**: quan sát sự thay đổi trên disassembly
   thực, không dùng tăng size/instruction count làm điểm bảo mật.
5. **Rollback riêng**: giữ Obfuscator STRONG hiện hành làm baseline;
   không tự động trộn Hikari + Obfuscator cùng một compilation và
   không thay đổi Makefile/workflow production khi chưa có điều kiện
   tương thích được xác minh.

**Ưu tiên thực tế kế tiếp:** thử **String CE hoặc Constant Encoding như
LLVM pass trên một fixture C/Objective-C riêng**, dùng Hikari nếu phù
hợp giấy phép và provenance; sau đó mới cân nhắc viết/đưa pass vào
custom `Obfuscator`. Bản thân workflow Hikari hiện có mới là plugin
**riêng**. Không tuyên bố nó đã gộp vào OLLVM.

## Kiểm tra fail-closed

```sh
python scripts/custom_ollvm/audit_passes.py
python scripts/test_custom_ollvm_pass_matrix.py
```

Bộ audit đọc đúng chính sách sản phẩm/demo, hai bộ log-checker OLLVM,
pin SHA/upstream, đường compiler arm64/arm64e và Hikari policy.
Nó FAIL nếu thêm flag `enable_ce` chưa được plugin hỗ trợ, gắn nhãn
Hikari là production Obfuscator hoặc nhận source-level canary làm pass
LLVM thật. Audit là **bằng chứng cấu hình**, không tự nhận đã chạy LLVM
native. Được nối vào hai workflow nghiên cứu manual-only:
`demo-ollvm-evaluation.yml` và `hikari-evaluation.yml`.

Crane OLLVM STRONG production vẫn giữ nguyên.
