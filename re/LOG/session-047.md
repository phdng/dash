# LOG/session-047.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: D684 single-function (bounded — lấp UNKNOWN có chủ). Git HEAD 90a8527 clean (re/), không artifact mới._

## Làm gì
1. Start protocol: đọc STATE + git log/status + đo evidence (ddz3_commit 61 / inventory 44 / cpuigen 25 dòng) + re-read ddz_inventory FULL. Scope decision: FastRelayout.m (D684 §4; DDz classes để dành).
2. Viết `RECONSTRUCTION/FastRelayout.m` — bodies: no-DDz-callees đính chính, fast (rect-compare + luôn-update-meta + same?re-arm:push+50ms), slow (tombstone-attach vs F150-drop + 2 họ entity + FB9C 14 reasons + ok-persist/foreground), trigger 3 đường, side-effects + no-DDZ-state, kiến trúc-HYPOTHESIS.
3. Cập nhật TODO (R-034 done, R-035 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới từ decompile (synthesis) → không FINDINGS mới.
- E7F4/ECB8/EE4C/ED5C/F150/F3E0/FC10/FF98/12D068 + rect-passing-chi-tiết giữ UNKNOWN.
- Lấp D684-UNKNOWN ở SpawnLaunch/SpawnMisc/9D64-U05 (ghi cross-ref trong file).
- Status APPROXIMATION. Không VERIFIED.

## File thay đổi
- Mới: RECONSTRUCTION/FastRelayout.m, LOG/session-047.md.
- Sửa: TODO (R-034), STATE.

## Chưa làm
- R-035 (DDz classes? P4 rows? COVERAGE touch-up? scope khác?); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session synthesis).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: FastRelayout.m wiring (static CONSISTENT với evidence, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ (UNVERIFIED).
- NEXT EXACT STEP (session-048): R-035 — chọn 1 trong: DDz1-shell/DDz2-hosting class synthesis (inventory §§1-3,5: central methods + cross-links + division — vừa), DDz3 UI-cluster map (§6 — lớn), P4 SIDE_EFFECTS/COMPARISON rows cho synthesis bodies (meta), COVERAGE touch-up (042-047: EventLaunch/PollFlush/SpawnMisc/Evict/DDzCommit/FastRelayout + spawn-row-042/043/044 — nhỏ), hoặc scope khác (quyết đầu session).
- FILES TO READ NEXT: tùy scope (ddz_inventory đã có).
- EVIDENCE NEEDED: đã đủ; 4C34 FULL infeasible + P0-3 blocked giữ nguyên.
