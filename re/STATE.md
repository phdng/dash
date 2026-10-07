# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-149 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-80 (session-149): GitHub Actions session-148 (`8ce0957`) đã xanh theo user. Executable target thêm data-only `371AC` DDz1 `dropOverdueNotice` catch-all outcome từ LSDA `0x1140D8` + raw ARM64. Một action-1 range `0x371C0..0x371D4` bao DDz1 shared+retain, x19 commit và selector send; landing `0x371E4` unconditional begin/end-catch rồi return ngay, không discriminator. Runtime tách pre-x19 shared acquisition khỏi post-x19 selector send; selector exception có thể bypass retained-DDz1 release tail và giữ side effects đã apply trước throw. Unprotected prefix/tail propagate. Không DDz1 lookup/selector execution, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-149):
- R-148 data-only 371AC DDz1 dropOverdueNotice catch-all outcome: action-1 catch-all→immediate return; exact pre/post x19 DDz1 ownership timing, retained-controller release bypass, possible selector-side-effect persistence and unprotected propagation recorded.

## CURRENT TASK:
- R-148 hoàn tất local; commit-only handoff. User confirmed session-148 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-149 batch, R-149: inspect `370F8 -> 0x1140B4`. Exact 4-entry table has typed action-5 `0x37110..0x37158 -> 0x3718C`, unprotected cleanup `0x37158..0x37168`, typed action-5 `0x37168..0x37178 -> 0x3718C`, then unprotected final tail `0x37178..0x371AC`. First protected range spans DDz1 shared+retain (`x19` commit at `0x3711C`), `visible`, `livePresentRunning`, NSFileManager defaultManager+retain (`x20` commit at `0x37148`), and `fileExistsAtPath:`; range ends before fileExists result commit to `w21` at `0x37158`. Second protected range covers only `nudgePresent:` after file-manager release and the false-marker branch. Expected type at common catch `0x3718C` begin/end-catches and returns; nonmatching type resumes unwind at `0x371A8`. Split pre/post x19, pre/post x20, guard/result availability, release-bypass, and possible nudge side effects exactly. Next earlier LSDA-bearing function is `36E00 -> 0x11409C`. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-149):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-149.md`.

## TEST STATUS:
Session-148 GitHub Actions build GREEN (`8ce0957`, user-confirmed). Session-149 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
