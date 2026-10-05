# LOG/session-020.md
_Date: 2026-10-05. Objective: function-level reconstruction, session budget 1 function (27E20, 711 dòng). Git HEAD 0f8e27d clean, không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/LOG-019 + git log/status. Scope decision đầu session: R-007 record 27E20 (host ctor lớn, đóng chuỗi init records).
2. Đọc trực tiếp FULL `decompile/27E20.c` (711 dòng, 3 passes offset 1/251/501) — không subagent (tôi đọc).
3. Viết `RECONSTRUCTION/functions/27E20.md` — full contract: ROLE/CALLERS (4C34 once, header none)/CALLEES/THREAD-QUEUE/INPUTS (a1 unused)/OUTPUT/GLOBAL READS-WRITES (counters + singletons)/OBJECT (allocs)/15 branches B01-B15/CALL TRACE 19 bước/SIDE-EFFECTS/ASYNC (không có)/TIMING/FAILURE/REENTRANCY (duplicate-observers phát hiện)/STALE-GUARD (không có)/NIL-EMPTY/U01-U08/CONFIDENCE/EVIDENCE.
4. SIDE_EFFECTS.md +6 (SE-27E20-001..006); COMPARISON.md +27E20 section + coverage; TODO (R-007 done, R-008 pending); STATE; commit.

## Evidence / quyết định
- Phát hiện mới: observers/singletons/migrator KHÔNG once-guarded (chỉ hooks/display/keyinput có once) → reentry duplicate INFERRED; v10/v11 indeterminate (lớp U01 2565C/cf 74C8); `layout`/`frame` keys vắng mặt CONFIRMED ở body (không phải handler notification).
- a1 unused; 76224(v1) arg semantics UNKNOWN; @catch body UNKNOWN.
- Không tuyên bố VERIFIED. Status tối đa INFERRED.

## File thay đổi
- Mới: RECONSTRUCTION/functions/27E20.md, LOG/session-020.md.
- Sửa: SIDE_EFFECTS.md (+6), COMPARISON.md (+27E20), TODO (R-007), STATE.

## Chưa làm
- R-008 records (44C0/4C34/163EC...) hoặc Tweak.x bodies; dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: sub_44C0 (0x44C0) — role dispatcher (suffix-switch + block dispatch) — ỨNG VIÊN; hoặc Tweak.x bodies (quyết scope).
- CURRENT OFFSET: 44C0.c:29 (role switch) — NHỎ (124 dòng, 1 pass), đã đọc trước đây (F-011/STATE) nhưng chưa tách branches.
- CURRENT BRANCH: chưa bắt đầu.
- LAST VERIFIED BEHAVIOR: 27E20 contract (static OBSERVED, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ 27E20 + 8 records trước (UNVERIFIED).
- NEXT EXACT STEP (nếu chọn records): đọc decompile/44C0.c (124 dòng, đã đọc ở session-002 — re-read nhanh) → viết RECONSTRUCTION/functions/44C0.md.
- FILES TO READ NEXT: `Library/.../decompile/44C0.c` (+ `AC5FC.c`/`AC738.c` đã đọc — cross-ref F-012).
- EVIDENCE NEEDED: exact operands role-switch :29-123, block table (đã có memory dump F-011), role5 bundle-list path :41-98.
