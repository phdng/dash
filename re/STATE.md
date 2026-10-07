# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-146 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-77 (session-146): GitHub Actions session-145 (`75828a5`) đã xanh theo user. Executable target thêm data-only `37398` keypane center-forward exception outcome từ LSDA `0x114114` + raw ARM64. Ba action-5 ranges hội tụ catch `0x374AC`. Raw branch target resolve d10/d11 gap: caller center được giữ ở d9/d8; normal candidate midpoint chỉ copy d10/d11→d9/d8 tại `0x37460/64`, còn catch jump thẳng `0x37468` nên luôn forward original caller center qua `off_163C50`. Catch bỏ candidate adoption, counter decrement và first retained-input release nhưng vẫn callback + final release. Site timing tách pre-helper/candidate/null/MidX/MidY. Unprotected/nonmatching propagate/unwind. Không geometry/midpoint/callback execution, counter mutation, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-146):
- R-145 data-only 37398 keypane center-forward exception outcome: 3 typed ranges→original caller center fallback+skip candidate midpoint adoption/counter decrement+still invoke off_163C50; raw branch ordering closes prior d10/d11 uncertainty; exact candidate/null/MidX/MidY timing, one-release bypass/final-release continuation, unprotected propagation and nonmatching unwind recorded.

## CURRENT TASK:
- R-145 hoàn tất local; commit-only handoff. User confirmed session-145 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-146 batch, R-146: inspect `37284 -> 0x114100` (`dropSplashIfOverdue`). LSDA header decodes one action-1 catch-all range `0x37298..0x372AC -> 0x372BC`, followed by unprotected tail `0x372AC..0x372CC`. Protected range covers `+[DDz1 shared]`, retain-autoreleased result, x19 commit at `0x372A4`, and `dropSplashIfOverdue` send at `0x372A8`. Landing `0x372BC` unconditional begin/end-catches and returns; no discriminator. Split shared-acquisition vs callback-send timing: first may throw before x19 commit; callback site has retained DDz1 committed and catch skips normal release tail at `0x372AC..0x372B8`, preserving any callback side effect before throw. Next earlier LSDA-bearing function is `371F4 -> 0x1140EC`, same catch-all shape around `dropServerNoticeNow`. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-146):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-146.md`.

## TEST STATUS:
Session-145 GitHub Actions build GREEN (`75828a5`, user-confirmed). Session-146 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
