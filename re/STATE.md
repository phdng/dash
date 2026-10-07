# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-155 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-86 (session-155): session-154 commit `2ca7d2a` đã sync origin; user yêu cầu tiếp tục nhưng chưa explicit xác nhận CI của batch đó trong turn này. Executable target thêm data-only `3640C` `+[DDz1 carPlayConnected]` typed-false outcome từ LSDA `0x113FD0` + raw ARM64. Một action-5 range `0x36418..0x3643C` bao AVExternalDevice class lookup, optional current-device send và retain-autoreleased result; range kết thúc trước pointer test/boolean commit/release. Expected catch force false; class-lookup site không có device ownership, current-device site có thể bypass temporary retained-device release. Nonmatching unwind `0x36470`; unprotected tail propagate. Không live class/device query, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-155):
- R-154 data-only 3640C `carPlayConnected` typed-false exception outcome: one typed range→false; exact class-lookup vs current-device acquisition timing, uncommitted boolean result, temporary-device release bypass, unprotected propagation and nonmatching unwind recorded.

## CURRENT TASK:
- R-154 hoàn tất local; commit-only handoff. Session-154 commit `2ca7d2a` is synced with origin; this turn did not explicitly confirm its CI result. Assistant không push.

## NEXT TASK:
- R-155: inspect `361C4 -> 0x113FBC`, block helper around `teardownWindow` + `buildShellIfNeeded`. Exact action-1 catch-all `0x361D8..0x361E4 -> 0x361FC`, then unprotected tail `0x361E4..0x3620C`. Catch return occurs before the captured result byte store at `0x361E4..0x361EC`, so covered exceptions swallow+return and leave that byte unmodified while preserving any teardown/build side effect already applied before throw. After R-155, `36158 -> 0x113FA8` has action-1 catch-all only around `removeFromSuperview` (`0x3616C..0x36170 -> 0x361B8`); catch resumes at `0x36170`, continuing weak-owner clearing and `nudgePresent:@"splash.fade"` rather than returning. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-155):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-155.md`.

## TEST STATUS:
Session-154 commit `2ca7d2a` is synchronized with origin; no explicit CI result was reported in this turn. Session-155 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
