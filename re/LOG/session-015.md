# LOG/session-015.md
_Date: 2026-10-05. Objective: function-level reconstruction, session budget 1 function (202D0). Git HEAD e468754 clean, không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/LOG-014 + git log/status. Resume từ HANDOFF LOG-014 (R-004b record 202D0).
2. Đọc trực tiếp FULL `decompile/202D0.c` (272 dòng, 1 pass) — không subagent (tôi đọc).
3. Viết `RECONSTRUCTION/functions/202D0.md` — full contract: ROLE/CALLERS (NSDistributed, header none)/CALLEES/THREAD-QUEUE/INPUTS (double-read userInfo, keys exact, layout-absent)/OUTPUT/GLOBAL READS-WRITES/OBJECT READS/8 branches B01-B08/CALL TRACE 2 routes/SIDE-EFFECTS/ASYNC (1 dispatch_after)/TIMING/FAILURE/REENTRANCY/STALE-GUARD (không có)/NIL-EMPTY/U01-U06/CONFIDENCE/EVIDENCE.
4. SIDE_EFFECTS.md +9 (SE-202D0-001..009); COMPARISON.md +202D0 section + coverage; TODO (R-004b1 done, R-004b2 pending); STATE; commit.

## Evidence / quyết định
- Mọi arg từng call ghi exact (switchCarPlayUIInPlace gen, hostSlots bids/skipEvict/block, 27AC8 block layout, dismiss/hide/log/teardown).
- Phát hiện: B01 decrement không check tiếp trong body (consumer UNKNOWN); `layout` vắng mặt CONFIRMED ở body; block flags khác nhau 2 blocks (không diễn giải).
- Không tuyên bố VERIFIED. Status tối đa INFERRED.

## File thay đổi
- Mới: RECONSTRUCTION/functions/202D0.md, LOG/session-015.md.
- Sửa: SIDE_EFFECTS.md (+9), COMPARISON.md (+202D0), TODO (R-004b1), STATE.

## Chưa làm
- R-004b2 records (74C8/9D64); Tweak.x bodies từ records; dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: sub_74C8 (0x74C8) — central prefs resolver/publisher (14 keys + post resolved).
- CURRENT OFFSET: 74C8.c:100 (clearpanes phase) — EVIDENCE/prefs_split_autostart.md §1 đã có full breakdown; cần tách branches + args.
- CURRENT BRANCH: chưa bắt đầu.
- LAST VERIFIED BEHAVIOR: 202D0 contract (static OBSERVED, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ 202D0 + 218D8 + 2565C + 2410C (UNVERIFIED).
- NEXT EXACT STEP: đọc EVIDENCE/prefs_split_autostart.md §1 + decompile/74C8.c (430 dòng, 2 passes) → viết RECONSTRUCTION/functions/74C8.md theo contract.
- FILES TO READ NEXT: `Library/.../decompile/74C8.c`, `EVIDENCE/prefs_split_autostart.md` §1.
- EVIDENCE NEEDED: exact lines clearpanes :100-206, sync :207-209, bridged filter :210-279, bulk :280-330, publish :331-419 (đã có tóm tắt + lines, cần re-read để tách operands).
