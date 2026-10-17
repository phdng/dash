# DuoDash / Crane: kế hoạch Protection Engine cho arm64, arm64e và VM

Ngày cập nhật: 2026-10-17. Trạng thái: **Sprint P0/P1 prototype đã có mã và CI thủ công, native iOS chưa xác minh; SLLVM và VMProtect thương mại chưa tích hợp**.

## Kiểm kê các LLVM pass mới và pass thật trong custom OLLVM

Đã bổ sung [CUSTOM_OLLVM_PASS_STATUS.md](CUSTOM_OLLVM_PASS_STATUS.md)
và machine registry `scripts/custom_ollvm/pass_registry.json` để tránh
nhầm CE/ICALL/IGV/IBR/VM source-level canary đã PASS trên iPhone
với **LLVM IR pass** đã tích hợp vào compiler. Hiện `Obfuscator` production
và demo STRONG vẫn chỉ chạy **SPLIT, BCF, FLA, SUB trên arm64**.
Hikari `strcry`/`constenc` là LLVM passes **thuộc plugin riêng**;
chưa được gộp vào custom Obfuscator. Các hướng string CE,
constant encoding, indirect branch/call, global indirection và
virtualization vẫn là **pass candidates chưa triển khai trong OLLVM**.

Hai workflow nghiên cứu manual-only có thêm
`scripts/test_custom_ollvm_pass_matrix.py` để chặn flag/pass ảo, nhầm
LLVM source-level canary và nhầm arm64e PAC ABI. **Crane OLLVM STRONG
production không thay đổi.**

## Kagura / SLLVM-inspired custom MAX compiler pipeline (2026-10-17)

Mục tiêu dài hạn: phối hợp các pass LLVM có mã thực từ **Kagura MIT**
với những ý tưởng chọn lọc trong SLLVM, không sao chép binary SLLVM
proprietary. Đã có `MAX_CANDIDATE` tách biệt để chạy **LLVM19 opt**
với `kagura-str,fla,bcf,sub,co`, native host parity 8.192 vector,
IR/object plaintext audit, iOS arm64 build-only và arm64e Apple Clang
ABI audit. K0 đã được xác minh từ artifact macOS người dùng gửi (8.192 native vector
trùng, IR/object thay đổi, public plaintext canary biến mất). K1
đã bổ sung 7 giai đoạn pass tăng dần, hai ứng viên mới BBR/BBS và phân
loại delta cho từng giai đoạn; **K1 đã có artifact macOS thực, bảy pass đều tạo IR/object delta,
8.192 vector native parity/pass**, nhưng chưa có runtime iOS; xem
[KAGURA_K1_ARTIFACT_REVIEW.md](KAGURA_K1_ARTIFACT_REVIEW.md).
K2a bổ sung kiểm tra **scope theo TU**, sentinel object không qua
Kagura, benchmark native median/p95 theo stage và checksum; đây **chưa phải
function allowlist đầy đủ**, không thể bảo vệ tùy ý các method ObjC/hook.
Xem [KAGURA_K2_SCOPE_BENCH.md](KAGURA_K2_SCOPE_BENCH.md).
K3 mới có workflow và regression portable cho **16 vòng chạy cân bằng
thứ tự, 176 mẫu/biến thể**, để đánh giá lại BBR/BBS sau outlier K2a;
**chưa chạy macOS native K3 hoặc iOS Kagura runtime**. Chi tiết
[KAGURA_K3_INTERLEAVED_BENCH.md](KAGURA_K3_INTERLEAVED_BENCH.md).
Đã nối **IPA KaguraLab arm64 thử trực tiếp** vào workflow Kagura
manual-only: hai hàm baseline/protected từ cùng source, 7 LLVM IR pass,
8192 vector parity trong UIKit, benchmark tùy chọn và log kiểm tra
hợp lệ; CI tạo `KaguraLab-TrollStore-arm64.ipa` với pass-trace audit,
LC_UUID và SHA-256. **Chưa chạy macOS CI bản IPA hoặc Kagura runtime
trên iPhone**. Đọc [KAGURA_IOS_TROLLSTORE_PILOT.md](KAGURA_IOS_TROLLSTORE_PILOT.md).
Đây không phải pass đã nhập vào OLLVM STRONG production.

