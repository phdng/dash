# LOG/session-043.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: poll/UI-flush §C (bounded, 4 funcs). Git HEAD 7617af6 clean (re/), không artifact mới._

## Làm gì
1. Start protocol: đọc STATE + git log/status + grep 22AD0/365D4 cross-refs (218D8 B11 + PresentCommitAck — cùng function 2 callers, không duplicate). Scope decision: PollFlush.m (BEE4/B768/B144 + CCEC/D684 để dành R-031).
2. Viết `RECONSTRUCTION/PollFlush.m` từ evidence §C — bodies: 22AD0 (connect/disconnect + labels + conditional main/async flushes + chốt + re-arm 3s), 365D4 (display probe + clamp + persist-đổi-mới-post + return h>0), 371AC (dropOverdueNotice vô điều kiện), 370F8 (guards visible/running/nonudgetick + nudgePresent tick).
3. Cập nhật TODO (R-030 done, R-031 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới từ decompile (synthesis) → không FINDINGS mới.
- Label strings exact, 163C40 nghĩa, 34250 body, nudgePresent-posts giữ UNKNOWN.
- 218D8:552 second-caller + ble-status consumer + cpconnect cross-ref hiện có.
- Status APPROXIMATION. Không VERIFIED.

## File thay đổi
- Mới: RECONSTRUCTION/PollFlush.m, LOG/session-043.md.
- Sửa: TODO (R-030), STATE.

## Chưa làm
- R-031 (BEE4/B768/B144 + CCEC/D684? scope khác?); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session synthesis).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: PollFlush.m wiring (static CONSISTENT với evidence, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ (UNVERIFIED).
- NEXT EXACT STEP (session-044): R-031 — BEE4/B768/B144 misc cluster (view-move predicate + active-bid + dock ticker) + CCEC/D684 notes HOẶC scope khác (quyết đầu session).
- FILES TO READ NEXT: EVIDENCE/spawn_teardown_kb.md §A items 1,6,11,17 (đã có).
- EVIDENCE NEEDED: đã đủ; không cần re-read decompile.
