# LOG/session-014.md
_Date: 2026-10-05. Objective: function-level reconstruction, session budget 1 function (218D8). Git HEAD 8fa6923 clean, không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/TODO + git log/status. Resume từ HANDOFF LOG-013 (R-004 record 218D8).
2. Đọc trực tiếp FULL `decompile/218D8.c` (717 dòng, 2 passes offset 1/361) — không subagent (tôi đọc).
3. Viết `RECONSTRUCTION/functions/218D8.md` — full contract: ROLE/CALLERS(202D0/217EC)/CALLEES/THREAD-QUEUE/INPUTS(a3/a4/a5 exact use)/OUTPUT/GLOBAL READS-WRITES (reset block + knob overrides + gen pair + 162E60++)/OBJECT READS/15 branches B01-B14/CALL TRACE 2 routes/SIDE-EFFECTS/ASYNC (2 fire-and-forget)/TIMING/FAILURE/REENTRANCY/STALE-GUARD (không có)/NIL-EMPTY/U01-U08/CONFIDENCE/EVIDENCE.
4. SIDE_EFFECTS.md +6 (SE-218D8-001..006); COMPARISON.md +218D8 section + coverage; TODO (R-004a done, R-004b pending); STATE; commit.

## Evidence / quyết định
- Mọi arg từng call ghi exact (3DD4C/22D64/22E40/89D8/9424/A8424/ABB7C...). Clamp bounds exact (40/13/1..8/a,b/1..99).
- Phát hiện mới: double-call 73E8 (1 dùng + 1 bỏ); B06 fallthrough INFERRED; v13 uninit? không — v13 luôn gán trước dùng (khác U01 2565C); &stru_20+18 UNKNOWN; @catch body UNKNOWN; sizes array không guard (U07).
- Không tuyên bố VERIFIED. Status tối đa INFERRED.

## File thay đổi
- Mới: RECONSTRUCTION/functions/218D8.md, LOG/session-014.md.
- Sửa: SIDE_EFFECTS.md (+6), COMPARISON.md (+218D8), TODO (R-004a), STATE.

## Chưa làm
- R-004b records (202D0/74C8/9D64); Tweak.x bodies từ records; dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: sub_202D0 (0x202D0) — onHostRequestSplit: (parse userInfo + envOnly short-circuit + reapdelay + hostSlots call + delayed verify).
- CURRENT OFFSET: 202D0.c:89 (userInfo double-read) — EVIDENCE/cnab_observers.md §2 đã có full breakdown; cần tách branches + args.
- CURRENT BRANCH: chưa bắt đầu.
- LAST VERIFIED BEHAVIOR: 218D8 contract (static OBSERVED, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ 218D8 + 2565C + 2410C (UNVERIFIED).
- NEXT EXACT STEP: đọc EVIDENCE/cnab_observers.md §2 + decompile/202D0.c (272 dòng, 1 pass) → viết RECONSTRUCTION/functions/202D0.md theo contract.
- FILES TO READ NEXT: `Library/.../decompile/202D0.c`, `EVIDENCE/cnab_observers.md` §2.
- EVIDENCE NEEDED: exact lines userInfo keys :89-140, activate branch :179-246, deactivate :257-264 (đã có tóm tắt + lines, cần re-read để tách operands).
