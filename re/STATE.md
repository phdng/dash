# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-165 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-96 (session-165): GitHub Actions session-164 (`e28c5a6`) đã xanh theo user. Executable target thêm data-only `34524` reset/teardown catch-all outcome từ LSDA `0x113CB8` + raw ARM64. Exact table có 3 entries: unprotected prefix, action-1 catch-all `0x34598..0x345A4`, unprotected tail. Reset path clears +0xA9, sentinel +0xB0, CGRectNull +0xC0, state bytes +0x130/+0x131, counter +0x138 and strong slot +0x140 before unprotected release of old slot value. Release failure propagates after reset/slot clear, before collection clear/teardown. Protected removeAllObjects failure is swallowed after old-slot release completed and before teardown; protected teardown-after-reset occurs only after collection clear completed; no-reset path jumps directly to protected teardown with no reset milestones. Landing `0x345B0` unconditionally begin/end-catches and returns. Không live reset/collection/teardown/ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-165):
- R-164 data-only 34524 reset/teardown catch-all outcome: exact preprotected reset writes, unprotected old-slot release propagation, protected collection-clear/teardown partial-side-effect timing, teardown-after-reset vs teardown-without-reset separation, and immediate caught return recorded.

## CURRENT TASK:
- R-164 hoàn tất local; commit-only handoff. User confirmed session-164 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-165 batch, R-165: inspect `34250 -> 0x113C60`, CarPlay CADisplay resolver. Exact 13-entry table is mostly action-0 cleanup plus typed action-5 `0x34440..0x34448 -> 0x3448C` around bounds capability check and `0x3444C..0x34458 -> 0x34488` around bounds read. Typed expected catches begin/end-catch, release retained candidate display x24, force x24=nil, then continue final screenIDs/displays/external-device cleanup and nil return; action-0/nonmatching paths resume unwind at `0x34520`. Map CADisplay/AVExternalDevice class gate, current device, screenIDs/NSArray/firstObject ownership, displays enumeration, uniqueId match, retained candidate, capability/bounds validation, candidate nil fallback and every cleanup range. After R-165, `34020 -> 0x113C1C` has 9 entries: action-7 `buildShellIfNeeded` gate, action-5 UI construction/install/present ranges, common typed catch `0x341C0` return, nonmatching unwind `0x341DC`. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-165):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-165.md`.

## TEST STATUS:
Session-164 GitHub Actions build GREEN (`e28c5a6`, user-confirmed). Session-165 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
