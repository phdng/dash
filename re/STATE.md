# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-160 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-91 (session-160): GitHub Actions session-159 (`65a413d`) đã xanh theo user. Executable target thêm data-only `35880` splash-opacity CATransaction catch-all outcome từ LSDA `0x113EC8` + raw ARM64. Một action-1 range `0x35894..0x358D4` bao layer opacity read và conditional CATransaction begin -> setDisableActions:YES -> setOpacity:1.0 -> commit; landing `0x358E0` unconditional begin/end-catch rồi return ngay, không discriminator. Runtime tách opacity read, begin, disable-actions, opacity mutation và commit; mỗi site ghi exact prior effects đã hoàn tất và current-call side effect có thể đã apply trước throw. Catch không chạy compensating commit/rollback hay opacity restore. Unprotected tail propagate. Không live CALayer/CATransaction/UI mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-160):
- R-159 data-only 35880 splash-opacity CATransaction catch-all outcome: action-1 catch-all→immediate return with exact opacity/begin/disable/setOpacity/commit side-effect timing, no compensating transaction/opacity rollback, and unprotected-tail propagation recorded.

## CURRENT TASK:
- R-159 hoàn tất local; commit-only handoff. User confirmed session-159 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-160 batch, R-160: inspect `356A0 -> 0x113E98`. Exact 6-entry table: unprotected `0x356A0..0x356DC`; typed action-5 `0x356DC..0x356F8 -> 0x35858`; typed `0x356FC..0x3573C -> 0x35854`; unprotected `0x3573C..0x35750`; typed `0x35750..0x35778 -> 0x35854`; unprotected `0x35778..0x35880`. `0x35854` aliases common discriminator `0x35858`; expected type begin/end-catches and returns immediately, nonmatching resumes unwind at `0x3587C`. Map weak-owner and retained target/layer lifetime, hidden/livePresent admission, layer opacity and opacity-animation probe, CATransaction begin/disable/setOpacity/commit timing, counter decrement, retained layer capture, delayed dispatch, and which normal releases are bypassed by each catch. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-160):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-160.md`.

## TEST STATUS:
Session-159 GitHub Actions build GREEN (`65a413d`, user-confirmed). Session-160 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
