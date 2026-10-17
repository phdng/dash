# Protection Lab — Apple arm64/arm64e và VM bytecode canary

**Trạng thái:** mã canary/test/CI đã triển khai trong nhánh làm việc. Không phải
phần của bản build Crane và không chứng minh ứng dụng trên A12+ đã chạy đúng.

## Thành phần

- `canary.c/.h`: cùng một hàm uint64 tham chiếu cho hai kiến trúc; API
  function-pointer `dd_canary_indirect` dành riêng cho thử đường ABI/PAC.
- `program.py`: generator 52 byte bytecode **xác định**. Mã và hằng chỉ là
  dữ liệu canary, không chứa key, không phục vụ license hay securityd.
- `vm.c`: VM interpreter thuần C có 4 registers, giới hạn 64 instruction,
  kiểm tra biên, không cấp phát hay sinh executable code; không có JIT/RWX.
- `runner.c`: trên host macOS so sánh native, VM và lời gọi qua function
  pointer với **8.192** vector trên cùng một binary.
- `audit.py`: kiểm tra filetype `MH_DYLIB`, CPU type arm64, subtype
  `arm64=0`, `arm64e=2`, và yêu cầu bit
  `CPU_SUBTYPE_ARM64E_VERSIONED_PTRAUTH_ABI_MASK=0x80000000`, không
  cho kernel ABI. Không patch headers/ép ABI.
- `scripts/test_protection_lab.py`: 10.004 Python reference vectors,
  malformed bytecode, subtype legacy (không versioned), bad filetype và
  static CI isolation tests; chạy được trên Windows không cần Xcode.
- `.github/workflows/protection-lab.yml`: workflow **chạy thủ công**, độc
  lập workflow Crane đã xanh, macOS-14 Apple Clang compile native host
  vector runner + hai iOS Mach-O dynamic libraries, `lipo -create`,
  `lipo -thin`, kiểm tra đúng ABI và binary hash. Chỉ upload artifact
  nghiên cứu; **không** package .deb/codesign/inject vào thiết bị.

## Chạy

**Cục bộ (Windows/macOS/Linux):**

```sh
python scripts/test_protection_lab.py
python scripts/test_demo_ollvm.py
```

**GitHub macOS:**

Actions → **Protection Lab - Apple arm64e ABI and VM canary (Experimental)**
→ Run workflow. Nếu job xanh, tải artifact
`ProtectionLab-Apple-arm64-arm64e-VM-EXPERIMENTAL`:

- `report.json`: SHA-256, kích thước và ABI của hai binary, rõ
  `device_runtime=NOT_TESTED`, `obfuscation=none` trong bước này.
- `protection-arm64.dylib`, `protection-arm64e.dylib`,
  `protection-universal.dylib`: **canary nghiên cứu, không phải tweak
  đã ký hay artifact cài đặt trên iPhone**.
- `universal-extraction-report.json`, `otool-*.txt`, `lipo-info.txt`,
  `macho-hashes.txt`: kiểm tra đúng 2 slice đã link.
- `host-vectors.txt`: bằng chứng runner host có 8.192 vector PASS.
  Đây **không** phải iOS runtime hay PAC test.


## Sprint CE/ICALL theo ý tưởng SLLVM — thử nghiệm riêng

Workflow thủ công: **Protection Lab - SLLVM-inspired CE and ICALL (Experimental)**
trong `.github/workflows/protection-sllvm-pilot.yml`.

Phạm vi (không tích hợp SLLVM proprietary, không động vào Crane):
- `sllvm_plain.c`: C baseline giữ **chuỗi canary công khai** làm đối chứng.
- `sllvm_generator.py`: tạo `sllvm_encoded.h` (35 byte XOR với
  keystream cố định), **chỉ là obfuscation dễ đảo**, không mã hóa bảo vệ key.
- `sllvm_protected.c`: đọc byte mã hóa bằng `const volatile` rồi
  giải mã để chạy phép kiểm tra hash; gọi hàm qua **bảng function pointer
  có kiểu**, không ép con trỏ số nguyên, để Apple Clang giữ ABI/PAC.
- `sllvm_runner.c`: **8.192 test vector thực** trên host macOS so sánh
  native/plain với CE+indirect phiên bản mới.
- `sllvm_audit.py`: kiểm tra ABI trên Mach-O plain/protected cho hai
  slice, yêu cầu chuỗi canary hiện diện trong baseline, **không còn nguyên
  chuỗi** trong protected, có byte đã mã hóa trong protected, và kiểm tra
  log runtime host. Xuất `report.json`.
