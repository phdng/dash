# LOG/session-016.md
_Date: 2026-10-05. Objective: function-level reconstruction, session budget 1 function (74C8). Git HEAD b2ce62c clean, không artifact mới._

## Làm gì
1. Start protocol: đọc STATE/TODO/LOG-015 + git log/status. Resume từ HANDOFF LOG-015 (R-004b2 record 74C8).
2. Đọc trực tiếp FULL `decompile/74C8.c` (430 dòng, 2 passes offset 1/216) — không subagent (tôi đọc).
3. Viết `RECONSTRUCTION/functions/74C8.md` — full contract: ROLE/CALLERS(8)/CALLEES/THREAD-QUEUE/INPUTS (CF domain + files + call-args 7EA4/8058/85CDC)/OUTPUT/GLOBAL READS-WRITES/OBJECT (không có)/12 branches B01-B11/CALL TRACE 18 bước/SIDE-EFFECTS/ASYNC (không có)/TIMING/FAILURE/REENTRANCY/STALE-GUARD (không có)/NIL-EMPTY/U01-U06/CONFIDENCE/EVIDENCE.
4. SIDE_EFFECTS.md +3 (SE-74C8-001..003); COMPARISON.md +74C8 section + coverage; FINDINGS (+F-041 errata); TODO (R-004b2 done, R-004b3 pending); STATE; commit.
5. Sửa lỗi thứ tự FINDINGS: F-041 bị append nhầm giữa file (oldString trùng) → di chuyển về cuối. Phát hiện thêm: F-039/F-040 đứng trước F-037/F-038 (di sản các session cũ, cùng nguyên nhân) — GHI NHẬN, không sửa (tránh rủi ro corrupt; chỉ là thứ tự hiển thị).

## Evidence / quyết định
- Đính chính quan trọng (đọc exact lần này): wipe **9 keys** (not 8); filter giữ-lỏng (not đảo); call args hiện trong decompile dù callees argless; `cf` indeterminate (lớp U01 2565C).
- Truth tables B07/B09 ghi INFERRED (cần runtime để VERIFIED).
- Không tuyên bố VERIFIED. Status tối đa INFERRED.

## File thay đổi
- Mới: RECONSTRUCTION/functions/74C8.md, LOG/session-016.md.
- Sửa: SIDE_EFFECTS.md (+3), COMPARISON.md (+74C8), FINDINGS (+F-041, reorder), TODO (R-004b2), STATE.

## Chưa làm
- R-004b3 record 9D64 (775 dòng — lớn nhất; cần 3 passes); Tweak.x bodies từ records; dynamic verify.

## HANDOFF (REQUIRED)
- CURRENT FUNCTION: sub_9D64 (0x9D64) — onHostState: (refused-rollback + base-rect + cpuiMore + acks).
- CURRENT OFFSET: 9D64.c:198 (Branch 0 hostRefused) — EVIDENCE/cnab_observers.md §7 đã có full breakdown 3 chunks; cần tách branches + args.
- CURRENT BRANCH: chưa bắt đầu.
- LAST VERIFIED BEHAVIOR: 74C8 contract (static OBSERVED, chưa runtime).
- LAST UNVERIFIED BEHAVIOR: toàn bộ 74C8 + 202D0 + 218D8 + 2565C + 2410C (UNVERIFIED).
- NEXT EXACT STEP: đọc EVIDENCE/cnab_observers.md §7 + decompile/9D64.c (775 dòng, 3 passes offset 1/260/520) → viết RECONSTRUCTION/functions/9D64.md theo contract.
- FILES TO READ NEXT: `Library/.../decompile/9D64.c`, `EVIDENCE/cnab_observers.md` §7.
- EVIDENCE NEEDED: exact operands refused :744-774, header :205-246, LABEL_20 :248-355, base-rect :357-490, cpuiMore :492-734 (đã có tóm tắt + lines, cần re-read để tách).
