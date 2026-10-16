# OLLVM test độc lập trên demo/Crane

## Phạm vi và trạng thái

Thư mục `demo/` do người dùng bổ sung là một reconstruction của Crane, không
phải DuoDash; gồm **7 subproject Theos**, Preferences UI, container manager,
SpringBoard tweak và helper daemon. Tài liệu riêng của demo ghi nhiều chức năng
chưa hoàn chỉnh, vì vậy phép thử vẫn phải phân biệt build PASS với runtime PASS.

Workflow root: `.github/workflows/demo-ollvm-evaluation.yml` →
**Evaluate OLLVM on Crane Demo (Experimental)**, chỉ `workflow_dispatch`.

**Quan trọng:** Lúc khảo sát đầu tiên, `demo/` là thư mục **untracked**
trong Git. Hiện người dùng đã chạy CI thành công với demo trên GitHub, nhưng
vẫn cần giữ `demo/reconstruction/` (mã nguồn, layout, vendor và build tools)
trong commit của từng lần build. **Rà soát quyền sử dụng và tránh đưa
demo/usr, demo/Library, binaries gốc hay dữ liệu riêng lên GitHub vô ý.**
Workflow fail ngay nếu thiếu `demo/reconstruction/Makefile`.

## Chiến lược giai đoạn 1: CranePrefs Credits UI

Policy ở `scripts/demo_ollvm/policy.json`, chỉ chọn source
`sources/prefs/CRCredits.m` và hai helper sau:

| Function | SPLIT | BCF | FLA | SUB |
| --- | --- | --- | --- | --- |
| `CRCreditsOpenTwitter` | 4 block | 100%, 2 vòng | On | 3 vòng |
| `CRCreditsLocalizedRows` | 4 block | 100%, 2 vòng | On | 3 vòng |

Đây là hai helper liên quan đến trang Credits của giao diện Preferences.
Không thêm pass vào selectors, ObjC class metadata, constructor, daemon,
container switching, SpringBoard hooks hoặc các source khác. Việc có gọi
helper trong bản thực tế phụ thuộc runtime; không kết luận từ log build.

`scripts/demo_ollvm/prepare.py` copy `demo/reconstruction/` vào các
sandbox riêng trong `$RUNNER_TEMP`. Các thay đổi scheme-specific về
layout, dependencies, postinst và Makefile chỉ xảy ra trong **bản sao**;
source demo gốc không bị sửa. Bản OLLVM tạo `policy.json` trong sandbox. Bản chuẩn dùng Apple Clang. Bản OLLVM dùng adapter
`scripts/demo_ollvm/compiler_select.py` qua `TARGET_CC`, **ủy quyền
mọi file khác** (bao gồm `CRCommon.m`, tweak/daemon/hooks) cho Apple Clang.
Với `CRCredits.m`, **chỉ lát cắt arm64** dùng Homebrew LLVM19 Clang và
nạp OLLVM plugin; **lát cắt arm64e** dùng Apple Clang nguyên bản do LLVM19
sinh object `arm64e.old` không tương thích với Apple linker cần `arm64e`.
Plugin lấy từ `lich4/ollvm-pass` commit
`592f215f852e3957da01b2b15024dc63713a462e`. Apple clang++ được dùng
để link. Adapter đặt tường minh LLVM19 `-resource-dir`, có module cache
riêng. Workflow yêu cầu đúng **một** log `DEMO_OLLVM_SELECTED` cho
`arm64` và **một** log `DEMO_OLLVM_BYPASS` cho `arm64e`, đồng thời yêu cầu
đúng 8 sự kiện pass/hàm. Không tự bật pass trên toàn bundle.

Workflow hiện chạy **hai job độc lập rootless/roothide**, cùng giữ
kiểm tra Mach-O arm64 + arm64e cho dylib/bundle nhưng chỉ obfuscate
CRCredits.m ở lát cắt arm64.

## Tăng độ rối mã để kiểm chứng trực quan (STRONG, thử nghiệm)

Sau khi người dùng xác nhận **bản roothide cũ chạy bình thường trên
iPhone 6s / iOS 15.8.8**, cấu hình mới nâng hai helper Credits từ:

- Đã thử trên máy: SPLIT2 / BCF30% × 1 / FLA / SUB × 1.
- STRONG mới: **SPLIT4 / BCF100% × 2 / FLA / SUB × 3**.

