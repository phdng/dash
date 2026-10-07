# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-163 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-94 (session-163): GitHub Actions session-162 (`783c8ae`) đã xanh theo user. Executable target thêm data-only `34F28` `-[CNABLivePresenter tick:]` typed/action-0 outcome từ LSDA `0x113D8C` + raw ARM64. Exact table có 26 entries. Typed action-5 ranges bao window/noop/timer-maintenance admission, window-layer hidden/opacity-animation gate, targets presence/provider/fallback collection, phase + target-opacity preparation, CATransaction begin/disable, fast enumeration, per-layer opacity-animation/alt/group-opacity probes và mutations, transaction commit + tick increment. Expected type common catch `0x35314` begin/end-catch rồi jump `0x352A8`, nên chỉ final retained timer/input release được tiếp tục; selected collection/window-layer/window và site-local intermediates có thể bypass cleanup. Action-0 release failures và nonmatching typed exceptions resume unwind `0x3530C`, không vào timer-cleanup continuation. Final release range cũng phục vụ early-exit pre-transaction paths nên không infer commit từ cleanup PC. Không live timer/window/layer/collection/CATransaction/tick/ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-163):
- R-162 data-only 34F28 `tick:` typed/action-0 exception outcome: 26-entry LSDA with typed catch→timer-only final cleanup, exact window/layer/targets/phase/transaction/enumeration/group-opacity/opacity/tick milestones, eight action-0 release→unwind stages, retained-local release bypass, and nonmatching propagation recorded.

## CURRENT TASK:
- R-162 hoàn tất local; commit-only handoff. User confirmed session-162 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-163 batch, R-163: inspect `345E4 -> 0x113CD4`, server-notice UI construction pipeline. Exact LSDA has 29 entries. Initial file/text gates use action index 7 = typed catch-only; later UI-build ranges use action index 5 = typed catch + cleanup. Landing aliases `0x34B8C/90/94/98/9C/A0/A4/A8` converge at `0x34BA8`; expected type begin-catches, replaces the captured result/reason slot with a static failure reason, releases the previous slot value, then end-catches/returns; nonmatching resumes unwind at `0x34BFC`. Map no-notice marker, text validation, contentView/bounds gates, removeServerNotice, label/container/layer styling, hierarchy/global notice store, presentation/deadline/weak-dispatch path, failed-present teardown, and cleanup ownership separately. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-163):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-163.md`.

## TEST STATUS:
Session-162 GitHub Actions build GREEN (`783c8ae`, user-confirmed). Session-163 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