VM Kagura có mã chuyển LLVM IR thành bytecode thực nhưng chỉ dự kiến
thử sau vì overhead cao, không bật trên ObjC callback/hook/daemon.
Các kiểu indirect branch/call/global của Kagura có semantics khác
SLLVM, cần xác thực riêng trước khi phối hợp. Đọc
[KAGURA_SLLVM_CUSTOM_MAX.md](KAGURA_SLLVM_CUSTOM_MAX.md).

## Sprint P0/P1 đã được hiện thực hóa trong workspace

- Có lab riêng ở [`scripts/protection_lab/README.md`](../scripts/protection_lab/README.md):
  native C reference + function pointer, bytecode builder và static VM interpreter,
  10.004 Python vectors cùng test negative, macOS host 8.192 native/VM vectors.
- `.github/workflows/protection-lab.yml` chỉ chạy thủ công, dùng Apple Clang
  link **2 Mach-O dylib slice** arm64/arm64e, kiểm tra `arm64e` subtype 2
  **kèm versioned PAC ABI bit**, lipo extract + SHA và upload report JSON.
  Đây là source/CI setup; chỉ gọi Apple iOS link PASS khi Actions thực sự xanh.
- OLLVM STRONG hiện có thêm `CRCredits-machine-report.json`: công bố rõ
  arm64 LLVM19/OLLVM STRONG, arm64e Apple Clang bypass, report object-level
  ratio và hash, không gắn nhãn bảo vệ arm64e.
- Người dùng xác nhận workflow Protection Lab trước đã build xanh; đây là
  kết quả CI do người dùng báo, chưa phải thử PAC runtime trên A12+.
- **Sprint P2 thử nghiệm đã viết:** workflow riêng
  `.github/workflows/protection-sllvm-pilot.yml` với phép biến đổi
  **CE/ICALL-inspired ở mức source C**, build Apple Clang plain/protected
  cho arm64 và arm64e; strict Mach-O subtype/PAC ABI audit, kiểm tra chuỗi
  canary biến mất và dữ liệu mã hóa xuất hiện, native host parity 8.192 vector
  và 10.003 portable fixture vectors. Xem
  [`scripts/protection_lab/README.md`](../scripts/protection_lab/README.md).
  Người dùng xác nhận workflow CE/ICALL trước đó **build xanh**;
  kết quả này là biên dịch/audit CI, không phải thử A12+ PAC runtime.
- **Sprint IGV/IBR source-level canary (mới triển khai):** workflow thủ công
  `.github/workflows/protection-igv-ibr-pilot.yml` sinh Mach-O Apple Clang
  baseline/protected trên arm64 và arm64e. Protected dùng hai bước đọc
  global pointer/volatile (IGV-inspired) và bảng handler có kiểu (IBR-inspired,
  thực tế là gọi gián tiếp an toàn ABI, không phải pass IBR của SLLVM).
  Chạy host 8.192 vector và benchmark 100.000 lời gọi mỗi hàm, có 10.004
  Python reference vectors và negative audit, tạo 4 ASM, 2 diff, JSON theo
  slice/benchmark cho IDA. Người dùng đã xác nhận workflow IGV/IBR **build
  xanh**, nhưng chưa cung cấp kết quả IDA theo hàm hay runtime A12+.
- **Sprint Objective-C NSString CE mới:** workflow riêng
  `.github/workflows/protection-objc-ce-pilot.yml` thử ba literal công khai
  (ASCII, tiếng Việt/emoji, Credits), byte XOR được sinh xác định, decode
  và tạo NSString bằng Apple Clang/ARC. Có 10.008 vector Python mô hình,
  macOS host Foundation 8.192 lượt đối chiếu được cấu hình, bốn Mach-O
  arm64/arm64e plain/protected, kiểm tra marker/encoded bytes và ABI trước
  khi xuất artifact IDA. Người dùng báo workflow ObjC CE đã **build xanh**,
  nhưng chưa xác nhận chạy trên iPhone; Crane OLLVM STRONG giữ nguyên.
