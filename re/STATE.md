# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-117 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-48 (session-117): GitHub Actions session-116 (`335f97d`) đã xanh theo user. Executable target thêm data-only `3EA0C` aux private-executor exception outcome được xác nhận bằng LSDA `0x1148B8` + raw ARM64: only protected private `updateSettingsWithBlock:` send `0x3EADC..0x3EAEC` lands at typed catch `0x3EB4C`; expected discriminator catch/swallow, skips applied write, decrements `dword_162F14` only when positive, then clears reentrancy and disposes both byref captures. Nonmatching discriminator disposes captures and resumes unwind at `0x3EB98` without expected counter decrement/reentrancy clear. Không invoke private executor/block, mutate globals, synthesize/catch exception hay execute unwind.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-117):
- R-116 data-only 3EA0C exception outcome: private-executor throw→typed catch swallow+no applied mark+bounded counter decrement+reentrancy clear+capture dispose; nonmatching type→capture dispose+unwind without counter/reentrancy cleanup.

## CURRENT TASK:
- R-116 hoàn tất local; commit-only handoff. User sẽ tự push và báo compiler green/pass trước khi R-117 bắt đầu.

## NEXT TASK:
- Sau compiler xanh, R-117 promote exact `3E670` LSDA `0x114880`: protected aux gates/current-settings reads/update-executor preparation→common typed catch swallow+outer cleanup; nonmatching type→resume unwind. Late protected range begins after retained working object `x22`, and catch bypasses its normal release at `0x3E93C`; expose only data-only continuation/lifetime metadata, không private selector/method lookup/dispatch hay mutate globals. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-117):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-117.md`.

## TEST STATUS:
Session-116 GitHub Actions build GREEN (`335f97d`, user-confirmed). Session-117 local verifier + py_compile PASS trước docs/log finalization; `git diff --check` sẽ chạy trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit; user tự push và báo compiler result. Dynamic device tests vẫn pending.
