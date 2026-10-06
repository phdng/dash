# LOG/session-038.md
_Date: 2026-10-05. Objective: function-level reconstruction; scope decision đầu session: hostSplit/switchInPlace synthesis (COVERAGE P2 GAP #6 tiếp — chỉ 217EC/208F4). Git HEAD 46efb9c clean (re/), không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/LOG-037 + git log/status. Scope decision: HostSplit.m (bounded — hosting_engine §§2-3; 218D8 đã có record, 279F4/27AC8 đã cover ở PresentCommitAck/202D0, spawn/teardown 17 callees để dành R-026).
2. Re-read hosting_engine §§2-4 FULL + grep 217EC/208F4 cross-refs (202D0/218D8/2410C/PresentCommitAck) rồi viết `RECONSTRUCTION/HostSplit.m` — bodies: 217EC wrapper (nil-coalesce + [L,R] + onHosted=nil), 208F4 (guards từ chối → 0, phân loại slots, convert+rollback-nhưng-return-1, async qua 25EDC/25FE0 100ms), 26FE4 continuation (gates + 85B8 + setSlot/spike/replacePane/geometry + 9424 cpuiGen + 4D0F4).
3. Cập nhật TODO (R-025 done, R-026 pending); STATE; commit.

## Evidence / quyết định
- Không claim mới từ decompile (synthesis) → không FINDINGS mới.
- return-1-on-rollback, killed-set 2595C, resolve-display 77244, L/R/C index-order, re-host HYPOTHESIS giữ nguyên.
- envOnly-caller + onHosted-nil + layout-so-không-đọc cross-ref records hiện có.
- Status APPROXIMATION. Không VERIFIED.

## File thay đổi
- Mới: RECONSTRUCTION/HostSplit.m, LOG/session-038.md.
- Sửa: TODO (R-025), STATE.

## Chưa làm
- R-026 (spawn/teardown 17 callees? scope khác?); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: N/A (session synthesis).
- CURRENT OFFSET/BRANCH: N/A.
- LAST VERIFIED BEHAVIOR: HostSplit.m wiring (static CONSISTENT với evidence, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ (UNVERIFIED).
- NEXT EXACT STEP (session-039): R-026 — spawn/teardown callees (EVIDENCE/spawn_teardown_kb.md §A: 17 callees — lớn, cân nhắc chia nhỏ: launch-route C37C/BFF4/D01C/D4C4 vs teardown CE5C/D154/B9A8/BB98 vs waiter CB08/BCDC/BD18/C2A4/BEE4/BE34/B768/B144) HOẶC scope khác (quyết đầu session).
- FILES TO READ NEXT: tùy scope.
- EVIDENCE NEEDED: đã đủ cho spawn/teardown; không cần re-read decompile.
