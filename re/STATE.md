# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-142 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-73 (session-142): GitHub Actions session-141 (`b45bfb2`) đã xanh theo user. Executable target thêm data-only `37A7C` keyboard-lost recovery summary exception outcome từ LSDA `0x11418C` + raw ARM64. Một action-5 range bao DDz2 shared+retain và keyPaneSceneSummary+retain; expected catch không return mà substitute static fallback summary rồi jump `0x37B18`, tiếp tục NSFileManager marker/rebuild flow. Runtime tách pre-x21 shared acquisition (temporary controller only) khỏi summary acquisition (retained DDz2 committed, temporary summary possible), với exact local release-bypass timing. Unprotected/nonmatching propagate/unwind. Không DDz2 calls, marker/rebuild execution, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-142):
- R-141 data-only 37A7C keyboard-lost recovery summary exception outcome: expected typed catch substitutes fallback scene summary and continues existing marker/rebuild flow; exact pre/post x21 DDz2 commit, temporary controller/summary release-bypass, unprotected propagation and nonmatching unwind recorded.

## CURRENT TASK:
- R-141 hoàn tất local; commit-only handoff. User confirmed session-141 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-142 batch, R-142: inspect `37924 -> 0x114178` CarPlay UI-status callback. Exact 2-entry table has one action-1 catch-all range `0x3793C..0x37958 -> 0x37968` covering `+[DDz1 shared]` + retain and `noteCarPlayUIStatus:gen:ok:`. Landing unconditionally begin-catches/end-catches and returns immediately; no discriminator/nonmatching path. Split DDz1 shared acquisition vs callback send timing: shared acquisition may throw before x19 commit; callback send runs with retained DDz1 x19 committed and catch skips its normal release/tail call. Any callback side effect before throw can persist. Next earlier LSDA-bearing function is `375B8 -> 0x11415C`: one typed range `0x375EC..0x37610 -> 0x37628` around geometry helpers, CGRectIsNull, center getter and setCenter; expected catch jumps directly to cleanup. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-142):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-142.md`.

## TEST STATUS:
Session-141 GitHub Actions build GREEN (`b45bfb2`, user-confirmed). Session-142 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
