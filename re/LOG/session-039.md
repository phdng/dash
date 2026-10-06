# LOG/session-039.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: teardown/evict cluster (spawn_teardown §A chia nhỏ — chỉ 6 funcs). Git HEAD 83bc408 clean (re/), không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/LOG-038 + git log/status. Scope decision: SpawnTeardown.m (bounded — D154/CE5C/B9A8/BBF8/BCDC/BD18; launch-route 8 funcs + KB §B + poll §C để dành R-027+).
2. Re-read spawn_teardown_kb.md FULL + grep D154/CE5C/B9A8 cross-refs (9D64 record/COMPARISON/SIDE_EFFECTS/KeyinputRelay) rồi viết `RECONSTRUCTION/SpawnTeardown.m` — bodies: D154 (background-scene + 15s schedules + detach + tombstone-gated), CE5C (snapshot-copy teardown-all), B9A8 (2 nhánh abort + grace delayed-evict HYPOTHESIS), BBF8 (gen-conditional evict), BCDC (idempotent cancel), BD18 (guards + register + bump), ack-why strings wiring-note.
3. Cập nhật TODO (R-026 done, R-027 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới từ decompile (synthesis) → không FINDINGS mới.
- v5/v28, 13AB8/EEF0/13F90/14040/1404C/F150/10188/127B4/15A94/15CBC/15DA4/159FC, CE5C-arg, BD18-gen-value giữ UNKNOWN.
- 9D64 call-graph/ack cross-ref record hiện có; KB §B cross-ref KeyinputRelay.m (không duplicate).
- Status APPROXIMATION. Không VERIFIED.

## File thay đổi
- Mới: RECONSTRUCTION/SpawnTeardown.m, LOG/session-039.md.
- Sửa: TODO (R-026), STATE.

## Chưa làm
- R-027 (launch-route? scope khác?); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session synthesis).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: SpawnTeardown.m wiring (static CONSISTENT với evidence, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ (UNVERIFIED).
- NEXT EXACT STEP (session-040): R-027 — spawn launch-route (C37C/BFF4/D01C/D4C4 + BE34/C2A4/CB08 + BEE4/B768/B144) HOẶC poll/UI-flush §C (365D4/371AC/370F8, nhỏ) HOẶC COVERAGE.md refresh (stale rows: CrashReporting/Migration/Respring/163EC — nhỏ, meta) HOẶC scope khác (quyết đầu session).
- FILES TO READ NEXT: tùy scope.
- EVIDENCE NEEDED: đã đủ cho mọi options trên; không cần re-read decompile.
