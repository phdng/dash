# COVERAGE.md — RECONSTRUCTION/ vs subsystems audit (session-032; refresh session-041)
_Mục đích: cho biết subsystem nào đã có synthesis/record, subsystem nào còn thiếu, để direct sessions tiếp theo._
_Trạng thái file: RECORD (function contract) / SYNTH (Tweak.x bodies) / EVIDENCE-only / MISSING._
_Không có gì VERIFIED (chưa runtime test) — coverage ở đây là static-artifact coverage._

## A. Init / entry / process gating
| Subsystem | Artifact | Status | Ghi chú |
|---|---|---|---|
| Role dispatcher 44C0 | functions/44C0.md | RECORD (INFERRED) | + F-042 blocklist errata |
| Role detect AC5FC/AC7A4 | — (EVIDENCE: F-011/F-012) | EVIDENCE-only | Chưa tách record (nhỏ, có thể gộp vào Tweak.x init) |
| Mega-ctor 4C34 | — (EVIDENCE: F-003/F-019/F-020/F-021 + 4C34_import_defaults.md) | EVIDENCE-only | 1465 dòng, phases đã cover; record riêng là R-item mở |
| Host ctor 27E20 | functions/27E20.md | RECORD (INFERRED) | + P0-3 blocked (4049C args) |
| CarPlay ctor 163EC | functions/163EC.md | RECORD (INFERRED) | session-033 FULL direct read (529 dòng, B01-B11) + SE-163EC-001..006 |
| UIApp/IPC/kbd/display ctors | ReconstructionRuntime.m + evidence | BUILDABLE PARTIAL | s075 promotes evidence-safe 4CBDC UIApp IPC/state half; key-probe callbacks, 4C858 keyboard hooks, 4DEB4 display hooks and other ctors remain evidence/private-hook scope |
| Tweak.x init section | Tweak.x + ReconstructionRuntime.m | BUILDABLE SYNTH (APPROXIMATION) | ctor thật + AC5FC-style role detect; SpringBoard safe runtime + UIApp IPC consumer active, other private-hook roles remain gated out |

