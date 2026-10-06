# TODO.md — DuoDash Reconstruction
_Priority: P0 > P1 > P2 > P3 > P4. Cập nhật mỗi checkpoint._

## P0 — Thay đổi toàn bộ behavioral model
- [x] [P0-1] Dump Mach-O `__mod_init_func` order (FAT 2 slices, init_offsets={44C0,7F010,842EC,9460C} + block invoke table). → F-011.
- [x] [P0-2] Resolve `sub_AC5FC` suffixes (pointers 27884-27892). → F-012.
- [ ] [P0-3] Resolve `sub_4049C` hook-fn/orig — BLOCKED ON ARTIFACTS (cần raw asm 27E20, export thiếu). → F-018.
- [x] [P0-4] Dump `off_12DB98` loop → 7 AZ* hooks. → F-017.
- [x] [P0-5] Xác định `off_164450` = BKSDisplayServicesSetScreenBlanked. → F-013.

## P1 — Hook/API/runtime quan trọng
- [x] [P1-0] Inventory + entry + hook map static + prefs/IPC/network static (session-001, 3 subagents). → STATE/FINDINGS/HOOKS/API_MAP.
- [x] [P1-1] Đọc full `27E20.c` (subagent + verify 4049C/blocks). → B-01b, F-018.
- [x] [P1-2] Đọc full `163EC.c` (elig/dock/scene KNOWN toàn bộ). → HOOKS.md.
- [x] [P1-3] Đọc full `4C34.c` import/defaults/sleeper (subagent P1-3). → F-019/F-020/F-021, EVIDENCE/4C34_import_defaults.md.
- [x] [P1-4] Đọc full `455D0.c` + `4CBDC.c` (43 hooks + AZ loop + notifies). → HOOKS.md.
- [x] [P1-5] Grep `openLicenseActivation:|openTweakManagement:` → dylib native classes. → F-015.
- [x] [P1-6] Đọc `9E014.c` + `9DE28.c` (crash endpoint configurable). → F-016.
- [x] [P1-7] Đọc license chain + `license_endpoint` negative. → F-016, B-09.
- [x] [P1-8] Notify sweep full (12 notify_dispatch + 68 Darwin observers). → EVIDENCE/notify_matrix.md + API_MAP merge (session-003 rebuild vì sweep cũ mất).

## P2 — Core feature logic
- [x] [P2-1] Behavioral model prefs resolver (74C8 14 keys + 7EA4/8058/746C + helpers). → BEHAVIOR B-15, EVIDENCE/prefs_split_autostart.md.
- [x] [P2-2] Behavioral model keyinput relay (focus intercept + seed/apply + dismiss/fallback + password bypass + keypane OFF). → BEHAVIOR B-17, EVIDENCE/keyinput_relay.md.
- [x] [P2-3] Behavioral model CarPlay elig cloak (mutate + synth + injector + icon/name) + dock/focus/statusbar. → BEHAVIOR B-18, EVIDENCE/elig_cloak.md.
- [x] [P2-4] Behavioral model split/autostart/disconnect (split_enabled YES + 12s SIGKILL + pane_unload SIGKILL + autostart observe-only). → B-15, EVIDENCE/prefs_split_autostart.md.
- [x] [P2-5] RECONSTRUCTION skeleton — Shared.h + Tweak.x + subsystem synthesis. Session-070 nâng phần evidence-safe thành buildable runtime; private-hook bodies vẫn chưa compile cho tới khi resolve contracts.

## P3 — Edge cases
- [x] [P3-1] Toggle matrix `/var/tmp/duodash_*` (~100 knobs: ~80 KILL + ~25 VALUE + ~10 ONESHOT + 4 đảo semantics). → EVIDENCE/toggle_matrix.md.
- [x] [P3-2] TrueDash migration (one-way successor — F-019; bundle-id TrueDash.app UNKNOWN, rename-map nội dung UNKNOWN).
- [x] [P3-3] CarSleeper static (handlers + daemon + boot_id + 8s — F-021; còn runtime verify).
- [x] [P3-4] SiriProbe end-to-end (7 hooks + swallow gate + fakepress + voicecmd cache/rescan). → BEHAVIOR B-19, EVIDENCE/siriprobe.md.
- [x] [P3-5] Version/device-specific (4008 generic + A3558 đính chính + branch CF duy nhất + language flow). → BEHAVIOR B-20, EVIDENCE/version_device_ainfo.md.

