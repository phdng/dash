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
- [ ] [R-022] Migration synthesis HOẶC spikeHostSlots records HOẶC scope khác — quyết scope session sau.
- [ ] [R-004] FUNCTION records tiếp theo theo ưu tiên: 218D8 → 202D0 → 74C8 → 9D64.
