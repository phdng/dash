# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-140 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-71 (session-140): GitHub Actions session-139 (`f988197`) đã xanh theo user. Executable target thêm data-only `38240` keypane/aux-scene host-construction exception outcome từ LSDA `0x1141D0` + raw ARM64. Mười action-5 ranges hội tụ catch `0x388E4`: expected catch explicit nil/release C88/C90/C78, request teardown trên retained controller, force false, release aux-scene/controller locals rồi rejoin splitHost/input cleanup. Catch không explicit clear C68/C70. Geometry range có thể để partial size/flag stores; transparency/activation ranges bắt đầu sau geometry/flags/time/generation và initial delayed dispatch đã commit. Late activation còn sau completed transparency + four staggered dispatch schedules. Không UIKit/private scene construction, global mutation, dispatch scheduling, teardown execution, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-140):
- R-139 data-only 38240 keypane/aux-scene host-construction exception outcome: 10 typed ranges→explicit C88/C90/C78 clear+teardown request+false return; C68/C70 survive local explicit clear; site-aware local release-bypass, hierarchy/key insertion, partial/definite geometry-state, delayed-dispatch and late transparency/fronting/activation timing recorded.

## CURRENT TASK:
- R-139 hoàn tất local; commit-only handoff. User confirmed session-139 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-140 batch, R-140: inspect `3815C -> 0x1141AC` plist-reader. Exact 4-entry table has typed file-read `0x38184..0x38194 -> 0x38208` and typed plist-decode/class-check `0x381A4..0x381DC -> 0x3820C`; both expected catches begin/end-catch, force result nil, release input x19, and return nil. First range ends before retained NSData x20 commit. Second starts with x20 committed and can bypass its explicit release; within the same range property-list x21 may also have been retained before throw, so split decode vs class-check sub-sites for exact x21 lifetime. Nonmatching type resumes unwind at `0x3823C`; unprotected ranges propagate. Next earlier unwind-bearing function after 3815C is `37A7C -> 0x11418C`. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-140):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-140.md`.

## TEST STATUS:
Session-139 GitHub Actions build GREEN (`f988197`, user-confirmed). Session-140 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
