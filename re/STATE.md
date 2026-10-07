# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-164 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-95 (session-164): GitHub Actions session-163 (`316f678`) đã xanh theo user. Executable target thêm data-only `345E4` server-notice UI typed outcome từ LSDA `0x113CD4` + raw ARM64. Exact table có 29 entries. Early no-notice marker/text gates dùng action index 7 = typed catch-only; later backdrop/UI-build/presentation/remove ranges dùng action index 5 = typed catch + cleanup. Expected type common catch `0x34BA8` begin-catch, ghi confirmed `CFSTR("threw")` vào captured reason slot **trước** release reason cũ, rồi end-catch/return; catch-internal release nằm unprotected. Runtime tách manager/text/contentView/bounds/remove-existing, label/container styling, hierarchy/current-notice store, present/state/deadline/interaction ordering, unprotected weak+6s dispatch success tail, failed-present remove và unprotected slot-clear/`present-failed` teardown. Không live file/UI/global/dispatch/ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-164):
- R-163 data-only 345E4 server-notice UI exception outcome: 29-entry LSDA with action-7 early gates vs action-5 UI-build paths, confirmed catch reason `threw` replacement-before-release, exact backdrop/label/container/style/hierarchy/current-notice ownership, presentation/deadline side effects, unprotected success dispatch and failed-present teardown propagation recorded.

## CURRENT TASK:
- R-163 hoàn tất local; commit-only handoff. User confirmed session-163 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-164 batch, R-164: inspect `34524 -> 0x113CB8`. Exact 3-entry table has unprotected prefix `0x34524..0x34598`, action-1 catch-all `0x34598..0x345A4 -> 0x345B0`, then unprotected tail. When reset flag byte `+0xA9` is set, prefix clears reset flag, generation/sentinel, CGRectNull geometry, state bytes/counter, clears strong slot `+0x140` and releases old value before protected `removeAllObjects`; teardownWindow follows inside the same protected range. If flag is not set, control enters protected range directly at teardownWindow. Landing unconditionally begin/end-catches and returns. Split removeAllObjects, teardown-after-reset, teardown-without-reset, and unprotected partial-reset propagation. After R-164, `34250 -> 0x113C60` has 13 entries, mostly action-0 cleanup plus two typed action-5 ranges around matched-display bounds capability/read; typed expected catches continue local display cleanup/null fallback while action-0 failures resume unwind. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-164):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-164.md`.

## TEST STATUS:
Session-163 GitHub Actions build GREEN (`316f678`, user-confirmed). Session-164 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
