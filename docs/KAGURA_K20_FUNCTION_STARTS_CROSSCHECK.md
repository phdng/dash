# K20 — đối chiếu LC_FUNCTION_STARTS với LC_SYMTAB sau linker

Ngày triển khai mã: **24/10/2026**. Trạng thái:
**STAGED_MANUAL_LC_FUNCTION_STARTS_K19_CROSSCHECK_NOT_MACOS_VERIFIED**.

## Cơ sở trực tiếp

K19 đã có ZIP GitHub Actions thực được kiểm chứng offline: 55 entry
CRC sạch, ba Mach-O arm64 và các khoảng symbol `_dd_k8_evaluate`,
`_dd_k14_ios_parity` đều khớp manifest K19 và raw byte SHA-256.
Tổng cộng **4 khoảng mã mục tiêu**: macOS baseline 460 byte,
macOS CSEBreak 544 byte, iOS parity 484 byte và iOS evaluate 544 byte.

K19 dùng `LC_SYMTAB`/`nlist_64` để chọn *địa chỉ bắt đầu* symbol
và *địa chỉ symbol cao hơn gần nhất* làm cận trên, **không cung cấp
function length chính xác**. Quan sát riêng từ artifact K19 thực cho
thấy các điểm bắt đầu và kết thúc của 4 khoảng này đều xuất hiện
trong `LC_FUNCTION_STARTS` (macOS baseline 3, macOS protected 3,
iOS 30 function starts).

## Nội dung K20

`scripts/custom_ollvm/kagura_k20/function_starts.py`:
1. Bắt buộc `k19.verify(out)`: điều này chạy lại `k16.replay(out)`
   và đối chiếu raw K13 native parity, K14 IPA, cả ba Mach-O executable,
   `LC_UUID`, vùng `__TEXT,__text` và symbol-range hash.
2. Parse chính xác một `LC_FUNCTION_STARTS` (`linkedit_data_command`,
   `cmdsize=16`), lấy `dataoff`/`datasize` giới hạn trong file.
3. Đọc stream **ULEB128 unsigned 64-bit**, offset cộng dồn tính từ
   `__TEXT` *segment* vmaddr. Chặn thiếu terminator 0, overlong,
   overflow, byte nonzero sau terminator, offset vượt `__TEXT`,
   không align ARM64 và duplicate/mất thứ tự. Các byte zero sau
   terminator cho phép như padding.
4. Bắt buộc `LC_SYMTAB` target symbol address là một trong các
   `LC_FUNCTION_STARTS`, và cận trên là **function start tiếp theo**
   có mặt trong stream. Đòi đúng SHA-256 các byte tương ứng với
   interval K19 qua offset/size Mach-O gốc, không dựa vào JSON PASS.
5. Xuất `Kagura-K20-FUNCTION-START-CROSSCHECK.json` chứa UUID,
   SHA whole executable, SHA text, SHA raw LC_FUNCTION_STARTS payload,
   số function starts, decoded offsets, 4 đối chiếu start/end/hash
   và tất cả cờ bảo mật **FALSE**. `--verify` tính lại từ file thật
   và so với report gốc.

**Giới hạn diễn giải quan trọng:** `LC_SYMTAB` và
`LC_FUNCTION_STARTS` là **hai biểu diễn metadata trong cùng
một executable**, không phải hai hệ thống tin cậy mật mã độc lập.
Ngay cả khi start/end trùng, không thể suy ra hàm có kích thước
chính xác, không chứng minh nhận dạng riêng từng basic block,
không có mã runtime tự kiểm tra, anti-tamper, hay iPhone attestation.

## Manual GitHub Actions

Workflow `.github/workflows/kagura-k20-function-starts.yml`:
**Kagura K20 - Function Starts vs Symbol Ranges Offline (Experimental)**.

- `macos-14`, LLVM19 Kagura commit
  `ac2136ee0408677cf7cdee55307e9b16edd5f4d5`, pin registry
  `6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa`.
- Rerun test K20/K19/K16/K15/K14/K13, audit OLLVM.
- Rebuild K13 macOS/native 4096 vectors và K14 IPA standalone,
  K16 manifest rồi K19 nlist symbol manifest.
- Run `function_starts.py --out "$K20_OUT"` rồi `--verify`.
- Upload artifact kể cả bước fail:
  `DuoDash-Kagura-K20-FUNCTION-STARTS-DUAL-SOURCE-OFFLINE-EXPERIMENTAL`.

**Không có dependency K18**, không cần K18 Ed25519 secret, không chạy
`kagura-bbcheck` K15 (weak always-return-1 stub), không thay
Crane production, arm64e/PAC, K11–K19 hay cài IPA mới.

## Trạng thái bằng chứng

- Test `scripts/test_kagura_k20_function_starts.py` tạo thin arm64
  synthetic Mach-O có `LC_FUNCTION_STARTS` byte thật cho portable
  positive/negative; các binary này **không phải native macOS evidence**.
- Bản K20 chỉ được phép chuyển sang *real macOS verified* sau khi
  kiểm tra ZIP CI thực, replay manifest, raw load commands,
  ULEB128 stream và 4 target interval. **Không tự nhận real CI PASS
  vì portable tests xanh**.
