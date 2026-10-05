# LOG/session-013.md
_Date: 2026-10-05. Objective: function-level reconstruction, session budget 1 function (2565C). Git HEAD b6c2999 clean, không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/TODO + git log/status. Resume từ HANDOFF LOG-012 (R-003 record 2565C).
2. Đọc trực tiếp FULL `decompile/2565C.c` (146 dòng) + FULL `decompile/9424.c` (108 dòng) — không dùng subagent (file nhỏ).
3. Viết `RECONSTRUCTION/functions/2565C.md` — full contract: ROLE/CALLERS/CALLEES/THREAD-QUEUE/INPUTS (captures +32..+89, a2)/OUTPUT/GLOBAL READS-WRITES/OBJECT READS-WRITES/10 branches B01-B10/CALL TRACE 17 bước (+9424 11a-11f)/ASYNC (không có)/TIMING/FAILURE (incl. v13-uninit U01, v3-nil U02)/REENTRANCY/STALE-GUARD (không có)/NIL-EMPTY/U01-U07/CONFIDENCE/EVIDENCE.
4. SIDE_EFFECTS.md +5 (SE-2565C-001..005); COMPARISON.md +2565C section + coverage update; TODO (R-003 done); STATE; commit.

## Evidence / quyết định
- Mọi arg từng call ghi exact (spike 4 args + sources, showLayoutPanes 4 args, 9424 10 args + dict cond, onHosted block invoke).
- U01 (v13 uninit) là phát hiện mới đáng chú ý — cần verify assembly (có thể compiler nil-init).
- Không tuyên bố VERIFIED (rule). Status tối đa INFERRED.

## File thay đổi
- Mới: RECONSTRUCTION/functions/2565C.md, LOG/session-013.md.
- Sửa: SIDE_EFFECTS.md (+5), COMPARISON.md (+2565C), TODO (R-003), STATE.

## Chưa làm
- R-004 records (218D8/202D0/74C8/9D64); Tweak.x bodies từ records; dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: sub_218D8 (0x218D8) — hostSlots:skipEvict:onHosted: (dirty-check + full-host vs reshow).
- CURRENT OFFSET: 218D8.c:307 (quyết định reshow-vs-full-host) — EVIDENCE/hosting_engine.md đã có full breakdown; cần tách branches B01… + args từng call.
- CURRENT BRANCH: chưa bắt đầu.
- LAST VERIFIED BEHAVIOR: 2565C contract (static OBSERVED, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ 2565C + 2410C (UNVERIFIED).
- NEXT EXACT STEP: đọc EVIDENCE/hosting_engine.md §1 + decompile/218D8.c (717 dòng, 2 passes) → viết RECONSTRUCTION/functions/218D8.md theo contract.
- FILES TO READ NEXT: `Library/.../decompile/218D8.c`, `EVIDENCE/hosting_engine.md`.
- EVIDENCE NEEDED: exact lines dirty-check :178-313, full-host :314-654, reshow :656-710 (đã có tóm tắt + lines, cần re-read để tách operands từng condition).
