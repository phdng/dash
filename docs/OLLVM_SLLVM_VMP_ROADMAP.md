# DuoDash / Crane: kế hoạch Protection Engine cho arm64, arm64e và VM

Ngày cập nhật: 2026-10-16. Trạng thái: **Sprint P0/P1 prototype đã có mã và CI thủ công, native iOS chưa xác minh; SLLVM và VMProtect thương mại chưa tích hợp**.

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
  Workflow mới **chưa chạy**, không được gọi arm64e device PASS.
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