- `scripts/test_sllvm_pilot.py`: test fixture cross-platform
  **10.003 vector** và negative gates (sai PAC ABI, thiếu baseline marker,
  lộ plaintext, host log giả). **Kết quả fixture không phải bằng chứng
  binary sản phẩm thực tế.**

Chạy local: `python scripts/test_sllvm_pilot.py`. Trên Actions chọn
workflow thủ công vừa nêu. Nếu CI xanh, artifact
`ProtectionLab-SLLVM-inspired-arm64-arm64e-EXPERIMENTAL` gồm
`plain-arm64*.dylib`, `protected-arm64*.dylib` cho cả hai slice,
4 tệp `.asm`, `report.json`, header, hashes, log host vectors. Mở
hai cặp binary trong IDA để xem chênh lệch. **Không cài các dylib
canary này trên thiết bị**; chưa kiểm chứng PAC A12+ runtime, chưa gọi
đây là SLLVM chính thức hoặc bảo mật chống dịch ngược.

**Chiến lược tiếp theo:** thử IGV/IBR và CE cho ObjC literal trong
canary tách biệt trước khi cân nhắc một helper CranePrefs không trọng yếu.

## Sprint IGV/IBR theo ý tưởng SLLVM — thử nghiệm riêng

Workflow thủ công:
**Protection Lab - IGV IBR source pilot (Experimental)**,
`.github/workflows/protection-igv-ibr-pilot.yml`.

Đây là **biến đổi mã nguồn C riêng cho canary**, không phải LLVM plugin
SLLVM/IBR thật và không áp dụng lên Crane đang hoạt động:

- `igv_ibr_plain.c`: hai hàm baseline `dd_igv_plain` (switch chọn
  hằng số) và `dd_ibr_plain` (7 vòng state switch trực tiếp).
- `igv_ibr_protected.c`: `dd_igv_protected` dùng **hai bước truy xuất
  global pointer có kiểu** và volatile load; `dd_ibr_protected` thay
  state switch bằng **bảng handler pointer có kiểu**, Apple Clang tự xử lý
  pointer authentication cho arm64e. Không chuyển function pointer sang
  số nguyên, không JIT/RWX, không gọi private framework.
- `igv_ibr_runner.c`: so sánh đầy đủ plain/protected **8.192 vector**
  trên macOS host, bổ sung microbenchmark 100.000 calls cho từng hàm.
  Số microsecond là **đo trên host CI**, rất dễ nhiễu; không áp ngưỡng
  hiệu năng hay kết luận tốc độ trên thiết bị.
- `igv_ibr_audit.py`: fail-closed khi Mach-O sai CPU subtype/PAC ABI,
  binary đối chứng trùng bản bảo vệ, disassembly thiếu symbol hoặc trùng
  nhau, host parity/benchmark log thiếu hoặc sai; xuất JSON/hash và
  `igv-ibr-arm64.diff`, `igv-ibr-arm64e.diff`. Số opcode indirect
  chỉ là heuristic toàn assembly, **không chứng minh indirect branch
  trong đúng từng hàm**, cần kiểm tra với IDA.
- `scripts/test_igv_ibr_pilot.py`: **10.004 vector Python** đối chiếu
  mô hình và negative fixture. Test Python chỉ kiểm tra logic/model/audit,
  không thay thế C native host hoặc iOS arm64e runtime.

Chạy local: `python scripts/test_igv_ibr_pilot.py`. Để có **binary
thật**, cập nhật GitHub rồi chạy workflow thủ công. Artifact
`ProtectionLab-IGV-IBR-arm64-arm64e-EXPERIMENTAL` gồm 4 dylib
plain/protected, 4 asm, 2 diff, JSON report, SHA và host benchmark.
**Không cài lên iPhone**, chưa chạy signed canary trên A12+ hoặc kiểm
chứng PAC runtime. Không tự suy diễn rằng chính thức tích hợp SLLVM.


## Sprint Objective-C literal CE — NSString/ARC dual-ABI canary

Workflow thủ công:
**Protection Lab - Objective-C literal CE (Experimental)**,
`.github/workflows/protection-objc-ce-pilot.yml`.

Đây là canary riêng **Objective-C `.m` sử dụng Foundation và ARC**, không
đưa vào Crane tweak, không sửa `CRCredits.m`, hook hay daemon:

