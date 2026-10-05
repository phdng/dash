# LOG/session-019.md
_Date: 2026-10-05. Objective: function-level reconstruction, session budget 1 function (20010, nhỏ nhất 91 dòng). Git HEAD 5869026 clean, không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/LOG-018 + git log/status. Scope decision đầu session: R-006 record 20010 (đóng cpuiGen consumer loop với 162E60).
2. Đọc trực tiếp FULL `decompile/20010.c` (91 dòng, 1 pass) — không subagent (tôi đọc).
3. Viết `RECONSTRUCTION/functions/20010.md` — full contract: ROLE/CALLERS (NSDistributed, header none)/CALLEES/THREAD-QUEUE/INPUTS (4 reads riêng lẻ + why dead-read)/OUTPUT/GLOBAL READS-WRITES (set reset)/OBJECT (không có)/5 branches B01-B05/CALL TRACE 9 bước/SIDE-EFFECTS/ASYNC (1 hop)/TIMING/FAILURE/REENTRANCY/STALE-GUARD (B03 chính là consumer)/NIL-EMPTY/U01-U06/CONFIDENCE/EVIDENCE.
4. SIDE_EFFECTS.md +3 (SE-20010-001..003); COMPARISON.md +20010 section + coverage; TODO (R-006 done, R-007 pending); STATE; commit.

## Evidence / quyết định
- Phát hiện: `cpuiWhy` đọc rồi release bỏ (dead-read) — không dùng trong body.
- Forward xảy ra TRƯỚC stale-check (check không chặn forward) — quan trọng cho equivalence.
- Bid invalid → skip toàn bộ (khác 1FB5C nil→"?" path).
- Không tuyên bố VERIFIED. Status tối đa INFERRED.

## File thay đổi
- Mới: RECONSTRUCTION/functions/20010.md, LOG/session-019.md.
- Sửa: SIDE_EFFECTS.md (+3), COMPARISON.md (+20010), TODO (R-006), STATE.

## Chưa làm
- R-007 records (27E20...) hoặc Tweak.x bodies; dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: sub_27E20 (0x27E20) — SpringBoard host ctor (toggle scanner + observers + config-repair) — ỨNG VIÊN; hoặc Tweak.x bodies (quyết scope).
- CURRENT OFFSET: 27E20.c:107 (toggle scanner?) — EVIDENCE (27E20 deep-read session-002, subagent) đã có breakdown; cần tách branches + args. NOTE: 27E20.c 711 dòng — lớn, cần 2-3 passes.
- CURRENT BRANCH: chưa bắt đầu.
- LAST VERIFIED BEHAVIOR: 20010 contract (static OBSERVED, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ 20010 + 7 records trước (UNVERIFIED).
- NEXT EXACT STEP (nếu chọn records): đọc decompile/27E20.c (711 dòng, passes offset 1/250/500) → viết RECONSTRUCTION/functions/27E20.md.
- FILES TO READ NEXT: `Library/.../decompile/27E20.c`, (EVIDENCE 27E20: rải trong LOG-002/subagent reports cũ — kiểm tra EVIDENCE/ có file 27E20 không; nếu không, đọc trực tiếp).
- EVIDENCE NEEDED: exact lines toggle scanner :107-197, suspended-killer, observers :201-459, config-repair :460-707 (lines từ subagent report session-002 — verify lại khi đọc).
