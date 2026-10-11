# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-11 session-384 (22D64 display geometry mismatch gate)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
Session-384 directly ports the pure-data geometry mismatch predicate of original `DuoDash.dylib_export_for_ai/decompile/22D64.c`, used by 218D8 and 208F4, as DDHostDisplayGeometryMismatch. Caller supplies actual shell bounds, saved shell dimensions, CarPlay display size and calculated dimensions from private sub_23D94. The 40-point saved-shell threshold and 1-point comparisons are preserved. Test smoke cases and structural verifier were updated; local checks PASS. Private acquisition/23D94, CI arm64 and device tests are outstanding.

Session-383 adds DDHostPreparedSlotsAndFlagsMatch combining only directly evidenced 218D8:213–295 conditions: normalized vs hosted BIDs, active first slot dimensions, and prepared-vs-hosted CarPlay UI flags. Mac smoke regression cases ensure each independent gate can reject. Structural verifier registers new public helper. Local reconstruction verifier/diff PASS. Additional private guards sub_22D64 and controller state not incorporated; Objective-C macOS CI, Theos arm64 and CarPlay device tests unconfirmed.

Session-382 directly ported the prepared-vs-hosted CarPlay UI flag comparison from original DuoDash dylib decompile/218D8.c:264–295 into DDHostPreparedCarPlayFlagsMatch (DuoDashShared.h/HostFlowAdapter.m), without speculating about private sub_22E40. Test-only macOS smoke now covers exact matches, missing flags, ignored trailing entries, mismatch, and malformed/zero-count inputs. Structural verifier updated; local verifier and git diff PASS. This helper remains opt-in and does not perform UI hosting. macOS Objective-C and Theos arm64 CI unconfirmed.

Session-381 hardens scripts/verify_reconstruction.py with explicit guards for both macOS arm64 Objective-C object compilation steps, the arm64 link target, lipo architecture validation, Foundation/CoreFoundation and Theos build invocation. Local verifier and diff PASS; macOS Objective-C executable/link and iOS arm64 CI outcomes remain unconfirmed.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-384):
- Ported 22D64 geometry mismatch decision and added boundary/undersized regression tests.

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

## FILES CHANGED (sessions 375–377, uncommitted):
- Sửa: `re/RECONSTRUCTION/HostFlowAdapter.m`, `re/RECONSTRUCTION/DuoDashShared.h`, `re/STATE.md`.
- Mới: `re/LOG/session-361.md`, `re/LOG/session-362.md`, `re/LOG/session-363.md`, `re/LOG/session-364.md`, `re/LOG/session-365.md`, `re/LOG/session-366.md`, `re/LOG/session-367.md`, `re/LOG/session-368.md`, `re/LOG/session-369.md`, `re/LOG/session-370.md`, `re/LOG/session-371.md`, `re/LOG/session-372.md`, `re/LOG/session-373.md`, `re/LOG/session-375.md`, `re/LOG/session-376.md`, `re/LOG/session-377.md`. Earlier sessions 346–350 already in HEAD at this session start.
- Prior sessions 335–342 are in the current clean HEAD observed at session start.

## TEST STATUS:
Theos arm64 CI GREEN was last explicitly confirmed through session-312. Session-381 structural local checks PASS (Objective-C tests not executed locally): reconstruction verifier and git diff --check (LF/CRLF warnings only). New Objective-C code is not locally compiled; arm64 CI unconfirmed. Assistant không push.
