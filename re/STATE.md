# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-141 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-72 (session-141): GitHub Actions session-140 (`ca03cf3`) đã xanh theo user. Executable target thêm data-only `3815C` plist-reader exception outcome từ LSDA `0x1141AC` + raw ARM64. Hai typed ranges hội tụ catch `0x3820C`: expected catch begin/end-catch, force nil, chỉ cleanup retained input x19 rồi return nil. File-read range kết thúc trước NSData x20 commit; plist-decode subsite bắt đầu với x20 committed và có thể bypass release; dictionary-type-check subsite bắt đầu sau plist x21 commit và có thể bypass cả x21+x20 releases. Unprotected/nonmatching propagate/unwind. Không file read, plist decode/type-check, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-141):
- R-140 data-only 3815C plist-reader exception outcome: 2 typed ranges→nil fallback+input cleanup; exact pre-x20 file read, committed NSData during plist decode, committed plist+NSData during dictionary type-check, release-bypass, unprotected propagation and nonmatching unwind recorded.

## CURRENT TASK:
- R-140 hoàn tất local; commit-only handoff. User confirmed session-140 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-141 batch, R-141: inspect `37A7C -> 0x11418C` keyboard-lost recovery. Exact 3-entry table has one typed action-5 range `0x37AD0..0x37AEC -> 0x37C20` covering `+[DDz2 shared]` retain plus `keyPaneSceneSummary` retain. Expected catch `0x37C20` begin/end-catches, substitutes fallback `&stru_146AD8` into x20, then jumps to `0x37B18` and continues NSFileManager marker/rebuild flow instead of returning. Split shared-acquisition vs scene-summary sub-sites: shared-acquisition may end before x21 commit; summary subsite runs with retained DDz2 x21 committed and can bypass its normal release, while a retained summary result may exist before x22 commit and its release can also be bypassed. Nonmatching type resumes unwind at `0x37C3C`; unprotected async-dispatch/rebuild/cleanup paths propagate. Next earlier unwind-bearing function is `37924 -> 0x114178`. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-141):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-141.md`.

## TEST STATUS:
Session-140 GitHub Actions build GREEN (`ca03cf3`, user-confirmed). Session-141 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
