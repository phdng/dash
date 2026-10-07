# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-166 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-97 (session-166): GitHub Actions session-165 (`723505f`) đã xanh theo user. Executable target thêm data-only `34250` CarPlay CADisplay resolver outcome từ LSDA `0x113C60` + raw ARM64. Exact table có 13 entries: action-0 current-device/screenIDs, first-screenID/displays, enumeration/uniqueId và staged cleanup ranges; two typed action-5 ranges quanh matched-candidate bounds capability/read. Runtime tách class/type gates, displays double-retain, uniqueId acquisition/type/equality, unprotected matched-candidate retain, typed bounds checks, action-0 post-bounds candidate release, valid-bounds unprotected return re-retain, và từng final release stage. Expected typed catch swallow rồi qua unprotected end-catch → action-0 candidate release; x24 chỉ nil và remaining cleanup chỉ tiếp tục nếu nested catch cleanup hoàn tất. Nonmatching typed/action-0 failures resume unwind `0x34520`. Không live CADisplay/AVExternalDevice/enumeration/ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-166):
- R-165 data-only 34250 CarPlay CADisplay resolver exception outcome: 13-entry LSDA with action-0 acquisition/enumeration/cleanup unwind, exact external-device/screenIDs/firstObject/displays/uniqueId/candidate ownership, typed bounds capability/read catches, conditional catch-cleanup nil fallback, valid-bounds return re-retain and staged final releases recorded.

## CURRENT TASK:
- R-165 hoàn tất local; commit-only handoff. User confirmed session-165 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-166 batch, R-166: inspect `34020 -> 0x113C1C`, Phase-4a display-OK UI builder. Exact 9-entry table: action-7 `0x34038..0x3403C -> 0x341B8` around `buildShellIfNeeded`; action-5 `0x34048..0x340A8 -> 0x341BC` UIView/background construction; unprotected color release `0x340A8..0x340B8`; action-5 `0x340B8..0x34118 -> 0x341C0` UILabel/properties/white-color path; unprotected color release; action-5 `0x34128..0x34148 -> 0x341C0` font path; unprotected font release; action-5 `0x34150..0x34180 -> 0x341C0` text/addSubview/installContent/present; unprotected tail stores present result byte then releases label/root view. Expected type common catch `0x341C0` begin/end-catches and returns immediately, bypassing normal retained label/root-view cleanup and, for present exceptions, before result-byte store; nonmatching resumes unwind `0x341DC`. After R-166, `33F5C -> 0x113C08` has one action-1 catch-all `0x33F70..0x33F88` over buildShellIfNeeded/installContent/present and returns before captured result-byte store; then `33DB4 -> 0x113BE8`. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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