- **Sprint iOS Device Runtime Canary mới:** workflow thủ công
  `.github/workflows/protection-device-runtime.yml` tạo executable riêng
  cho `arm64` và `arm64e` từ bốn nhóm thử VM, CE/ICALL, IGV/IBR và NSString CE.
  Chạy 4 x 8.192 vector trên macOS host, xác minh log chính xác rồi biên
  dịch hai iOS `MH_EXECUTE` với audit subtype/PAC ABI, SHA và dependencies.
  Workflow tuyệt đối không ký/cài/chạy vào iPhone, không tạo `.deb`; người
  dùng cần ký và chạy riêng trên máy dự phòng A12+ để có runtime evidence.
  `device_audit.py verify-log` kiểm tra 7 dòng log nhưng không thể chứng
  thực nguồn log. Người dùng xác nhận workflow device-runtime CLI đã **build
  xanh**, chưa có kết quả runtime thực trên máy A12+.
  Hướng dẫn [PROTECTION_DEVICE_RUNTIME.md](PROTECTION_DEVICE_RUNTIME.md).
- **Sprint UIKit on-device app (mới):** workflow
  `.github/workflows/protection-ios-app.yml` tạo hai bundle `.app` UIKit
  chưa được provisioning cho Apple Clang iPhoneOS arm64 và arm64e, dùng
  cùng các C/ObjC canary đã thử và nút Run tự kiểm tra ABI/PAC đang được
  loader nạp, so sánh 4 x 8.192 vector. Kết quả có thể chia sẻ dưới dạng
  7 dòng để chạy `device_audit.py verify-log`. CI kiểm tra Mach-O và
  đóng gói riêng, **không ký/cài/chạy iPhone**. Người dùng xác nhận
  workflow UIKit trước đã **build xanh**, chưa có log on-device A12+.
  Hướng dẫn [PROTECTION_IOS_APP.md](PROTECTION_IOS_APP.md).
- **Sprint benchmark on-device tùy chọn:** thêm `perf_pilot.c/.h` đo
  5 cặp VM/CE/ICALL/IGV/IBR (20.000 calls x 5 repeats, median monotonic
  elapsed ns) sau khi chức năng PASS, log 17 dòng riêng với parser
  `perf_audit.py`, host CI kiểm thử giao thức, không có security/perf
  gate trên iPhone. Xem
  [PROTECTION_PERFORMANCE.md](PROTECTION_PERFORMANCE.md).
- **Sprint CI/device evidence correlation:** đã tạo `device_evidence.py`
  với LC_UUID Mach-O load commands per slice `arm64`/`arm64e`, thêm
  artifact `build-identity.json`. UIKit xuất riêng 7 dòng
  `DD_EVIDENCE_*` ghi loaded main binary LC_UUID, architecture, máy
  và iOS version (không UDID). Parser buộc identity UUID khớp với
  artifact, 7 dòng PASS chức năng và tùy chọn 17 dòng perf; không
  có attestation mật mã, chưa xác minh provenance hay PAC trên máy thật.
  Người dùng xác nhận workflow so LC_UUID đã build xanh. Hướng dẫn
  [PROTECTION_DEVICE_EVIDENCE.md](PROTECTION_DEVICE_EVIDENCE.md).
- **Sprint local Xcode signing/runtime (mới):** project
  `scripts/protection_lab/ios_xcode/ProtectionLab.xcodeproj` với shared
  scheme `ProtectionLab`, đúng 12 source C/ObjC, build phase sinh 3 header,
  iPhoneOS target arm64, tự chọn Apple Development team ở Xcode. Workflow
  UIKit chạy `xcodebuild` **không ký** trên macOS và kiểm tra MH_EXECUTE
  của project bên cạnh cặp binary arm64/arm64e nghiên cứu hiện có.
  Bổ sung `device_evidence.py verify-local` để khớp UUID của **binary Xcode
  local**, không nhầm với CI unsigned. Chưa xác nhận chạy trên iPhone hay
  `arm64e` PAC runtime. Xem
  [PROTECTION_XCODE_DEVICE_TEST.md](PROTECTION_XCODE_DEVICE_TEST.md).
