# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-129 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-60 (session-129): GitHub Actions session-128 (`3e36eaa`) đã xanh theo user. Executable target thêm data-only `3B8F8` cnabBuildSceneHost exception outcome từ LSDA `0x1144C4` + raw ARM64. Exact table có 11 action-5 ranges: 10 range common typed catch `0x3BBA4`→`resetHostingState`→force nil; 3 protected normal failure-reset ranges vì vậy retry reset một lần. Riêng `0x3BAA4..0x3BAEC` (`_deviceAppViewController`/home-grabber decoration) catch `0x3BB74` swallow rồi rejoin `0x3BB24`, giữ/return main view đã acquire. Post-controller ranges ghi nhận `_appVC` đã store; common catch có thể bypass normal retained-intermediate releases, special catch có thể bypass retained device-controller release. Catch-internal reset action-0 end-catch→unwind; nonmatching/unprotected propagate. Không private construction/view/device/reset execution hay live state mutation.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-129):
- R-128 data-only 3B8F8 cnabBuildSceneHost exception outcome: 10 typed ranges→common resetHostingState+nil, 3 failure-reset ranges retry once, special private device/home-grabber range→swallow+return acquired main view, nested catch reset action-0→end-catch+unwind; `_appVC` timing and possible retained-intermediate/device-controller release bypass recorded.

## CURRENT TASK:
- R-128 hoàn tất local; commit-only handoff. User confirmed session-128 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-129 batch, R-129: inspect next earlier LSDA-bearing `3AE50 -> 0x114424` (`evictFromPhoneThen:`). Scout decoded 25 call-site entries with 12 action-5 ranges, three action-0 ranges (`0x3AEE4..0x3AF00`, `0x3AF14..0x3AF50`, `0x3B29C..0x3B2A4`), and unprotected gaps. All action-5 landing stubs `0x3B25C..0x3B278` converge at typed catch `0x3B278`; expected type begin-catches, invokes the retained completion/fallback block, end-catches, and rejoins final cleanup at `0x3B0BC`. Nonmatching resumes unwind; nested fallback-block throw is action-0 and ends the active catch before unwind. Map exact per-range scheduling/executeTransition state and callback timing before promotion. 73E8/80D0 and full 7E908 remain unresolved; dynamic device verify still needed.

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

## FILES CHANGED (session-129):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-129.md`.

## TEST STATUS:
Session-128 GitHub Actions build GREEN (`3e36eaa`, user-confirmed). Session-129 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
