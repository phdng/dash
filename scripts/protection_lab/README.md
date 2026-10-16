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