- `objc_ce_plain.m`: 3 literal `NSString` làm đối chứng, bao gồm
  ASCII marker công khai, một chuỗi tiếng Việt/emoji UTF-8 và tên Credits;
  `choice & 3` có cả đường chuỗi rỗng.
- `objc_ce_generator.py`: tạo `objc_ce_data.h` **UTF-8/LF xác định**
  với 3 mảng byte đã XOR; khóa/thuật toán đều hiển thị trong binary, không
  chứa bí mật và **không phải mã hóa bảo mật**.
- `objc_ce_protected.m`: đọc dữ liệu byte `volatile`, giải mã vào
  buffer stack có giới hạn rồi tạo `NSString` bằng
  `initWithBytes:length:encoding:`; Apple Clang/ARC xử lý lifetime,
  không tạo class ObjC giả, không đổi selector hay PAC ABI.
- `objc_ce_runner.m`: 8.192 lượt đối chiếu `NSString` equality,
  Unicode `length`, độ dài UTF-8 và `UTF8String` qua nhiều
  `@autoreleasepool` **trên macOS host**.
- `objc_ce_audit.py`: bắt buộc 4 Mach-O dylib Apple arm64/arm64e
  subtype hợp lệ; baseline phải chứa marker ASCII, protected không được
  chứa 3 literal plaintext và phải chứa đầy đủ 3 byte sequence đã mã hóa;
  host parity và generated header đúng checksum. Báo cáo JSON ghi rõ
  `ios_device_runtime=NOT_TESTED`.
- `scripts/test_objc_ce_pilot.py`: **10.008 vector portable**, Unicode
  round-trip và negative tests: lỗi ABI arm64e.old, plaintext bị lộ,
  thiếu marker, host log giả và header thay đổi.

Khi chạy macOS Actions, artifact
`ProtectionLab-ObjC-CE-arm64-arm64e-EXPERIMENTAL` gồm 4 dylib,
4 assembly, 4 bản danh sách symbol xuất, JSON report, hashes và host log
để so sánh trong IDA. **Build và host Foundation ARC** chỉ xác nhận sau
khi workflow mới chạy; không đánh dấu runtime A12+/iOS PAC PASS.

## Sprint iOS device runtime: kiểm thử thực tế trên thiết bị A12+

Workflow thủ công **Protection Lab - iOS device runtime canary (Experimental)**
trong `.github/workflows/protection-device-runtime.yml` liên kết toàn bộ
**VM / CE-ICALL / IGV-IBR / Objective-C NSString CE** vào một executable
độc lập. Chạy cùng bộ test **4 x 8.192 vector** trên host macOS, sau đó
biên dịch riêng executable iOS **arm64 và arm64e** và kiểm tra đúng
`MH_EXECUTE`, subtype/PAC ABI cùng SHA-256. Không auto-sign/install vào
thiết bị, không chạm đến package/hook/daemon Crane.

- Mã mới: `device_suites.c/.h`, `device_main.m`, `device_audit.py`.
- Kiểm tra hồi quy: `scripts/test_device_runtime_canary.py` bao gồm
  log giả/mất dòng, sai CPU, subtype `arm64e.old`, kernel ABI và metadata
  artifact; test giả lập không chứng minh runtime thực tế.
- Trên thiết bị thật, dùng binary độc lập đã được ký đúng bootstrap và
  lưu nguyên stdout + exit code. Parser `device_audit.py verify-log`
  xác minh **7 dòng** bắt buộc nhưng không xác thực nguồn gốc log.
- Xem chi tiết [docs/PROTECTION_DEVICE_RUNTIME.md](../../docs/PROTECTION_DEVICE_RUNTIME.md).

**Lưu ý:** build xanh ở CI mới chỉ kiểm chứng build và macOS host parity;
đến khi có iPhone A12+ và log thật, `arm64e` runtime vẫn `NOT_TESTED`.

## Sprint UIKit app: chạy canary bằng giao diện trên iPhone thật

Workflow `.github/workflows/protection-ios-app.yml` (chạy thủ công)
tạo **hai bundle iPhoneOS chưa được provisioning** cho `arm64` và `arm64e`.
Nguồn `ios_app_main.m` + `ios_app_Info.plist` sử dụng UIKit, cùng
`device_suites.c` và các canary C/Objective-C đang có. Người thử nghiệm
phải bấm **Run 4 suites × 8192**; app kiểm tra loaded Mach-O ABI/PAC rồi
so sánh 4 x 8.192 vector. Nút Share chỉ cho chia sẻ report **sau khi**
test đã hoàn tất, report chứa đúng 7 dòng khi mọi bước PASS, dùng được với
`device_audit.py verify-log`. Các bundle chưa được provision/sign để
cài máy; không tự động cài hay thay thế Crane.

