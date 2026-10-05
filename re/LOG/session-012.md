# LOG/session-012.md
_Date: 2026-10-05. Objective mới: 1:1 behavioral reconstruction (function records, không chấp nhận flow summaries). Git HEAD 36f88be clean, không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/TODO/OPEN_QUESTIONS + git log/status. Xác định session budget: ONE function — 2410C (giá trị cao nhất, evidence sâu nhất: 878 dòng/3 passes).
2. Đọc lại EVIDENCE/async_host_2410C.md (nguồn duy nhất, không re-read decompile).
3. Viết `RECONSTRUCTION/functions/2410C.md` — full FUNCTION contract: ROLE/CALLERS/CALLEES/THREAD-QUEUE/INPUTS/OUTPUT/GLOBAL+OBJECT READS-WRITES/14 branches B01-B14/CALL TRACE 27 bước/SIDE-EFFECTS/ASYNC/TIMING/FAILURE/REENTRANCY/STALE-GUARD/NIL-EMPTY/STATE MACHINE + TRANSITION TABLE 12 dòng/U01-U08/CONFIDENCE/EVIDENCE. Sửa 2 lỗi edit (khôi phục body B-16/B-17, header UNKNOWN).
4. Viết `RECONSTRUCTION/SIDE_EFFECTS.md` (SE-2410C-001..009) + `RECONSTRUCTION/COMPARISON.md` (2410C rows, max INFERRED — chưa có gì VERIFIED).
5. Cập nhật TODO (section R), STATE, checkpoint + commit.

## Evidence / quyết định
- Mọi claim trong record gắn line hoặc ghi INFERRED/HYPOTHESIS/UNKNOWN; không flow-summary thay reconstruction.
- 2565C tách record riêng session sau (hiện tóm tắt B13 trong 2410C.md).
- Không tuyên bố VERIFIED nếu chưa test/compare (rule OBSERVATION≠IMPLEMENTATION).

## File thay đổi
- Mới: RECONSTRUCTION/functions/2410C.md, RECONSTRUCTION/SIDE_EFFECTS.md, RECONSTRUCTION/COMPARISON.md, LOG/session-012.md.
- Sửa: TODO (section R), STATE.

## Chưa làm
- R-003 record 2565C; R-004 records tiếp theo; Tweak.x bodies từ records; dynamic verify.

## HANDOFF (REQUIRED — session sau resume từ đây, không chỉ từ phase)
- CURRENT FUNCTION: sub_2565C (0x2565C) — present-commit + IPC + onHosted (hiện tóm tắt ở 2410C.md B13).
- CURRENT OFFSET: 2565C.c:37 (spikeHostSlots call) — chưa tách branches.
- CURRENT BRANCH: chưa bắt đầu (cần lập B-branches từ EVIDENCE/async_host_2410C.md §2).
- LAST VERIFIED BEHAVIOR: 2410C contract đầy đủ trừ U01-U08 (static OBSERVED, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ 2410C (UNVERIFIED — chưa test/compare với original).
- NEXT EXACT STEP: đọc EVIDENCE/async_host_2410C.md §2 + decompile/2565C.c FULL → viết RECONSTRUCTION/functions/2565C.md theo contract (branches B01… + args spikeHostSlots/9424/onHosted + success/fail paths).
- FILES TO READ NEXT: `Library/.../decompile/2565C.c` (146 dòng), `9424.c` (dict build :45-102), `EVIDENCE/async_host_2410C.md` §2.
- EVIDENCE NEEDED: exact lines 2565C.c:37-145 (đã có tóm tắt, cần re-read để tách args từng call: spikeHostSlots bids/natives/carPlayUI/skipEvict values, showLayoutPanes args, 9424 7 args, onHosted call condition).
