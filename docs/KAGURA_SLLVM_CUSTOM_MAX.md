# DuoDash — Kagura × ý tưởng SLLVM: custom MAX compiler-pass lab

Ngày bắt đầu: 2026-10-17 · Trạng thái: **K0 và K1 đều đã có artifact LLVM19 macOS CI thực; K1 có 7/7 pass tạo IR/object delta và mỗi pass giữ 8.192 vector native parity.** Chưa có kết quả Kagura K1 runtime iOS.

## Mục tiêu đúng

Xây bộ custom pass làm phân tích tĩnh hàm nhạy cảm **khó, tốn công và
ít hiệu quả hơn**, nhưng **không bảo đảm không thể phân tích tĩnh hoặc
không thể trích xuất logic**. IDA/Ghidra vẫn phân tích được thông tin ở
nhiều mức; runtime instrumentation, input-output và decompiler hiện đại
vẫn là các hướng có thể khai thác. Không dùng bất cứ con số độ bảo mật
nào suy ra trực tiếp từ số instruction, basic blocks hoặc entropy.

**Kagura** [source MIT](https://github.com/qusamulab/kagura) là plugin
LLVM New Pass Manager (17+), có mã source C++ thật, test và pipeline.
**SLLVM** [README](https://github.com/lich4/sllvm) hiện chủ yếu là tài
liệu/tuyên bố tính năng; không có cây compiler/plugin source công khai
trong repository đã khảo sát. Vì thế chúng ta dùng *ý tưởng* và mục
tiêu thiết kế từ SLLVM, chọn Kagura làm nền mã nguồn khả dụng;
không dùng pass SLLVM proprietary, không nhận các tên giống nhau
là tương đương.

Upstream pin cho thử nghiệm Kagura:
`ac2136ee0408677cf7cdee55307e9b16edd5f4d5` (nhánh main
được kiểm tra khi chuẩn bị sprint này, không phải luôn là HEAD).
License nguồn là MIT, cần giữ giấy phép khi tạo derivative.

## Ma trận phối hợp pass

| Nhu cầu | SLLVM mô tả | Kagura có trong nguồn/docs | Quyết định DuoDash |
|---|---|---|---|
| CE / literal | `CE` stack/non-stack | `str`, `str_aes`, `wstr`, `string_split`, `co` | **Ưu tiên thử `str` + `co`**, sau đó kiểm ObjC NSString/CFString; không nhận tương đương SLLVM CE |
| Control flow | FLA, BCF, ECF | `fla`, `bcf`, `sub`, `bbs`, `bbr`, `lt`, `dci` | Kết hợp có gate theo từng pass, không bật ồ ạt |
| IBR / ICALL | Indirect branch/call | `ibr` (theo docs Kagura là direct-call→global pointer), `ci` (runtime-resolved external thunk) | **Không xem là tương đương**; chặn trong iOS hook/PAC-sensitive trước khi kiểm |
| IGV | Indirect globals | `genc`, `mvo` | Thử riêng trên integer globals/local; không coi `genc` là SLLVM IGV |
| FW | Function wrapper | `fsplit` (outlines blocks) | Không tương đương FW; chỉ thử hàm C nội bộ không callback |
| VM | LLVM IR→bytecode | **`kagura-vm` có mã và runtime** | Tầng MAX_VIRTUALIZED riêng; chưa bật mặc định vì overhead/ABI |
| FCC/SVC/SEC | ABI, syscall, anti-debug | Có một số PAC/anti-debug/integrity tương tự ở Kagura | **Không bật** trong Crane tweak/hook/daemon, tránh xung đột PAC/Substrate/iOS |

Nguồn: Kagura
[passes](https://qusamulab.github.io/kagura/passes/),
[order](https://qusamulab.github.io/kagura/pass-order/),
[VM](https://qusamulab.github.io/kagura/passes/platform/),
SLLVM README.

## Ba cấp thử nghiệm, không gọi cấp nào là production MAX

**Pha K0 — MAX_CANDIDATE** (đã có macOS CI artifact thực được kiểm tra; xem [KAGURA_K0_ARTIFACT_REVIEW.md](KAGURA_K0_ARTIFACT_REVIEW.md)):

- Workflow mới `.github/workflows/kagura-max-candidate.yml`,
  `workflow_dispatch` độc lập, **không sửa Crane production**.
- Lấy Kagura từ đúng SHA, xác minh MIT LICENSE, build real C++ LLVM
  plugin với **LLVM 19**.
- Biên dịch `critical.c` thành bitcode bằng cùng LLVM19; bản baseline
  không có plugin, bản candidate gọi `opt --load-pass-plugin` với:
  `kagura-str,function(kagura-fla,kagura-bcf,kagura-sub,kagura-co)`.
- Biên dịch thành native binary và chạy **8.192 vector**, yêu cầu từng
  dòng output giống baseline; kiểm tra IR và object khác nhau, chuỗi
  public canary biến mất khỏi object và Mach-O sau transform.
- Cross-compile `arm64` plain/Kagura iOS Mach-O dylibs để kiểm tra
  `MH_DYLIB`, CPU subtype và hash. `arm64e` **Apple Clang only**,
  subtype raw `0x80000002`; không gắn nhãn Kagura protected hoặc
  A12+ PAC runtime PASS.
- Output artifacts chứa native vector logs, `.ll`, pass logs,
  iOS dylibs và audit JSON. Đây là pipeline thật dự kiến thực thi
  trong macOS CI, **không phải source-level canary**.

**Pha K1 — MAX_STRUCTURAL** (đã có artifact CI thực và được đối chiếu; xem [KAGURA_K1_ARTIFACT_REVIEW.md](KAGURA_K1_ARTIFACT_REVIEW.md)):

Đã bổ sung `stage_pipeline.py` vào chính workflow K0 để dùng cùng LLVM19
và cùng fixture: **str → fla → bcf → sub → co → bbr → bbs**.
Sau mỗi pass riêng, CI ghi debug-pass-manager, LLVM IR/object delta,
số basic blocks, SHA-256 và chạy lại 8.192 native vector so baseline.
Nếu pass không biến đổi hàm hoặc biến đổi chỉ tồn tại trên IR mà
không thấy trên object, report phân loại rõ thay vì nhận là bảo vệ thêm.
BBR/BBS có **IR_AND_OBJECT_DELTA và 8.192 native parity PASS trên macOS**, nhưng **chưa có runtime iPhone hay đo chi phí**. BBR thay đổi object dù basic blocks giữ 19; BBS tăng basic blocks 19→38. Debug log còn cho thấy function passes chạy trên helper decrypt, nên phải kiểm soát allowlist khi áp dụng lên hàm thật.
Có thể thử `dci`, `lt`, `elt` sau khi xem báo cáo và sửa fixture nếu
phù hợp. Bắt buộc kiểm tra ngoại lệ/ARC, lỗi và overhead trước khi
xét composite. `ci`/`ibr` chỉ áp
dụng C-only với ABI typed, tránh ObjC selectors và callback/ptrauth.

**Pha K2a — TU scope + native overhead** (đã kiểm tra artifact macOS CI và benchmark thật; xem [KAGURA_K2_ARTIFACT_REVIEW.md](KAGURA_K2_ARTIFACT_REVIEW.md)):

Đã tạo `sentinel.c` làm object không qua Kagura; chỉ TU `critical.c`
được chạy qua LLVM19 `opt`. Test kiểm tra function definitions đầu vào,
chỉ cho phép helper `kagura_decrypt_*` được sinh thêm, và xác minh
sentinel không xuất hiện trong pass debug log. Đây là **TU isolation**, chưa
phải compiler-pass function allowlist; helper vẫn có thể nhận pass.
Benchmark macOS có 11 mẫu × 32.768 calls ở mỗi stage,
so median/p95 với cùng LLVM19 baseline và verify checksum parity.
Xem [KAGURA_K2_SCOPE_BENCH.md](KAGURA_K2_SCOPE_BENCH.md).

**Pha K3 — COUNTERBALANCED HOST BENCHMARK** (mới có mã và regression portable, chưa có native macOS CI):

Đã bổ sung 16 vòng chạy cân bằng cho 8 biến thể (baseline + 7 giai đoạn),
thứ tự đảo chiều ở nửa sau, thu 176 mẫu/biến thể. Mỗi vòng kiểm tra
checksum; báo cáo median/p95 pooled và tỷ lệ median ghép cặp theo vòng.
Với 176 mẫu, p95 nearest-rank không còn là mẫu lớn nhất như ở K2a
11 mẫu. Chưa có kết quả native macOS K3, cũng chưa thử Kagura runtime iPhone.
Xem [KAGURA_K3_INTERLEAVED_BENCH.md](KAGURA_K3_INTERLEAVED_BENCH.md).

**K4 — KaguraLab TrollStore arm64 IPA (người dùng đã báo IPA chạy PASS trên thiết bị; chưa có log được đối chiếu độc lập):**

Đã tạo app UIKit riêng **KaguraLab**, biên dịch cùng `critical.c` thành
`dd_kagura_plain` và `dd_kagura_protected` bằng LLVM19, rồi chạy
**STR→FLA→BCF→SUB→CO→BBR→BBS** bằng `opt` thật trên bản protected.
Hai object arm64 được link vào MH_EXECUTE và đóng gói IPA riêng để cài
song song ProtectionLab trên máy TrollStore. UI có parity **8192 vector**,
benchmark iPhone **5 cặp × 4096 calls** chỉ sau parity PASS, và chia sẻ
text log. CI có audit pass trace, SHA-256/LC_UUID, chế độ từ chối
nhầm `arm64e`; đã có hồi quy portable trên Windows. Người dùng báo IPA chạy PASS trên
iPhone; K5 đã có artifact macOS CI thực được kiểm tra hash, nhưng chưa
có log text thật từ thiết bị để xác minh UUID do app báo. Xem
[KAGURA_IOS_TROLLSTORE_PILOT.md](KAGURA_IOS_TROLLSTORE_PILOT.md).

**K5 — iOS checksum oracle + build UUID correlation** (đã kiểm tra artifact macOS CI; người dùng báo iPhone PASS, chưa có text log để đối chiếu UUID thực tế):

KaguraLab báo cáo schema 2 ghi LC_UUID của Mach-O đang chạy, và log
benchmark phải ghi cùng UUID. Trình audit tương thích schema 1 cũ nhưng
chỉ ghép schema 2 với cả hai báo cáo IPA/7-pass của CI. Thêm mô hình
Python độc lập tính lại checksum parity/benchmark C (số liệu công khai),
reject checksum sai/UUID chéo/pass evidence thiếu. Tất cả chỉ là phép
so log người dùng gửi, **không chứng thực thực thi bằng mật mã**; chưa
chạm Crane production. Artifact K5 thực đã được kiểm tra hash 7 pass và
bản executable IPA: [KAGURA_K5_ARTIFACT_REVIEW.md](KAGURA_K5_ARTIFACT_REVIEW.md).
Xem [KAGURA_IOS_TROLLSTORE_PILOT.md](KAGURA_IOS_TROLLSTORE_PILOT.md).

**K6 / Pha K2b — MAX_VM_SELECTIVE** (đã có artifact CI thật, macOS native parity PASS + iOS arm64 build-only; chưa thử iPhone VM):

Thử `kagura-vm` trên đúng **một hàm C thuần, nhỏ, hiếm gọi**
(như một thuật toán xác nhận kết quả công khai) kèm runtime
`libkagura_runtime.a`, so sánh kết quả với bản native; giữ function
boundary và interface ABI. Tài liệu Kagura cảnh báo VM có thể chậm
**10–50 lần** — chỉ số từ tài liệu upstream, không phải benchmark
DuoDash. Workflow thủ công riêng `.github/workflows/kagura-vm-selective.yml`
đã được thêm để kiểm thử Kagura VM thực, allowlist một hàm C và guard
cùng TU, 4096 parity/3 cặp thời gian trên macOS và iOS arm64 ABI build-only.
Artifact thực kiểm tra được blob bytecode 171 byte, checksum parity, guard,
Mach-O UUID và VM overhead theo 3 cặp là khoảng 48–64× baseline. Xem
[KAGURA_K6_ARTIFACT_REVIEW.md](KAGURA_K6_ARTIFACT_REVIEW.md).

**K7 — KaguraVMLab real VM iPhone IPA** (artifact macOS CI SHA/UUID/IR đã kiểm chứng; `a.txt` nguyên bản từ iPhone đã qua kiểm tra schema 9+14 dòng, UUID, checksum 4096 vector và ba cặp benchmark; VM chậm median ghép cặp **71,5×**. Đây là user-shared device text, không phải chứng thực mật mã): sử dụng một ứng dụng iPhone arm64 riêng với
bundle ID `com.duodash.research.kaguravmlab` để kiểm thử VM thật trên 4096
vector, optional benchmark và chia sẻ log UUID. Workflow manual-only
`.github/workflows/kagura-vm-ios-ipa.yml` chỉ xuất IPA khi pass evidence,
real macOS VM parity và Mach-O/IPA SHA đều khớp. **Không đưa VM vào IPA K5 đã
PASS hoặc Crane production**. Xem
[KAGURA_K7_VM_TROLLSTORE.md](KAGURA_K7_VM_TROLLSTORE.md) và
[KAGURA_K7_ARTIFACT_REVIEW.md](KAGURA_K7_ARTIFACT_REVIEW.md) và
[KAGURA_K7_DEVICE_LOG_REVIEW.md](KAGURA_K7_DEVICE_LOG_REVIEW.md).
**K8 — kiểm chứng 5 pass còn thiếu**: đã chuẩn bị CI manual-only
cho `ibr`, `mvo`, `genc`, `fsplit`, `ci` với fixture phù hợp đúng registry
Kagura commit pin, 4096 vector native mỗi pass, bắt buộc IR/object delta,
và iOS arm64 build-only. **Chưa chạy macOS K8 native hoặc iPhone K8**;
chưa bật kết hợp 5 pass, không đổi production. Xem
[KAGURA_K8_FIVE_PASS_VALIDATION.md](KAGURA_K8_FIVE_PASS_VALIDATION.md).
Tài liệu K6 gốc: [KAGURA_K6_VM_SELECTIVE.md](KAGURA_K6_VM_SELECTIVE.md).
Không virtualize Objective-C methods, initializer, licensing
storage hooks, selector dispatch, SpringBoard/CarPlay hostflow,
XPC callbacks hoặc function pointer PAC paths trong pha này.

## Đặt chế độ mạnh nhất lên hàm quan trọng như thế nào?

- Mặc định **allowlist 1 hàm thuần C** `dd_kagura_critical` trong
  `scripts/custom_ollvm/kagura_max/critical.c`. Chứa marker vô hại,
  không có UDID, key, credential hay code Crane.
- Kể cả khi profile `STRONG` Kagura tồn tại, không dùng bật toàn bộ
  lên `re/RECONSTRUCTION`. Upstream preset STRONG cũng cố tình
  **tắt VM/CI/PAC/...** vì thay đổi ABI hoặc chi phí cao.
- Chỉ chọn helper thực sau khi chứng minh ABI và parity trên một
  chức năng không trọng yếu, opt-in trên thiết bị dự phòng có
  TrollStore, rollback rõ ràng, và không ảnh hưởng CranePrefs ổn định.
- Cần test với IDA/Ghidra ở bản baseline/candidate **cùng LLVM19,
  cùng flags** và ghi mức thay đổi về CFG, độ dễ đọc, strings, call
  graph, biến đổi bị optimizer hoàn nguyên, chi phí analyzer;
  tránh kết luận bằng một công cụ/heuristic duy nhất.

## Điểm tương thích LLVM19 quan trọng

Upstream Kagura nói flags `-mllvm -kagura-*` với
`clang -fpass-plugin` **cần LLVM 22**; LLVM 17–21 nhận flags trước khi
load plugin, sinh lỗi unknown option. Vì DuoDash đang ở LLVM19, workflow
dùng **`opt --load-pass-plugin ... -passes=...` trên .bc**. Hướng
này là thật sự chạy các LLVM IR passes, không thêm cờ giả vào OLLVM.

Không thể suy ra từ việc Kagura *liệt kê iOS* rằng toàn bộ pass của nó
ổn định với Apple Clang, roothide, arm64e PAC hay iOS 15. Chỉ nhận
kết quả khi CI và bài thử thật tương ứng PASS.

## Tiêu chí nghiệm thu tối thiểu trước khi nói “custom MAX”

1. Kagura tại SHA pin **biên dịch LLVM19 thành công**; từng pass
   chạy thực và có dấu vết IR/object tương ứng, không chỉ plugin load.
2. Native 8.192 vector baseline/protected **giống nhau**, có tests âm tính
   khi output lệch/marker lộ/ABI sai; kiểm tra `-O1`/Release.
3. iOS arm64 binary hợp lệ, test chạy thực trên iPhone bằng app
   lab riêng; `arm64e` build/audit-only cho tới khi có A12+.
4. So sánh latency p50/p95, allocation, code size, startup và kết quả
   decompilation; nếu quá chậm hoặc crash => rollback.
5. Chỉ sau đó mới tính chuyện tích hợp pass đã kiểm chứng vào
   **custom plugin** riêng (với chính sách license, nguồn và version pin).
   Không sao chép binary proprietary của SLLVM hoặc ép load cùng lúc
   Hikari/Kagura/OLLVM nếu chưa test được ordering/incompatibility.

Mốc hiện tại: **K0 và K1 Kagura LLVM19 đều có artifact CI thực đã kiểm tra**;
K2a cách ly TU và benchmark native **đã có artifact macOS thật được kiểm chứng** (7 pass có native parity, median BBS 82 ns/call = 5,467× baseline); **người dùng đã báo KaguraLab iPhone PASS nhưng chưa có log đối chiếu; chưa có strict per-function allowlist hoặc bằng chứng MAX production**. Crane OLLVM STRONG
hiện hành **không bị sửa**.
