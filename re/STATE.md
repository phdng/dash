# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-152 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-83 (session-152): GitHub Actions session-151 (`42153ac`) đã xanh theo user. Executable target thêm data-only `369E8` layout-area publish exception outcome từ LSDA `0x114058` + raw ARM64. Năm typed ranges + hai action-0 ranges được tách thành precommit label/status construction, committed-status dedup, global `qword_163AE8` store unwind, ordered CFPreferences SetValue/synchronize, Darwin center/name/post, và final release unwind. Typed catch expected type jump final stack cleanup, giữ nguyên side effects đã xảy ra và có thể bypass retained x20/x19 releases; action-0 store/release ranges resume unwind, không swallow. Nonmatching typed exceptions unwind. Không live formatting/global/prefs/notify execution, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-152):
- R-151 data-only 369E8 layout-area publish exception outcome: five typed ranges plus two action-0 ranges; exact precommit label/status ownership, committed-status dedup, global-store unwind, ordered prefs/notify side-effect persistence, retained-release bypass, final cleanup unwind, unprotected propagation and nonmatching unwind recorded.

## CURRENT TASK:
- R-151 hoàn tất local; commit-only handoff. User confirmed session-151 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-152 batch, R-152: inspect `365D4 -> 0x113FFC`, display configuration/resolution-quality publish helper. Exact 14-entry table: no landing `0x365D4..0x36608`; typed `0x36608..0x36614 -> 0x369A0`; typed `0x3661C..0x36628 -> 0x36998`; typed `0x3663C..0x36678 -> 0x369A4`; typed `0x3667C..0x36688 -> 0x3698C`; typed `0x366B0..0x366CC -> 0x369A4`; no landing `0x366CC..0x366E4`; typed `0x366E4..0x36734 -> 0x369B8`; typed `0x36814..0x3682C -> 0x36994`; no landing `0x3682C..0x3688C`; typed `0x3688C..0x368A8 -> 0x3699C`; no landing `0x368A8..0x368CC`; typed `0x368CC..0x36938 -> 0x3699C`; final tail unprotected. Landing families differ: `0x369A4` expected catch continues geometry fallback at `0x366DC`; `0x369B8` continues later bounds/frame fallback at `0x36758`; aliases `0x36994/98/9C/A0 -> 0x369CC` force result false and jump cleanup `0x36958`; `0x3698C` first restores d8=d9 then routes through `0x369A4`. Map FBSDisplayConfiguration acquisition, pixelSize/scale probes, bounds/frame fallback, global geometry commits, resolution/quality string ownership, dedup, prefs/Darwin side effects and release bypass separately. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-152):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-152.md`.

## TEST STATUS:
Session-151 GitHub Actions build GREEN (`42153ac`, user-confirmed). Session-152 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
