# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-136 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-67 (session-136): GitHub Actions session-135 (`686806a`) đã xanh theo user. Executable target thêm data-only `38EF8` CNABKeyPaneHideKey SF-Symbol exception fallback outcome từ LSDA `0x114308` + raw ARM64. Hai typed action-5 ranges hội tụ catch `0x39248`: expected catch bỏ remaining SF-Symbol path rồi jump `0x390C8` để tiếp tục manual chevron UIView/UIBezierPath/CAShapeLayer fallback và phần constructor còn lại. Exact ownership timing: config range đầu kết thúc trước `x24` assignment nên không record config release bypass; range hai bắt đầu với config đã retained, image-lookup throw có thể bypass config release, image-view-init throw xảy ra sau `x25` retained image commit nên có thể bypass cả image+config releases. Manual fallback/later tail unprotected; nonmatching unwind. Không UIKit symbol/image/fallback construction hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-136):
- R-135 data-only 38EF8 CNABKeyPaneHideKey SF-Symbol exception outcome: 2 typed symbol ranges→manual-chevron fallback continuation, with exact config/image retained-object timing, config-only vs image+config release-bypass, unprotected fallback/tail propagation, and nonmatching-type unwind metadata.

## CURRENT TASK:
- R-135 hoàn tất local; commit-only handoff. User confirmed session-135 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-136 batch, R-136: inspect next earlier LSDA-bearing `38E14 -> 0x1142DC` (`sub_38E14`, `/var/tmp/duodash_ab_keypane_hidegap` parser). Scout decoded 6 entries: typed action-5 `0x38E34..0x38E50 -> 0x38ED4` (file read + retain), typed `0x38E50..0x38E58 -> 0x38ED8` (retained string + length), unprotected `0x38E58..0x38E6C` (includes `objc_retainAutorelease` before UTF8String), typed `0x38E6C..0x38E70 -> 0x38ED8` (UTF8String), typed `0x38E7C..0x38E88 -> 0x38ED0` (`strtod`), then unprotected tail. Expected catches converge at `0x38ED8`, begin/end-catch, force default `71.0`, and return via `0x38EB4`; from length/UTF8/parse sites onward the retained NSString explicit release at `0x38EAC` is bypassed. First file-read range ends before `x19` assignment, so no established retained-string release bypass there. Nonmatching type resumes unwind at `0x38EF4`. Map exact default-value/release-bypass/unprotected-retainAutorelease behavior before promotion. 73E8/80D0 and full 7E908 remain unresolved; dynamic device verify still needed.

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

## FILES CHANGED (session-136):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-136.md`.

## TEST STATUS:
Session-135 GitHub Actions build GREEN (`686806a`, user-confirmed). Session-136 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
