# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-125 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-56 (session-125): GitHub Actions session-124 (`6dcbcb9`) đã xanh theo user. Executable target thêm data-only `3C808` aux-scene teardown exception outcome từ LSDA `0x11466C` + raw ARM64: private `view`/remove/invalidate range `0x3C858..0x3C894` typed-catch tại `0x3C8F0`, swallow expected type và rejoin `0x3C89C`; `_auxVC` đã clear trước protected range, catch bỏ phần private teardown còn lại nhưng vẫn tiếp tục clear aux bundle/native-size/orientation + `3E428` generation-state refresh. Nonmatching type và unprotected ranges unwind/propagate. Không private selector/view/controller execution, live state/lifetime mutation hay exception synthesis.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-125):
- R-124 data-only 3C808 aux-scene teardown exception outcome: private teardown throw→swallow after pre-cleared `_auxVC`→continue aux state reset/3E428 refresh; possible retained-view release bypass recorded; nonmatching/unprotected paths→unwind/propagate.

## CURRENT TASK:
- R-124 hoàn tất local; commit-only handoff. User confirmed session-124 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-125 batch, R-125: inspect exact `3C368` LSDA `0x1145D8` createAuxScene exception ranges. Unwind enumeration confirms it is the next earlier LSDA-bearing function. Raw ARM64 tail shows landing stubs `0x3C7AC..0x3C7BC` converge at typed catch `0x3C7C0`; expected discriminator calls `teardownAuxScene` then falls back to nil-return path `0x3C3D8`, while nonmatching resumes unwind at `0x3C800`. Decode exact call-site ranges before promotion. 73E8/80D0 and full 7E908 remain unresolved; dynamic device verify still needed.

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

## FILES CHANGED (session-125):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-125.md`.

## TEST STATUS:
Session-124 GitHub Actions build GREEN (`6dcbcb9`, user-confirmed). Session-125 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
