# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-159 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-90 (session-159): GitHub Actions session-158 (`93c1aea`) đã xanh theo user. Executable target thêm data-only `358F0` splash presentation/preferences/image/dispatch exception outcome từ LSDA `0x113EDC` + raw ARM64. Exact table có 29 call-site entries. Initial no-splash marker probe dùng action index 7 = typed catch-only; các protected ranges còn lại dùng action index 5 = typed catch + cleanup-chain. Tất cả expected typed exceptions hội tụ common catch `0x35F84` rồi return ngay; nonmatching unwind, action-5 ranges có thể qua local cleanup landing. Runtime tách marker manager, selected view/bounds, preference load+parse, image-path probing, removeSplash, splash UIView/image hierarchy, global splash store, duration parsing, disabled-selection removeSplash, và unprotected deadline/weak/two-dispatch tail. `qword_163C30`, weak captures và cả hai dispatch_after nằm unprotected nên exceptions propagate. Không live prefs/file/image/UI/dispatch/global/ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-159):
- R-158 data-only 358F0 splash presentation/preferences/image/dispatch exception outcome: 29-entry LSDA with action-7 typed-only marker probe vs action-5 typed+cleanup ranges; exact ownership/side-effect milestones, global splash-store timing, expected catch return, nonmatching unwind, and unprotected deadline/weak/two-dispatch propagation recorded.

## CURRENT TASK:
- R-158 hoàn tất local; commit-only handoff. User confirmed session-158 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-159 batch, R-159: inspect `35880 -> 0x113EC8`. Exact table has action-1 catch-all `0x35894..0x358D4 -> 0x358E0`, then unprotected tail. Protected path covers layer opacity read and, only when opacity==0.99, CATransaction begin -> setDisableActions:YES -> setOpacity:1.0 -> commit. Landing `0x358E0` unconditional begin/end-catches and returns; no discriminator. Split opacity-read exception from transaction begin/disable/setOpacity/commit so prior side effects are preserved and no rollback is asserted. After R-159, `356A0 -> 0x113E98` is a typed multi-range weak-owner/layer-opacity/nudge helper with CATransaction, counter decrement and delayed dispatch; decode separately. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-159):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-159.md`.

## TEST STATUS:
Session-158 GitHub Actions build GREEN (`93c1aea`, user-confirmed). Session-159 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
