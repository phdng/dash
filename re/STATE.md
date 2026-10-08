# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-169 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-100 (session-169): Executable target thêm data-only `33DB4` mat-alpha resolver outcome từ LSDA `0x113BE8` + raw ARM64. Exact table có two typed action-5 ranges: `0x33DCC..0x33DF0 -> 0x33E40` cho NSString file-read/retain/length và `0x33DF8..0x33E00 -> 0x33E3C` cho `doubleValue`; tail còn lại unprotected. Raw code xác nhận path `/var/tmp/duodash_ab_mat_alpha`, valid parsed range `(0,1]`, fallback exact `254/255 = 0.996078431372549`. Expected type catch trả fallback qua epilogue và bypass normal retained-string release `0x33E20`; nonmatching resume unwind `0x33E5C`. Không live file/Foundation/ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-169):
- R-168 data-only `33DB4` mat-alpha resolver exception outcome: exact two-range typed LSDA, `/var/tmp/duodash_ab_mat_alpha`, exact 254/255 fallback, temporary-vs-committed NSString timing, retained-string cleanup bypass, and nonmatching unwind recorded.

## CURRENT TASK:
- R-168 implementation + docs complete locally; verify/commit-only handoff in progress. Assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-169 batch, locate/decode the next earlier LSDA-bearing path below `33DB4` before promotion. `33D18`, `33D24`, and `33D70` are small helper/block-lifetime functions without local catch semantics in the export; `33A00` is decompiled as an exception landing/cleanup handler that jumps back to `0x339A4`, so its owning function/LSDA must be mapped from raw unwind metadata before assigning the next R-number. 73E8/80D0/full 7E908 and jailbroken-device smoke tests remain unresolved.

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
