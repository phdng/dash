# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-130 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-61 (session-130): GitHub Actions session-129 (`877e143`) đã xanh theo user. Executable target thêm data-only `3AE50` evictFromPhoneThen exception outcome từ LSDA `0x114424` + raw ARM64/callback helpers. Exact table có 12 action-5 ranges hội tụ typed catch `0x3B278`: expected catch gọi retained one-shot fallback wrapper rồi bỏ phần eviction còn lại và vào final cleanup `0x3B0BC`. Ba protected direct fallback-call ranges đã set delivered gate trước mọi callback-related throw, nên catch gọi wrapper lại không duplicate user callback. Late execute range có thể đã arm completion handler + 2s timeout hoặc đã bắt đầu transition; catch fallback dùng cùng gate khiến callback/timer sau đó no-op. Early file/no-evict/frontmost ranges và catch-internal fallback là action-0 cleanup→propagate. Không file I/O, private transition execution, dispatch scheduling, live callback invocation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-130):
- R-129 data-only 3AE50 evictFromPhoneThen exception outcome: 12 typed ranges→common one-shot fallback wrapper+final cleanup; protected direct fallback throws are gate-suppressed on catch re-invocation; late completion-handler/2s-timeout/transition timing and possible retained-intermediate release bypass recorded; early/catch-internal action-0 ranges propagate with byref/end-catch cleanup.

## CURRENT TASK:
- R-129 hoàn tất local; commit-only handoff. User confirmed session-129 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-130 batch, R-130: inspect next earlier LSDA-bearing `3A0D0 -> 0x114404` (`sub_3A0D0`, split-host geometry update). Direct unwind enumeration proves no LSDA-bearing function between `3A0D0` and `3AE50`. Scout decoded exactly three call-site entries: unprotected `0x3A0D0..0x3A1F4`, typed action-5 `0x3A1F4..0x3A254 -> 0x3A2A8`, then unprotected `0x3A254..0x3A2C0`. Expected catch `0x3A2A8` begin/end-catches and jumps to `0x3A254` final retained-view cleanup, skipping remaining frame/center/geometry synchronization; nonmatching resumes unwind at `0x3A2BC`. Map exact writes completed before each possible throw in the protected geometry block before promotion. 73E8/80D0 and full 7E908 remain unresolved; dynamic device verify still needed.

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

## FILES CHANGED (session-130):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-130.md`.

## TEST STATUS:
Session-129 GitHub Actions build GREEN (`877e143`, user-confirmed). Session-130 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