## B. AppBridge hosting (split/layout/panes)
| Subsystem | Artifact | Status | Ghi chú |
|---|---|---|---|
| hostSlots decision 218D8 | functions/218D8.md | RECORD | + reshow/fast paths |
| Split request parse 202D0 | functions/202D0.md | RECORD | layout-absent CONFIRMED |
| Async execute 2410C | functions/2410C.md | RECORD (+state machine) | sâu nhất (878 dòng) |
| Present-commit 2565C | functions/2565C.md | RECORD | + 9424 dict exact |
| Single-app host 1FB5C | functions/1FB5C.md | RECORD | cặp với 202D0 |
| Hosting observers/consumers | PresentCommitAck.m (+ HostedCallbacks.m s067) | SYNTH | 202D0→218D8→2410C→2565C→9424/onHosted; onHosted-blocks 279F4/27AC8 tách riêng; KHÔNG rows riêng (record rows cover — audit s067) |
| spikeHostSlots: internals | SpikeHosting.m + ReconstructionRuntime.m (F-035) | SYNTH + BUILDABLE PARTIAL | s037 synthesis; s076 mirror/retries/CarPlay; s077 prep/parser+dismiss; s078 lscape+resize; s079 geometry/pane-orient; s080 aux candidate/mirror/desired settings; s081 exact aux retry/state-machine; s082 post-identity callback routing; s083 raw-ARM64-confirmed 41D80/41E94 size/orientation/settings decisions; s084 40C5C/40DA8 size + 40F0C equality rewrites; s085 40FF4 foreground + 41138 destroy decisions; s086 41730 yield-vs-swallow; s087 421CC flag clear + 41BA0 probe budget; s088 9C3BC/9C4AC type plans; s089 adds 9C2C4 diagnostic key/dedup plus raw-ARM64-confirmed 41F50 `{CGRect=` frame and exact c/B foreground mutation/failure-budget plans; s090 adds exact 3FA90 zero-fallback orientation read and 400D0 slot-mark→frame-width→orientation update-gate descriptor; s091 adds raw-ARM64-confirmed 3F5C0 admission/counter-class + method-signature plan and 3ECD0/3F990 q/Q setter/frame-orientation mutation descriptors; s092 adds raw-ARM64-confirmed 3F7C8 generation/reentrancy admission plus normal/exception slot-mark and counter outcome descriptors; s093 adds raw-ARM64-cross-checked 4138C any-slot(host incl. CarPlay)→aux update routing plus non-CarPlay foreground-false original-callback suppression/count decisions; s094 adds raw-ARM64-confirmed 3F3F0 post-resize attempt reset/general-counter floor and caller-supplied probeScene→landscape-adjusted private-update descriptor; s095 adds raw-ARM64-confirmed 40DA8 substitution-success dword_162F40 outcome and strict-positive/NaN-safe callback size rewrite; s096 adds Mach-O-LSDA-confirmed 40C5C/40DA8 route/native-size fallback catches plus original-callback exception bounded EA8/EB0 diagnostic outcomes; s097 adds Mach-O-LSDA-confirmed 40F0C route/orientation catch→original fallback, original-callback catch→41BA0 probe→forced-false-after-probe outcome, plus nested-probe unwind metadata; s098 adds Mach-O-LSDA/raw-ARM64-confirmed 40FF4 original-callback catch→41BA0 probe→resume post-original foreground evaluation, route/mutable-settings catch→swallow+skip remaining foreground forcing, plus nested-probe unwind metadata; s099 adds exact 41138 pre-original route/identity catch→saved-identity restore+original continuation, original-callback catch→41BA0 probe→prepared destroy-routing continuation, post-callback destroy-range propagate/unwind behavior, plus nested-probe unwind metadata; s100 adds exact 4138C initial-scene catch→original fallback, update-routing/private-executor catches→suppression continuation when scene survives (else original), suppression-decision catches→original fallback, original-callback catch→41BA0 probe+cleanup, plus nested-probe unwind metadata; s101 adds exact 41730 pre-yield/entity-enumeration/toggle catches→original fallback, dismiss→remaining side effects, cpdisconnect→original with stuck yield-in-progress metadata, hide→yield-log continuation, yield-log→cleanup/reset, cleanup-only→resume-unwind, and original-callback catch→41BA0 probe+cleanup; s102 adds exact 421CC private `_otherSettings`/`_setFlag:forSetting:` catch→swallow+skip remaining flag clear+normal cleanup with no reason probe; s103 adds exact 41F50 frame/foreground/private-update typed catches→swallow+skip remaining private mutation/control+skip failure-budget decrement+normal return, with no reason probe; s104 adds exact 400D0 pre-settings catch→original fallback, scene-settings catch→mutable-settings continuation, mutable-settings catch→post-settings routing continuation, later routing/frame/orientation/private-executor catches→original fallback, original-callback catch→41BA0 probe+cleanup, plus nested-probe unwind metadata; s105 adds exact 40514 all-custom-path catches→original fallback, original-callback catch→41BA0 probe+cleanup/no retry, plus nested-probe cleanup/unwind metadata; s106 adds exact 40AE8 original-callback catch→41BA0 probe→post-original evaluation continuation, nopresupdate file-probe no-landing-pad propagate/unwind behavior, `_updateFrameAndTransform` catch→swallow+cleanup, plus nested-probe unwind metadata; s107 adds exact 3F5C0 no-local-LSDA propagate semantics with post-attempt-increment non-rollback, plus 3F7C8 private-invocation typed catch→exception counter/no slot mark/reentrancy clear/capture dispose and nonmatching-type cleanup→unwind semantics; s108 adds exact 3F990 frame-path catch→swallow+continue orientation, orientation signature/current-orientation/setter catches→swallow+cleanup/return, plus nonmatching-type unwind metadata; s109 adds exact 3FA90 interfaceOrientation capability/send exception→local catch-all swallow+forced-zero return; s110 adds exact 3FBC8 protected scene/client identity-resolution exception→common typed catch swallow+nil return and nonmatching-type unwind metadata; s111 adds exact 3EFD4 caller-supplied string-selector capability/send/type-check exceptions→common typed catch swallow+nil return and nonmatching-type unwind metadata; s112 adds exact 3F100 `setActivatingEntity:` capability/send exception→local catch-all swallow+cleanup/return; s113 adds exact 3F224 protected UI-app request dictionary/bundle/slot-match/89D8 exceptions→common typed catch swallow+final cleanup and nonmatching-type unwind metadata; s114 adds exact 3F3F0 protected 89D8 publish exception→typed catch swallow+continue post-publish counter normalization/scene follow-up and nonmatching-type unwind metadata; s115 adds exact 3EDFC SpringBoard/frontmost-app/string-identity exceptions→common typed catch swallow+false return and nonmatching-type unwind metadata; s116 adds exact 3EB9C catch-all aux frame/orientation mutation exception→skip remaining mutation+cleanup, with frame-applied timing persistence and guaranteed orientation-applied write skip metadata. Private scene/entity traversal, FBSSceneSettingsDiff construction, ivar lookup/memory access/settings mutation, diagnostic-set/lock mutation, global counter mutation, private setters, 30960 notice execution, slot clearing, to-apps side effects, aux scene/view creation, and dismiss/settings executors remain excluded |
| hostSplit/switchInPlace | HostSplit.m (F-031) | SYNTH (APPROXIMATION) | session-038: 217EC/208F4/26FE4 từ evidence (218D8/279F4 cross-ref records) |
| Spawn/teardown callees | SpawnTeardown.m + SpawnLaunch.m + EventLaunch.m + PollFlush.m + SpawnMisc.m + FastRelayout.m (F-032) | SYNTH partial | s039 teardown + s040 routing + s042 event-launch C37C + s043 poll (22AD0/365D4/371AC/370F8) + s044 misc (B768/BEE4/CCEC/D684-note/B144) + s047 D684 bodies; còn §B KB observers (cross-ref KeyinputRelay.m) |
| DDz1/DDz2 classes | DDzCore.m (F-034) | SYNTH (APPROXIMATION) | session-048: maps 63+35 + 8 central + cross-links + division |
| DDz3 UI (153 methods) | DDzPicker.m (F-034 §6) | SYNTH-map (APPROXIMATION) | session-049: cluster map, bodies HYPOTHESIS (commit bodies ở DDzCommit.m; buildKitLevel asm-only UNKNOWN) |
| DDz3 commit chain | DDzCommit.m (F-039) | SYNTH (APPROXIMATION) | session-046: 5 files picker→prefs bridge |
| cpuiGen lifecycle | Cpuigen.m (F-040) | SYNTH (APPROXIMATION) | session-050: 5 hits + idiom + consume/stale-check từ evidence (init/reset UNKNOWN) |
| Evict (3 hệ thống) | Evict.m + ReconstructionRuntime.m (F-036/F-037) | SYNTH + BUILDABLE PARTIAL | session-071 promotes exact prefs-only 85B8; session-072 promotes read-only 7764C liveness probe with libproc. 3AE48/3AE50 Home-transition remains synthesis/private SpringBoard scope |