Đây là **obfuscation mã máy**, **không phải mã hóa dữ liệu/binary bằng
thuật toán mật mã**. Các tên ObjC selector, metadata, nội dung UI và
các thư viện/hook/daemon khác không bị can thiệp; code protection chỉ
được bật ở **arm64** trên hai helper như trước, `arm64e` vẫn dùng
Apple Clang. Build và runtime của cấu hình STRONG chưa được xác nhận.

Để phân biệt thay đổi do compiler với OLLVM, workflow mới **biên dịch
`CRCredits.m/arm64` hai lần bằng cùng LLVM19**, cùng SDK, flags,
optimization, v.v., chỉ khác có/không có
`-fpass-plugin=Obfuscator.dylib`. Bộ đối chứng **không được link** vào
package. Audit trong `scripts/demo_ollvm/analyze_binary.py` yêu cầu
Mach-O objects đều arm64, mã lệnh khác nhau, tăng số lệnh ít nhất
**1,20×** ở toàn file (ngưỡng *dễ quan sát*, không phải điểm bảo mật).

Trong artifact `CraneDemo-OLLVM-STRONG-roothide-EXPERIMENTAL`:

| File | Mục đích |
| --- | --- |
| `CRCredits-disassembly-report.md` | Số lệnh, số nhánh có điều kiện (ước lượng), SHA object và hệ số tăng |
| `CRCredits-llvm19-no-pass-arm64.asm` | Assembly object không OLLVM |
| `CRCredits-ollvm-strong-arm64.asm` | Assembly object có OLLVM STRONG |
| `CRCredits-arm64.diff` | Diff hiển thị sự khác biệt trực tiếp |
| `CRCredits-llvm19-no-pass-arm64.o` và `CRCredits-ollvm-strong-arm64.o` | Hai binary object để tải vào Ghidra, IDA hoặc công cụ Mach-O |
| `CranePrefs-baseline-arm64` và `CranePrefs-ollvm-strong-arm64` | Hai lát cắt **arm64 được trích từ binary đã link và đóng gói** để kiểm tra sản phẩm thực tế |

Các đối tượng `.o` chỉ phục vụ phân tích, **không cài lên iPhone**.
Muốn quan sát trực tiếp có thể mở hai file `.asm` cạnh nhau, hoặc dùng
Ghidra/IDA để so sánh hai `.o` và hai bản `CranePrefs-*arm64`.

Chỉ phân tích chức năng/đường đi đã nhắm đến, không suy diễn rằng mã
được bảo vệ toàn bộ. Tăng nhánh, số lệnh và băm khác nhau không tự chứng
minh chống được reverse engineering. FLA/BCF mạnh có thể tăng thời
gian chạy/crash; cần chạy lại bài test Credits, giấy phép, links, mở
đóng nhiều lần trên iPhone 6s, luôn giữ bản đã hoạt động làm rollback.

## Package cho iPhone 6s iOS 15.8.8: rootless và roothide

Thông báo `package architecture (iphoneos-arm) does not match system
(iphoneos-arm64)` đến từ metadata Debian của `.deb` rootful, **không**
phải do CPU iPhone 6s thiếu arm64e. CPU iPhone 6s là arm64.

| Job | THEOS_PACKAGE_SCHEME | Theos | Architecture của .deb |
| --- | --- | --- | --- |
| rootless | `rootless` | `theos/theos` | `iphoneos-arm64` |
| roothide | `roothide` | `roothide/theos` | `iphoneos-arm64e` |

Roothide chuẩn dùng architecture `iphoneos-arm64e` như **namespace
đóng gói** dù máy chỉ có CPU arm64. Nếu thiết bị thông báo hệ thống
`iphoneos-arm64` như trường hợp này, cần kiểm tra bootstrap đang hoạt
động; không mặc định cho rằng package rootless có thể cài vào roothide.

Trên thiết bị chạy `dpkg --print-architecture` để xác nhận package manager.
Với môi trường rootless chuẩn thật sự dùng `iphoneos-arm64`, chọn artifact
`CraneDemo-OLLVM-rootless-EXPERIMENTAL`; với roothide chuẩn (đúng bootstrap
roothide) chọn `CraneDemo-OLLVM-roothide-EXPERIMENTAL` khi kiến trúc dpkg
tương thích. Nếu dùng roothide nhưng dpkg vẫn in `iphoneos-arm64`, **không
cài hai artifact ngay**: xác định rõ dpkg/bootstrap trước để tránh đụng
cấu trúc hệ thống.

