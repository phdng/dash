# LOG/session-017.md
_Date: 2026-10-05. Objective: function-level reconstruction, session budget 1 function (9D64, lớn nhất 775 dòng). Git HEAD 8ad44ef clean, không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/TODO/LOG-016 + git log/status. Resume từ HANDOFF LOG-016 (R-004b3 record 9D64).
2. Đọc trực tiếp FULL `decompile/9D64.c` (775 dòng, 3 passes offset 1/261/521) — không subagent (tôi đọc).
3. Viết `RECONSTRUCTION/functions/9D64.md` — full contract: ROLE/CALLERS (NSDistributed, header none)/CALLEES/THREAD-QUEUE/INPUTS (~10 userInfo reads riêng lẻ)/OUTPUT/GLOBAL READS-WRITES/OBJECT (không có)/16 branches B00-B15/CALL TRACE 2 routes (refused 4 bước + normal 19 bước)/SIDE-EFFECTS/ASYNC (1 hop)/TIMING/FAILURE/REENTRANCY/STALE-GUARD (không có)/NIL-EMPTY (full-nil walk INFERRED)/U01-U08/CONFIDENCE/EVIDENCE.
4. SIDE_EFFECTS.md +5 (SE-9D64-001..005); COMPARISON.md +9D64 section + coverage; TODO (R-004b3 done, R-005 pending); STATE; commit.

## Evidence / quyết định
- Phát hiện mới: v126/v127 alias cùng stack slot (INFERRED cùng biến); `:762 162DF8=163DF0` anomaly (literal OBSERVED, intent UNKNOWN); CB08/CE5C/D4C4 elided-args (gọi hiện ít arg hơn signature — UNKNOWN).
- B06 v127-nil path, B01-else flow, full-nil walk đều INFERRED từ labels (không early-return ẩn thấy được).
- Không tuyên bố VERIFIED. Status tối đa INFERRED.

## File thay đổi
- Mới: RECONSTRUCTION/functions/9D64.md, LOG/session-017.md.
- Sửa: SIDE_EFFECTS.md (+5), COMPARISON.md (+9D64), TODO (R-004b3), STATE.

## Chưa làm
- R-005 records (1FB5C/20010/27E20...) hoặc Tweak.x bodies; dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: sub_1FB5C (0x1FB5C) — onHostRequest: (single-app host: hide/spike/fast-represent/full-host + ack) — ỨNG VIÊN; hoặc Tweak.x bodies (quyết scope).
- CURRENT OFFSET: 1FB5C.c:66 (userInfo read) — EVIDENCE/cnab_observers.md §1 đã có full breakdown; cần tách branches + args.
- CURRENT BRANCH: chưa bắt đầu.
- LAST VERIFIED BEHAVIOR: 9D64 contract (static OBSERVED, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ 9D64 + 5 records trước (UNVERIFIED).
- NEXT EXACT STEP (nếu chọn R-005 records): đọc EVIDENCE/cnab_observers.md §1 + decompile/1FB5C.c (214 dòng, 1 pass) → viết RECONSTRUCTION/functions/1FB5C.md.
- FILES TO READ NEXT: `Library/.../decompile/1FB5C.c`, `EVIDENCE/cnab_observers.md` §1.
- EVIDENCE NEEDED: exact lines branches :89-208, DDz calls, 9424 acks, LABEL_10/11/22 (đã có tóm tắt + lines trong evidence cũ).
