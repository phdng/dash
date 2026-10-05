# LOG/session-021.md
_Date: 2026-10-05. Objective: function-level reconstruction, session budget 1 function (44C0). Git HEAD ade197c clean, không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/LOG-020 + git log/status. Scope decision đầu session: R-008 record 44C0 (124 dòng, đóng chuỗi init records dispatcher→ctors).
2. Đọc trực tiếp FULL `decompile/44C0.c` (124 dòng, 1 pass) — không subagent (tôi đọc).
3. Viết `RECONSTRUCTION/functions/44C0.md` — full contract: ROLE/CALLERS (dyld, header none)/CALLEES/THREAD-QUEUE/INPUTS (AC5FC + mainBundle)/OUTPUT/GLOBAL (không có)/OBJECT (không có)/7 branches B01-B07/CALL TRACE 10 bước/SIDE-EFFECTS/ASYNC (2 sites)/TIMING/FAILURE/REENTRANCY/STALE-GUARD (không có)/NIL-EMPTY/U01-U05/CONFIDENCE/EVIDENCE.
4. Phát hiện + sửa F-042 errata: `off_12CCC0` là EXCLUSION (match→return, mismatch→dispatch) — đảo shorthand cũ trong HOOKS.md:4 + FINDINGS F-011 (đã sửa cả hai).
5. SIDE_EFFECTS.md +1 (SE-44C0-001); COMPARISON.md +44C0 section + coverage; TODO (R-008 done, R-009 pending); STATE; commit.

## Evidence / quyết định
- Trace tay loop 5 iters để chốt inversion (match→return luôn vì v14∈{0..3}<4).
- QOS 17 = UTILITY (INFERRED decode 0x11); bid-nil→probably-dispatch (INFERRED); v0==0 unreachable (INFERRED).
- Không tuyên bố VERIFIED. Status tối đa INFERRED.

## File thay đổi
- Mới: RECONSTRUCTION/functions/44C0.md, LOG/session-021.md.
- Sửa: HOOKS.md (F-042), FINDINGS.md (F-011 + F-042), SIDE_EFFECTS.md (+1), COMPARISON.md (+44C0), TODO (R-008), STATE.

## Chưa làm
- R-009 (Tweak.x bodies hoặc records 4C34/163EC...); dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: chưa chọn — R-009 quyết scope đầu session-022: (A) Tweak.x present/commit/ack bodies từ 7+3 records, hoặc (B) record 4C34 mega-ctor (1465 dòng, cần chia 3-4 passes theo phases F-003/F-019).
- CURRENT OFFSET/BRANCH: N/A (chưa bắt đầu).
- LAST VERIFIED BEHAVIOR: 44C0 contract (static OBSERVED, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ 44C0 + 9 records trước (UNVERIFIED).
- NEXT EXACT STEP: quyết scope (A) vs (B) rồi thực hiện; nếu (B): đọc decompile/4C34.c passes offset 1/350/700/1050/1300.
- FILES TO READ NEXT: tùy scope: `RECONSTRUCTION/functions/*.md` (7 records) cho (A); `Library/.../decompile/4C34.c` cho (B).
- EVIDENCE NEEDED: (A) cross-record consistency (gen/ack/IPC/prefs flows đã có trong từng record); (B) EVIDENCE/4C34_import_defaults.md đã có breakdown import/defaults/sleeper.
