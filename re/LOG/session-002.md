# LOG/session-002.md
_Date: 2026-10-05. Tiếp tục từ STATE session-001, không có artifact mới, không git._

## Làm gì
1. Start protocol: đọc STATE/TODO/FINDINGS/HYPOTHESES/ARCHITECTURE/OPEN_QUESTIONS/HOOKS/BEHAVIOR + check filesystem (re/ đủ 12 files).
2. Quick wins tự làm: grep missing actions (0 hit decompile → lần ra CN* classes trong strings/function_index); đọc 4DEB4/4001C/AC5FC/AC738/AC7A4/4049C/44C0/4760/4A08/7F010/842EC/9460C/9DE28/9E014(120-460)/4C34(1260-1300); FAT Mach-O parse bằng `python` (slice0 init_offsets={44C0,7F010,842EC,9460C}); block invoke table từ memory dump (role→ctor); pointers cross-ref (146AB8→AC7A4, 12DCE8→4D0B8, 12DB98 đã resolve).
3. 2 subagents song song: (A) full 27E20+163EC → init order/toggle+notify tables/behavioral models A–R, xác nhận 10 SB hook-fn UNKNOWN có căn cứ; (B) full 455D0+4CBDC+license chain+9DE28/9E014+notify sweep (12 dispatch + 68 Darwin) → 43-hook table, AZ loop resolve, ECDSA codes, endpoint negative, crash semantics.

## Evidence / quyết định
- Đóng H-001/H-002/H-004/H-006/H-007 (CONFIRMED hoặc negative); bác H-005 (BKS không phải IOMFB); Q-06/Q-08 đóng.
- P0-3 chuyển BLOCKED ON ARTIFACTS (F-018): cần raw asm 27E20, export thiếu.
- Thêm F-011..F-018, B-01b/B-08/B-09, HOOKS §0/AZ/BKS/controllers, RECONSTRUCTION/DuoDashShared.h (APPROXIMATION).

## File thay đổi
- Sửa: FINDINGS/HYPOTHESES/HOOKS/BEHAVIOR/TODO. Mới: RECONSTRUCTION/DuoDashShared.h, LOG/session-002.md (STATE.md cập nhật sau cùng).

## Chưa làm
- P1-3 (4C34 TrueDash import/defaults chi tiết), merge notify sweep vào API_MAP, ObjC method bodies (CNAB/DDz/CNLicense*), P2 behavioral models còn lại (P2-1..4), dynamic verify.

## Tiếp theo
- P1-3 + API_MAP merge + P2-1 (prefs resolver model) + EVIDENCE/ trích dẫn; rồi mới mở rộng RECONSTRUCTION bodies.
