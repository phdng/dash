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
| 163EC | RECONSTRUCTION/functions/163EC.md | INFERRED |
| 202D0 | RECONSTRUCTION/functions/202D0.md | INFERRED |
| 74C8 | RECONSTRUCTION/functions/74C8.md | INFERRED |
| 9D64 | RECONSTRUCTION/functions/9D64.md | INFERRED |
| 1FB5C | RECONSTRUCTION/functions/1FB5C.md | INFERRED |
| 20010 | RECONSTRUCTION/functions/20010.md | INFERRED |
| 27E20 | RECONSTRUCTION/functions/27E20.md | INFERRED |
| 44C0 | RECONSTRUCTION/functions/44C0.md | INFERRED |
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

## 9D64 (onHostState:) — INFERRED overall (session-017, đọc FULL trực tiếp)
| Feature | Original (evidence) | Reconstruction (9D64.md) | Difference | Evidence | Status |
|---|---|---|---|---|---|
| Refused gate + rollback 11 stores | :198-205, :744-774 exact | B00/B15 reproduced | :762 anomaly UNKNOWN (U02) | 9D64.c | INFERRED |
| Header sbPid/activated/bid | :206-222 exact | B02 reproduced | none known | 9D64.c:206-222 | INFERRED |
| Activated-else + bid-checks + split-notify | :223-246 exact | B01/B02/B03 reproduced | none known | 9D64.c:223-246 | INFERRED |
| cpuiKilled filter + store | :247-349 exact predicates | B04 reproduced (LABEL_20) | none known | 9D64.c:247-349 | INFERRED |
| Activated/cpuiBid gate + B9A8 | :350-356 exact | B05 reproduced | v126/v127 alias INFERRED (U01) | 9D64.c:350-356 | INFERRED |
| Base-rect fast/already/evict/store | :357-490 exact | B06-B10 reproduced | CB08 elided args UNKNOWN (U03) | 9D64.c:357-490 | INFERRED |
| cpuiMore 2-pass classify | :492-638 exact | B11 reproduced | CE5C-arg UNKNOWN (U04) | 9D64.c:492-638 | INFERRED |
| GC + spawn + epilogue | :640-735 exact | B12-B14 reproduced | D4C4 rect-passing UNKNOWN (U05) | 9D64.c:640-735 | INFERRED |

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

## 1FB5C (onHostRequest:) — INFERRED overall (session-018, đọc FULL trực tiếp)
| Feature | Original (evidence) | Reconstruction (1FB5C.md) | Difference | Evidence | Status |
|---|---|---|---|---|---|
| Parse + gen++ + singletons | :65-87 exact | reproduced | 27670 mapping U01 | 1FB5C.c:65-87 | INFERRED |
| Deactivate hide + ack-zero | :89-92 → :166-178 exact | B01/B10 reproduced | hide-fail UNKNOWN | 1FB5C.c | INFERRED |
| Spike + ack(result) | :94-112 exact | B02 reproduced | return semantics U07 | 1FB5C.c:94-112 | INFERRED |
| Fast re-present gate + chain | :113-148 exact | B03/B04 reproduced | renderSize-double U05 | 1FB5C.c:113-148 | INFERRED |
| Dismiss/prepare/hostBundle/show | :151-194 exact | B05-B08 reproduced | bid-rỗng path U06 | 1FB5C.c:151-194 | INFERRED |
| 89D8 6-args + acks gen-0 | :133, :98-192 exact | reproduced | 89D8 semantics U04 | 1FB5C.c | INFERRED |
| LABEL_22 + 7B6D8 argless | :195-206 exact | B09 reproduced | built-array unused U03 | 1FB5C.c:195-206 | INFERRED |

## 20010 (onCarPlayUIStatus:) — INFERRED overall (session-019, đọc FULL trực tiếp)
| Feature | Original (evidence) | Reconstruction (20010.md) | Difference | Evidence | Status |
|---|---|---|---|---|---|
| 4 userInfo reads + bid gate | :33-51 exact | B01 reproduced | why dead-read U03 | 20010.c:33-51 | INFERRED |
| Async handoff (main-or-async) | :53-68 exact | B02 reproduced | 37924 body cross-ref U02 | 20010.c:53-68 | INFERRED |
| Stale-check + dedup + prune | :69-85 exact | B03-B05 reproduced | set names U05 | 20010.c:69-85 | INFERRED |

