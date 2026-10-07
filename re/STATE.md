# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-147 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-78 (session-147): GitHub Actions session-146 (`41c0195`) đã xanh theo user. Executable target thêm data-only `37284` DDz1 `dropSplashIfOverdue` catch-all outcome từ LSDA `0x114100` + raw ARM64. Một action-1 range `0x37298..0x372AC` bao DDz1 shared+retain, x19 commit và selector send; landing `0x372BC` unconditional begin/end-catch rồi return ngay, không discriminator. Runtime tách pre-x19 shared acquisition khỏi post-x19 selector send; selector exception có thể bypass retained-DDz1 release tail và giữ side effects đã apply trước throw. Unprotected prefix/tail propagate. Không DDz1 lookup/selector execution, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-147):
- R-146 data-only 37284 DDz1 dropSplashIfOverdue catch-all outcome: action-1 catch-all→immediate return; exact pre/post x19 DDz1 ownership timing, retained-controller release bypass, possible selector-side-effect persistence and unprotected propagation recorded.

## CURRENT TASK:
- R-146 hoàn tất local; commit-only handoff. User confirmed session-146 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-147 batch, R-147: inspect `371F4 -> 0x1140EC` (`dropServerNoticeNow`). Exact same action-1 shape: protected `0x37208..0x3721C -> 0x3722C`, unprotected tail `0x3721C..0x3723C`, x19 commit at `0x37214`, selector send `0x37218`. Split shared acquisition before x19 commit from selector send after commit; catch-all returns immediately and can bypass normal release tail/preserve pre-throw selector side effects. R-148 after that is `371AC -> 0x1140D8` (`dropOverdueNotice`) with protected `0x371C0..0x371D4 -> 0x371E4`. Next earlier LSDA-bearing function after 371AC is `370F8 -> 0x1140B4`. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-147):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-147.md`.

## TEST STATUS:
Session-146 GitHub Actions build GREEN (`41c0195`, user-confirmed). Session-147 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
