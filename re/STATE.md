# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-134 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-65 (session-134): GitHub Actions session-133 (`0cdbf25`) đã xanh theo user. Executable target thêm data-only `39954` recursive view-transparency exception outcome từ LSDA `0x11435C` + raw ARM64. Năm action-5 ranges quanh clearColor/background setter, opaque setter, initial subviews/enumeration, recursive-child step và next enumeration batch đều hội tụ catch `0x39AC0`: expected catch swallow rồi jump final input cleanup `0x39A6C`, bỏ toàn bộ remaining sibling/descendant traversal. Transparency writes không rollback; site-aware metadata ghi background/opaque definite-vs-possible writes, retained clearColor/subviews-array release bypass, recursive-child exception có thể bị parent swallow sau partial descendant mutation, và prior-batch completion. Cleanup action-0/unprotected propagate. Không UIColor/view setter execution, traversal/recursion hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-134):
- R-133 data-only 39954 recursive transparency exception outcome: 5 typed ranges→swallow+abort remaining traversal+final input cleanup; site-aware background/opaque write persistence, retained clearColor/subviews release-bypass, parent-swallowed recursive-child exception with possible partial descendant mutation, prior-batch timing, and cleanup action-0 unwind recorded.

## CURRENT TASK:
- R-133 hoàn tất local; commit-only handoff. User confirmed session-133 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-134 batch, R-134: inspect next earlier LSDA-bearing `39884 -> 0x114330` (`sub_39884`, top-level host/split/root transparency wrapper). Direct unwind enumeration shows no LSDA-bearing function between `39884` and `39954`. Scout decoded 6 entries with catch-all action-1 ranges `0x398A8..0x398C4`, `0x398D0..0x39904`, and `0x39910..0x3992C`, each landing at `0x3993C` which begin/end-catches and returns immediately. First range covers host clearColor/background setter; second covers host opaque setter plus split clearColor/background; third covers split opaque setter plus recursive `39954(root,0)`. Map exact host/split transparency persistence and recursive-root partial mutation before promotion. 73E8/80D0 and full 7E908 remain unresolved; dynamic device verify still needed.

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

## FILES CHANGED (session-134):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-134.md`.

## TEST STATUS:
Session-133 GitHub Actions build GREEN (`0cdbf25`, user-confirmed). Session-134 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
