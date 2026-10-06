# LOG/session-036.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: Respring/latch synthesis (COVERAGE P2 GAP #5). Git HEAD c9bc054 clean (re/), không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/LOG-035 + git log/status. Scope decision: Respring.m (bounded, evidence đủ — F-023/B-14 + notify/toggle rows; spikeHostSlots để dành R-024 vì lớn 3 evidence files).
2. Grep 9C790/respring_last/21.6s/ack-flag/toggles rồi viết `RECONSTRUCTION/Respring.m` — bodies: latch.reset 80574 (reenable-guard → wipe plists + flag=false + unlink collecting + Idle + post request), respring.request 8097C (norespring → throttle 8/60s + touch last → carsleep → 9C790 → post ack + after 21.6s + 811B0/81624 hoặc async 812F4/81304/81344), respring.ack 96D60 (164B4E=1), toggles (reenable/norespring×2/respring_soft/no_msrv_restart).
3. Cập nhật TODO (R-023 done, R-024 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới từ decompile (synthesis) → không FINDINGS mới.
- respring_last path exact, 9C790 điều kiện, 8/60s branch exact, 811B0/81624-vs-async mapping, wipe-glob list, flag=false target giữ UNKNOWN.
- Registrar không duplicate (cross-ref DataRouter.m); collecting-file cross-ref CrashReporting.m; carsleep cross-ref CarSleeper.m.
- Status APPROXIMATION. Không VERIFIED.

## File thay đổi
- Mới: RECONSTRUCTION/Respring.m, LOG/session-036.md.
- Sửa: TODO (R-023), STATE.

## Chưa làm
- R-024 (spikeHostSlots/hostSplit/spawn-teardown records? scope khác?); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session synthesis).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: Respring.m wiring (static CONSISTENT với evidence, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ (UNVERIFIED).
- NEXT EXACT STEP (session-037): R-024 — spikeHostSlots records (từ EVIDENCE/spike_hostslots.md + hosting_engine.md + spawn_teardown_kb.md) HOẶC scope khác (quyết đầu session; spike = 3 evidence files, cân nhắc chia nhỏ).
- FILES TO READ NEXT: tùy scope (EVIDENCE hiện có đủ cho spike options).
- EVIDENCE NEEDED: đã đủ; không cần re-read decompile cho spike options.
