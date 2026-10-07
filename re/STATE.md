# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-150 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-81 (session-150): GitHub Actions session-149 (`c072275`) đã xanh theo user. Executable target thêm data-only `370F8` DDz1 nudge-present gate exception outcome từ LSDA `0x1140B4` + raw ARM64. Hai action-5 ranges hội tụ catch `0x3718C`: first range bao DDz1 shared/visible/livePresent + NSFileManager/fileExists; second range chỉ `nudgePresent:@"tick"`. Runtime tách exact pre/post x19, visible=true, livePresent=false, pre/post x20 manager, marker-result bridge, manager-release-complete, marker=false trước nudge. Expected catch return ngay; late nudge exception có thể bypass final DDz1 release và giữ side effects đã apply. Nonmatching unwind `0x371A8`; unprotected ranges propagate. Không DDz1/NSFileManager operation, file probe, nudge execution, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-150):
- R-149 data-only 370F8 DDz1 nudge-present gate exception outcome: 2 typed ranges→immediate return; exact x19/x20 ownership, visible/livePresent guard completion, marker bridge/result, manager-release-complete state, marker-absent nudge admission, release-bypass, possible nudge-side-effect persistence, unprotected propagation and nonmatching unwind recorded.

## CURRENT TASK:
- R-149 hoàn tất local; commit-only handoff. User confirmed session-149 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-150 batch, R-150: inspect `36E00 -> 0x11409C`. Exact 2-entry table has typed action-5 `0x36E18..0x36E2C -> 0x36E80`, then unprotected tail. Protected range covers `+[UIScreen mainScreen]`, retain-autoreleased UIScreen, x19 commit at `0x36E24`, and `bounds` at `0x36E28`; range ends before width/height capture into d8/d9. Expected catch `0x36E80` begin/end-catches then jumps to `0x36E60`, forcing return `0.0`; nonmatching type resumes unwind at `0x36E94`. Split pre-x19 screen acquisition from post-x19 bounds send so only bounds-site records retained-screen release bypass. After R-150, `369E8 -> 0x114058` is a larger 9-entry layout-area/preferences-notify function with five typed action-5 ranges and two action-0 cleanup ranges; decode separately. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-150):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-150.md`.

## TEST STATUS:
Session-149 GitHub Actions build GREEN (`c072275`, user-confirmed). Session-150 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
