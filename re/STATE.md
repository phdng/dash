# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-156 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-87 (session-156): GitHub Actions session-155 (`0be4c67`) đã xanh theo user. Executable target thêm data-only `361C4` shell-rebuild block catch-all outcome từ LSDA `0x113FBC` + raw ARM64. Một action-1 range `0x361D8..0x361E4` bao `teardownWindow` + `buildShellIfNeeded`; landing `0x361FC` unconditional begin/end-catch rồi return ngay. Range kết thúc đúng trước captured result-byte store `0x361E4..0x361EC`, nên caught path không ghi captured byte. Teardown-site có thể giữ partial teardown side effects; build-site chỉ reachable sau teardown return và có thể giữ partial build side effects. Unprotected store/tail propagate. Không teardown/build execution, block-state mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-156):
- R-155 data-only 361C4 shell-rebuild block catch-all outcome: action-1 catch-all→immediate return before captured result-byte store; teardown/build side-effect timing and unprotected propagation recorded.

## CURRENT TASK:
- R-155 hoàn tất local; commit-only handoff. User confirmed session-155 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-156 batch, R-156: inspect `36158 -> 0x113FA8`. Exact action-1 catch-all `0x3616C..0x36170 -> 0x361B8` protects only `removeFromSuperview`; landing unconditionally begin/end-catches then branches back to `0x36170`, so expected catch does NOT return. It continues weak-owner acquisition, conditional owner-slot clear/release, `nudgePresent:@"splash.fade"`, and final weak-retained-owner release. Record possible remove side effect before throw, continued cleanup/nudge after catch, and unprotected later propagation. Next earlier LSDA-bearing function is `35FBC -> 0x113F94`, a larger UIView animation/capture-cleanup helper. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-156):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-156.md`.

## TEST STATUS:
Session-155 GitHub Actions build GREEN (`0be4c67`, user-confirmed). Session-156 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
