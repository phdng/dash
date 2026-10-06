# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-080 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-11 (session-080): GitHub Actions session-079 batch đã xanh. Executable target hiện thêm exact aux-scene pre/private normalization + post-application-lookup state mirror/teardown từ 3C368/3E4A8/3E590/3E428/3C808, cùng pure 3E670 desired-settings/±0.5 early-out plan. Private aux scene/view creation và updateSettings executor vẫn giữ explicit gap.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-080):
- R-078 exact aux candidate/capability/post-app-lookup mirror/teardown; R-079 exact 3E670 desired-settings plan + applied/current-settings early-out.

## CURRENT TASK:
- Chờ compiler gate cho session-080 changes; final local structural checks chạy sau tracking/log update.

## NEXT TASK:
- Sau CI xanh, R-080 inspect 3C368 retry scheduling + 3E604/3E670/3EA0C generation/counter state; chỉ promote retry/state-machine descriptors hoặc explicit caller-driven transitions, không gọi private auxSceneObject/updateSettingsWithBlock và không giả apply thành công. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-080):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-080.md`.

## TEST STATUS:
Session-079 GitHub Actions build GREEN (user-confirmed). Session-080 local verifier + py_compile + `git diff --check` PASS after final docs/log edits; CatDesk standard verifier = NOT_CONFIGURED (expected for this Theos-only repo without Cargo.toml/package.json/Python project manifest). Current Objective-C runtime-introspection/aux-state edits need next macOS CI run; dynamic device tests vẫn pending.