- **Điều chỉnh theo thiết bị người dùng (2026-10-17):** đã có TrollStore,
  chưa có iPhone A12+. Workflow UIKit xuất thêm
  `ProtectionLab-TrollStore-arm64.ipa` đúng `Payload/ProtectionLab.app`
  cho thử nghiệm arm64 thủ công; không yêu cầu Apple certificate trong CI.
  Arm64e chỉ cần Apple Clang compile/link + strict subtype/PAC ABI và
  LC_UUID/SHA audit PASS, **không chờ device runtime**. Report
  `build-gates.json` ghi arm64e build PASS và
  `a12_plus_device_runtime=DEFERRED_NO_DEVICE`. Khi có thiết bị mới quay
  lại kiểm tra arm64e runtime. Xem
  [PROTECTION_TROLLSTORE_ARM64.md](PROTECTION_TROLLSTORE_ARM64.md).
- **Post-install QA trên TrollStore (2026-10-17):** người dùng xác nhận
  app đã cài và mở hoạt động ổn trên thiết bị arm64, **chưa cung cấp log
  chứng minh bốn suite x 8.192 PASS**. Đã sửa điều kiện export identity
  sử dụng `DD_RUNTIME_COMPLETE=PASS` với newline sai thành helper chung
  `DDValidationPassed`, thêm progress label thực tế VM→CE/ICALL→IGV/IBR
  →ObjC/ARC và trạng thái NOT TESTED/RUNNING/PASS/FAILED. New
  `scripts/test_ios_postinstall_ui.py` chặn regression newline escape đôi,
  bảo vệ log 7/7/17 dòng; workflow UIKit chạy test này khi build.
  Người dùng tiếp tục xác nhận **4 nhóm test arm64 trên thiết bị đã PASS**,
  nhận diện UDID đúng theo quan sát của họ. Đã ghi nhận dưới dạng
  `USER_REPORTED_PASS`, không thu/lưu UDID hay giả lập log; khi có 7 dòng
  chức năng và identity có thể xác minh nhất quán qua
  `device_acceptance.py`. Xem
  [PROTECTION_ARM64_DEVICE_ACCEPTANCE.md](PROTECTION_ARM64_DEVICE_ACCEPTANCE.md).
  Arm64e vẫn chỉ Apple Clang build+ABI/UUID, A12+ runtime hoãn.
- **Soát artifact CI đính kèm + sprint soak trên arm64 (2026-10-17):**
  đã kiểm tra thực tế IPA/binary trong ZIP do người dùng gửi: arm64
  `MH_EXECUTE` subtype 0, arm64e `MH_EXECUTE` subtype `0x80000002`,
  SHA-256 và LC_UUID của binary đối chiếu thành công với báo cáo CI.
  [Chi tiết artifact](PROTECTION_CI_ARTIFACT_REVIEW.md). UI lab đã có
  nút soak tự chọn (chỉ sau functional PASS): 5 vòng × 4 suite × 8.192
  vector, fail-fast, báo cáo 12 dòng độc lập và parser
  `soak_audit.py` với hồi quy âm tính. **Soak mới chưa chạy trên iPhone**;
  arm64e tiếp tục build/audit-only. Xem
  [PROTECTION_ARM64_SOAK.md](PROTECTION_ARM64_SOAK.md).
- **Nghiệm thu bản soak trên thiết bị và artifact CI `(4)` (17/10/2026):**
  người dùng xác nhận tất cả test trên iPhone arm64 đã PASS. Đã đối chiếu
  byte thật IPA arm64 và MH_EXECUTE arm64e, hash và LC_UUID với ba báo
  cáo CI; hai binary có mã soak. `device_acceptance.py` có thêm mức
  `soak.status=USER_REPORTED_PASS` khi được xác nhận, hoặc xác minh
  định dạng log thật bằng `--soak` nếu có. **Không có log soak trong ZIP,
  không có chứng thực cryptographic, không lưu UDID**. Xem
  [PROTECTION_CI_ARTIFACT_REVIEW.md](PROTECTION_CI_ARTIFACT_REVIEW.md).
  Arm64e vẫn chỉ build/audit; PAC runtime chờ A12+.
