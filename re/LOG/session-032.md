# LOG/session-032.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: audit coverage (thay vì function/record mới). Git HEAD c16ccb8 clean, không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/LOG-031 + git log/status. Scope decision: audit coverage (bounded, định hướng sessions tới).
2. Đọc ARCHITECTURE.md component map + liệt kê RECONSTRUCTION/ (10 records + 10 .m/.h + ledger/matrix) rồi viết `RECONSTRUCTION/COVERAGE.md` — tables A-J (init/hosting/prefs/cloak-keyboard/siri/sleeper/license-crash/data-HUD/apps/IPC/meta) với artifact + status + ghi chú GAP, + priority lấp GAP 1-9.
3. Cập nhật TODO (R-019 done, R-020 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới từ decompile (audit, không synthesis mới) → không FINDINGS/BEHAVIOR mới.
- Phát hiện audit: KeyApp full breakdown có nguy cơ mất (chỉ F-007/F-008 essentials persisted) — ghi rõ, không re-derive.
- GAP lớn nhất còn làm được (không device): record 163EC, CrashReporting/Migration synthesis, spikeHostSlots records.
- Status: audit artifact (không APPROXIMATION mới).

## File thay đổi
- Mới: RECONSTRUCTION/COVERAGE.md, LOG/session-032.md.
- Sửa: TODO (R-019), STATE.

## Chưa làm
- R-020 (theo COVERAGE priority); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session audit).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: COVERAGE.md mapping (CONSISTENT với ARCHITECTURE + git tree, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ (UNVERIFIED).
- NEXT EXACT STEP (session-033): R-020 — khuyến nghị record 163EC (CarPlay ctor: elig/dock/scene install + guards; EVIDENCE từ session-002 subagent + HOOKS CarPlay section; file 163EC.c size kiểm tra khi đọc).
- FILES TO READ NEXT: `Library/.../decompile/163EC.c` (+ HOOKS.md CarPlay cloak section).
- EVIDENCE NEEDED: exact lines elig install :181-295, dock/focus/statusbar (18A7C cross-ref), guards DUODASH_AB_ELIG_HOOKED/DOCK_HOOKED.
