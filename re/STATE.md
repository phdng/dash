# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-135 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-66 (session-135): GitHub Actions session-134 (`7fa7b80`) đã xanh theo user. Executable target thêm data-only `39884` top-level host/split/root transparency catch-all outcome từ LSDA `0x114330` + raw ARM64. Ba action-1 ranges đều landing `0x3993C` và unconditional begin/end-catch rồi return ngay. Runtime tách 5 semantic sites để giữ exact write ordering: host background possible; host opaque sau host background definite; split background sau host background+opaque definite; split opaque sau split background definite; recursive root chỉ sau host+split background/opaque đều definite. Background sites có possible retained-clearColor release bypass; recursive-root propagation có thể bị outer wrapper swallow sau partial subtree mutation. Không UIColor/view setter execution, recursion/live ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-135):
- R-134 data-only 39884 top-level transparency catch-all outcome: 3 catch-all ranges split into 5 semantic sites with exact host/split definite-vs-possible background/opaque writes, immediate-return continuation, possible retained clearColor release bypass, and outer-swallowed recursive-root partial-subtree mutation metadata.

## CURRENT TASK:
- R-134 hoàn tất local; commit-only handoff. User confirmed session-134 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-135 batch, R-135: inspect next earlier LSDA-bearing `38EF8 -> 0x114308` (`sub_38EF8`, `CNABKeyPaneHideKey` construction). Scout decoded 4 entries: unprotected `0x38EF8..0x39050`, typed action-5 `0x39050..0x39064 -> 0x39244`, typed action-5 `0x39070..0x390A4 -> 0x39248`, then unprotected tail. Both typed ranges converge catch `0x39248`; expected type begin/end-catches then jumps to `0x390C8`, abandoning SF Symbol configuration/image path and continuing the manual chevron UIView/UIBezierPath/CAShapeLayer fallback. First range covers `UIImageSymbolConfiguration configurationWithPointSize:weight:` + retain; second covers `UIImage systemImageNamed:withConfiguration:` + retain and optional `UIImageView initWithImage:`. Catch may bypass retained symbol-configuration/image releases depending on throw timing. Nonmatching type resumes unwind at `0x3925C`; manual-fallback construction is unprotected. Map exact retained-object timing and fallback continuation before promotion. 73E8/80D0 and full 7E908 remain unresolved; dynamic device verify still needed.

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

## FILES CHANGED (session-135):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-135.md`.

## TEST STATUS:
Session-134 GitHub Actions build GREEN (`7fa7b80`, user-confirmed). Session-135 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
