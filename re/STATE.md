# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-126 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-57 (session-126): GitHub Actions session-125 (`123b913`) đã xanh theo user. Executable target thêm data-only `3C368` aux-scene creation exception outcome từ LSDA `0x1145D8` + raw ARM64. Mười hai action-5 ranges hội tụ common typed catch `0x3C7C0`: expected type swallow, request `teardownAuxScene`, bỏ phần creation còn lại và ra nil path `0x3C3D8`; ba protected normal-failure teardown calls vì vậy được retry teardown một lần trong catch. Nonmatching type unwind tại `0x3C800`; nếu teardown bên trong catch ném tiếp (`0x3C7E0..0x3C7E8`, action 0), landing `0x3C7F8` end-catch rồi resume unwind. Không private SpringBoard construction/selector/view/teardown execution, live state mutation hay exception synthesis.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-126):
- R-125 data-only 3C368 aux-scene creation exception outcome: 12 typed action-5 ranges→common catch teardown-request+nil return; protected normal-failure teardown exceptions retry teardown once; catch-internal teardown throw→end-catch+resume unwind; nonmatching/unprotected paths propagate.

## CURRENT TASK:
- R-125 hoàn tất local; commit-only handoff. User confirmed session-125 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-126 batch, R-126: inspect next earlier LSDA-bearing `3C1F0 -> 0x1145B8` (`degradeSlot:bid:native:why:`). Existing decompile shows private hosted-controller view/remove/invalidate teardown followed by controller ivar clear, hosted-bid replacement with empty string, and placeholder creation via `36E98`; decode exact LSDA/raw ARM64 continuation before promotion. 73E8/80D0 and full 7E908 remain unresolved; dynamic device verify still needed.

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

## FILES CHANGED (session-126):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-126.md`.

## TEST STATUS:
Session-125 GitHub Actions build GREEN (`123b913`, user-confirmed). Session-126 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