## C. Prefs / settings
| Subsystem | Artifact | Status | Ghi chú |
|---|---|---|---|
| Resolver/publisher 74C8 | functions/74C8.md + PrefsResolver.m + ReconstructionRuntime.m | RECORD + SYNTH + BUILDABLE PARTIAL | + F-041 errata; runtime phase-1 implements clearpanes/cache/notify + typed raw prefs, unresolved normalize/filter helpers deliberately omitted |
| Setters (746C/84D8/637E8) | PrefsResolver.m + ReconstructionRuntime.m | BUILDABLE PARTIAL | session-071: layout 1..8, CarPlay UI normalize/dedup, resolved-plist autostart toggle compile-safe; DDz3 refresh/watchdog private UI side effects intentionally omitted |
| Prefs UI spec + CN controllers | F-009/F-015 (inventory) | EVIDENCE-only | CN* bodies (~32 methods) chưa đọc |
| Toggle matrix (~100 knobs) | EVIDENCE/toggle_matrix.md (F-025/P3-1) | EVIDENCE-only | Chưa bake hết vào bodies (mới refs chính) |
| Migration/defaults (TrueDash) | Migration.m (F-019/F-020) | SYNTH (APPROXIMATION) | session-035 từ 4C34_import_defaults.md (license branch cross-ref License.m) |
| Cache/pure-pref helpers | ReconstructionRuntime.m (7044/70FC/836C/8058/7EA4/7E63C/7EEDC/8154/81EC) | BUILDABLE PARTIAL | s071 exact cache/keypane/font-floor; s072 integer validator+self-heal; s073 exact frac wrappers; s074 adds cached 7EA4/8058 state used by 89D8 + notify refresh. 73E8/80D0 bounds and full 7E908 blacklist/numerics remain unresolved |
| Language flow | LocaleFlow.m (F-030/B-20) | SYNTH (APPROXIMATION) | session-053 §A: write/post + read-4-tầng + whitelist-17 + 6 observers (Q-10 §B ở License.m) |

