# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-123 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-54 (session-123): GitHub Actions session-122 (`afd88df`) đã xanh theo user. Executable target thêm data-only `3D704` convert-slot-to-CarPlay exception outcome được xác nhận bằng LSDA `0x114774` + raw ARM64: private hosted-view teardown typed catch `0x3D890` swallows rồi rejoin `0x3D7F0`, nên controller ivar clear/release, bridge-off phase và hosted-bundle/CarPlay state commit vẫn eligible; copied-bundle length/`89D8` typed catch `0x3D87C` swallows rồi rejoin `0x3D828`, nên publish failure vẫn không chặn state commit. Both nonmatching types `0x3D8A4` resume unwind. Không remove/invalidate private views, invoke `89D8`, mutate live ivar/global state hay synthesize/catch exception.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-123):
- R-122 data-only 3D704 exception outcome: private teardown throw→swallow+continue controller clear/bridge-off/state commit; publish throw→swallow+continue bundle/CarPlay state commit; nonmatching types→resume unwind.

## CURRENT TASK:
- R-122 hoàn tất local; commit-only handoff. User sẽ tự push và báo compiler green/pass trước khi R-123 bắt đầu.

## NEXT TASK:
- Sau compiler xanh, R-123 promote exact `3CC44` LSDA `0x11468C`: all typed landscape-coordination catches→common `0x3D4E0`, swallow+clear parsed landscape orientation only, then `0x3D21C` fallback orientation/hosting continuation; nonmatching/action-0 paths→resume unwind. Late catches after swap/cswap/rotation state writes do not roll those fields back. Chỉ data-only clear/fallback/persistence/unwind metadata, không file IO, global mutation, `3DFC8`, slot creation/private hooks hay exception synthesis. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-123):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-123.md`.

## TEST STATUS:
Session-122 GitHub Actions build GREEN (`afd88df`, user-confirmed). Session-123 local verifier + py_compile PASS trước docs/log finalization; `git diff --check` sẽ chạy trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit; user tự push và báo compiler result. Dynamic device tests vẫn pending.
