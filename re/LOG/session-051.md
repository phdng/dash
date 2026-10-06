# LOG/session-051.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: COVERAGE touch-up 042-045 (nhỏ, due). Git HEAD 8dd7f0c clean (re/), không artifact mới._

## Làm gì
1. Start protocol: đọc STATE + git log/status + grep COVERAGE rows (xác nhận stale: spawn row thiếu 042-044, Evict row EVIDENCE-only, P2-#6 partial). Scope decision: touch-up 3 điểm (P4 audit để dành — cần định cỡ riêng).
2. Sửa COVERAGE: spawn row (+EventLaunch/PollFlush/SpawnMisc/FastRelayout, còn §B KB), Evict row (→ Evict.m SYNTH s045), priority #6 (→ DONE, còn §B KB giá trị thấp).
3. TODO (R-038 done, R-039 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới (audit-only) → không FINDINGS mới.
- Mọi row sửa verify bằng files hiện có. Status giữ nguyên. Không VERIFIED.

## File thay đổi
- Mới: LOG/session-051.md.
- Sửa: COVERAGE (3 điểm), TODO (R-038), STATE.

## Chưa làm
- R-039 (P4 rows audit? §B KB? scope khác?); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session audit).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: COVERAGE spawn/Evict/#6 rows khớp files hiện có.
- LAST UNVERIFIED BEHAVIOR: toàn bộ (UNVERIFIED).
- NEXT EXACT STEP (session-052): R-039 — chọn 1 trong: P4 audit (đọc SIDE_EFFECTS.md + COMPARISON.md heads/tails + đếm rows/files — định cỡ trước khi viết), §B KB observers synthesis (spawn_teardown §B: onKbShow/Hide stubs + onDismiss/449C8 + onEndEditing + onApply-bonus — vừa, KeyinputRelay cross-refs), hoặc scope khác (quyết đầu session).
- FILES TO READ NEXT: tùy scope.
- EVIDENCE NEEDED: đã đủ; 4C34 FULL infeasible + P0-3 blocked giữ nguyên.
