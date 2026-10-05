# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-05 session-010_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
Session-010 đóng evictFromPhone (F-037) + AA validators/A7E04 đính chính (F-038) + Tweak.x present/commit/ack bodies. Chỉ còn DDz3 bodies, Q-10 tàn dư, Q-12/Q-13, dynamic verify.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT CƠ BẢN (tàn dư: DDz3 bodies/buildKitLevel, Q-10 mapping số/whitelist/MITM, Q-12/Q-13); P0-P4 DONE (P4-2 partial); còn Tweak.x bodies chi tiết, dynamic verify.

## LAST COMPLETED TASK (session-010):
- 2 subagents (evictFromPhone, AA-validators/A7E04) + persist 2 EVIDENCE + FINDINGS/BEHAVIOR/OPEN_QUESTIONS + Tweak.x bodies.

## CURRENT TASK:
Checkpoint: commit + STATE/TODO/LOG session-010 (đang làm).

## NEXT TASK (session-011):
1. DDz3 bodies trọng tâm: commitSlotBids/resolveSlotBids/commitPick.
2. 162E60 setter trace (cpuiGen nguồn).
3. Đóng project static: FINAL verdict + tag.

## BLOCKERS:
- P0-3 blocked (raw asm 27E20). Không device. Git local-only. Q-12/Q-13 UNKNOWN.

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

## FILES CHANGED (session-010):
- Mới: `EVIDENCE/evict_from_phone.md`, `EVIDENCE/aa_validators.md`, `LOG/session-010.md`.
- Sửa: FINDINGS (+F-037/F-038), BEHAVIOR (+B-27/B-28), OPEN_QUESTIONS (Q-10/Q-11), RECONSTRUCTION/Tweak.x.

## TEST STATUS:
Static asserts session-002..004 pass (TESTS.md). Dynamic + build vẫn pending (không device/toolchain).
