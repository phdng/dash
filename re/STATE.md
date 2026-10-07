# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-124 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-55 (session-124): theo lệnh tiếp tục của user, executable target thêm data-only `3CC44` landscape-coordination exception outcome từ LSDA `0x11468C` + raw ARM64 đã scout ở session-123. Mọi action-5 range hội tụ common typed catch `0x3D4E0`: expected type swallow, clear riêng parsed landscape orientation, rồi rejoin `0x3D21C` để đi qua normal fallback-orientation path và tiếp tục hosting. Late catches sau các accepted-state writes giữ nguyên swap/cswap/rotation; action-0 và nonmatching type unwind/propagate. Không file I/O, global mutation, `3DFC8`, slot/private-hook execution hay exception synthesis.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-124):
- R-123 data-only 3CC44 landscape exception outcome: typed action-5 throw→swallow+clear parsed orientation→normal fallback-orientation/hosting continuation; late post-state-commit catches preserve swap/cswap/rotation; action-0/nonmatching paths→unwind/propagate.

## CURRENT TASK:
- R-123 hoàn tất local; commit-only handoff. Session-123 commit `9f5e535` vẫn ahead origin trong workspace khi session-124 bắt đầu; assistant không push.

## NEXT TASK:
- Sau khi user push và compiler xanh cho batch local mới, scout function LSDA-bearing kế tiếp trước `3CC44` rồi chỉ promote contract data-only nếu evidence đủ. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-124):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-124.md`.

## TEST STATUS:
Session-122 GitHub Actions build GREEN (`afd88df`, user-confirmed). Session-124 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