- **Chưa** có plugin SLLVM, backend VMProtect thương mại, codesign/thiết bị
  A12+ runtime; không biến canary thành tweak được phát hành.


## Mốc đã xác nhận

- Người dùng báo: workflow OLLVM STRONG build PASS, app vẫn chạy đúng chức năng trên thiết bị thử roothide iPhone 6s (iOS 15.8.8), và kiểm tra bằng IDA thấy biến đổi mã rõ rệt.
- Hiện tại `scripts/demo_ollvm/policy.json` chỉ bật SPLIT4/BCF100%x2/FLA/SUB3 trên `CRCreditsOpenTwitter` và `CRCreditsLocalizedRows` của `CRCredits.m`, **arm64 slice**.
- `scripts/demo_ollvm/compiler_select.py` cố ý bypass LLVM19 trên **arm64e slice** để tránh object `arm64e.old` không tương thích Apple linker; bản STRONG chạy trên iPhone 6s chứng minh arm64 runtime, **không phải arm64e/PAC runtime**.
- Roothide `iphoneos-arm64e` là kiến trúc **package dpkg/bootstrap**. Không thể coi nó tương đương Mach-O slice arm64e.
- Kết quả IDA là quan sát trực quan, chưa chứng minh mọi hàm đã được bảo vệ, chống deobfuscation hoặc mức độ bảo mật đo lường được.

## Nguồn công nghệ đã khảo sát

1. **SLLVM:** https://github.com/lich4/sllvm — README nêu CE (bao gồm ObjC strings; tuyên bố hỗ trợ arm64/arm64e), FLA cải tiến, BCF, ECF, FW, FCC, IBR, ICALL, IGV, SVC, SPLIT, INLINE, SEC. Công khai chủ yếu tài liệu/screenshots chứ chưa có một backend/plugin build sẵn có thể kiểm chứng độc lập trong workspace. Tính sẵn có, license, binary, LLVM version và tương thích Apple ABI **chưa kiểm chứng**. Đặc biệt FCC trên ARM64 được tác giả mô tả chỉ triển khai một phần.
2. **OLLVM standalone plugin hiện tại:** https://github.com/lich4/ollvm-pass — hỗ trợ IR-pass LLVM19 hiện hành; tác giả nói plugin cố giữ OLLVM gốc, không phải cải thiện đáng kể độ mạnh.
3. **VMProtect thương mại:** https://www.vmpsoft.com/vmprotect/overview — bản mô tả mới nhắc ARM64 cho Windows/Linux/macOS/Android, **không nêu iOS/arm64e**. Forum support 2025 từng trả lời không hỗ trợ ARM64; thông tin thay đổi theo phiên bản. Cần chứng cứ chính thức cho iOS arm64e Mach-O dylib + PAC + packaging roothide trước khi lập kế hoạch tích hợp thực.
4. **Kagura:** https://github.com/qusamulab/kagura — dự án MIT có mã nguồn LLVM pass, iOS trong danh sách nền tảng, README mô tả VM virtualization; **chưa thử build hoặc xác nhận arm64e ABI/PAC**. Là ứng viên nghiên cứu riêng, không kết luận tương thích.
5. **Apple arm64e/PAC:** https://clang.llvm.org/docs/PointerAuthentication.html và https://developer.apple.com/documentation/security/preparing-your-app-to-work-with-pointer-authentication — ABI/PAC khác arm64 thường; phải test trên A12+ thật, không giả lập trên iPhone 6s.

## Thứ tự triển khai ưu tiên

### P0 — Khóa baseline và thiết kế phép đo

- Gắn nhãn/gắn hash cho artifact STRONG roothide + rootless đã xanh và lưu bản roothide chạy ổn định để rollback; giữ CI hiện tại chạy thủ công.
- Tách `report.json` theo **target CPU slice** và từng hàm: compiler, pass set, source checksum, Mach-O subtype, số instruction/basic-block/branch, byte code section, binary hash, thời gian build, mức tăng code, smoke runtime; không lấy mức tăng instruction làm thước đo độ bảo mật.
- Thêm negative gate: không cho pass nào đánh vào selector ObjC/constructor/hook/daemon/critical storage ngoài allowlist; không đổi subtype; không cho artifact VMP/arm64e công bố khi runtime chưa test.
- Khi kết quả IDA có thật, chỉ ghi «quan sát bị làm rối» theo báo cáo người dùng; không thay bằng con số fixture.

