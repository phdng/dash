# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-154 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-85 (session-154): GitHub Actions session-153 (`fbf3b4f`) đã xanh theo user. Executable target thêm data-only `365A8` display.changed wrapper catch-all outcome từ LSDA `0x113FE8` + raw ARM64. Một action-1 range `0x365B0..0x365C0` bao static `display.changed`, force flag 1 và `sub_365D4`; landing `0x365C8` unconditional begin/end-catch rồi return ngay, không discriminator. Wrapper không rollback hay cleanup inner state; inner R-152 global/prefs/notify side effects có thể đã xảy ra trước escaping exception và vẫn do R-152 metadata mô tả. Unprotected wrapper paths propagate. Không inner-call execution, side-effect mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-154):
- R-153 data-only 365A8 display.changed outer-wrapper catch-all outcome: action-1 catch-all→immediate return; no discriminator, no wrapper rollback/cleanup, possible inner R-152 side-effect persistence, and unprotected propagation recorded.

## CURRENT TASK:
- R-153 hoàn tất local; commit-only handoff. User confirmed session-153 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-154 batch, R-154: inspect `3640C -> 0x113FD0`, `+[DDz1 carPlayConnected]`. Exact table: typed action-5 `0x36418..0x3643C -> 0x3644C`, then unprotected `0x3643C..0x36474`; prefix before `0x36418` is unprotected. Protected range covers `objc_getClass("AVExternalDevice")`, optional `currentCarPlayExternalDevice`, and retain-autoreleased current device. Range ends before pointer test/boolean commit and normal release. Expected catch begin/end-catches then forces false via `0x3645C`; nonmatching type resumes unwind at `0x36470`. Split class lookup from current-device acquisition so retained-device timing/release bypass is evidence-safe. After R-154, `361C4 -> 0x113FBC` is an action-1 catch-all around `teardownWindow` + `buildShellIfNeeded`, with catch return before the block-result byte store. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-154):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-154.md`.

## TEST STATUS:
Session-153 GitHub Actions build GREEN (`fbf3b4f`, user-confirmed). Session-154 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
