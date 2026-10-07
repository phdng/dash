# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-162 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-93 (session-162): GitHub Actions session-161 (`899e242`) đã xanh theo user. Executable target thêm data-only `35328` `-[CNABLivePresenter restoreTargets]` typed/action-0 outcome từ LSDA `0x113E30` + raw ARM64. Exact table có 16 entries. Typed action-5 ranges bao initial targets probe, CATransaction begin/disable, enumeration source+collection acquisition, enumeration reads/mutation/type filter, retained per-layer opacity/animation probes, `setOpacity:1.0`, và final CATransaction commit. Expected typed exceptions hội tụ `0x35534`, begin/end-catch rồi branch epilogue `0x354DC`, nên sau khi transaction đã bắt đầu có thể bypass retained layer/collection cleanup và bỏ final commit `0x354D4`; commit-site itself may partially apply before catch. Ba action-0 release ranges (animation-result, retained-layer, collection) resume unwind qua `0x3552C` với remaining-cleanup bypass khác nhau. Nonmatching typed exceptions cũng unwind. Không live targets enumeration/CALayer/CATransaction/ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-162):
- R-161 data-only 35328 `restoreTargets` typed/action-0 exception outcome: 16-entry LSDA with typed catch→epilogue/skipped final commit, exact collection/layer/animation ownership timing, opacity mutation persistence, three action-0 release→unwind stages, and nonmatching propagation recorded.

## CURRENT TASK:
- R-161 hoàn tất local; commit-only handoff. User confirmed session-161 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-162 batch, R-162: inspect `34F28 -> 0x113D8C`, `-[CNABLivePresenter tick:]`. Exact LSDA has 26 call-site entries mixing many typed action-5 ranges, action-0 release/cleanup ranges, and unprotected gaps. Landing aliases `0x352F4/2F8/2FC/300/304/308/310/314` converge at common discriminator `0x35314`; expected type begin/end-catches then jumps to final retained-input cleanup at `0x352A8`, while action-0/nonmatching paths resume unwind via `0x3530C`. Map timer/window/layer admission, targets/alt fallback selection, phase/ticks state, CATransaction setup, enumerated CALayer ownership, animation/group-opacity/opacity mutation, transaction commit, tick increment, and which retained locals are still cleaned vs bypassed on each catch. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-162):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-162.md`.

## TEST STATUS:
Session-161 GitHub Actions build GREEN (`899e242`, user-confirmed). Session-162 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