**Điều kiện PASS:** CI build baseline và STRONG với 2 scheme, object và Mach-O audit, report theo CPU slice; có mốc rollback, có log khác biệt chức năng.

### P1 — Hỗ trợ thực sự cả arm64 và arm64e

- Đừng sửa `arm64e.old` thành `arm64e` bằng patch Mach-O headers, `lipo` hay ép linker. Giữ Apple Clang native arm64e cho production cho đến khi toolchain thay thế tương thích.
- Thử một dự án **canary thuần C riêng biệt**: build `-arch arm64` và `-arch arm64e` bằng đúng compiler/linker của Xcode, trích `lipo -thin` và kiểm tra `otool -hv`, ký/chạy đúng bootstrap.
- Thử khả năng plugin với **Apple Clang** và đường build IR nếu tương thích; không giả định plugin LLVM19 load được trong Apple Clang khác ABI/version. Nếu không, ưu tiên phép biến đổi source C giữ nguyên Apple toolchain, hoặc backend LLVM được port/kiểm chứng riêng cho Apple arm64e.
- Quan sát mã arm64e/PAC bằng `otool`/IDA; trên thiết bị **A12+ thực** chạy canary với function pointers, ObjC callbacks, blocks, exceptions, dynamic symbol lookup và reload. iPhone 6s/A9 chỉ xác nhận arm64.
- Chỉ khi link + ký + cài + chạy đúng ở A12+ mới bật protected arm64e. Nếu fail, artefact vẫn giữ **arm64e Apple Clang bypass** (không quảng cáo dual-slice obfuscation).

**Điều kiện PASS:** canary 2 slice với subtype chính xác, không ABI/PAC crash; quan sát pass thực thi trong arm64e bằng cùng-compiler reference, không chỉ có slice tồn tại.

### P2 — Học kỹ thuật SLLVM theo tầng trên từng hàm

Ưu tiên theo mức rủi ro và khả năng kiểm thử:

- **Bậc A:** mã hóa string/constant `CE` trên *literal thử nghiệm*; phép đo strings plaintext có/không ở artifact, so sánh runtime. ObjC constant string phải test xử lý bridge/ARC/lifetime.
- **Bậc B:** thử `IBR`, `ICALL`, `IGV` rồi `ECF`/FLA cải tiến trên hai hàm thuần C nhỏ. Dùng feature flags riêng; mỗi run chỉ thêm một kỹ thuật mới để tách nguyên nhân crash.
- **Bậc C:** thử `FW`/điều chỉnh control flow tối ưu có kiểm tra performance. Không tự áp dụng `FCC`, `SVC` hay anti-debug `SEC` lên code ObjC callback/hook/daemon: có thể phá ABI, PAC, security model và khả năng debug.
- Không trộn nhiều lần BCF/FLA vô hạn. Chọn profile `balanced`, `strong`, `vm-experimental`; mỗi profile allowlist hàm/kiến trúc, thông số seed lặp lại được, trần build-time/latency/binary size.
- Nếu SLLVM proprietary plugin không sẵn/licensing chưa rõ, có thể nghiên cứu/tự viết pass cùng **ý tưởng kỹ thuật** trên mã thử nghiệm riêng, không giả mạo là đã tích hợp sản phẩm SLLVM.

**Điều kiện PASS:** đo được string/constant/CFG diff; 100% test vector đúng, không lỗi reentrancy/memory, thời gian và binary budget chấp nhận được.

### P3 — VMP đúng nghĩa, trước hết như một canary thuần C

