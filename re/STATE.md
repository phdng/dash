# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-161 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-92 (session-161): GitHub Actions session-160 (`07e9ad4`) đã xanh theo user. Executable target thêm data-only `356A0` splash-nudge preparation typed outcome từ LSDA `0x113E98` + raw ARM64. Ba action-5 ranges tách admission (`isHidden`/owner gate/`livePresentRunning`), layer acquisition + opacity/animation probe, và nil-animation-gated CATransaction begin/disable/setOpacity:0.99/commit. Weak owner x19 + retained target x20 commit trong unprotected prefix; layer x21 commit trong range 2; animation result vẫn temporary khi range 2 kết thúc trước x23 commit. Expected type common catch `0x35858` return ngay, có thể bypass normal owner/target/layer releases; nonmatching unwind `0x3587C`. Counter decrement + retained layer block capture + 50ms dispatch_after + normal releases nằm unprotected, nên exceptions propagate while prior counter/dispatch side effects may persist. Không live weak-owner/layer/CATransaction/counter/dispatch mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-161):
- R-160 data-only 356A0 splash-nudge preparation typed exception outcome: three action-5 ranges with committed weak-owner/target admission, pre/post-layer commit opacity/animation probing, nil-animation-gated CATransaction opacity-0.99 mutation, expected catch return/release bypass, and unprotected counter/deferred-dispatch propagation recorded.

## CURRENT TASK:
- R-160 hoàn tất local; commit-only handoff. User confirmed session-160 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-161 batch, R-161: inspect `35328 -> 0x113E30`, `-[CNABLivePresenter restoreTargets]`. Exact LSDA has 16 call-site entries, mixing typed action-5 ranges and action-0 cleanup ranges. Typed landing aliases (`0x3551C/20/28/30/34`) converge at `0x35534`; expected type begin/end-catches then branches to epilogue `0x354DC`, **skipping final `+[CATransaction commit]` at `0x354D4`**. Action-0/nonmatching paths resume unwind via `0x3552C`. Map initial targets/CATransaction setup, fast-enumeration collection lifetime, CALayer type filtering, per-layer retain/opacity/animation probing, setOpacity:1.0 side effects, enumeration mutation, local releases, and which catches leave transaction begun but uncommitted. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-161):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-161.md`.

## TEST STATUS:
Session-160 GitHub Actions build GREEN (`07e9ad4`, user-confirmed). Session-161 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
