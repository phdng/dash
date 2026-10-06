# LOG/session-041.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: COVERAGE.md refresh (meta, stale sau 8 sessions). Git HEAD d280dcd clean (re/), không artifact mới._

## Làm gì
1. Start protocol: đọc COVERAGE FULL + ls RECONSTRUCTION/ + git log/status. Scope decision: refresh audit (không synthesis mới; C37C/poll để dành R-029).
2. Verify từng stale row bằng grep/ls (163EC record + SE-163EC-001..006 + COMPARISON §163EC tồn tại; SpikeHosting/HostSplit/SpawnTeardown/SpawnLaunch/Migration/CrashReporting/Respring .m tồn tại) rồi sửa 10 điểm: header, 163EC row, spike/hostSplit/spawn rows (spawn = partial, liệt kê còn lại), Migration row, CrashReporting + Respring rows, SIDE_EFFECTS/COMPARISON counts 10→11, priorities (1/3/4/5 DONE, 6 partial).
3. Cập nhật TODO (R-028 done, R-029 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới (audit-only) → không FINDINGS mới.
- Mọi row sửa đều verify bằng file hiện có (không đoán).
- Status các file giữ nguyên (APPROXIMATION/INFERRED). Không VERIFIED.

## File thay đổi
- Mới: LOG/session-041.md.
- Sửa: RECONSTRUCTION/COVERAGE.md (R-028), TODO (R-028), STATE.

## Chưa làm
- R-029 (C37C? BEE4/B768/B144 + poll §C? scope khác?); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session audit).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: COVERAGE rows khớp files hiện có (ls + grep verified).
- LAST UNVERIFIED BEHAVIOR: toàn bộ reconstruction (UNVERIFIED).
- NEXT EXACT STEP (session-042): R-029 — event-launch C37C (heavy, riêng 1 file EventLaunch.m?) HOẶC BEE4/B768/B144 + poll §C (365D4/371AC/370F8, nhỏ — HudBle/DataRouter cross-refs) HOẶC scope khác (quyết đầu session).
- FILES TO READ NEXT: tùy scope (EVIDENCE/spawn_teardown_kb.md §A item 9 + §C đã có).
- EVIDENCE NEEDED: đã đủ; không cần re-read decompile.
