# TESTS.md (updated session-004)
## Static checks (done session-001)
- [x] plist decode (DuoDash.plist, DuoDashPrefs.plist, Info.plists) — pass.
- [x] imports grep MSHook/notify/CFNotification — pass (17 hook sites).
- [x] strings grep sensetechlab//var/tmp/plist/https — pass (132/168/54/2 hosts).

## Static checks (done session-002/003)
- [x] FAT macho `__init_offsets` dump: slice0={44C0,7F010,842EC,9460C} (4 ctors, không ≥10 — assert cũ sai, sửa lại: ==4 + block table 7 roles).
- [x] AC5FC suffixes (pointers 27884-27892: SpringBoard/Preferences/CarPlay/mediaserverd/kbd).
- [x] 12DB98 table → 7 AZ* hooks (stride 32B, memory+pointers).
- [x] 164450 target = BKSDisplayServicesSetScreenBlanked (4DDC0.c:19).
- [ ] 4049C addrs — BLOCKED (F-018, export thiếu asm 27E20).

## Static checks (done session-004)
- [x] 74C8 publish keys==14 (74C8.c:375-381) — pass.
- [x] 746C range: guard `(result-9)>=0xFFF...F8` → 1..8 (HYPOTHESIS, cần review lại assert cũ "0..8").
- [x] license codes 0-8,10 (9 vắng — A397C) — pass.
- [x] disconnect default 12s (7B9EC.c:27: 12000000000ns) — pass.
- [x] kill API = kill(pid,9) SIGKILL cả 2 paths (763E0.c:247, 7792C.c:321) — pass, không SB terminate.
- [x] CNAB 12 methods inventory (function_index) + 8 bodies FULL + produce/consume matrix 7 notifies — pass.
- [x] notify matrix: 12 notifyd + 68 Darwin + 8 NSNotification, mỗi dòng file:line+callback — pass (EVIDENCE/notify_matrix.md).
- [ ] prefs spec assert 30 vs 11 (chưa chạy lại sau F-015 — actions đã resolve về dylib, assert cũ lỗi thời).

## Dynamic (cần device jailbroken, chưa chạy)
- [ ] `notifyutil -w com.sensetechlab.appbridge.resolved` sau đổi layout.
- [ ] `plutil -p .../com.sensetechlab.duodash.settings.plist` + `/var/tmp/com.sensetechlab.appbridge.plist` (expect 14+2 keys, split_enabled=1).
- [ ] MITM `license.sensetechlab.com/{activate,info,env,healthz}` + offline blob verify (expect codes 0-8,10).
- [ ] Tail `/var/tmp/duodash_keypane_relay.log` + `seed→take→kbshown→type` sequence.
- [ ] Toggle files: `nodiscoclose` (skip kill), `discoclose_secs=5` (fire 5s), `reapdelay`, `noreap`, `noautostart`, `split_deactivate_dismiss`, `cpui_nonudge`.
- [ ] Verify HYPOTHESIS mở: 74C8.c:251 filter đảo, 746C 1..8 vs 0..8, 85CDC arg inline, 10 keys off_154208 mapping, schedulers 1A820/7B9EC/7BD58, 162E60 setter, layout downstream use.

## Build (session-119)
- [x] `python scripts/verify_reconstruction.py` — PASS: 30 synthesis modules present + Makefile/runtime/filter wiring đúng.
- [x] Substrate filter reconstruction đối chiếu artifact gốc: 4 Bundles + 2 Executables + Mode=Any.
- [x] `Tweak.x` có compile-safe ctor gọi `DDReconstructionStart()`; runtime role-gates SpringBoard prefs/host-safe behavior và UIApp IPC/state consumer, các private-hook roles khác vẫn inactive.
- [x] Theos compiler build `make clean all` — GitHub Actions macOS GREEN for session-118 batch (`d5fa917`, user-confirmed before session-119 changes).
- [x] Static runtime contracts through session-119: verifier checks LSDA/raw-ARM64-confirmed 3E33C primary `sceneIfExists` path has no local landing pad and therefore propagates exceptions, while protected fallback `scene` capability/send exceptions → typed catch swallow + nil result; nonmatching catch type → resume unwind. No selector construction/invocation, runtime method-signature inspection, real scene lifetime effects, synthesized/runtime catch execution, or unwind execution.
- [ ] Jailbroken-device runtime smoke test cho cache + `appbridge.resolved`, layout setter, CarPlay UI normalize/evict, autostart toggle.
- Tiêu chí DONE toàn dự án vẫn là behavior fidelity + unknowns minh bạch + dynamic verify; compiler xanh chỉ là một gate, không thay thế evidence.
