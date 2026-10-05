# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-05 session-007_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
Session-007 đóng Q-11 hosting engine (F-031) + spawn/teardown/KB/poll (F-032) + P2-5 Tweak.x APPROXIMATION. Chỉ còn 2410C/DDz-core, Q-10 validators, Q-12/Q-13, P4-2, dynamic verify.

## CURRENT PHASE:
Phase 1-3 DONE (trừ P0-3 blocked). Phase 4 static GẦN HOÀN TẤT (chỉ còn 2410C/2565C async, DDz classes, Q-10 validators, Q-12/Q-13); còn P4-2, dynamic verify.

## LAST COMPLETED TASK (session-007):
- 2 subagents (hosting engine, spawn/teardown+KB+poll) + persist 2 EVIDENCE + Tweak.x APPROXIMATION + FINDINGS/BEHAVIOR/TODO/OPEN_QUESTIONS.

## CURRENT TASK:
Checkpoint: commit + STATE/TODO/LOG session-007 (đang làm).

## NEXT TASK (session-008):
1. 2410C async body (slots/evict/DDz present) — Q-11 lõi cuối.
2. DDz1/DDz2 class inventory + D684.
3. Đánh giá STOP conditions → coverage verdict.

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

## FILES CHANGED (session-007):
- Mới: `EVIDENCE/hosting_engine.md`, `EVIDENCE/spawn_teardown_kb.md`, `RECONSTRUCTION/Tweak.x`, `LOG/session-007.md`.
- Sửa: FINDINGS (+F-031/F-032), BEHAVIOR (+B-21/B-22), TODO (P2-5), OPEN_QUESTIONS (Q-11).

## TEST STATUS:
Static asserts session-002..004 pass (TESTS.md). Dynamic + build vẫn pending (không device/toolchain).
