# LOG/session-040.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: spawn-routing cluster (spawn_teardown §A chia nhỏ — 6 funcs, trừ C37C heavy). Git HEAD 2291a66 clean (re/), không artifact mới._

## Làm gì
1. Start protocol: đọc STATE + git log/status (LOG-039 content đã nắm từ handoff). Scope decision: SpawnLaunch.m (bounded — D4C4/D01C/BFF4/BE34/C2A4/CB08; C37C + BEE4/B768/B144 + poll §C để dành R-028).
2. Viết `RECONSTRUCTION/SpawnLaunch.m` từ evidence §A items 5,7,8,10,12,14 — bodies: D4C4 (fast-vs-waiter router), D01C (base-gate), BFF4 (confine/retry/timeout dispatcher + 986C acks), BE34 (predicate hướng-chứa), C2A4 (knob-gated killed-list), CB08 (waiter 50ms).
3. Cập nhật TODO (R-027 done, R-028 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới từ decompile (synthesis) → không FINDINGS mới.
- D684/13220/14C80/14CA0/14E74/14060/14080/15238/1423C/163560/1427C/E7C4/E7DC, rect-passing, 9D64:473 retry-count, base-tên giữ UNKNOWN.
- 9D64 call-sites cross-ref record hiện có; C37C/CB08-args-elided cross-ref U-notes.
- Status APPROXIMATION. Không VERIFIED.

## File thay đổi
- Mới: RECONSTRUCTION/SpawnLaunch.m, LOG/session-040.md.
- Sửa: TODO (R-027), STATE.

## Chưa làm
- R-028 (C37C + BEE4/B768/B144 + poll §C? scope khác?); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session synthesis).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: SpawnLaunch.m wiring (static CONSISTENT với evidence, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ (UNVERIFIED).
- NEXT EXACT STEP (session-041): R-028 — event-launch C37C (heavy 324 dòng, có thể riêng 1 file) HOẶC BEE4/B768/B144 + poll §C (365D4/371AC/370F8) HOẶC COVERAGE.md refresh (stale rows sau sessions 033-040) HOẶC scope khác (quyết đầu session).
- FILES TO READ NEXT: tùy scope.
- EVIDENCE NEEDED: đã đủ cho mọi options trên; không cần re-read decompile.
