# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-139 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-70 (session-139): GitHub Actions session-138 (`f1ef1bf`) đã xanh theo user. Executable target thêm data-only `3896C` property-list writer exception outcome từ LSDA `0x114250` + raw ARM64. Serialization/write typed catches trả false và final-clean arguments; write site có retained NSData committed nên có thể bypass data release. Post-write attributes range chỉ reachable sau write success; expected catch cố ý trả true, vẫn release retained data + final args, nhưng có thể bypass manager/dictionary releases. Runtime tách file-manager acquisition, permissions-dictionary construction, setAttributes với temporary-vs-committed ownership và possible partial attributes application. Action-0 cleanup/unprotected propagate; nonmatching unwind. Không plist serialization/file I/O/chmod, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-139):
- R-138 data-only 3896C property-list writer exception outcome: serialization/write typed catches→false, post-success attribute typed catches→true; exact retained-data/manager/dictionary lifetime, release-bypass, partial attributes timing, action-0 cleanup unwind and final-argument continuation recorded.

## CURRENT TASK:
- R-138 hoàn tất local; commit-only handoff. User confirmed session-138 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-139 batch, R-139: inspect next earlier LSDA-bearing `38240 -> 0x1141D0` (`sub_38240`, keypane/aux-scene host construction). Exact 16-entry table has 10 action-5 ranges: `0x3852C..0x38590`, `0x38598..0x385A4`, `0x385A8..0x38680`, `0x38688..0x386AC`, `0x386BC..0x386C0`, `0x386C0..0x386D8`, `0x386D8..0x3870C`, `0x3875C..0x387A0`, `0x38814..0x38818`, and `0x38878..0x38890`; all landing stubs converge common typed catch `0x388E4`. Expected catch clears/releases globals `qword_163C88` and `qword_163C90`, invokes teardown on retained DDz2 x21, clears/releases `qword_163C78`, ends catch, forces result false, releases retained aux scene x22/DDz2 x21, then rejoins splitHost/input cleanup. Protected ranges span outer/inner UIView construction+transparency, splitHost addSubview, 38E14 gap read, left/right 38EF8 key creation+addSubview, 39260 geometry/global-state commit, 39884 transparency wrapper, and late bringSubviewToFront/30F48 activation. Map exact prior global stores (especially C68/C70/C78/C88/C90 and size/generation flags), local-view/key release bypass, and which late state survives catch before promotion. 73E8/80D0 and full 7E908 remain unresolved; dynamic device verify still needed.

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

## FILES CHANGED (session-139):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-139.md`.

## TEST STATUS:
Session-138 GitHub Actions build GREEN (`f1ef1bf`, user-confirmed). Session-139 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
