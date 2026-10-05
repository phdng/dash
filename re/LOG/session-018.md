# LOG/session-018.md
_Date: 2026-10-05. Objective: function-level reconstruction, session budget 1 function (1FB5C). Git HEAD 8ad44ef clean, không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/LOG-017 + git log/status. Scope decision đầu session: R-005 record 1FB5C (214 dòng, cặp với 202D0 split; Tweak.x bodies lùi lại).
2. Đọc trực tiếp FULL `decompile/1FB5C.c` (214 dòng, 1 pass) — không subagent (tôi đọc).
3. Viết `RECONSTRUCTION/functions/1FB5C.md` — full contract: ROLE/CALLERS (NSDistributed, header none)/CALLEES/THREAD-QUEUE/INPUTS (userInfo 1 lần + keys exact, layout-absent)/OUTPUT/GLOBAL READS-WRITES (gen++ duy nhất)/OBJECT READS/11 branches B01-B11/CALL TRACE 14 bước/SIDE-EFFECTS/ASYNC (không có)/TIMING/FAILURE/REENTRANCY/STALE-GUARD (không có)/NIL-EMPTY (nil→"?" vs nil→empty)/U01-U07/CONFIDENCE/EVIDENCE.
4. SIDE_EFFECTS.md +5 (SE-1FB5C-001..005); COMPARISON.md +1FB5C section + coverage; TODO (R-005 done, R-006 pending); STATE; commit.

## Evidence / quyết định
- Mọi arg từng call ghi exact (9424 ×4 sites gen-0 ZeroRect, 89D8 6 args, 7B6D8 argless vs array built).
- Phát hiện: bid nil→"?" (KHÁC empty — hậu quả full-path với "?"); U03 argless-call lớp mới (cùng họ CB08/CE5C/D4C4); renderSize double-call; 9424 ở đây KHÔNG kèm 8D78 call-site (8D78 nằm trong 9424 body — cross-ref 2565C B08).
- Không tuyên bố VERIFIED. Status tối đa INFERRED.

## File thay đổi
- Mới: RECONSTRUCTION/functions/1FB5C.md, LOG/session-018.md.
- Sửa: SIDE_EFFECTS.md (+5), COMPARISON.md (+1FB5C), TODO (R-005), STATE.

## Chưa làm
- R-006 records (20010/27E20...) hoặc Tweak.x bodies; dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: sub_20010 (0x20010) — onCarPlayUIStatus: (stale-check + prune-once + async handoff) — ỨNG VIÊN; hoặc Tweak.x bodies (quyết scope).
- CURRENT OFFSET: 20010.c:35 (cpuiGen read) — EVIDENCE/cnab_observers.md §3 đã có full breakdown; cần tách branches + args.
- CURRENT BRANCH: chưa bắt đầu.
- LAST VERIFIED BEHAVIOR: 1FB5C contract (static OBSERVED, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ 1FB5C + 6 records trước (UNVERIFIED).
- NEXT EXACT STEP (nếu chọn records): đọc EVIDENCE/cnab_observers.md §3 + decompile/20010.c (91 dòng, 1 pass) → viết RECONSTRUCTION/functions/20010.md.
- FILES TO READ NEXT: `Library/.../decompile/20010.c`, `EVIDENCE/cnab_observers.md` §3.
- EVIDENCE NEEDED: exact lines guards :50-51, block :53-68, failure-tracking :69-85 (đã có tóm tắt + lines).