## 27E20 (host ctor) — INFERRED overall (session-020, đọc FULL trực tiếp)
| Feature | Original (evidence) | Reconstruction (27E20.md) | Difference | Evidence | Status |
|---|---|---|---|---|---|
| Preamble + tmp migrator (cap/bounds/copy) | :107-196 exact | B01-B06 reproduced | v10/v11 indet. (U01); modes U05 | 27E20.c:107-196 | INFERRED |
| 76224 call + onces + dashboard obs. | :198-225 exact | reproduced | 76224 body cross-ref U02 | 27E20.c:198-225 | INFERRED |
| Dashboard retire (2 keys + Sync) | :226-248 exact | B08 reproduced | 290F4 cross-ref | 27E20.c:226-248 | INFERRED |
| Master/latch gate + host hooks | :249-280 exact | B09/B10 reproduced | 4049C args U04 (F-018) | 27E20.c:249-280 | INFERRED |
| Display once + observers alloc | :281-311 exact | B11 reproduced | none known | 27E20.c:281-311 | INFERRED |
| Darwin ×8 + NavData + purge | :312-387 exact | B12/B13 reproduced | none known | 27E20.c:312-387 | INFERRED |
| Keyinput once + purge/reset/post | :388-451 exact | B14 reproduced | none known | 27E20.c:388-451 | INFERRED |
| Config-repair + republish | :452-709 exact | B15 reproduced | formats verbatim kept | 27E20.c:452-709 | INFERRED |

## 44C0 (role dispatcher) — INFERRED overall (session-021, đọc FULL trực tiếp)
| Feature | Original (evidence) | Reconstruction (44C0.md) | Difference | Evidence | Status |
|---|---|---|---|---|---|
| Role-switch + dispatches | :29-123 exact | B01-B03/B06/B07 reproduced | default v0==0 INFERRED unreachable | 44C0.c:29-123 | INFERRED |
| Role5 bundle-gate + Siri-exclusion | :39-67, :93-97 exact literals | B03/B04 reproduced | none known | 44C0.c:39-67 | INFERRED |
| Blocklist scan (exclusion!) | :68-91 exact (trace 5 iters) | B05 reproduced | contents UNKNOWN (U01); F-042 errata | 44C0.c:68-91 | INFERRED |
| 4760 sync + pool balance + QOS | :41/:76/:85/:89/:96/:112/:34/:116 exact | reproduced | QOS INFERRED; balance INFERRED | 44C0.c | INFERRED |

## 163EC (CarPlay ctor) — INFERRED overall (session-033, đọc FULL trực tiếp)
| Feature | Original (evidence) | Reconstruction (163EC.md) | Difference | Evidence | Status |
|---|---|---|---|---|---|
| Master gate + observer + sendEvent | :123-144 exact | B01/B02 reproduced | thread INFERRED | 163EC.c:123-144 | INFERRED |
| Darwin ×3 + notifyd ×2 + 17410 | :145-180 exact | B03/B04 reproduced | block bodies U (Q-12) | 163EC.c:145-180 | INFERRED |
| Elig gate + 8 hooks + probe | :181-298 exact | B05-B07 reproduced | magic/nil/class U01-U03 | 163EC.c:181-298 | INFERRED |
| Chain + 5s + 191A4 | :299-308 exact | B08/B09 reproduced | chain semantics U04 | 163EC.c:299-308 | INFERRED |
| One-shot files + holds | :309-501 exact | B10 reproduced | holdsec blocks U06 | 163EC.c:309-501 | INFERRED |
| cproleup + cpuicaps gate | :502-528 exact | B11 reproduced | F3E0 U07 | 163EC.c:502-528 | INFERRED |

## CrashReporting (synthesis bodies) — INFERRED overall (session-055, synthesis từ evidence)
| Feature | Original (evidence) | Reconstruction (CrashReporting.m) | Difference | Evidence | Status |
|---|---|---|---|---|---|
| Trigger + spinlock | 80C04 → async 9DFD4; busy → Already sending | DDCrashReportSend reproduced | spinlock type/op exact UNKNOWN | notify_matrix 7F14C:136-142 | INFERRED |
| Guards collecting/cr_off | collecting → Disabled-last-crashed; cr_off → disabled | DDCrashMayCollect reproduced | collecting lifecycle INFERRED | B-08/F-016 | INFERRED |
| Collect + queue cap | 9EE88 bundle+meta; giữ ≤3 | DDCollectCrashReport reproduced | meta schema + subdir layout UNKNOWN | B-08/F-016 | INFERRED |
| Endpoint nil-default | 9DE28 NSString-only else nil | DDCrashEndpoint reproduced | — | F-016 9DE28:18-35 | INFERRED |
| Upload + semaphore + dryrun | POST 60s + headers + sem 300s; dryrun local-only | DDUploadCrashReport reproduced | progress/timer/cleanup UNKNOWN | F-016 9E014:228+ | INFERRED |

