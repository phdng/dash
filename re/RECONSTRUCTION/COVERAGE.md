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
| UIApp/IPC/kbd/display ctors | — (EVIDENCE: session-002 + F-011 once-chain) | EVIDENCE-only | 455D0/4CBDC/4C858/4DEB4/4D0B8/7F010/842EC/9460C |
| Tweak.x init section | Tweak.x (init) | SYNTH (APPROXIMATION) | Từ F-011/HOOKS, chưa bodies chi tiết |

## B. AppBridge hosting (split/layout/panes)
| Subsystem | Artifact | Status | Ghi chú |
|---|---|---|---|
| hostSlots decision 218D8 | functions/218D8.md | RECORD | + reshow/fast paths |
| Split request parse 202D0 | functions/202D0.md | RECORD | layout-absent CONFIRMED |
| Async execute 2410C | functions/2410C.md | RECORD (+state machine) | sâu nhất (878 dòng) |
| Present-commit 2565C | functions/2565C.md | RECORD | + 9424 dict exact |
| Single-app host 1FB5C | functions/1FB5C.md | RECORD | cặp với 202D0 |
| Hosting observers/consumers | PresentCommitAck.m | SYNTH | 202D0→218D8→2410C→2565C→9424/onHosted |
| spikeHostSlots: internals | SpikeHosting.m (F-035) | SYNTH (APPROXIMATION) | session-037: 3CC44/3BBF0/3C1F0/3D4FC từ evidence |
| hostSplit/switchInPlace | HostSplit.m (F-031) | SYNTH (APPROXIMATION) | session-038: 217EC/208F4/26FE4 từ evidence (218D8/279F4 cross-ref records) |
| Spawn/teardown callees | SpawnTeardown.m + SpawnLaunch.m + EventLaunch.m + PollFlush.m + SpawnMisc.m + FastRelayout.m (F-032) | SYNTH partial | s039 teardown + s040 routing + s042 event-launch C37C + s043 poll (22AD0/365D4/371AC/370F8) + s044 misc (B768/BEE4/CCEC/D684-note/B144) + s047 D684 bodies; còn §B KB observers (cross-ref KeyinputRelay.m) |
| DDz1/DDz2 classes | DDzCore.m (F-034) | SYNTH (APPROXIMATION) | session-048: maps 63+35 + 8 central + cross-links + division |
| DDz3 UI (153 methods) | DDzPicker.m (F-034 §6) | SYNTH-map (APPROXIMATION) | session-049: cluster map, bodies HYPOTHESIS (commit bodies ở DDzCommit.m; buildKitLevel asm-only UNKNOWN) |
| DDz3 commit chain | DDzCommit.m (F-039) | SYNTH (APPROXIMATION) | session-046: 5 files picker→prefs bridge |
| cpuiGen lifecycle | Cpuigen.m (F-040) | SYNTH (APPROXIMATION) | session-050: 5 hits + idiom + consume/stale-check từ evidence (init/reset UNKNOWN) |
| Evict (3 hệ thống) | Evict.m (F-036/F-037) | SYNTH (APPROXIMATION) | session-045: 85B8/7764C/3AE48/3AE50 + caller matrix + verdicts (kill cross-ref Tweak.x) |

## C. Prefs / settings
| Subsystem | Artifact | Status | Ghi chú |
|---|---|---|---|
| Resolver/publisher 74C8 | functions/74C8.md + PrefsResolver.m | RECORD + SYNTH | + F-041 errata baked in |
| Setters (746C/84D8/637E8) | PrefsResolver.m (cross-ref) | SYNTH (cross-ref) | Bodies trong EVIDENCE, chưa tách record |
| Prefs UI spec + CN controllers | F-009/F-015 (inventory) | EVIDENCE-only | CN* bodies (~32 methods) chưa đọc |
| Toggle matrix (~100 knobs) | EVIDENCE/toggle_matrix.md (F-025/P3-1) | EVIDENCE-only | Chưa bake hết vào bodies (mới refs chính) |
| Migration/defaults (TrueDash) | Migration.m (F-019/F-020) | SYNTH (APPROXIMATION) | session-035 từ 4C34_import_defaults.md (license branch cross-ref License.m) |
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
| Notify matrix (12+68+8) | EVIDENCE/notify_matrix.md + API_MAP.md | EVIDENCE-only | Đã merge API_MAP; chưa ledger hóa từng notify vào SIDE_EFFECTS |
| NSDistributed fabric | F-026 + cnab_observers produce/consume matrix | EVIDENCE-only | Chưa tách per-notify records |

## J. Meta (contract/tracking)
| Artifact | Status |
|---|---|
| SIDE_EFFECTS.md (ledger SE-*) | Có cho 11 records + slices synthesis (s1-s4 + s5a SPAWN session-059); còn lại thiếu |
| COMPARISON.md (matrix) | Có cho 11 records + 10 synthesis sections (s1-s5a); còn lại thiếu |
| TESTS.md (static asserts + dynamic list) | Static pass; dynamic pending (cần device) |
| Tweak.x (skeleton) + Shared.h | APPROXIMATION skeleton |

## Ưu tiên lấp GAP (đề xuất cho sessions tới, theo PRIORITY P0>P1>P2>P4)
1. ~~**P1**: record 163EC~~ — DONE session-033 (functions/163EC.md + SE/COMPARISON rows).
2. **P1**: record 4C34 phases còn lại dưới dạng FUNCTION record (import/defaults đã có evidence sâu;_ctor body 1465 dòng).
3. ~~**P2**: CrashReporting.m synthesis~~ — DONE session-034.
4. ~~**P2**: Migration.m synthesis~~ — DONE session-035.
5. ~~**P2**: Respring/latch synthesis~~ — DONE session-036 (Respring.m riêng).
6. ~~**P2**: spike/hostSplit/spawn/teardown~~ — DONE sessions 037-040 + 042-044 + 047 (17/17 callees + C37C + poll + misc + D684); còn §B KB observers (cross-ref KeyinputRelay.m, giá trị thấp).
7. **P3**: DDz3 bodies còn lại / DDz classes records (lớn, giá trị/giá thấp).
8. **P4** (slices done s055-s059: +SPAWN core): rows cho synthesis bodies còn lại; TESTS dynamic (cần device).
9. **Blocked**: P0-3 (asm), Q-09 entitlements, Q-10 MITM, Q-12/Q-13 (disasm blocks), dynamic verify.