- **VMP khác OLLVM:** biên dịch một vùng logic thuần C thành **bytecode**, gói bytecode cùng một **interpreter native**. Không gọi một loạt nhánh giả là virtualization.
- Tách ba thành phần: **bytecode builder ở máy build** (IR/AST hợp lệ, ban đầu manual bytecode), **static bytecode blob** trong Mach-O, và **native interpreter runtime** với các giới hạn stack, heap, instruction budget rõ ràng. Không cần JIT / RWX / sửa code ký tại runtime.
- Interface mẫu `uint64_t protected_eval(uint64_t a, uint64_t b)` độc lập UIKit, ObjC selector, pthread/hook/XPC. Native bridge được Apple Clang biên dịch cho arm64 và arm64e; không truyền function pointers có PAC qua ranh giới VM bằng phép cast chưa kiểm chứng.
- Canary đầu tiên: toán học/kiểm tra token mẫu *không chứa bí mật thực*, trăm/nghìn test vector (boundary, overflow, random seed cố định); đối chiếu baseline 1:1. Kết quả IDA cần thấy dispatch/handlers + bytecode thay cho logic gốc.
- Test iPhone 6s arm64, tiếp theo iPhone A12+ arm64e. Chỉ sau đó cân nhắc tích hợp một helper CranePrefs **không nhạy cảm hệ thống**; không virtualize constructor, SpringBoard injection, hook ABI, shared caches, storage/securityd, XPC, license ownership hay code gọi private runtime liên tục.
- VMProtect thương mại chỉ là backend tùy chọn nếu có **bằng chứng vendor** hỗ trợ đúng Mach-O iOS arm64/arm64e và entitlement/code-sign/pointer-authentication; Kagura hoặc custom LLVM IR virtualizer cũng cần cùng bằng chứng. Không phụ thuộc vào download bất minh/công cụ closed-source chưa xác minh.

**Điều kiện PASS:** native vs VM cùng kết quả, không crash, không JIT, code ký chính xác, runtime và CPU overhead đo được trên hai thiết bị, file có thể quan sát IDA.

### P4 — CI matrix và rollout theo allowlist

| Trục | Baseline | OLLVM STRONG | SLLVM-inspired pilot | VMP pilot |
| --- | --- | --- | --- | --- |
| rootless arm64 | Bắt buộc | Đã có | Thử độc lập | Thử độc lập |
| roothide arm64 | Bắt buộc | Người dùng báo PASS trên iPhone 6s | Thử độc lập | Thử độc lập |
| arm64e Mach-O | Apple Clang | Hiện **bypass** | Chỉ mở khi PAC gate PASS | Chỉ mở khi A12+ PAC gate PASS |
| Device functional test | Đối chứng | Người dùng báo ổn | A/B trên máy phụ | A/B trên máy phụ |
| IDA diff | No pass | Đã có quan sát | Trích riêng từng pass | Thấy bytecode/VM dispatcher |

Theo nguyên tắc **fail closed**: backend báo không hỗ trợ arm64e phải thể hiện rõ trong report, không tự fallback mà lại gắn nhãn «protected arm64e»; nếu chạy fail thì giữ bản đã xanh, không nới gate để build pass giả.

## Sprint tiếp theo đề xuất

**Chọn P0 + P1 là sprint đầu:** khóa artifact đang chạy tốt, bổ sung báo cáo theo slice/func; thêm canary build arm64e bằng Apple toolchain, phát hiện PAC/subtype/linked binary đúng và kiểm chứng trên A12+. Song song nghiên cứu kỹ thuật CE/IBR ở mã thử nghiệm. P3 VMP chỉ bắt đầu sau khi ABI gate rõ ràng, tránh xây xong VM mà không dùng được trên arm64e.

## Điều cần tránh

- Không đánh đồng `iphoneos-arm64e` của **dpkg roothide** với hỗ trợ CPU `arm64e` của Mach-O.
- Không sửa giả subtype `arm64e.old`; không dùng iPhone 6s để tuyên bố test PAC trên A12+.
- Không đẩy plugin không rõ xuất xứ, key/license proprietary hay mã nguồn private lên CI artifacts.
- Không dùng tăng instruction/hash khác nhau như bằng chứng chống reverse engineering tuyệt đối; không mã hóa string nhạy cảm rồi xem đó là bảo mật key.
- Không bật hook, daemon hoặc container-switch logic vào policy chỉ vì Credits đã ổn.
