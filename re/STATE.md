# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-167 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-98 (session-167): Executable target thêm data-only `34020` Phase-4a display-OK UI builder outcome từ LSDA `0x113C1C`. Exact table có 9 entries: action-7 shell gate; action-5 root-view/background, label/white-color, font, và text/addSubview/installContent/present; xen giữa là unprotected style releases và result-store/final-cleanup tail. Expected typed aliases converge `0x341C0`, begin/end-catch rồi return ngay; nonmatching type resumes unwind `0x341DC`. Runtime ghi rõ root-view/label commitment, style-release milestones, possible UI side effects, present timing, cleanup bypass, và captured result-byte store skip. Không live UIKit/private presentation/ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-167):
- R-166 data-only `34020` display-OK UI builder exception outcome: exact 9-entry LSDA split, immediate expected typed catch return, root-view/label ownership and style-release timing, UI-side-effect persistence, final cleanup bypass, and present-result-byte store skip recorded.

## CURRENT TASK:
- R-166 implementation + docs complete locally; verify/commit-only handoff in progress. Assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-167 batch, R-167: inspect `33F5C -> 0x113C08`. Single action-1 catch-all `0x33F70..0x33F88 -> 0x33FA0` protects `buildShellIfNeeded`; if true `installContent`; then `present`. Landing unconditionally begin/end-catches and returns. Captured present-result byte store at `0x33F90` is outside protection, so any caught protected exception skips it. Direct next after R-167 is `33DB4 -> 0x113BE8`. 73E8/80D0/full 7E908 and jailbroken-device smoke tests remain unresolved.

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

## FILES CHANGED (session-166):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-166.md`.

## TEST STATUS:
Session-165 GitHub Actions build GREEN (`723505f`, user-confirmed). Session-166 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
