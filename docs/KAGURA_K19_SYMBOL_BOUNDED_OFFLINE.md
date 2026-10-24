# K19 — offline LC_SYMTAB / nlist symbol-address-bounded Mach-O canary

Ngày triển khai: **24/10/2026**. Trạng thái:
**STAGED_MANUAL_REAL_SYMTAB_OFFLINE_NOT_MACOS_VERIFIED**.

## K18 đã bỏ qua theo yêu cầu người dùng

K18 Swift CryptoKit có mã và kiểm thử portable nhưng **chưa có CI
macOS Swift executable/IPA hoặc log thiết bị được chứng thực**.
Theo yêu cầu "bỏ qua K18, mặc định pass, triển khai tiếp",
**K18 được ghi là `SKIPPED_BY_USER_NO_MACOS_OR_DEVICE_VERIFICATION`**,
không được ghi `PASS` giả, không được dùng làm nguồn bằng chứng.
Các file K18 được bảo tồn để có thể xét sau; K19 không gọi K18
workflow, không đòi bất kỳ khóa `K18_*` nào.

## Mục tiêu độc lập từ K16/K13/K14

K16 đã kiểm tra các byte `__TEXT,__text` của ba executable
thật được tạo bằng macOS CI, nhưng chỉ ở phạm vi toàn section.
K19 phân tích bảng symbol Darwin `LC_SYMTAB`, các bản ghi
`nlist_64` và địa chỉ section **sau linker**:

- macOS baseline K13: external `_dd_k8_evaluate`.
- macOS CSEBreak K13: external `_dd_k8_evaluate`.
- iOS K14 standalone CSEBreak lab: external
  `_dd_k8_evaluate` và `_dd_k14_ios_parity`.

Chỉ nhận Mach-O thin arm64 subtype0 `MH_EXECUTE` và dùng
parser `scripts/custom_ollvm/kagura_k16/macho_measure.py`
đã có làm kiểm tra `LC_UUID`, offset/size SHA-256 của
`__TEXT,__text`. Parse thật segment/section list theo thứ tự
toàn Mach-O để lấy đúng `n_sect` ordinal; parse đúng
`LC_SYMTAB` + mảng `nlist_64` + Darwin string table.
Yêu cầu symbol là external `N_SECT` thực và có địa chỉ
nằm trong section code; chặn thiếu/trùng/alias bất thường,
tràn range, overlap table, nlist sai/không căn hàng.

Phép băm **theo khoảng địa chỉ**:

1. Tìm địa chỉ máy của symbol mục tiêu từ `n_value`.
2. Tính ranh giới **địa chỉ cao hơn gần nhất** của symbol bất kỳ
   cùng `__TEXT,__text`, hoặc điểm cuối section nếu không còn.
3. Map ranh giới `[start,end)` từ vmaddr qua section file offset,
   đảm bảo offset/sizes hợp lệ và 4-byte-aligned cho ARM64.
4. Tính SHA-256 các file byte đã link; lưu nlist section ordinal,
   symbol vmaddr, ranh giới địa chỉ tiếp theo, file offset,
   length, hash và `n_desc` vào JSON để replay.
5. Bắt buộc `k16.replay` trước khi đo K19. Đòi SHA whole-file/
   __text và UUID của cả ba specimen phải trùng K16 manifest.
   Hai phiên bản macOS baseline/CSEBreak phải có hash vùng
   `_dd_k8_evaluate` khác nhau. Replay dữ liệu file gốc
   không dựa vào JSON `PASS`.

**Quan trọng:** đây là *symbol-address interval*, không chứng minh
function size thật. Nó **có thể bao gồm padding, stub hoặc code
hàm khác**; symbol có thể bị strip, đổi tên, optimizer inline/ICF,
hoặc không còn ranh giới symbol thích hợp. Không có unique
basic-block IDs, no-runtime-self-verifier, không cung cấp
anti-tamper/chống reverse trên thiết bị.

## Workflow manual / artifact

Workflow:
`.github/workflows/kagura-k19-symbol-bounded.yml`

Tên: `Kagura K19 - Symbol-Bounded Mach-O Research Without K18 (Experimental)`

- macOS-14; LLVM19 pinned Kagura commit
  `ac2136ee0408677cf7cdee55307e9b16edd5f4d5`,
  registry SHA
  `6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa`.
- Test portable K19/K16/K15/K14/K13 + OLLVM matrix/audit.
- Chạy lại K13 `pilot.py` và `audit.py` cho 4096-vector
  native parity, K14 unsigned IPA build thật, K16 section SHA
  và exact manifest replay. **Không dùng K18**.
- Chạy
  `scripts/custom_ollvm/kagura_k19/symbol_ranges.py --out <folder>`
  và lệnh `--verify`. Xuất
  `Kagura-K19-SYMBOL-RANGES.json`.
- Artifact:
  `DuoDash-Kagura-K19-SYMBOL-BOUNDED-MACHO-OFFLINE-EXPERIMENTAL`,
  luôn upload cả log lỗi nếu CI fail.

Portable tests
`scripts/test_kagura_k19_symbol_ranges.py` dùng Mach-O fake **chỉ
để kiểm parser** và negative corruption, không phải bằng chứng
macOS thật. Chưa có artifact K19 real CI, chưa xác minh được nlist
trên thiết bị.

## Giới hạn bắt buộc

Không có chữ ký mới, trust anchor, on-device runtime execution,
replay code trong memory, attestation, `arm64e`/PAC hoặc thay đổi
Crane production. **K15 BBCheck runtime vẫn là weak stub luôn trả
`1`** và không được tích hợp. K17 chữ ký Ed25519 TEST hợp lệ
ở mức tính toán nhưng private TEST đã lộ trong chat, không có
secure signer identity; K19 không gọi hay phụ thuộc bước K18.