Workflow chạy hai job độc lập, kiểm tra `dpkg-deb -f <file.deb> Architecture`,
dependency, đủ 33 tệp layout, nội dung và mode 0755 của `postinst`, kiến
trúc Mach-O, pass logs và sự khác biệt CranePrefs. Rootless chỉ stage vào
`/var/jb` và chuyển path launchd/postinst **trong sandbox**; roothide dùng
roothide/theos và kiểm tra helper entitlements. Không có thao tác đổi
metadata hậu đóng gói nhằm lách dpkg.

Build PASS **không đảm bảo** thiết bị đã cài và chạy được: còn phụ thuộc
bootstrap, loader, code signing, launchd và chức năng reconstruction.
Chỉ cài thử trên máy phụ có backup và đường rollback, không cài song
song bản rootless/roothide hay baseline/OLLVM cùng package ID.


## Chạy và kiểm tra GitHub Actions

Vào **Actions → Evaluate OLLVM on Crane Demo (Experimental) → Run workflow**
sau khi push workflow, script và mã nguồn demo cần thiết.

CI:
1. Kiểm tra policy và mã nguồn demo đang hiện diện trong commit.
2. Dùng cùng `waruhachi/theos-action@v2.6.3` như CI gốc của demo; cài
   thêm Homebrew `dpkg` và kiểm tra `dpkg-deb --version` trước khi build.
   Theos dùng `dm.pl` để đóng gói nhưng runner không nhất thiết có `dpkg-deb`
   để đọc/giải nén package.
3. Build `make clean package FINALPACKAGE=1` phiên bản **baseline**. Unpack
   `.deb` bằng `dpkg-deb -x` (data) **và** `dpkg-deb -e` (control/postinst),
   truyền cả hai thư mục cho `verify_package_layout.py` để kiểm tra chính xác
   `postinst` cùng mode 0755; chạy verifier Mach-O architecture, rồi upload
   `CraneDemo-Baseline-rootless-EXPERIMENTAL` hoặc
   `CraneDemo-Baseline-roothide-EXPERIMENTAL` trước khi biên dịch OLLVM.
   Rootless kiểm tra nội dung data trong `/var/jb`; roothide thêm kiểm tra
   entitlement helper theo chính verifier gốc của demo.
4. Build OLLVM plugin bằng LLVM19 và preflight khả năng biên dịch Objective-C
   Foundation/UIKit với bộ LLVM19 resource headers và SDK của Xcode, sau đó
   biên dịch lại package với **LLVM19 chỉ cho `CRCredits.m` ở arm64**. Apple
   Clang xử lý `CRCredits.m` ở arm64e và toàn bộ source khác. Yêu cầu đúng
   một sự kiện chọn LLVM19 ở arm64 và một sự kiện bypass ở arm64e; chỉ tạo
   `CraneDemo-OLLVM-STRONG-rootless-EXPERIMENTAL` hoặc
   `CraneDemo-OLLVM-STRONG-roothide-EXPERIMENTAL` khi các audit đều đạt.
   Audit bổ sung so sánh object LLVM19 không-pass với có-pass và hai lát
   cắt arm64 đã link, lưu báo cáo và disassembly chi tiết.
5. `scripts/demo_ollvm/verify.py` yêu cầu cả **4 pass trên từng hàm**,
   không có sự kiện OLLVM trên các hàm ngoài danh sách, hai package có cùng
   đường dẫn payload, `CranePrefs` binary thay đổi và ba class UI Credits
   vẫn tồn tại trong Mach-O. Verifier nguồn demo tiếp tục kiểm tra đủ 7
   artifact, layout và kiến trúc.
6. Tạo `report.md` so sánh SHA-256 và dung lượng bundle UI, số lần pass
   được ghi trong log; giữ `CraneDemo-OLLVM-Diagnostics` cả khi job lỗi.

**Không coi chênh lệch binary là bằng chứng riêng của OLLVM:** riêng
`CRCredits.m` (arm64) được biên dịch bằng LLVM19 ở bản OLLVM thay vì
Apple Clang trong baseline. Lát arm64e tiếp tục dùng Apple Clang.
Audit pass log và selector compiler được xác minh độc lập.

## Kiểm tra trên thiết bị dự phòng

Các package dùng **cùng Package ID** nhưng có scheme/đường dẫn khác nhau;
không được cài đồng thời. Chỉ thử trên thiết bị jailbreak phụ có thể
rollback, đã backup dữ liệu, không phải iPhone chính.