## D. CarPlay cloak / keyboard / display
| Subsystem | Artifact | Status | Ghi chú |
|---|---|---|---|
| Elig + dock/focus/statusbar/icon | CarPlayCloak.m (F-028) | SYNTH | Hook bodies từ subagent evidence |
| Keyboard relay + focus + swizzle | KeyinputRelay.m + KeyboardHooks.m (F-027) | SYNTH | KeyApp HYPOTHESIS; hook-fn bodies UNKNOWN |
| AZ spoof + BKS display | F-017/F-013 (cross-ref trong KeyboardHooks.m) | EVIDENCE-only | Bodies đã có ở evidence cũ |
| SB scene hooks ×10 | F-018 BLOCKED | MISSING (blocked) | Cần raw asm 27E20 |

## E. Siri / voice
| Subsystem | Artifact | Status | Ghi chú |
|---|---|---|---|
| SiriProbe hooks + gates + cache | SiriProbe.m (F-029) | SYNTH | Sink/writers/opaque UNKNOWN giữ nguyên |
| Voicecmd rescan pipeline | SiriProbe.m §rescan (F-029) | SYNTH | Worker 81CE4 cross-ref |

## F. Sleeper / perf
| Subsystem | Artifact | Status | Ghi chú |
|---|---|---|---|
| CarSleeper daemon + handlers | CarSleeper.m (F-021) | SYNTH | Handler bodies cross-ref notify_matrix |
| Perf tweak (fps) | B-07 (HIGH CONFIDENCE) + prefs rows | EVIDENCE-only | Chưa synthesis riêng (nhỏ) |

## G. License / crash / respring
| Subsystem | Artifact | Status | Ghi chú |
|---|---|---|---|
| License verify/clients/validators/unrefuse | License.m (F-006/B-09/F-016/F-030) | SYNTH | MITM/server-side UNKNOWN |
| Crash reporting | CrashReporting.m (B-08/F-016) | SYNTH (APPROXIMATION) | session-034 từ evidence + strings |
| Respring/latch pipeline | Respring.m (F-023) | SYNTH (APPROXIMATION) | session-036: 80574/8097C/96D60 từ notify/toggle rows |

