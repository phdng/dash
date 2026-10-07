# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-116 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-47 (session-116): GitHub Actions session-115 (`f5fdd32`) đã xanh theo user. Executable target thêm data-only `3EB9C` aux settings-mutation exception outcome được xác nhận bằng LSDA `0x1148D8` + raw ARM64: single protected range `0x3EBC8..0x3EC34` covers frame capability/setter through orientation signature/setter; catch-all landing `0x3EC58` swallows rồi cleanup `0x3EC44`. Frame-path throw occurs before frame-applied byref write; orientation-path throw may happen after that frame write and does not roll it back; every protected throw skips orientation-applied write at `0x3EC34`. Không invoke private setters/signature checks, mutate settings/byrefs hay synthesize/catch exception.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-116):
- R-115 data-only 3EB9C exception outcome: catch-all aux frame/orientation mutation throw→skip remaining mutation+cleanup with site-aware byref persistence metadata.

## CURRENT TASK:
- R-115 hoàn tất local; commit-only handoff. User sẽ tự push và báo compiler green/pass trước khi R-116 bắt đầu.

## NEXT TASK:
- Sau compiler xanh, R-116 promote exact `3EA0C` LSDA `0x1148B8`: protected private `updateSettingsWithBlock:` throw→typed catch swallow, no applied mark, bounded failure-counter decrement, reentrancy clear + capture dispose; nonmatching type→capture dispose+unwind without reentrancy clear/counter decrement. Chỉ data-only metadata, không private executor/block invocation hay mutate globals. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-116):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-116.md`.

## TEST STATUS:
Session-115 GitHub Actions build GREEN (`f5fdd32`, user-confirmed). Session-116 local verifier + py_compile PASS trước docs/log finalization; `git diff --check` sẽ chạy trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit; user tự push và báo compiler result. Dynamic device tests vẫn pending.
