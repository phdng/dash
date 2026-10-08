# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-173 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-104 (session-173): Tiếp tục site-scoped trong `sub_3257C -> LSDA 0x113860`. Exact adjacent entries được tách đúng: `0x338C0..0x338D0 -> 0x33D18`, action 0, bao `objc_storeStrong(&qword_164510, controller)` và chỉ resume unwind; `0x338D0..0x338E8 -> 0x33A1C`, action 5, bao host `addSubview:` rồi `tick:15`. Với root-attach catch, global controller đã commit, attach có thể đã áp dụng, tick chưa chạy; với tick catch, global commit + attach đã hoàn tất, tick có thể đã áp dụng. Shared typed cleanup remove committed root khi có, clear/release `qword_164510`, rồi outer-return. Data-only only.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-173):
- R-172 data-only `3257C` post-commit layout-confirm routing: cleanup-only global storeStrong unwind plus typed root-attach/tick recovery, exact progress timing, committed-root cleanup, and nonmatching unwind recorded.

## CURRENT TASK:
- R-172 implementation + docs complete locally; verify/commit-only handoff in progress. Assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-173 batch, continue site-scoped decoding inside `3257C -> LSDA 0x113860`; prefer the next exact protected operation/sequence after the layout-confirm post-commit region. 73E8/80D0/full 7E908 and jailbroken-device smoke tests remain unresolved.

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

## FILES CHANGED (session-166):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-166.md`.

## TEST STATUS:
Session-165 GitHub Actions build GREEN (`723505f`, user-confirmed). Session-166 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