## H. Data / HUD / apps
| Subsystem | Artifact | Status | Ghi chú |
|---|---|---|---|
| DataRouter/nav | DataRouter.m (F-022) | SYNTH | Worker bodies cross-ref |
| HUD/BLE/speed | HudBle.m (F-024 + strings) | SYNTH | Scan/pairing bodies UNKNOWN |
| DuoDash.app / DuoDashKey.app / Prefs.bundle | F-007/F-008 (essentials persisted) | EVIDENCE-only | Full KeyApp 255-func breakdown chỉ trong conversation session-001 (nguy cơ mất như sweep-002 — KHÔNG re-derive trừ khi cần) |
| Version/device | F-030/B-20 | EVIDENCE-only | Nhỏ, ít behavior (fail-soft) |

## I. IPC / notify / IPC model
| Subsystem | Artifact | Status | Ghi chú |
|---|---|---|---|
| Notify matrix (12+68+8) | EVIDENCE/notify_matrix.md + API_MAP.md + ReconstructionRuntime.m | BUILDABLE PARTIAL | s071 SpringBoard 29198 trio Immediate→republish; s074 adds exact Immediate fontfloor/keypane cache refresh plus runtime-resolved DDz2 per-host broadcasts from 291F4/29400. Keypane-OFF toast 30960 and other callbacks remain evidence/private scope |
| NSDistributed fabric | F-026 + cnab_observers + ReconstructionRuntime.m | BUILDABLE PARTIAL | s073-s075 publishers + UIApp consumers; s076 responder/retries; s077 prep+dismiss; s078 adds 3F3F0 raw slot resize → uiapp.state state/IPC half. Private scene probe/layout remains separated from mirror/IPC state |

## J. Meta (contract/tracking)
| Artifact | Status |
|---|---|
| SIDE_EFFECTS.md (ledger SE-*) | Có cho 11 records + slices synthesis s1-s11; P4 ledger DONE session-068 (mọi subsystem có bodies đã có rows hoặc no-rows verdict: PresentCommitAck s067, Tweak.x-init s068; Shared.h constants — không behavior) |
| COMPARISON.md (matrix) | Có cho 11 records + 28 synthesis sections (s1-s11); P4 DONE cùng điều kiện trên |
| TESTS.md (static asserts + dynamic list) | Static pass; dynamic pending (cần device) |
| Tweak.x + Shared.h + ReconstructionRuntime | Buildable APPROXIMATION phase-1; Theos target + GitHub Actions session-070. Remaining synthesis modules are evidence-only until promoted safely |

## Ưu tiên lấp GAP (đề xuất cho sessions tới, theo PRIORITY P0>P1>P2>P4)
1. ~~**P1**: record 163EC~~ — DONE session-033 (functions/163EC.md + SE/COMPARISON rows).
2. **P1**: record 4C34 phases còn lại dưới dạng FUNCTION record (import/defaults đã có evidence sâu;_ctor body 1465 dòng).
3. ~~**P2**: CrashReporting.m synthesis~~ — DONE session-034.
4. ~~**P2**: Migration.m synthesis~~ — DONE session-035.
5. ~~**P2**: Respring/latch synthesis~~ — DONE session-036 (Respring.m riêng).
6. ~~**P2**: spike/hostSplit/spawn/teardown~~ — DONE sessions 037-040 + 042-044 + 047 (17/17 callees + C37C + poll + misc + D684); còn §B KB observers (cross-ref KeyinputRelay.m, giá trị thấp).
7. **P3**: DDz3 bodies còn lại / DDz classes records (lớn, giá trị/giá thấp).
8. **P4** ledger DONE session-068 (slices s055-s066 + verdicts s067-s068); còn TESTS dynamic (cần device — blocked).
9. **Blocked**: P0-3 (asm), Q-09 entitlements, Q-10 MITM, Q-12/Q-13 (disasm blocks), dynamic verify.
