# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-09 session-299 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-230 (session-299): Canonicalize DataRouter pure-helper ownership. Three DataRouter entry points from sessions 296-298 now delegate to the already-verified canonical NavProvider/CameraRelay helpers for exact 83FDC/84258/83EB4 semantics, eliminating duplicate implementations without changing behavior or side-effect boundaries.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-299):
- R-298 DataRouter canonical-helper delegation: `DDDataRouterIsTrueDashNotification`, `DDDataRouterSourceCode`, and `DDDataRouterProviderPayloadMatches` now delegate to the canonical helpers already compiled and verified in sessions 221-224.

## CURRENT TASK:
- R-298 implementation + docs complete locally; verify/commit-only handoff in progress. Assistant không push.

## NEXT TASK:
- Switch away from the saturated DataRouter/NavProvider seam unless a genuinely new direct exact helper is recovered. Do not re-promote 83250, 83FDC, 84258, or 83EB4: canonical executable helpers already exist. Respring and A2800 remain largely exhausted. Jailbroken-device smoke tests remain unresolved.

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

## FILES CHANGED (session-299):
- Sửa: `RECONSTRUCTION/DataRouter.m`, `RECONSTRUCTION/BUILD.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-299.md`.

## TEST STATUS:
Session-299 PASS: `python scripts/verify_reconstruction.py`; PASS: `python -m py_compile scripts/verify_reconstruction.py`; PASS: `git diff --check` (LF/CRLF warnings only). CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo; established project override applies. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
