# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-09 session-303 (array-nullability syntax repair)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-231 + CI HEADER REPAIR (session-303): Theos confirmed the session-302 spelling `name[N] _Nonnull` is invalid C/Objective-C declarator syntax. The six public sized-array parameters are now written as ABI-equivalent pointer parameters (`T * _Nonnull` / `const T * _Nonnull`), matching implementations that dereference/index them without null guards.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-303):
- Repaired the CI array-nullability syntax regression by replacing sized-array parameter spellings with explicit nonnull pointer spellings in declarations and definitions; strengthened the verifier against the invalid `[N] _Nonnull` form.

## CURRENT TASK:
- Await the next Theos CI result from the session-303 repair. If Clang advances, fix only the next concrete diagnostic. Assistant không push.

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

## FILES CHANGED (session-303):
- Sửa: `RECONSTRUCTION/DuoDashShared.h`, `RECONSTRUCTION/Migration.m`, `RECONSTRUCTION/CrashReporting.m`, `scripts/verify_reconstruction.py`, `STATE.md`.
- Mới: `LOG/session-303.md`.

## TEST STATUS:
Session-303 local static gates PASS: public header no longer uses sized-array parameter declarators for the six affected contracts; declarations/definitions use explicit `_Nonnull` pointer types; `python scripts/verify_reconstruction.py`; `python -m py_compile scripts/verify_reconstruction.py`; `git diff --check` (LF/CRLF warnings only). Exact arm64 Theos compile remains CI-only on this Windows workspace. CatDesk standard verifier remains NOT_CONFIGURED. Assistant không push.
