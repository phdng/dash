# OLLVM test độc lập trên demo/Crane

## Phạm vi và trạng thái

Thư mục `demo/` do người dùng bổ sung là một reconstruction của Crane, không
phải DuoDash; gồm **7 subproject Theos**, Preferences UI, container manager,
SpringBoard tweak và helper daemon. Tài liệu riêng của demo ghi nhiều chức năng
chưa hoàn chỉnh, vì vậy phép thử vẫn phải phân biệt build PASS với runtime PASS.

Workflow root: `.github/workflows/demo-ollvm-evaluation.yml` →
**Evaluate OLLVM on Crane Demo (Experimental)**, chỉ `workflow_dispatch`.

**Quan trọng:** Lúc khảo sát, `demo/` là thư mục **untracked** trong Git của
DuoDash. GitHub Actions **không nhìn thấy file trên máy người dùng**. Cần đưa
ít nhất `demo/reconstruction/` (mã nguồn, layout, vendor và build tools) vào
commit/nhánh trên GitHub trước khi chạy. **Rà soát quyền sử dụng và tránh đưa
demo/usr, demo/Library, binaries gốc hay dữ liệu riêng lên GitHub vô ý.**
Workflow fail ngay nếu thiếu `demo/reconstruction/Makefile`.

## Chiến lược giai đoạn 1: CranePrefs Credits UI

Policy ở `scripts/demo_ollvm/policy.json`, chỉ chọn source
`sources/prefs/CRCredits.m` và hai helper sau:

| Function | SPLIT | BCF | FLA | SUB |
| --- | --- | --- | --- | --- |
| `CRCreditsOpenTwitter` | 2 block | 30%, 1 vòng | On | 1 vòng |
| `CRCreditsLocalizedRows` | 2 block | 30%, 1 vòng | On | 1 vòng |

Đây là hai helper liên quan đến trang Credits của giao diện Preferences.
Không thêm pass vào selectors, ObjC class metadata, constructor, daemon,
container switching, SpringBoard hooks hoặc các source khác. Việc có gọi
helper trong bản thực tế phụ thuộc runtime; không kết luận từ log build.

`scripts/demo_ollvm/prepare.py` copy `demo/reconstruction/` vào **hai
sandbox** hoàn toàn riêng trong `$RUNNER_TEMP`. Bản OLLVM thêm
`CranePrefs_CFLAGS += -O1 -fpass-plugin=<pinned-plugin>` vào **Makefile của
CranePrefs trong sandbox** và tạo hai `policy.json` phục vụ compiler CWD.
Không chỉnh sửa bất kỳ source/Makefile nào của demo gốc. Bản chuẩn build
với toolchain mặc định; bản OLLVM build bằng LLVM19 Clang tương ứng với
plugin `lich4/ollvm-pass` commit
`592f215f852e3957da01b2b15024dc63713a462e`. Apple clang++ được dùng
để link. Cả 7 target vẫn được biên dịch; **chỉ CranePrefs nạp OLLVM pass**.

Phạm vi hiện tại chỉ chạy **rootful** theo action Theos của demo, với
architectures gốc (arm64 + arm64e cho dylib/bundle); roothide là giai đoạn
tiếp theo sau khi rootful thử nghiệm xanh.

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
   `.deb`, chạy verifier layout và Mach-O architecture của demo, rồi upload
   `CraneDemo-Baseline-EXPERIMENTAL` trước khi biên dịch OLLVM.
4. Build OLLVM plugin cùng phiên bản và toolchain đã dùng trong DuoDash,
   biên dịch lại toàn bộ package với đúng **hai hàm đã chọn** để tạo
   `CraneDemo-OLLVM-EXPERIMENTAL`.
5. `scripts/demo_ollvm/verify.py` yêu cầu cả **4 pass trên từng hàm**,
   không có sự kiện OLLVM trên các hàm ngoài danh sách, hai package có cùng
   đường dẫn payload, `CranePrefs` binary thay đổi và ba class UI Credits
   vẫn tồn tại trong Mach-O. Verifier nguồn demo tiếp tục kiểm tra đủ 7
   artifact, layout và kiến trúc.
6. Tạo `report.md` so sánh SHA-256 và dung lượng bundle UI, số lần pass
   được ghi trong log; giữ `CraneDemo-OLLVM-Diagnostics` cả khi job lỗi.

**Không coi chênh lệch binary là bằng chứng riêng của OLLVM:** bản OLLVM
đồng thời dùng LLVM19 Clang còn baseline dùng Apple Clang.

## Kiểm tra trên thiết bị dự phòng

Hai `.deb` dùng **cùng Package ID và đường dẫn cài đặt Crane**; chúng
không được cài đồng thời. Chỉ thử trên thiết bị jailbreak phụ có thể
rollback, đã backup dữ liệu, không phải iPhone chính.

Ghi lại cho *cả hai bản* ở cùng môi trường:

- Mở Settings → Crane/CranePrefs, vào Credits & Licenses; xác minh tên trang,
  specifier/nhãn, link ZipArchive, MiniZip và nút mở liên kết.
- Mở/tắt các trang Settings khác, so sánh crash, thời gian phản hồi, lag,
  CPU/bộ nhớ và log exception.
- Kiểm tra daemon, container switch, hook/injection **một cách riêng biệt**;
  các chức năng chưa hoàn thiện trong reconstruction không được ghi nhầm
  là regressions của OLLVM.
- Test phiên bản baseline trước, sau đó thay bằng bản OLLVM; ghi phiên bản
  thiết bị, iOS, jailbreak/rootful, artifact hash và các lỗi thực tế. Giữ
  đường rollback về chính bản baseline đã thử.

**Khả năng hoạt động trên thiết bị chưa được xác minh** bởi việc build CI.
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
mới phân tích pass OLLVM. Chưa có xác nhận CI macOS chạy lại sau sửa.