## Respring/latch (synthesis bodies) — INFERRED overall (session-055, synthesis từ evidence)
| Feature | Original (evidence) | Reconstruction (Respring.m) | Difference | Evidence | Status |
|---|---|---|---|---|---|
| latch.reset wipe+post | reenable-guard → wipe + Idle + post request | DDOnLatchReset reproduced | glob list + flag target UNKNOWN | F-023 80574 | INFERRED |
| respring.request pipeline | norespring → throttle → carsleep → 9C790 → ack + 21.6s execute | DDOnRespringRequest reproduced | last-path/branch/exec-mapping UNKNOWN | F-023 8097C + toggles | INFERRED |
| respring.ack flag | 96D60 set 164B4E=1 | DDOnRespringAck reproduced | — | notify_matrix 96D2C:14-20 | INFERRED |

## PollFlush (synthesis bodies) — INFERRED overall (session-056, synthesis từ evidence)
| Feature | Original (evidence) | Reconstruction (PollFlush.m) | Difference | Evidence | Status |
|---|---|---|---|---|---|
| Poll tick + transitions | 22AD0 atomics + disconnect/connect + labels + flushes + re-arm 3s | DDPollTick reproduced | label strings + 163C40 UNKNOWN | spawn_teardown §C / cnab §5 | INFERRED |
| Display probe + persist | 365D4 FBSDisplay + clamp + persist-đổi-mới-post | DDProbeDisplay reproduced | 34250 body UNKNOWN | 365D4.c:9 | INFERRED |
| Flushes overdue/nudge | 371AC vô điều kiện; 370F8 guards + knob | DDFlushOverdue/DDFlushNudgeTick reproduced | nudge-posts UNKNOWN | 371AC/370F8.c:9 | INFERRED |

## CNABConn (synthesis bodies) — INFERRED overall (session-056, synthesis từ evidence)
| Feature | Original (evidence) | Reconstruction (CNABConn.m) | Difference | Evidence | Status |
|---|---|---|---|---|---|
| Fabric + registration | 887C add vs 8D78 post; đăng ký 2 phía | header reproduced | entitlement UNKNOWN | cnab_observers §0 | INFERRED |
| ConnChanged/ScreenDisconnect | bool-gate → log/disconnect; !connected → disconnect | DDOnCarPlayConnChanged/DDOnScreenDisconnect reproduced | 229FC reason UNKNOWN | 229FC/22A8C.c:9 | INFERRED |
| Disconnect teardown | active-gated dismiss/invalidate/state/posts | DDDoCarPlayDisconnect reproduced | 371F4/146308 UNKNOWN | 227E4.c:9 | INFERRED |
| CarWindow registry | gates + size/pid dicts + pid-change clear + nudger | DDOnCarWindow reproduced | 1635C8/nudger-arithmetic UNKNOWN | 99D4.c:9 | INFERRED |

## SpikeHosting (synthesis bodies) — INFERRED overall (session-057, synthesis từ evidence)
| Feature | Original (evidence) | Reconstruction (SpikeHosting.m) | Difference | Evidence | Status |
|---|---|---|---|---|---|
| skipEvict single-use gate | 3CC44:311 duy nhất; =1 suppress, =0 +flag-vắng no-evict | DDSpikeHostSlots reproduced | evictFromPhone nội bộ UNKNOWN | F-035 3CC44 | INFERRED |
| Slots guard + error path | 0..3 (≥4 nil); nil → dismiss + cpdisconnect | loop reproduced | return-count-check HYPOTHESIS | F-035 3CC44 | INFERRED |
| Create/degrade 3 nhánh | CPUI tag-7020 / SB chain + 3 degrades / empty placeholder | DDSpikeCreateSlot/DDDegradeSlot reproduced | 36E98-success HYPOTHESIS | F-035 3BBF0/3C1F0 | INFERRED |
| Geometry pushes | delays off_154160 + captures gen/size/orient/bid | DDScheduleGeometryPushes reproduced | delays + 3DC38 UNKNOWN | F-035 3D4FC | INFERRED |

## HostSplit (synthesis bodies) — INFERRED overall (session-057, synthesis từ evidence)
| Feature | Original (evidence) | Reconstruction (HostSplit.m) | Difference | Evidence | Status |
|---|---|---|---|---|---|
| 2-pane wrapper | nil-coalesce + [L,R] + onHosted=nil | DDHostSplit reproduced | — | F-031 217EC | INFERRED |
| In-place guards + convert | guards→0; convert + rollback-nhưng-1 + async 100ms | DDSwitchCarPlayUIInPlace reproduced | return-semantics HYPOTHESIS | F-031 208F4 | INFERRED |
| Continuation | gates + 85B8 + slots + 9424 cpuiGen++ + log | DDInPlaceContinuation reproduced | evict-nghĩa HYPOTHESIS | F-031 26FE4 | INFERRED |
