# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-132 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-63 (session-132): GitHub Actions session-131 (`a951e33`) đã xanh theo user. Executable target thêm data-only `39D4C` scene-layer-host predicate exception outcome từ LSDA `0x1143C8` + raw ARM64. Bốn action-5 ranges trong class/array setup, traversal step, count refresh và candidate bounds/convertRect đều hội tụ catch `0x39FE8`: expected catch force `w23=0`, vẫn đi qua signed-positive `dword_162EF8` decrement attempt, rồi skip toàn bộ dispatch-once/orientation/file/rotation/rebuild path và return false qua final input cleanup. Catch có thể bypass normal releases của retained root/array và site-dependent candidate/subviews. Nonmatching/unprotected propagate. Không private traversal/geometry calls, counter mutation, file I/O, rebuild/notice execution hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-132):
- R-131 data-only 39D4C scene-layer-host predicate exception outcome: 4 typed scan/geometry ranges→force predicate false→post-scan counter decrement attempt→skip rotation/rebuild→final input cleanup+false return; site-aware root/array/current-candidate/subviews release-bypass and geometry-read-start metadata recorded; nonmatching/unprotected propagate.

## CURRENT TASK:
- R-131 hoàn tất local; commit-only handoff. User confirmed session-131 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-132 batch, R-132: inspect next earlier LSDA-bearing `39B70 -> 0x11439C` (`sub_39B70`, slide animation setup). Scout decoded 5 entries: unprotected `0x39B70..0x39CA4`, typed action-5 `0x39CA4..0x39CC8 -> 0x39CFC`, unprotected `0x39CC8..0x39D1C`, action-0 `0x39D1C..0x39D2C -> 0x39D3C`, then unprotected tail. Typed range is the `UIView animateWithDuration:delay:options:animations:completion:` send. Expected catch begin-catches, retains exception, directly sends `setCenter:` to the captured view using already-computed `d8/d9`, end-catches, then rejoins normal releases at `0x39CD0`; nonmatching resumes unwind. If catch-internal fallback `setCenter:` throws, action-0 landing end-catches then resumes unwind. Map exact pre-animation flag/timer state and fallback-center persistence before promotion. 73E8/80D0 and full 7E908 remain unresolved; dynamic device verify still needed.

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

## FILES CHANGED (session-132):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-132.md`.

## TEST STATUS:
Session-131 GitHub Actions build GREEN (`a951e33`, user-confirmed). Session-132 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
