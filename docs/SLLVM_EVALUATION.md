# Đánh giá đưa kỹ thuật SLLVM vào DuoDash (16/10/2026)

## Kết luận và giới hạn nguồn

**Không thay thế trực tiếp OLLVM đang build xanh bằng SLLVM tại thời điểm này.**
Đã đối chiếu Git repositories (không chỉ README):
- [lich4/sllvm](https://github.com/lich4/sllvm), HEAD kiểm tra `bf2f5cd6d7e12092da8bbe249267842eb454b73a`: chỉ có `README.md`, `README_zh.md`, `screenshots/` (không có source pass, CMake hay compiler). README tự mô tả hỗ trợ host/target phần lớn là *planned*. Không có cách build plugin từ repo này.
- [lich4/ollvm-pass](https://github.com/lich4/ollvm-pass), SHA trùng bản CI đang pin `592f215f852e3957da01b2b15024dc63713a462e`: **có** `obfuscator/`, `hikari/`, `arkari/`, `pluto/`. `hikari/CMakeLists.txt`, `hikari/Pass.cpp`, `hikari/test/policy.json` có mã nguồn thực tế cho `enable-strcry`, `enable-constenc`, `enable-fco`, `enable-indibran`, `enable-funcwra`. Nguồn hiện tại dùng LLVM 19 trên macOS cho plugin OLLVM; Hikari plugin **chưa được biên dịch hay chạy cùng OLLVM trong CI DuoDash**.
- Trong hai cây được xem xét chưa thấy tệp `LICENSE` ở thư mục gốc. Không suy diễn quyền sử dụng/phân phối: cần kiểm tra điều khoản và xuất xứ các thành phần trước khi đưa binary/plugin đóng gói vào phát hành.
- **Đính chính:** README SLLVM không liệt kê tính năng đổi tên tất cả C/Objective-C symbols/hàm. Khả năng nhận diện tên *đã bị name-mangle* trong selector policy khác với **symbol renaming**. Hikari có `acd-rename-methodimp`, không tương đương generic function renaming.

## Ma trận khả thi cho DuoDash iOS tweak

| Kỹ thuật | SLLVM mô tả | Có nguồn khả dụng từ plugin Hikari đang cùng repo? | Ưu tiên |
| --- | --- | --- | --- |
| CE / mã hóa chuỗi C và hằng Objective-C | `enable_ce`, kể cả stack mode | Có `enable-strcry` nhưng thuật toán và stack-mode **không tương đương** SLLVM | P1: thử trên fixture và một helper không nhạy cảm |
| Constant encryption | không đồng nhất với CE của SLLVM | Có `enable-constenc` | P1: thử C-only fixture trước |
| Function call hiding / ICALL | `enable_icall` | Hikari có `enable-fco`, sử dụng `dlopen/dlsym`; kỹ thuật và semantics không đồng nhất | P2: tránh hooks, Objective-C runtime |
| Indirect branch | `enable_ibr` | Có `enable-indibran` | P2: chỉ hàm C thuần, kiểm thử hành vi |
| Function wrapper | `enable_fw` | Có `enable-funcwra` | P2: chỉ canary, sau P1 |
| ECF, IGV, custom calling convention (FCC) | Có trong tài liệu SLLVM | Chưa có triển khai SLLVM công khai/đã xác minh tương đương | P3: chưa triển khai |
| SVC/syscall obfuscation | `enable_svc` | Không có path tương đương xác minh; nhạy cảm với sandbox/iOS | Không khuyến nghị |
| SEC/anti-debug | `enable_sec` | Hikari có `enable-adb` và anti-hook, nhưng có nguy cơ xung đột Substrate/tweak | Không đưa vào release mặc định |
| Đổi tên symbol/hàm | Không được liệt kê rõ ràng trong SLLVM README | Không có generic symbol-renaming pass xác minh | Nhánh riêng: symbol visibility/stripping audit |
| FLA/BCF/SUB/SPLIT | Hiện có | Đang sử dụng plugin `obfuscator`, đã được người dùng báo CI xanh | Giữ nguyên baseline |

## Thiết kế kiểm thử và điều kiện phát hành

**Không thêm `enable_ce`, `enable_icall`, `enable_igv` từ SLLVM trực tiếp vào `policy.json` hiện tại:** plugin `obfuscator` không nhận những khóa đó theo mô hình pass tương ứng, tạo sự yên tâm sai.

1. **P1 / Thử plugin Hikari độc lập:** trong GitHub Actions với `workflow_dispatch` opt-in riêng (không bắt buộc trên push/PR), build `hikari/` từ **cùng SHA đã pin**, cùng LLVM 19, tạo fixture C và Objective-C nhỏ. Giữ `DuoDashReconstruction` và `DuoDashReconstruction-OLLVM` **không thay đổi**. Nạp Hikari trên fixture với policy `enable-strcry` + `enable-constenc` nhưng không tự tuyên bố `CE` stack-mode của SLLVM.
2. **Xác thực biến đổi:** yêu cầu log `run strenc` / `run constenc` cho hàm được chọn. So sánh output trước/sau, kiểm tra đối tượng/section `__cstring` và `__cfstring` với tool Mach-O để chắc chắn chuỗi **mục tiêu** không nằm dạng plaintext. Không in trực tiếp key/secret ra log. Kiểm tra chuỗi không thuộc mục tiêu và Objective-C selector không bị thay đổi.
3. **P1b / Pilot trên hàm thật:** chọn helper không mang tên selector/metadata/hook và có expected-value regression. Dùng **một** pass chuyên biệt trên module/hàm riêng trước, chưa nạp đồng thời Obfuscator + Hikari lên cùng module nếu chưa chứng minh chạy cùng nhau; 2 plugin đều đăng ký pipeline ở điểm khởi đầu, có thể trùng global symbols và thứ tự chạy.
4. **P2 / Các kỹ thuật khác:** FCO, indirect branch và wrapper chỉ sau khi P1 ổn. Giới hạn ở C helpers có ABI nội bộ. Tránh trực tiếp runtime methods, Objective-C selectors, `objc_msgSend`, CF/dyld resolution, `MSHookFunction`/Substrate, init/constructor, CarPlay hostflow/geometry.
5. **Baseline và rollback:** so sánh 3 kết quả (plain/OLLVM/experimental); ghi file size, thời gian build, thời gian thực thi probe, sự xuất hiện plaintext strings, exported/dynamic symbols. Fail closed nếu thử nghiệm sai; **không chặn artifact chuẩn**. Chỉ quảng bá phiên bản mới sau thử trên thiết bị với license/prefs/CarPlay lifecycle/regression và thống kê crash.

## Lộ trình thiết thực

- **Bước A (nên làm trước):** CI audit-only về string/symbol bề mặt tấn công, không đổi sản phẩm.
- **Bước B:** thêm độc lập Hikari probe (CE-string + constenc), so sánh kết quả và tự kiểm tra log.
- **Bước C:** đưa CE chọn lọc vào 1–2 hàm, kiểm tra Objective-C runtime/IPC/callback, giữ baseline.
- **Bước D:** thêm FCO/IBR/wrapper có ranh giới chức năng; sau đó mới cân nhắc viết hoặc cấp phép các pass tương tự SLLVM còn thiếu.

**Cập nhật triển khai (16/10/2026):** Đã thêm workflow manual-only `.github/workflows/hikari-evaluation.yml`, fixture C và checker fail-closed để thử Hikari `strcry` + `constenc` riêng biệt. Xem `docs/HIKARI_EVALUATION.md`. Chưa đưa Hikari vào binary phát hành, chưa kiểm chứng Hikari/LLVM 19 trên macOS; các thay đổi của workflow OLLVM hiện hành được giữ nguyên. Các giai đoạn pilot trên Objective-C / helper thật và phối hợp nhiều plugin chưa triển khai.

Tài liệu gốc: https://github.com/lich4/sllvm ; https://github.com/lich4/ollvm-pass