**Giới hạn đặc biệt của phiên bản này:** chỉ lát cắt **arm64** chứa OLLVM;
lát cắt **arm64e** chưa được mã hóa. Trên thiết bị tải lát cắt arm64e,
việc giao diện chạy đúng **không chứng minh** chức năng OLLVM đã được
thử trong runtime. Xác minh lát cắt được chọn khi chạy trước khi kết luận
về hiệu quả OLLVM trên thiết bị. Không chỉnh sửa Mach-O subtype để ép
liên kết `arm64e.old` sang `arm64e`.

Ghi lại cho *cả hai bản* ở cùng môi trường:

- Mở Settings → Crane/CranePrefs, vào Credits & Licenses; xác minh tên trang,
  specifier/nhãn, link ZipArchive, MiniZip và nút mở liên kết.
- Mở/tắt các trang Settings khác, so sánh crash, thời gian phản hồi, lag,
  CPU/bộ nhớ và log exception.
- Kiểm tra daemon, container switch, hook/injection **một cách riêng biệt**;
  các chức năng chưa hoàn thiện trong reconstruction không được ghi nhầm
  là regressions của OLLVM.
- Test phiên bản baseline trước, sau đó thay bằng bản OLLVM; ghi phiên bản
  thiết bị, iOS, scheme/bootstrap, `dpkg --print-architecture`, artifact
  hash và các lỗi thực tế. Giữ
  đường rollback về chính bản baseline đã thử.

**Cập nhật kiểm thử (16/10/2026):** Người dùng xác nhận bản OLLVM roothide
trước khi tăng độ rối đã build, **cài đặt và hoạt động bình thường** trên
iPhone 6s / iOS 15.8.8. Report CI có 33 đường dẫn khớp, 8 pass events,
CranePrefs có SHA-256 khác nhưng cùng kích thước. Đây là kết quả runtime
**người dùng trực tiếp báo**, chưa có log chứng minh từng test D01–D09 hoặc
bản STRONG mới. Bản cũ là mốc rollback khi kiểm thử STRONG.

Bài test D01–D09, bảng điền kết quả và tiêu chí đối chiếu baseline được
lưu trong [CRANE_ROOTHIDE_DEVICE_TEST.md](CRANE_ROOTHIDE_DEVICE_TEST.md).
Không phát hành/distribute bản demo OLLVM như bản production.

## Local verification

```sh
python3 scripts/test_demo_ollvm.py
python3 scripts/test_ollvm_integration.py
python3 scripts/verify_reconstruction.py
```

Các kiểm tra trên Windows chỉ xác minh policy, tính cô lập sandbox và logic
audit; iOS/Xcode/Theos/LLVM19 build yêu cầu runner macOS. Nếu baseline demo
không build được vì framework/vendor, cần xử lý lỗi baseline trước khi
quy lỗi cho OLLVM.

## Khắc phục lỗi runner macOS: thiếu dpkg-deb

Nếu thấy `dm.pl: building package ... .deb` rồi ngay sau đó
`dpkg-deb: command not found` (exit 127), đó là lỗi **thiếu công cụ giải
nén .deb trên runner**, không phải lỗi biên dịch OLLVM hay lỗi tạo package.
Workflow đã thêm step **Install Debian package inspection tool** chạy
`brew install dpkg`, `command -v dpkg-deb`, `dpkg-deb --version` trước
lần build baseline và kiểm tra lại trước cả hai lệnh `dpkg-deb -x`.

Homebrew `dpkg` trên macOS cung cấp `dpkg-deb` để **kiểm tra/giải nén**;
không sử dụng các lệnh `dpkg -i` hoặc cài package vào host macOS.
Dòng `od: stdout: Broken pipe` cạnh log đóng gói thường có thể do bên đọc
pipeline đóng sớm; không kết luận đó là lỗi build trừ khi có exit code
thực sự phát sinh từ lệnh đóng gói. Sau khi sửa, kiểm tra status các bước
**baseline package**, **verify package layout**, **verify architectures**, rồi
mới phân tích pass OLLVM.

## Khắc phục lỗi control archive: postinst was not verified

Nếu log báo `FAIL control archive root not supplied; postinst was not
verified` dù 33 data files đều OK, nguyên nhân là script verifier của demo
cần **hai** đối số thư mục; bản workflow cũ chỉ truyền thư mục data sau
`dpkg-deb -x`. Script kiểm tra `postinst` có nội dung khớp file đã review
trong `demo/reconstruction/layout/DEBIAN/postinst` và quyền thực thi **0755**.
Không nên tắt bài kiểm tra này.

