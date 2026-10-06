# LOG/session-029.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: (A8) Tweak.x keyboard-hook bodies (synthesis, bounded). Git HEAD ba704d0 clean, không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/LOG-028 + git log/status. Scope decision: (A8) — synthesis từ HOOKS.md hook table hiện có (không đọc decompile mới); 4C34 lùi lại (1465 dòng, phases đã cover).
2. Đọc HOOKS.md sections (UIApp table + swizzle + kbd PoC + AZ + BKS + controllers) rồi viết `RECONSTRUCTION/KeyboardHooks.m` — mapping ledger: ctor/guards, focus (cross-ref), orientation/geometry hooks (bodies UNKNOWN), keyboard-size hooks (bodies UNKNOWN, duodashkey-gated setters), didMoveToWindow/sendEvent/AVExternalDevice/NSBundle hooks, AZ cross-ref (F-017), swizzle cross-ref, PSTableCell mapping, BKS cross-ref.
3. Cập nhật TODO (R-016 done, R-017 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới từ decompile (pure synthesis) → không FINDINGS/BEHAVIOR mới.
- Phân biệt rõ mapping-CONFIRMED vs bodies-UNKNOWN (không nâng cấp nhãn).
- Focus/swizzle/AZ/BKS không duplicate (cross-ref files tương ứng).
- Status APPROXIMATION. Không VERIFIED.

## File thay đổi
- Mới: RECONSTRUCTION/KeyboardHooks.m, LOG/session-029.md.
- Sửa: TODO (R-016), STATE.

## Chưa làm
- R-017 (bodies DataRouter/nav/HUD-BLE hoặc records 4C34/163EC...); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session synthesis).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: KeyboardHooks.m wiring (static CONSISTENT với HOOKS.md, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ (UNVERIFIED).
- NEXT EXACT STEP (session-030): R-017 — hoặc Tweak.x bodies tiếp (DataRouter/nav từ F-022? HUD/BLE pairing từ F-024?) hoặc record 4C34 mega-ctor (passes offset 1/350/700/1050/1300 theo phases F-003).
- FILES TO READ NEXT: tùy scope đã chọn.
- EVIDENCE NEEDED: đã đủ trong records/EVIDENCE cho scope synthesis; scope records cần re-read decompile tương ứng.
