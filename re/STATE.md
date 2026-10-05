# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-05 session-006_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
Session-006 đóng P3-4 (SiriProbe swallow/log/fakepress/voicecmd — F-029) + P3-5 (version/device/language — F-030) + Q-10 partial (info-schema) + P4-1 (git init + commit local re/). Chỉ còn Q-11 callees, Q-12/Q-13, P4-2, RECONSTRUCTION bodies.

## CURRENT PHASE:
Phase 1-3 DONE (trừ P0-3 blocked). Phase 4: P0-P3 static GẦN HOÀN TẤT (chỉ còn Q-11 callees, Q-12 blocks, Q-13 schedulers); còn P2-5 bodies, P4-2, dynamic verify.

## LAST COMPLETED TASK (session-006):
- 2 subagents (siriprobe, version/device+A9840) + persist EVIDENCE/siriprobe.md + EVIDENCE/version_device_ainfo.md + FINDINGS/BEHAVIOR/TODO/OPEN_QUESTIONS + git init/add re/.

## CURRENT TASK:
Checkpoint: commit + STATE/TODO/LOG session-006 (đang làm).

## NEXT TASK (session-007):
1. Q-11 callees: hostSlots/hostSplit/switchInPlace + B*/C*/D* spawn/teardown.
2. RECONSTRUCTION mở rộng: Tweak.x entry/init/prefs/IPC (APPROXIMATION).
3. P4-2 EVIDENCE chuẩn hóa.

## BLOCKERS:
- P0-3 blocked (raw asm 27E20). Không device. Git local-only (không remote/push). Q-12/Q-13 UNKNOWN.

## IMPORTANT DISCOVERIES:
- `DuoDash.plist` Filter: Bundles=[springboard,Preferences,CarPlayApp,UIKit] Mode:Any + Executables=[mediaserverd,kbd]. CONFIRMED.
- Master enable `byte_168D19` set bởi `sub_AC7A4`, mọi ctor check nó. CONFIRMED.
- Prefs source-of-truth `com.sensetechlab.duodash.settings` + cache `/var/tmp/com.sensetechlab.appbridge.plist` via `sub_74C8` publish + `notify_post(resolved)`. CONFIRMED.
- License ECDSA P-256 verify + server `https://license.sensetechlab.com/{activate,info,env,healthz}`. CONFIRMED (static).
- KeyApp là transparent keyboard relay qua `seed/kb/out` plists + `card/kbshown/kbframe/type/kblost` notifies. CONFIRMED.
- DuoDash.app chỉ là black-screen launcher (hidden, location bg). CONFIRMED.

## CONFIRMED BEHAVIOR (short):
Xem FINDINGS.md + HOOKS.md + API_MAP.md. Tóm tắt: process-gated multi-ctor init; SpringBoard AppBridge host; CarPlay eligibility cloak; UIApp keyboard/orientation hooks; SiriActivation 7 hooks; SBApplication 2 hooks; PSListController 4 hooks + 1 swizzle; Darwin+notifyd IPC; CFPreferences persistence; ECDSA license.

## UNRESOLVED QUESTIONS:
Xem OPEN_QUESTIONS.md (Q-03 blocked, Q-09 entitlements, Q-10 server schema, Q-11 ObjC bodies, Q-12 opaque blocks; Q-01/Q-02/Q-04..Q-08 closed).

## FILES CHANGED (session-006):
- Mới: `EVIDENCE/siriprobe.md`, `EVIDENCE/version_device_ainfo.md`, `LOG/session-006.md`, `.git/` (init, track re/ only).
- Sửa: FINDINGS (+F-029/F-030), BEHAVIOR (+B-19/B-20), TODO (P3-4/P3-5), OPEN_QUESTIONS (Q-10 partial).

## TEST STATUS:
Static asserts session-002..004 pass (TESTS.md). Dynamic + build vẫn pending (không device/toolchain).
