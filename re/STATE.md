# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-127 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-58 (session-127): GitHub Actions session-126 (`d99b720`) đã xanh theo user. Executable target thêm data-only `3C1F0` degrade-slot exception outcome từ LSDA `0x1145B8` + raw ARM64. Chỉ một typed protected range `0x3C26C..0x3C2C8` quanh `viewIfLoaded`/remove/invalidate; expected catch `0x3C350` swallow rồi rejoin `0x3C2D0`, trước controller-ivar clear. Vì vậy catch vẫn đi tiếp qua controller clear/release, hosted-bid reset về empty string và `36E98` placeholder creation; retained-view release có thể bị bypass nếu view đã acquire. Nonmatching và mọi unprotected ranges unwind/propagate. Không private view/controller calls, live hosted-state mutation, placeholder creation hay exception synthesis.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-127):
- R-126 data-only 3C1F0 degrade-slot exception outcome: protected private teardown throw→typed swallow before controller-ivar clear→continue ivar clear/release, hosted-bid empty reset, and placeholder creation; possible retained-view release bypass recorded; nonmatching/unprotected paths propagate.

## CURRENT TASK:
- R-126 hoàn tất local; commit-only handoff. User confirmed session-126 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-127 batch, R-127: inspect next earlier LSDA-bearing `3BBF0 -> 0x114538` (`spikeCreateSlot:index:native:`). LSDA scout đã decode 19 call-site entries: 14 action-5 ranges with landing stubs around `0x3C12C..0x3C15C`, one action-0 range `0x3C184..0x3C1C4`, and unprotected gaps. Raw tail shows one expected catch path rejoins `0x3BF50`; the common path at `0x3C15C` builds an exception reason and routes through a degrade call before rejoining later normal cleanup. Decode exact per-site semantics before promotion. 73E8/80D0 and full 7E908 remain unresolved; dynamic device verify still needed.

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

## FILES CHANGED (session-127):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-127.md`.

## TEST STATUS:
Session-126 GitHub Actions build GREEN (`d99b720`, user-confirmed). Session-127 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
