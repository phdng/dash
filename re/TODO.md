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
- [x] [P2-5] RECONSTRUCTION skeleton — Shared.h (constants) + Tweak.x (init/prefs/IPC/hooks/kill APPROXIMATION). Chưa bodies chi tiết, chưa compile.

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
