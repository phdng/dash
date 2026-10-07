# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-128 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-59 (session-128): GitHub Actions session-127 (`f63a84d`) đã xanh theo user. Executable target thêm data-only `3BBF0` spikeCreateSlot exception outcome từ LSDA `0x114538` + raw ARM64. Exact table có 12 action-5 ranges: 11 range common typed catch `0x3C15C`→format exception reason→route qua `degradeSlot` và return degraded result; 3 normal failure-degrade ranges vì vậy retry degrade một lần. Riêng `0x3BF00..0x3BF48` (`_deviceAppViewController`/home-grabber decoration) catch `0x3C12C` swallow rồi rejoin `0x3BF50`, giữ/return main view không degrade. Mọi protected range đều sau spike flag + hosted-bid/native-size commit; post-controller ranges ghi nhận controller ivar đã store trước call. Catch-internal formatting/degrade action-0 end-catch→unwind; nonmatching/unprotected propagate. Không private construction/view/device/degrade execution hay live state mutation.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-128):
- R-127 data-only 3BBF0 spikeCreateSlot exception outcome: 11 typed ranges→common exception-reason degrade result, 3 failure-degrade ranges retry once, special private device/home-grabber range→swallow+return existing main view, nested catch degrade action-0→end-catch+unwind; pre-protected spike/bid/native and controller-store timing recorded.

## CURRENT TASK:
- R-127 hoàn tất local; commit-only handoff. User confirmed session-127 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-128 batch, R-128: inspect next earlier LSDA-bearing `3B8F8 -> 0x1144C4` (`cnabBuildSceneHostForBid:displaySize:`). Scout decoded 18 entries with 11 action-5 ranges, one action-0 range `0x3BBC4..0x3BBCC`, and unprotected gaps. Raw tail shows special typed catch `0x3BB74`→rejoin `0x3BB24`, while common catch `0x3BBA4` catches expected type, invokes `resetHostingState`, then forces nil return; nested reset failure action-0 ends catch and resumes unwind. Map exact per-range controller/view state before promotion. 73E8/80D0 and full 7E908 remain unresolved; dynamic device verify still needed.

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

## FILES CHANGED (session-128):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-128.md`.

## TEST STATUS:
Session-127 GitHub Actions build GREEN (`f63a84d`, user-confirmed). Session-128 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
