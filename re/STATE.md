# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-153 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-84 (session-153): GitHub Actions session-152 (`1299df0`) đã xanh theo user. Executable target thêm data-only `365D4` display-configuration/resolution-quality publish exception outcome từ LSDA `0x113FFC` + raw ARM64. Chín typed ranges được tách thành ba continuation families: FBS config/pixel/scale catches tiếp tục display bounds fallback; display bounds/frame catches tiếp tục geometry-validity gate; acquisition/class/format/dedup/publish catches force false và jump final input cleanup, có thể bypass committed display/resolution/quality releases. Runtime ghi exact x20/x22/x23/x24 ownership, pixel-width/scale fallback state, geometry globals, dedup global stores, ordered preferences/Darwin side effects. Nonmatching typed exceptions unwind `0x369E4`; unprotected gaps propagate. Không live display/FBS/prefs/notify execution, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-153):
- R-152 data-only 365D4 display-configuration/resolution-quality publish exception outcome: nine typed ranges with three distinct catch continuations; exact display/FBS/pixel/scale/bounds/frame fallback timing, geometry-global commit, resolution/quality ownership, dedup/global-store persistence, ordered prefs/Darwin side effects, release bypass, unprotected propagation and nonmatching unwind recorded.

## CURRENT TASK:
- R-152 hoàn tất local; commit-only handoff. User confirmed session-152 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-153 batch, R-153: inspect `365A8 -> 0x113FE8`, `display.changed` wrapper around `sub_365D4`. Exact 2-entry table: action-1 catch-all `0x365B0..0x365C0 -> 0x365C8`, then unprotected `0x365C0..0x365D4`. Protected range prepares static `display.changed`, force flag 1, and calls `sub_365D4`; landing `0x365C8` unconditionally begin/end-catches and returns immediately, with no discriminator/nonmatching path. Promote wrapper-level catch-all swallow/return metadata only; do not duplicate inner R-152 site semantics. Next earlier LSDA-bearing function is `3640C -> 0x113FD0`. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-153):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-153.md`.

## TEST STATUS:
Session-152 GitHub Actions build GREEN (`1299df0`, user-confirmed). Session-153 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
