# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-133 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-64 (session-133): GitHub Actions session-132 (`5b20ca6`) đã xanh theo user. Executable target thêm data-only `39B70` slide-animation exception outcome từ LSDA `0x11439C` + raw ARM64/helpers `3A004/3A034`. Protected UIView animation call xảy ra sau khi `byte_163C98=1`, generation snapshot capture, 1-second follow-up schedule, split-view retain, bounds read và target-center `d8/d9` computation. Expected catch direct `setCenter:` tới target đã tính rồi rejoin primary-view/input cleanup; normal local release của retained animation-block capture bị bypass, và animation có thể đã bắt đầu trước throw. Catch-internal fallback setter throw là action-0→end-catch+unwind và có thể xảy ra sau partial center side effect. Không dispatch scheduling, flag/UI mutation, animation/setCenter execution hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-133):
- R-132 data-only 39B70 slide-animation exception outcome: protected UIView animation throw→typed catch direct precomputed-center fallback+primary cleanup; prior slide flag/generation/1s-followup/target readiness, possible animation-start effects, capture-release bypass, and nested fallback-setter action-0 partial-write/unwind recorded.

## CURRENT TASK:
- R-132 hoàn tất local; commit-only handoff. User confirmed session-132 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-133 batch, R-133: inspect next earlier LSDA-bearing `39954 -> 0x11435C` (`sub_39954`, recursive view-transparency traversal). Direct unwind enumeration shows no LSDA-bearing function between `39954` and `39B70`. Scout decoded 9 call-site entries with action-5 ranges `0x399A0..0x399BC`, `0x399C4..0x399D0`, `0x399DC..0x39A00`, `0x39A24..0x39A3C`, `0x39A48..0x39A5C`, plus action-0 cleanup `0x39A64..0x39A74`. All expected typed catches converge at `0x39AC0`, begin/end-catch, then jump to final input cleanup `0x39A6C`, abandoning remaining recursive traversal. Map exact transparency writes already applied, enumerator/current-batch release bypass, and recursive-child exception continuation before promotion. 73E8/80D0 and full 7E908 remain unresolved; dynamic device verify still needed.

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

## FILES CHANGED (session-133):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-133.md`.

## TEST STATUS:
Session-132 GitHub Actions build GREEN (`5b20ca6`, user-confirmed). Session-133 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
