# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-143 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-74 (session-143): GitHub Actions session-142 (`13e2a56`) đã xanh theo user. Executable target thêm data-only `37924` CarPlay UI-status callback catch-all outcome từ LSDA `0x114178` + raw ARM64. Một action-1 range `0x3793C..0x37958` bao DDz1 shared+retain và `noteCarPlayUIStatus:gen:ok:`; landing `0x37968` unconditional begin/end-catch rồi return ngay, không discriminator. Runtime tách pre-x19 shared acquisition (temporary DDz1 only) khỏi callback-send sau x19 commit; callback throw có thể bypass normal retained-DDz1 tail release và giữ side effects đã apply trước throw. Unprotected tail propagate. Không DDz1 lookup/callback execution, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-143):
- R-142 data-only 37924 CarPlay UI-status callback exception outcome: action-1 catch-all→immediate return; exact pre/post x19 DDz1 commit, retained-controller release-bypass and possible callback-side-effect persistence recorded; unprotected tail propagates.

## CURRENT TASK:
- R-142 hoàn tất local; commit-only handoff. User confirmed session-142 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-143 batch, R-143: inspect `375B8 -> 0x11415C`. Exact 3-entry table has one typed action-5 range `0x375EC..0x37610 -> 0x37628`, with unprotected prefix/tail. Protected range covers helper `37640`, geometry helper `376DC`, `CGRectIsNull`, optional `center` getter, and optional `setCenter:`. Expected catch `0x37628` begin/end-catches then jumps directly to `0x37618`, skipping remaining geometry work and continuing retained-input cleanup; nonmatching type resumes unwind at `0x3763C`. Split pre-center geometry helper failure, center-getter failure, and center-setter failure so only setter site records possible center side-effect before throw. Next earlier LSDA-bearing function is `374C4 -> 0x11413C`, with typed `0x374FC..0x3751C -> 0x375A0`. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-143):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-143.md`.

## TEST STATUS:
Session-142 GitHub Actions build GREEN (`13e2a56`, user-confirmed). Session-143 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