- Portable regression: `python scripts/test_ios_app_canary.py`
  (UIKit nguồn, Info.plist, workflow, arm64/arm64e và log âm tính).
- Hướng dẫn: [docs/PROTECTION_IOS_APP.md](../../docs/PROTECTION_IOS_APP.md).
- Lưu ý: người dùng đã xác nhận workflow device-runtime CLI trước **build
  xanh**, nhưng chưa có nhật ký thiết bị A12+ đã chạy `arm64e` thật.

**Không được gọi app có bản ký hợp lệ hoặc device runtime PASS chỉ vì
workflow này build xanh.**


## Sprint đo overhead trực tiếp (tùy chọn, chưa chứng thực trên thiết bị)

UIKit app tiếp tục giữ nút **Run 4 suites × 8192** kiểm chứng chức
năng. Khi và chỉ khi xuất được `DD_RUNTIME_COMPLETE=PASS`, nút
**Measure overhead (optional)** mới bật. Benchmark là một công việc
riêng trên background queue, không thay thế 7 dòng `DD_RUNTIME_*`
và không thể biến kết quả fail chức năng thành PASS.

- `perf_pilot.c/.h`: đo **5 cặp** VM/native, CE/plain, ICALL/direct,
  IGV/plain, IBR/plain bằng đồng hồ đơn điệu `CLOCK_MONOTONIC`, mỗi
  biến thể **20.000 lời gọi x 5 lần lặp**, lấy trung vị nanosecond.
  Luân phiên thứ tự đo và giữ checksum qua `volatile` để tránh tối ưu
  loại bỏ kết quả; không benchmark Objective-C allocation/ARC trong bước
  này.
- `perf_report.c/.h`: tạo log **17 dòng** cố định, tách biệt tuyệt đối
  với log chức năng 7 dòng; trường `DD_PERF_NOTE` bắt buộc bằng
  `OBSERVATIONAL_NOT_SECURITY_PROOF`.
- `perf_audit.py`: parse log nghiêm ngặt, chỉ tính tỷ số
  protected/native quan sát được, không có giới hạn tỷ số PASS/FAIL, không
  tuyên bố benchmark host macOS là benchmark iOS.
- `perf_host_runner.c`: CI chạy benchmark trên **macOS host** như một
  kiểm thử compiler + định dạng log. Chỉ log chia sẻ từ iPhone thật mới
  có thể là quan sát hiệu năng thiết bị, và parser không thể chứng
  thực nguồn gốc log.
- `scripts/test_protection_perf.py`: 1.000 bộ thời gian mô phỏng,
  negative tests context/kiến trúc, thứ tự cặp, ngưỡng/NaN/định dạng,
  cùng guard app chỉ bật benchmark sau khi chức năng PASS.

Hướng dẫn chi tiết và lệnh kiểm tra báo cáo:
[docs/PROTECTION_PERFORMANCE.md](../../docs/PROTECTION_PERFORMANCE.md).

**Quan trọng:** kết quả timing phụ thuộc máy, CPU frequency, thermal và
load; chỉ xem là thông tin quyết định overhead, không chứng minh an toàn,
PAC runtime hay mức độ chống reverse engineering.

## Tiêu chí tiếp theo

1. Chạy workflow, kiểm tra ABI arm64e **trên binary thực**. Nếu Apple linker
   từ chối, giữ nguyên pipeline OLLVM STRONG và phân tích linker log; không
   sửa subtype hay tắt guard để ép xanh.
2. Trên **A12+** đã sao lưu, xây *riêng* bản canary ký/chạy phù hợp
   bootstrap và kiểm tra indirect call/PAC + 8.192 vector. Hiện chưa có
   device harness do người dùng chưa cung cấp A12+ và chưa xác định
   codesign/entitlement bootstrap; **không được đánh dấu PASS**.
3. Với dual-ABI canary đã xanh, khảo sát CE/IBR/ICALL/IGV (SLLVM-inspired)
   trên chức năng thuần C trước khi thêm compiler pass hoặc virtualize
   helper non-critical. Plugin SLLVM thương mại/VMProtect thực chưa tích hợp.
4. VMP thử nghiệm ở đây là *static-bytecode VM canary*, không phải
   VMProtect thương mại và không có claim chống phân tích độc lập.