## P4 — Cleanup/docs
- [x] [P4-1] Git init + commit local re/ only (binaries Applications/ + Library/ untracked; không remote/push). → session-006.
- [x] [P4-2] EVIDENCE chuẩn hóa — PARTIAL (audit session-009: mọi file có nguồn subagent + claims chính có file:line trong FINDINGS F-001..F-036; EVIDENCE mới rút gọn giữ detail, citations đầy đủ nhất ở notify_matrix/prefs_split_autostart; full verbatim subagent reports không lưu — chấp nhận mất chi tiết phụ).

## R — Function-level 1:1 reconstruction (session-012+, PRIMARY OBJECTIVE mới)
- [x] [R-001] FUNCTION record 2410C (contract + call trace + state machine + transition table) → RECONSTRUCTION/functions/2410C.md. Status INFERRED.
- [x] [R-002] SIDE_EFFECTS.md starter (SE-2410C-001..009) + COMPARISON.md starter (2410C rows).
- [x] [R-003] FUNCTION record 2565C (đọc FULL trực tiếp 146 dòng + 9424 108 dòng; branches + args + fail paths). Status INFERRED.
- [x] [R-004a] FUNCTION record 218D8 (đọc FULL trực tiếp 717 dòng 2 passes; 15 branches B01-B14; U01-U08). Status INFERRED.
- [x] [R-004b1] FUNCTION record 202D0 (đọc FULL trực tiếp 272 dòng; 8 branches; U01-U06). Status INFERRED.
- [x] [R-004b2] FUNCTION record 74C8 (đọc FULL trực tiếp 430 dòng 2 passes; 12 branches B01-B11 + trace 18 bước; F-041 errata). Status INFERRED.
- [x] [R-004b3] FUNCTION record 9D64 (đọc FULL trực tiếp 775 dòng 3 passes; 16 branches B00-B15 + trace 19 bước; U01-U08). Status INFERRED.
- [x] [R-005] FUNCTION record 1FB5C (đọc FULL trực tiếp 214 dòng; 11 branches B01-B11 + 2-route trace; U01-U07). Status INFERRED.
- [x] [R-006] FUNCTION record 20010 (đọc FULL trực tiếp 91 dòng; 5 branches B01-B05 + dead-read why; U01-U06). Status INFERRED.
- [x] [R-007] FUNCTION record 27E20 (đọc FULL trực tiếp 711 dòng 3 passes; 15 branches B01-B15 + U01-U08; reentry-duplicate phát hiện). Status INFERRED.
- [x] [R-008] FUNCTION record 44C0 (đọc FULL trực tiếp 124 dòng; 7 branches; F-042 blocklist errata). Status INFERRED.
- [x] [R-009] Tweak.x present/commit/ack bodies từ 10 records → RECONSTRUCTION/PresentCommitAck.m (APPROXIMATION synthesis session-022).
- [x] [R-010] Tweak.x keyinput relay bodies từ EVIDENCE/keyinput_relay.md → RECONSTRUCTION/KeyinputRelay.m (APPROXIMATION synthesis session-023, KeyApp = HYPOTHESIS).
- [x] [R-011] Tweak.x prefs resolver bodies từ functions/74C8.md → RECONSTRUCTION/PrefsResolver.m (APPROXIMATION synthesis session-024).
- [x] [R-012] Tweak.x license bodies từ F-006/B-09/F-016/F-030 + aa_validators → RECONSTRUCTION/License.m (APPROXIMATION synthesis session-025).
- [x] [R-013] Tweak.x carplay-cloak bodies từ EVIDENCE/elig_cloak.md → RECONSTRUCTION/CarPlayCloak.m (APPROXIMATION synthesis session-026).
- [x] [R-014] Tweak.x SiriProbe bodies từ EVIDENCE/siriprobe.md → RECONSTRUCTION/SiriProbe.m (APPROXIMATION synthesis session-027).
- [x] [R-015] Tweak.x CarSleeper daemon bodies từ F-021 + import_defaults §8 + notify_matrix → RECONSTRUCTION/CarSleeper.m (APPROXIMATION synthesis session-028).
- [x] [R-016] Tweak.x keyboard-hook mapping bodies từ HOOKS.md → RECONSTRUCTION/KeyboardHooks.m (APPROXIMATION synthesis session-029; hook-fn bodies UNKNOWN trừ focus/swizzle/AZ đã có).
- [x] [R-017] Tweak.x DataRouter/nav bodies từ F-022 + notify_matrix → RECONSTRUCTION/DataRouter.m (APPROXIMATION synthesis session-030).
- [x] [R-018] Tweak.x HUD/BLE bodies từ F-024 + strings (scan/prefs/speed/brightness) → RECONSTRUCTION/HudBle.m (APPROXIMATION synthesis session-031; scan/pairing bodies UNKNOWN).
- [x] [R-019] Audit coverage RECONSTRUCTION/ vs subsystems → RECONSTRUCTION/COVERAGE.md (session-032, kèm priority lấp GAP).
- [x] [R-020] FUNCTION record 163EC (đọc FULL trực tiếp 529 dòng 2 passes; 12 branches B01-B11 + U01-U08). Status INFERRED.
- [x] [R-021] Tweak.x CrashReporting bodies từ B-08/F-016 + notify row + strings → RECONSTRUCTION/CrashReporting.m (APPROXIMATION synthesis session-034).
- [x] [R-022] Tweak.x Migration bodies từ EVIDENCE/4C34_import_defaults.md → RECONSTRUCTION/Migration.m (APPROXIMATION synthesis session-035; license branch cross-ref License.m).
- [x] [R-023] Tweak.x Respring/latch bodies từ F-023/B-14 + notify/toggle rows → RECONSTRUCTION/Respring.m (APPROXIMATION synthesis session-036).
- [x] [R-024] Tweak.x spikeHostSlots bodies từ EVIDENCE/spike_hostslots.md (F-035: 3CC44/3BBF0/3C1F0/3D4FC) → RECONSTRUCTION/SpikeHosting.m (APPROXIMATION synthesis session-037).
- [x] [R-025] Tweak.x hostSplit/switchInPlace bodies từ EVIDENCE/hosting_engine.md §§2-3 (F-031: 217EC/208F4/26FE4) → RECONSTRUCTION/HostSplit.m (APPROXIMATION synthesis session-038; 218D8/279F4 cross-ref).
- [x] [R-026] Tweak.x teardown/evict bodies từ EVIDENCE/spawn_teardown_kb.md §A (F-032: D154/CE5C/B9A8/BBF8/BCDC/BD18) → RECONSTRUCTION/SpawnTeardown.m (APPROXIMATION synthesis session-039).
- [x] [R-027] Tweak.x spawn-routing bodies từ EVIDENCE/spawn_teardown_kb.md §A (F-032: D4C4/D01C/BFF4/BE34/C2A4/CB08) → RECONSTRUCTION/SpawnLaunch.m (APPROXIMATION synthesis session-040).
- [x] [R-028] Refresh RECONSTRUCTION/COVERAGE.md (stale sau sessions 033-040: 163EC/spike/hostSplit/spawn/Migration/CrashReporting/Respring rows + priorities) — session-041 audit, không claim mới.
- [x] [R-029] Tweak.x event-launch body từ EVIDENCE/spawn_teardown_kb.md §A item 9 (F-032: C37C 3 tiers + 9 fail reasons) → RECONSTRUCTION/EventLaunch.m (APPROXIMATION synthesis session-042).
- [x] [R-030] Tweak.x poll/UI-flush bodies từ EVIDENCE/spawn_teardown_kb.md §C (F-032: 22AD0/365D4/371AC/370F8) → RECONSTRUCTION/PollFlush.m (APPROXIMATION synthesis session-043).
- [x] [R-031] Tweak.x misc bodies từ EVIDENCE/spawn_teardown_kb.md §A items 1,6,11,17 (F-032: B768/BEE4/CCEC/D684-note/B144) → RECONSTRUCTION/SpawnMisc.m (APPROXIMATION synthesis session-044; đóng 17/17 callees).
- [x] [R-032] Tweak.x evict bodies từ EVIDENCE/evict_helpers.md + evict_from_phone.md (F-036/F-037: 85B8/7764C/3AE48/3AE50 + caller matrix + 3-hệ verdicts) → RECONSTRUCTION/Evict.m (APPROXIMATION synthesis session-045; kill cross-ref Tweak.x).
- [x] [R-033] Tweak.x DDz3 commit-chain bodies từ EVIDENCE/ddz3_commit.md (F-039: 5F044/5F224/5F538/5F74C/5F8A4 + why strings + parallel paths) → RECONSTRUCTION/DDzCommit.m (APPROXIMATION synthesis session-046).
- [x] [R-034] Tweak.x D684 fast/slow bodies từ EVIDENCE/ddz_inventory.md §4 (F-034: fast-vs-slow + 2 họ entity + 14 fail reasons + trigger 3 đường) → RECONSTRUCTION/FastRelayout.m (APPROXIMATION synthesis session-047; lấp D684-UNKNOWN ở SpawnLaunch/SpawnMisc/9D64-U05).
- [x] [R-035] Tweak.x DDz1/DDz2 class bodies từ EVIDENCE/ddz_inventory.md §§0-3,5 (F-034: maps 63+35 + 8 central + cross-links + division) → RECONSTRUCTION/DDzCore.m (APPROXIMATION synthesis session-048; DDz3 UI scope sau) + COVERAGE DDz rows touch-up.
- [x] [R-036] Tweak.x DDz3 UI-cluster map từ EVIDENCE/ddz_inventory.md §6 (F-034: 153 methods cụm + buildKitLevel-note) → RECONSTRUCTION/DDzPicker.m (APPROXIMATION synthesis-map session-049) + COVERAGE DDz3 touch-up.
- [x] [R-037] Tweak.x cpuiGen lifecycle bodies từ EVIDENCE/cpuigen_trace.md (F-040: 5 hits + idiom + consume/stale-check) → RECONSTRUCTION/Cpuigen.m (APPROXIMATION synthesis session-050) + COVERAGE cpuigen touch-up.
- [x] [R-038] COVERAGE touch-up 042-045 (spawn row + Evict row + P2-#6 DONE) — session-051 audit, không claim mới.
- [x] [R-039] Tweak.x KB-observer bodies từ EVIDENCE/spawn_teardown_kb.md §B (F-032: stubs no-op + onDismiss/449C8 + onEndEditing inverted-knob) → RECONSTRUCTION/KBObservers.m (APPROXIMATION synthesis session-052) + KeyinputRelay line-14 stale-fix.
- [x] [R-040] Tweak.x locale/version-device bodies từ EVIDENCE/version_device_ainfo.md §A (F-030/B-20/P3-5: fail-soft + write/post + read-4-tầng + 6 observers) → RECONSTRUCTION/LocaleFlow.m (APPROXIMATION synthesis session-053) + COVERAGE language touch-up.
- [x] [R-041] Tweak.x CNAB conn/window bodies từ EVIDENCE/cnab_observers.md §§4-6 (F-026: 229FC/22A8C/227E4/99D4 + fabric 887C/8D78) → RECONSTRUCTION/CNABConn.m (APPROXIMATION synthesis session-054; aa_validators verify-đã-cover ở License.m, không việc).
- [x] [R-042] P4 slice-1: SIDE_EFFECTS (SE-CRASH-001..005 + SE-RESPRING-001..003) + COMPARISON (2 sections CrashReporting/Respring) cho synthesis bodies — session-055, không claim mới.
- [x] [R-043] P4 slice-2: SIDE_EFFECTS (SE-POLL-001..003 + SE-CNAB-001..003) + COMPARISON (2 sections PollFlush/CNABConn) — session-056, không claim mới.
- [x] [R-044] P4 slice-3: SIDE_EFFECTS (SE-SPIKE-001..004 + SE-HSPLIT-001..003) + COMPARISON (2 sections SpikeHosting/HostSplit) — session-057, không claim mới.
- [x] [R-045] P4 slice-4: SIDE_EFFECTS (SE-EVICT-001..003 + SE-CPUIGEN-001..002) + COMPARISON (2 sections Evict/Cpuigen) — session-058, không claim mới.
- [x] [R-046] P4 slice-5a: SIDE_EFFECTS (SE-SPAWN-001..006) + COMPARISON (2 sections SpawnTeardown/SpawnLaunch) — session-059, không claim mới.
- [x] [R-047] P4 slice-5b: SIDE_EFFECTS (SE-EVLAUNCH-001 + SE-SPAWNMISC-001..002 + SE-FASTRELAY-001..002) + COMPARISON (3 sections) — session-060, không claim mới.
- [x] [R-048] P4 slice-6: SIDE_EFFECTS (SE-DDZ-001..005) + COMPARISON (3 sections DDzCore/DDzCommit/DDzPicker) — session-061, không claim mới.
- [x] [R-049] P4 slice-7: SIDE_EFFECTS (SE-PREFS-001 + SE-MIG-001..002 + SE-LOCALE-001) + COMPARISON (3 sections) — session-062, không claim mới.
- [x] [R-050] P4 slice-8: SIDE_EFFECTS (SE-LIC-001..003 + SE-KEY-001..002 + SE-KBD-001 + SE-KBOBS-001) + COMPARISON (4 sections) — session-063, không claim mới.
- [x] [R-051] P4 slice-9: SIDE_EFFECTS (SE-SIRI-001..003 + SE-SLEEP-001..002) + COMPARISON (2 sections SiriProbe/CarSleeper) — session-064, không claim mới.
- [x] [R-052] P4 slice-10: SIDE_EFFECTS (SE-DATA-001..003 + SE-HUD-001..002) + COMPARISON (2 sections DataRouter/HudBle) — session-065, không claim mới.
- [x] [R-053] P4 slice-11: SIDE_EFFECTS (SE-CLOAK-001..003) + COMPARISON (1 section CarPlayCloak) — session-066, không claim mới.
- [x] [R-054] Audit PresentCommitAck-overlap (covered bởi record rows → không rows riêng) + micro-synthesis 279F4/27AC8 từ hosting_engine §4 → RECONSTRUCTION/HostedCallbacks.m (APPROXIMATION session-067) + COVERAGE hosting-row note.
- [x] [R-055] P4 close-out: audit Tweak.x-init overlap (covered bởi SE-44C0-001/COMPARISON-44C0/F-011 → không rows riêng; Shared.h constants — không behavior) + COVERAGE J/P4-#8 final — session-068, P4 ledger DONE (còn TESTS dynamic blocked).
- [ ] [R-056] scope khác — quyết scope session sau (chỉ còn blocked/infeasible: P0-3 raw asm, P1 4C34 thiếu decompile, TESTS dynamic cần device, Q-09/Q-10/Q-12/Q-13).
- [x] [R-004] SUPERSEDED — covered bởi R-004a (218D8) + R-004b1 (202D0) + R-004b2 (74C8) + R-004b3 (9D64), tất cả done. (Ghi nhận session-069.)
- [x] [R-056] Integrity audit session-069: LOG 001-068 complete (68/68) + R-artifacts present (42/42) + TESTS static documented-pass; STEADY-STATE — static scope cạn (chỉ còn blocked/infeasible).
- [x] [R-057] Buildable reconstruction phase-1 (session-070): Theos target + exact Substrate filter + compile-safe role detect + AppBridge prefs/cache/notify runtime + local structural verifier + GitHub Actions build.
- [x] [R-058] Buildable prefs setters + notify reload fabric (session-071): 746C layout 1..8; 84D8 CarPlay UI normalize/dedup; 637E8/836C autostart toggle; 29198-safe republish observers for settings/listchanged/autostart with Immediate suspension; encode 85CDC CFBoolean-only trap.
- [x] [R-059] Buildable prefs-only logical evict 85B8 (session-071): resolved main/more read → remove bid → 84D8-equivalent setter; explicitly no kill/view teardown.
- [x] [R-060] Cache/pure-pref helpers (session-071): exact 7044/70FC/836C readers + 8058 keypane missing=>ON + 7EA4 font-floor override/parser (8..96); private 8C28 per-host broadcasts intentionally excluded.
- [x] [R-061] Buildable 7764C liveness probe (session-072): exact SpringBoard bundle gate + snapshot/filter type checks + pid>=2 + libproc proc_pidpath/strcmp + original 0xFFFFFFFF sentinel; no kill/unhost/prefs/private SB objects.
- [x] [R-062] Buildable 7E63C/7EEDC integer validation/self-healing (session-072): statuses 0/1/2/3, integer-CFNumber only, NSString coercion, inclusive range, writes/fixes only for status 2/3.
- [x] [R-063] Numeric cache readers (session-073): promote exact 8154(key,0..99,default0) + 81EC(frac_layout,0..8,default0); re-check 73E8/80D0 and keep unresolved because 7E63C args are elided and no per-function asm is available.
- [x] [R-064] Runtime-resolved NSDistributed IPC + host-state publishers (session-073): 8900/887C/8934/8C28/8D78 generic center/add/post; 97A0 hostRefused payload; 9424 host.state schema. No private-framework link or private receiver bodies.
- [x] [R-065] Exact AppBridge IPC payload builders (session-074): 8CC0 uiapp.request; 8DF8 host.request; 8F34 11-field frame metadata; 91B4 host.request.split; 986C cpui.status. DDHostFrameMetrics asserted 104 bytes; no private framework linkage.
- [x] [R-066] Cached UI state + 89D8 (session-074): resolver refresh order 7EA4→8058, Immediate fontfloor/keypane Darwin callbacks update cached globals, and uiapp.state uses those cached values rather than fresh prefs reads.
- [x] [R-067] Runtime-resolved 29810/DDz2 broadcast path (session-074): hostedSlotBids fallback hostedBundleId/2, exclude hostedSlotIsCarPlayUI, then exact uiapp.fontfloor/uiapp.keypane payloads per bundle. Private 30960 keypane-OFF toast intentionally omitted.
- [x] [R-068] UIApp-side IPC consumer (session-075): promote evidence-safe 4CBDC wiring + exact 4407C/443FC/444C4 parsing/defaults + 445F8/447C0 3s stale-state timeout + 446E4 background knob semantics + 42F10 temp/legacy marker lookup. Cache-only boundary; 422D0 relayout/font mutations and key-probe half remain excluded.
- [x] [R-069] SpringBoard onUIAppRequest 3F224 (session-076): resolved the per-slot size blocker with a compile-safe host-slot mirror matching DDz2 raw state (1..3 bids/sizes/CarPlay flags/split/orientation/generation), then wired a bundle-scoped request responder against that mirror. No slot-0 geometry substitution.
- [x] [R-070] DDz2 retry schedulers (session-076): recover `off_154160` constants exactly as 0.0/0.4/0.9/1.8/3.5s; promote 3B738/3ED88 app-side handshake and 3D4FC/3DC38 geometry retry gates with generation/active/bid checks and captured-size fallback.
- [x] [R-071] DDz2 CarPlay slot state (session-076): exact 3D6EC flag setter + state/IPC half of 3D704 conversion (main-thread/slot bounds, bridge-off state push, retain bid, set CarPlay flag); private view remove/invalidate intentionally omitted.
- [x] [R-072] Pre-private host preparation (session-077): exact 3B2D8 single-host mirror scaling (`duodash_ab_canvas=portrait` => min/max screen bounds; otherwise `duodash_ab_rscale` 1..3 else 2), 3DFC8 orientation, 3CC44 split mirror population with native per-slot sizes, plus strict pure landscape parser (orientation 3/4, swap/cswap, finite rot ±360). Private class gate/scene creation and lscape inflight/tripped coordination remain excluded.
- [x] [R-073] Dismiss state/IPC half (session-077): promote 3D8A8 main-thread marshaling + 3D990 per-slot bridge-off broadcasts + exact 3AAF8-compatible mirror reset ordering; omit private aux-scene/view removal/controller invalidation.
- [x] [R-074] Full evidence-safe 3CC44 landscape coordination (session-078): exact `.tripped` gate, `.inflight` NSString-int PID handling, stale-foreign cleanup only when `respring_planned.mtime_sec >= inflight.mtime_sec`, foreign-PID trip+unlink, accepted-state persistence, current-PID inflight rewrite (0644 truncate), and single-host/reset inflight cleanup. `sub_372CC` private keyboard-layer hooks intentionally omitted.
- [x] [R-075] Landscape-aware slot resize state/IPC (session-078): exact 3F3F0 gates, raw slot-size update + `uiapp.state` split publish, plus reusable lscape `swap` transform for downstream scene dimensions only; private probeScene/sub_3F5C0 and counter mutations omitted.
- [ ] [R-076] After CI green, inspect exact geometry consumers around 3F5C0/3257C/400D0 and promote only pure transform/decision helpers (including cswap/rotation if fully recoverable); do not instantiate or mutate private scene/view objects.
