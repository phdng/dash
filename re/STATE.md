# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-157 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-88 (session-157): GitHub Actions session-156 (`942c182`) đã xanh theo user. Executable target thêm data-only `36158` splash-fade completion catch-resume outcome từ LSDA `0x113FA8` + raw ARM64. Một action-1 range `0x3616C..0x36170` chỉ bao `removeFromSuperview`; landing `0x361B8` unconditional begin/end-catch rồi branch lại `0x36170`, không return. Caught path tiếp tục weak-owner acquisition, conditional matching owner-slot clear/release, `nudgePresent:@"splash.fade"`, và final weak-retained-owner release. Remove side effects có thể đã apply trước throw; toàn bộ continuation sau catch unprotected và có thể propagate. Không live UI/weak-owner mutation, nudge execution, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-157):
- R-156 data-only 36158 splash-fade completion catch-resume outcome: action-1 removeFromSuperview catch-all→resume weak-owner cleanup/nudge continuation; possible remove side-effect persistence and later unprotected propagation recorded.

## CURRENT TASK:
- R-156 hoàn tất local; commit-only handoff. User confirmed session-156 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-157 batch, R-157: inspect `35FBC -> 0x113F94`. Exact table has action-0 cleanup `0x3606C..0x36084 -> 0x360B4` around copied-weak capture setup plus `+[UIView animateWithDuration:animations:completion:]`; landing preserves the active exception, destroys the copied weak capture, then resumes unwind at `0x360C4`. Map copied weak lifetime, retained animation/completion captures, possible animation side effects before throw, weak cleanup ordering, and normal post-call releases outside protection. Next earlier LSDA-bearing function is `358F0 -> 0x113EDC`. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-157):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-157.md`.

## TEST STATUS:
Session-156 GitHub Actions build GREEN (`942c182`, user-confirmed). Session-157 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
