# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-05 session-009_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
Session-009 đóng spikeHostSlots: nội bộ + skipEvict truth (F-035) + kill-vs-unhost verdict (F-036) + P4-2 partial. Chỉ còn evictFromPhone, Q-10 validators, Q-12/Q-13, Tweak.x bodies, dynamic verify.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT CƠ BẢN (tàn dư: evictFromPhone, DDz3 bodies, Q-10 validators, Q-12/Q-13); P0-P3 + P4-1 + P4-2(partial) DONE; còn Tweak.x bodies mở rộng, dynamic verify.

## LAST COMPLETED TASK (session-009):
- 2 subagents (spikeHostSlots chain, 85B8/7764C) + persist 2 EVIDENCE + FINDINGS/BEHAVIOR/OPEN_QUESTIONS + P4-2 audit (partial).

## CURRENT TASK:
Checkpoint: commit + STATE/TODO/LOG session-009 (đang làm).

## NEXT TASK (session-010):
1. evictFromPhone (3AE50 FULL) — mảnh skipEvict cuối.
2. Tweak.x bodies: present/commit/ack path.
3. AA9FC/AAAD0 validators (Q-10) — nhỏ.

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

## FILES CHANGED (session-009):
- Mới: `EVIDENCE/spike_hostslots.md`, `EVIDENCE/evict_helpers.md`, `LOG/session-009.md`.
- Sửa: FINDINGS (+F-035/F-036), BEHAVIOR (+B-25/B-26), TODO (P4-2), OPEN_QUESTIONS (Q-11).

## TEST STATUS:
Static asserts session-002..004 pass (TESTS.md). Dynamic + build vẫn pending (không device/toolchain).
