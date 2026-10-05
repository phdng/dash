# LOG/session-022.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: (A) Tweak.x present/commit/ack bodies (synthesis, bounded) thay vì (B) record 4C34. Git HEAD d5cbb16 clean, không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/LOG-021 + git log/status. Scope decision: (A) — synthesis từ 10 records hiện có, không đọc decompile mới (trừ cross-check trí nhớ records).
2. Viết `RECONSTRUCTION/PresentCommitAck.m` — bodies present/commit/ack: 202D0 parse/dispatch → 218D8 decision → 2410C execute (refused/host/evict-delay/direct) → 2565C commit (spike/show/persist/ack/callback) → 9424 dict. Mỗi nhánh ghi nguồn record; UNKNOWN giữ nguyên (U-refs); semantics queue/retain/silent-drop giữ.
3. Cập nhật TODO (R-009 done, R-010 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới từ decompile (pure synthesis) → không FINDINGS/BEHAVIOR mới; chỉ RECONSTRUCTION + TODO + STATE + LOG.
- Mọi arg nontrivial dẫn về record tương ứng (không duplicate detail vào .m).
- Status APPROXIMATION (synthesis, chưa compile, chưa runtime). Không VERIFIED.

## File thay đổi
- Mới: RECONSTRUCTION/PresentCommitAck.m, LOG/session-022.md.
- Sửa: TODO (R-009), STATE.

## Chưa làm
- R-010 records (4C34/163EC...) hoặc mở rộng bodies (keyinput/prefs/license); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session synthesis, không function mới).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: PresentCommitAck.m wiring (static CONSISTENT với 10 records, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ (UNVERIFIED).
- NEXT EXACT STEP (session-023): R-010 — hoặc record 4C34 mega-ctor (passes offset 1/350/700/1050/1300 theo phases F-003) hoặc mở rộng bodies (keyinput relay từ EVIDENCE/keyinput_relay.md).
- FILES TO READ NEXT: tùy scope đã chọn.
- EVIDENCE NEEDED: đã đủ trong records cho scope synthesis; scope records cần re-read decompile tương ứng.
