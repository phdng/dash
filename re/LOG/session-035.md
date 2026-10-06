# LOG/session-035.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: Migration synthesis (COVERAGE P2 GAP). Git HEAD 58c896e clean (re/), không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/LOG-034 + git log/status. Scope decision: Migration.m (bounded, evidence đủ — F-019/F-020 + 4C34_import_defaults.md).
2. Đọc F-019/F-020 + EVIDENCE §§1-7 rồi viết `RECONSTRUCTION/Migration.m` — bodies: guards import.done/running, pre-check, prefs wipe-then-migrate (rename/denylist/off_154268 UNKNOWN), license branch cross-ref License.m, airplay/iconstate/navapps merge + flags + log format exact, defaults bootstrap (seed-false-only + done formats), TrueDash one-way HYPOTHESIS.
3. Cập nhật TODO (R-022 done, R-023 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới từ decompile (synthesis) → không FINDINGS mới.
- rename map/denylist/off_154268/off_154238 nội dung UNKNOWN giữ nguyên.
- License branch không duplicate (cross-ref License.m §DDMigrateLicense).
- Status APPROXIMATION. Không VERIFIED.

## File thay đổi
- Mới: RECONSTRUCTION/Migration.m, LOG/session-035.md.
- Sửa: TODO (R-022), STATE.

## Chưa làm
- R-023 (spikeHostSlots/hostSplit/spawn-teardown records? Respring/latch synthesis?); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session synthesis).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: Migration.m wiring (static CONSISTENT với evidence, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ (UNVERIFIED).
- NEXT EXACT STEP (session-036): R-023 — hoặc spikeHostSlots records (từ EVIDENCE/spike_hostslots.md + hosting_engine.md + spawn_teardown_kb.md) hoặc Respring/latch synthesis (F-023, gộp vào CarSleeper.m hoặc riêng).
- FILES TO READ NEXT: tùy scope (EVIDENCE hiện có đủ cho cả hai).
- EVIDENCE NEEDED: đã đủ; không cần re-read decompile cho 2 options này.
