# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-137 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-68 (session-137): GitHub Actions session-136 (`89152f3`) đã xanh theo user. Executable target thêm data-only `38E14` keypane-hide-gap parser exception outcome từ LSDA `0x1142DC` + raw ARM64. Bốn typed action-5 ranges (file read+retain, length, UTF8String, strtod) hội tụ catch `0x38ED8`: expected catch swallow rồi force return gap `71.0` qua `0x38EB4`. File-read range kết thúc trước `x19` commit nên không record retained-string cleanup bypass; length/UTF8/parse xảy ra sau x19 commit và catch bỏ qua explicit release `0x38EAC`. Gap `0x38E58..0x38E6C` chứa `objc_retainAutorelease` là unprotected nên exception propagate thay vì fallback. Nonmatching unwind. Không file I/O, NSString/UTF8 parsing, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-137):
- R-136 data-only 38E14 keypane-hide-gap parser exception outcome: 4 typed sites→swallow+forced `71.0` return; post-x19 sites record retained-string release bypass, retainAutorelease gap stays unprotected/propagating, nonmatching type unwinds.

## CURRENT TASK:
- R-136 hoàn tất local; commit-only handoff. User confirmed session-136 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-137 batch, R-137: inspect next earlier LSDA-bearing `38B0C -> 0x11428C` (`sub_38B0C`, display-scale width-cap helper). Direct unwind enumeration shows it immediately precedes `38E14`. Exact 12-entry table has 8 action-5 ranges: `0x38B3C..0x38B48 -> 0x38CCC` (display acquisition+retain), `0x38B48..0x38B58 -> 0x38CC8` (display committed + FBSDisplayConfiguration class lookup), `0x38B60..0x38B84 -> 0x38CD0` (config alloc/init/retain), `0x38B9C..0x38BA8 -> 0x38CD0` (scale capability probe), `0x38BAC..0x38BB8 -> 0x38CC0` (scale getter), `0x38BD4..0x38BEC -> 0x38CC4` (window+retain+bounds), `0x38C00..0x38C0C -> 0x38CC4` (pixelSize capability probe), and `0x38C24..0x38C30 -> 0x38CBC` (pixelSize getter). All stubs converge typed catch `0x38CD0`; expected type begin/end-catches then jumps to `0x38C58`, releases the two input-view ownerships and returns original bounds dimension `d8`, abandoning display-scale-derived 800/scale cap. Depending on site, catch may bypass retained display/config/window intermediates; first display-acquisition range ends before `x20` commit. Nonmatching type resumes unwind at `0x38CE4`. Map exact per-site ownership timing before promotion. 73E8/80D0 and full 7E908 remain unresolved; dynamic device verify still needed.

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

## FILES CHANGED (session-137):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-137.md`.

## TEST STATUS:
Session-136 GitHub Actions build GREEN (`89152f3`, user-confirmed). Session-137 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
