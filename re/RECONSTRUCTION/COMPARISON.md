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
| 218D8 | RECONSTRUCTION/functions/218D8.md | INFERRED |
| 202D0 | RECONSTRUCTION/functions/202D0.md | INFERRED |
| 74C8 | RECONSTRUCTION/functions/74C8.md | INFERRED |
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

## 218D8 (hostSlots:skipEvict:onHosted:) — INFERRED overall (session-014, đọc FULL trực tiếp)
| Feature | Original (evidence) | Reconstruction (218D8.md) | Difference | Evidence | Status |
|---|---|---|---|---|---|
| Slot-count/layout match gate | :183-201 (double 73E8 call) | B01 reproduced | second-call discard INFERRED side-effect-free | 218D8.c:183-201 | INFERRED |
| Dirty loop + flags + CPUI loop | :202-296 exact | B02/B03 reproduced | 3DD4C/flag-bits semantics UNKNOWN (U01/U02) | 218D8.c:202-296 | INFERRED |
| 7-way decision | :306-313 exact | B04 reproduced | none known | 218D8.c:306-313 | INFERRED |
| Full-host geometry + errors | :314-352 exact | B05/B06 reproduced | B06 fallthrough INFERRED (U04) | 218D8.c:314-352 | INFERRED |
| Reset + 7 knob files | :359-550 exact clamps | reset + B07-B10 reproduced | &stru_20+18 value UNKNOWN (U03) | 218D8.c:359-550 | INFERRED |
| Geometry log gate + async | :552-600 exact | B11 reproduced | consts/ABAEC INFERRED | 218D8.c:552-600 | INFERRED |
| Gen + block + dispatch | :601-653 exact captures | reproduced | none known | 218D8.c:601-653 | INFERRED |
| Reshow loop + ack | :656-710 exact | B12/B13 reproduced | CPUI-skip INFERRED intent | 218D8.c:656-710 | INFERRED |
| Exception handler | adb14/adb44 import, no body | U06 UNKNOWN | OPEN | — | UNKNOWN |

## 202D0 (onHostRequestSplit:) — INFERRED overall (session-015, đọc FULL trực tiếp)
| Feature | Original (evidence) | Reconstruction (202D0.md) | Difference | Evidence | Status |
|---|---|---|---|---|---|
| Debounce decrement (no in-body check) | :87-88 exact | B01 reproduced | consumer UNKNOWN | 202D0.c:87-88 | INFERRED |
| userInfo double-read + frame cache | :89-104 exact | INPUTS + SE-202D0-002 | field mapping U02 | 202D0.c:89-104 | INFERRED |
| Bids/bools parse (nil→empty/false) | :105-140 exact | INPUTS reproduced | layout absent CONFIRMED | 202D0.c:105-140 | INFERRED |
| Hosted fallback (empty→pair) | :143-177 exact | B03 reproduced | none known | 202D0.c:143-177 | INFERRED |
| Activate + gen++ | :179, :188 | B04 reproduced | none known | 202D0.c:179-188 | INFERRED |
| envOnly short-circuit + in-place args | :189-196 exact | B05 reproduced | intent INFERRED | 202D0.c:189-196 | INFERRED |
| Reapdelay read/trim/clamp | :198-224 exact (0,60] | B06 reproduced | none known | 202D0.c:198-224 | INFERRED |
| hostSlots call + captures | :225-238 exact block layout | B07 reproduced | 279F4 body cross-ref | 202D0.c:225-238 | INFERRED |
| Delayed verify dispatch | :239-246 exact (v60s, main) | B07 reproduced | 27AC8 body cross-ref | 202D0.c:239-246 | INFERRED |
| Deactivate (dismiss-cond/hide/log/teardown) | :257-264 exact | B08 reproduced | 76224 arg UNKNOWN (U04) | 202D0.c:257-264 | INFERRED |

## 74C8 (sub_74C8) — INFERRED overall (session-016, đọc FULL trực tiếp)
| Feature | Original (evidence) | Reconstruction (74C8.md) | Difference | Evidence | Status |
|---|---|---|---|---|---|
| Clearpanes one-shot + 9-key wipe | :100-204 exact | B01-B03 reproduced | đính chính 8→9 keys (F-041) | 74C8.c:100-204 | INFERRED |
| Sync + 7EA4/8058 calls (args) | :207-209 exact | reproduced + U03 | arg use UNKNOWN | 74C8.c:207-209 | INFERRED |
| Bridged filter (keep lỏng) | :210-271 exact | B04 reproduced | đính chính hypothesis đảo (F-041) | 74C8.c:210-271 | INFERRED |
| Autostart raw + 85CDC no-arg | :272-279 exact | B05 + U02 | x0-carryover HYPOTHESIS | 74C8.c:272-279 | INFERRED |
| Bulk nil-skip + 7E908 + 14 keys | :280-381 exact | B06 + build reproduced | keys content HYPOTHESIS (U04) | 74C8.c:280-381 | INFERRED |
| Derives enabled/nav (&&exists) | :331-337, :407-414 exact | B07/B09 + truth tables | edge U05 | 74C8.c | INFERRED |
| Plist write + cf-check + post | :416-419 exact | reproduced + U-new (cf indet.) | cf safety UNKNOWN | 74C8.c:416-419 | INFERRED |
