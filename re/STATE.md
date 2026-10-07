# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-131 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-62 (session-131): GitHub Actions session-130 (`35f2bd9`) đã xanh theo user. Executable target thêm data-only `3A0D0` split-host geometry exception outcome từ LSDA `0x114404` + raw ARM64. Chỉ một typed protected range `0x3A1F4..0x3A254`: expected catch `0x3A2A8` swallow rồi jump `0x3A254`, bỏ remaining geometry work nhưng vẫn release retained split-host view. Không rollback. Site-aware persistence: frame setter throw→frame có thể đã apply; center setter throw→frame chắc chắn đã apply, center có thể đã apply; gap-read throw→frame+center chắc chắn đã apply và final sync chưa start; `39260` throw→frame+center chắc chắn đã apply và final geometry sync có thể đã partial side effects. Nonmatching/unprotected propagate. Không real UI mutation, gap-file read, geometry helper execution hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-131):
- R-130 data-only 3A0D0 split-host geometry exception outcome: one typed range→swallow+skip remaining geometry+retained-view cleanup, with site-aware frame/center definite-vs-possible write persistence and final-sync partial-side-effect metadata; no rollback, nonmatching/unprotected propagate.

## CURRENT TASK:
- R-130 hoàn tất local; commit-only handoff. User confirmed session-130 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-131 batch, R-131: inspect next earlier LSDA-bearing `39D4C -> 0x1143C8` (`sub_39D4C`, scene-layer-host-container geometry/rotation predicate). Scout decoded 8 call-site entries with action-5 ranges `0x39DA4..0x39DD8 -> 0x39FE4`, `0x39DE0..0x39E30 -> 0x39FE8`, `0x39E40..0x39E48 -> 0x39FE8`, and `0x39F7C..0x39F90 -> 0x39FE4`; all converge typed catch `0x39FE8`. Expected catch begin/end-catches, forces local predicate register `w23=0`, and rejoins at `0x39E70`; nonmatching resumes unwind at `0x3A000`. Map exact loop/intermediate cleanup and downstream rotation/rebuild gating before promotion. 73E8/80D0 and full 7E908 remain unresolved; dynamic device verify still needed.

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

## FILES CHANGED (session-131):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-131.md`.

## TEST STATUS:
Session-130 GitHub Actions build GREEN (`35f2bd9`, user-confirmed). Session-131 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
