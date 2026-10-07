# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-144 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-75 (session-144): GitHub Actions session-143 (`6734571`) đã xanh theo user. Executable target thêm data-only `375B8` keypane center-adjustment exception outcome từ LSDA `0x11415C` + raw ARM64. Một action-5 range `0x375EC..0x37610` bao geometry helpers, CGRectIsNull, center getter và setCenter. Expected catch swallow rồi jump `0x37618`, bỏ remaining geometry và first normal release nhưng vẫn final-release retained view. Pre-geometry `off_163C60` đã hoàn tất trước protected range. Runtime tách geometry-helper, center-getter và center-setter; chỉ setter-site ghi possible center side effect trước throw, không rollback. Unprotected/nonmatching propagate/unwind. Không geometry/UIView execution, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-144):
- R-143 data-only 375B8 keypane center-adjustment exception outcome: one typed range→skip remaining geometry+final retained-view cleanup; pre-geometry callback completion, first-release bypass, setter-only possible center side effect, unprotected propagation and nonmatching unwind recorded.

## CURRENT TASK:
- R-143 hoàn tất local; commit-only handoff. User confirmed session-143 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-144 batch, R-144: inspect `374C4 -> 0x11413C`. Exact 3-entry table has one typed action-5 range `0x374FC..0x3751C -> 0x375A0`, covering `376DC` candidate-rect acquisition and `CGRectIsNull`. Expected catch begin/end-catches then jumps to `0x3755C`, preserving caller-supplied rectangle registers (`d9/d8/d10/d11`), skipping candidate adoption and `dword_162EF0` decrement, and still invoking `off_163C58` with the original rectangle before final retained-input cleanup; nonmatching type resumes unwind at `0x375B4`. Split geometry-helper vs CGRectIsNull timing and promote original-rectangle forwarding metadata only. Next earlier LSDA-bearing function is `37398 -> 0x114114`, whose 5-entry table has three typed ranges `0x373CC..0x373D0`, `0x373D0..0x373EC`, and `0x373FC..0x37428`. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-144):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-144.md`.

## TEST STATUS:
Session-143 GitHub Actions build GREEN (`6734571`, user-confirmed). Session-144 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
