# COMPARISON.md — Original-vs-reconstruction matrix (starter session-012, function 2410C)
_Trạng thái: UNKNOWN / INFERRED / IMPLEMENTED / VERIFIED / MISMATCH. Mục tiêu: UNKNOWN=0 (hoặc không observe được), MISMATCH=0._
_Chưa có gì VERIFIED (không runtime test). Reconstruction code bodies chưa viết (mới pseudocode Tweak.x) → Status tối đa INFERRED._

## 2410C (sub_2410C) — INFERRED overall
| Feature | Original (evidence) | Reconstruction (2410C.md) | Difference | Evidence | Status |
|---|---|---|---|---|---|
| Entry guards (stale + refused/host route) | :201-204, no-else silent drop | B01/B02 reproduced | none known | async_host_2410C.md §1.1 | INFERRED |
| Refused license map | A4450 codes → 4 verdict strings + no_internet gate | B03 reproduced | byte_165110 semantics INFERRED | §1.2 | INFERRED |
| Refused notice flow + file persist | discard/prepare/9B360/showServerNotice branches + mkdir/write/chmod | B04/B05 reproduced | verbatim format string chưa chép nguyên văn | §1.2 | INFERRED |
| Host snapshot + dismiss + prepare + geometry | :381-426 order | CALL TRACE 01-07 | none known | §1.3 | INFERRED |
| Answer parse → globals (clamps/defaults) | :427-492 exact | GLOBAL WRITES list | overflow intent HYPOTHESIS | §1.3 | INFERRED |
| Bids build + overflow rule | :493-591 pad v138, thừa gom-bỏ | B07 reproduced | intent HYPOTHESIS | §1.3 | INFERRED |
| CPUI filter + symmetric-diff | :592-705 | B08 reproduced | loop indices HYPOTHESIS (U02) | §1.3 | INFERRED |
| Evict-delay (resolve/kill/tombstone/schedule) | :756-834 exact calls | B10-B12 reproduced | 85B8/7764C bodies closed (F-036) | §1.4 | INFERRED |
| 2565C present-commit + ack + onHosted | 2565C:37-145 | B13/B14 (tóm tắt; record riêng session sau) | bodies chưa tách record | §1.6/§2 | INFERRED |
| a3 codes 0-4 meaning | off_146A18 table (chưa đọc) | U01 UNKNOWN | OPEN | — | UNKNOWN |
| Timing (100ms/20retries/stop/cancel) | 25EDC/25FE0/25C4C | TIMING section | first-attempt inclusivity UNKNOWN (U04) | §1.4 + files khác | INFERRED |
| Nil/empty (a2 null, bids rỗng, onHosted nil) | branches observed | NIL/EMPTY section | onHosted-nil exact lines UNKNOWN (U05) | §1.6 | INFERRED |
| Reentrancy/stale semantics | guards 3 lớp | REENTRANCY/STALE-GUARD | queue serial?/tombstone overwrite INFERRED (U06/U08) | §1.1 + 25FE0 | INFERRED |

## Coverage (functions)
| Function | Record | Status |
|---|---|---|
| 2410C | RECONSTRUCTION/functions/2410C.md | INFERRED |
| 2565C | RECONSTRUCTION/functions/2565C.md | INFERRED |
| Mọi function khác | chưa record | UNKNOWN |

## 2565C (sub_2565C) — INFERRED overall (session-013, đọc FULL trực tiếp)
| Feature | Original (evidence) | Reconstruction (2565C.md) | Difference | Evidence | Status |
|---|---|---|---|---|---|
| spike/show gate + success/fail route | :45-51 exact | B01 reproduced | none known | 2565C.c:45-51 | INFERRED |
| Natives loop + persist + splash | :53-81 exact | B02/B03 reproduced | loop luôn 3 lần (padding/cắt) INFERRED | 2565C.c:53-81 | INFERRED |
| Fail teardown + 52338/746C | :85-108 exact | B05/B06 reproduced | v13 uninit? UNKNOWN (U01) | 2565C.c:85-108 | INFERRED |
| cpui fetch + 9424 dict + ack | :110-128 + 9424.c:45-102 exact | B07/B08 + TRACE 11a-11f | none known | 2565C.c, 9424.c | INFERRED |
| onHosted 3-layer gate | :132-140 exact | B10 reproduced | nil-skip INFERRED | 2565C.c:132-140 | INFERRED |
| Timing/reentrancy/stale | sync body, no lock, no guard | TIMING/REENTRANCY | v3-nil edge UNKNOWN (U02) | — | INFERRED |