Workflow hiện đã thêm **cả hai nhánh baseline và OLLVM**:

```sh
# Baseline (nhánh OLLVM dùng demo-expanded-ollvm và demo-control-ollvm)
dpkg-deb -x "$deb" "$RUNNER_TEMP/demo-expanded-plain"
dpkg-deb -e "$deb" "$RUNNER_TEMP/demo-control-plain"
python3 "$GITHUB_WORKSPACE/demo/reconstruction/tools/verify_package_layout.py" \
  "$RUNNER_TEMP/demo-expanded-plain" "$RUNNER_TEMP/demo-control-plain"
```

Nếu lần chạy mới vẫn FAIL, thông báo sẽ xác định được lỗi thật ở
`postinst` (không tồn tại, nội dung khác hoặc sai mode) hoặc lỗi package
khác. Bản sửa này chưa được chạy trên runner macOS sau khi cập nhật.

## Khắc phục lỗi LLVM19/Xcode 15.4 resource headers

Sau khi baseline package PASS, lần build OLLVM có thể lỗi từ
`XcodeDefault.xctoolchain/.../clang/include/stddef.h` với
`__stddef_max_align_t.h file not found`, tiếp đó cascade
`could not build module 'Darwin'`, Foundation/UIKit và lỗi `CRCommon.m`.
Trong phiên bản workflow cũ, `TARGET_CC` trỏ thẳng LLVM19 cho **toàn bộ**
7 target dù OLLVM chỉ cần trên 2 helper của trang Credits. Đồng thời,
`CranePrefs_CFLAGS += -fpass-plugin=...` vô tình áp dụng plugin cho tất cả
source trong bundle. Đây là phạm vi quá rộng, dễ gây xung đột hệ thống
header/Clang module giữa Xcode và Homebrew LLVM.

Workflow mới dùng adapter `compiler_select.py` để dùng Apple Clang cho mọi
file trừ **một translation unit** `CRCredits.m` và bật pass chỉ ở lần
compile của file đó. LLVM19 được ép dùng đúng thư mục resource headers do
`clang -print-resource-dir` cung cấp, gồm `stddef.h` và
`__stddef_max_align_t.h`; module cache độc lập cho LLVM19. Trước build
OLLVM có một smoke test compile Objective-C Foundation/UIKit bằng đúng
LLVM19 và iPhoneOS SDK; lỗi SDK/Clang sẽ được tách ra sớm và rõ.

Kiểm thử cục bộ xác minh adapter chọn đúng file, giữ nguyên Makefile demo,
không chọn `CRCommon.m`/hook/daemon, và chỉ LLVM19 ở arm64 (Apple Clang
ở arm64e).
Build thực tế vẫn cần chạy lại trên macOS; nếu `CRCredits.m` vẫn gặp lỗi
resource/module, cần xem `CraneDemo-OLLVM-Diagnostics` và bước preflight,
không bỏ qua kiểm tra và không quay về ép LLVM19 cho toàn project.

## Khắc phục lỗi linker: arm64e.old không tương thích arm64e

Log mới cho thấy OLLVM đã chạy đầy đủ SPLIT/BCF/FLA/SUB trên hai helper,
nhưng Apple linker từ chối `CRCredits.m.*.o` với architecture
`arm64e.old` khi target cần `arm64e`, gây thiếu symbol
`_CRCreditsOpenTwitter` (sự cố ABI, không phải source thiếu hàm).
Cảnh báo `-multiply_defined is obsolete` không phải lỗi dừng link.

Không đổi tên/mã CPU subtype của object hoặc bỏ lát cắt arm64e trong
package chuẩn vì làm vậy che giấu lỗi ABI. Thay vào đó adapter
`compiler_select.py` dựa vào kiến trúc của lệnh biên dịch: ở `arm64`
dùng LLVM19 + OLLVM, ở `arm64e` dùng Apple Clang; các file khác cũng
Apple Clang. CI vẫn buộc package đủ arm64+arm64e bằng verifier gốc.
Audit mới fail nếu thiếu/nhân đôi một trong 8 pass events trên arm64,
hoặc thiếu hai sự kiện routing compiler. Việc kiểm chứng obfuscation
trực tiếp trên thiết bị arm64e cần giải pháp compiler/ABI tương thích
mới; hiện không tuyên bố đã bảo vệ lát arm64e.
