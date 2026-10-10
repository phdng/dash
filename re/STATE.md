# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-10 session-342 (switch predicate body-termination checks)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
Session-342 strengthens structural verification of DDHostSwitchSlotCountsMatch, DDHostSwitchInteractionStateAllows, DDHostSwitchConsistencyAllows and DDHostSwitchContinuationStateAllows by requiring closing braces directly after their return expressions. Preserves uncommitted Sessions 335–341. No runtime behavior changed; arm64 CI unconfirmed.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-342):
- Hardened four switch count/interaction/consistency/continuation predicate checks to reject trailing statements after return.

## CURRENT TASK:
- Continue bounded Phase-5 evidence-safe helper promotions after user-confirmed green CI. No speculative private-hook wiring. Assistant không push.

## NEXT TASK:
- Continue the `218D8` toggle slice only where constants are exact. `paneratio` still contains unresolved `&stru_20+18` fallback metadata, so do not promote it until that constant is recovered. HUD/BLE and A2720 remain insufficiently evidenced for exact promotion. Jailbroken-device smoke tests remain unresolved.

## BLOCKERS:
- Workspace hiện tại Windows không có Xcode/iOS SDK nên chưa compiler-build local. P0-3 vẫn blocked (raw asm 27E20); không device jailbroken; các private-hook contracts chưa đủ evidence vẫn chưa đưa vào executable target.

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

## FILES CHANGED (sessions 335–342, uncommitted):
- Sửa: `scripts/verify_reconstruction.py`, `re/STATE.md`.
- Mới: `re/LOG/session-335.md`, `re/LOG/session-336.md`, `re/LOG/session-337.md`, `re/LOG/session-338.md`, `re/LOG/session-339.md`, `re/LOG/session-340.md`, `re/LOG/session-341.md`, `re/LOG/session-342.md`.
- Sessions 320–334 already appear in HEAD `750902c` (external commit detected at session start).

## TEST STATUS:
Theos arm64 CI GREEN was last explicitly confirmed through session-312. Session-342 local checks PASS: reconstruction verifier, Python py_compile and git diff --check (LF/CRLF warnings only). Current arm64 CI status unconfirmed. Assistant không push.
