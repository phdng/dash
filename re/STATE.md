# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-074 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-5 (session-074): GitHub Actions session-073 batch đã xanh. Executable target hiện thêm exact request/status schemas 8CC0/8DF8/8F34/91B4/986C, cached 7EA4/8058 state + exact 89D8 uiapp.state, và runtime-resolved DDz2/29810 per-host fontfloor/keypane broadcasts. Private keypane-OFF toast 30960 và receiver bodies chưa promote vẫn giữ explicit gap.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-074):
- R-065 exact 8CC0/8DF8/8F34/91B4/986C IPC schemas; R-066 cached UI state + 89D8; R-067 runtime-resolved 29810/DDz2 per-host fontfloor/keypane broadcasts (30960 toast excluded).

## CURRENT TASK:
- Chờ compiler gate cho session-074 changes; local structural checks cần chạy lại sau final edits.

## NEXT TASK:
- Sau khi push, GitHub Actions build current runtime. Nếu xanh, R-068 inspect UIApp-side receiver/observer path quanh 4CBDC + CNABHostUIAppResponder và chỉ promote runtime-resolvable consumers không cần private framework linkage. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-074):
- Sửa: `RECONSTRUCTION/DuoDashShared.h`, `ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-074.md`.

## TEST STATUS:
Session-073 GitHub Actions build GREEN (user-confirmed). Session-074 local verifier + py_compile + `git diff --check` PASS; CatDesk standard verifier = NOT_CONFIGURED (expected for Theos-only repo without Cargo/package.json/Python manifest). Current Objective-C runtime-message/DDz2 dynamic-selector edits need next macOS CI run; dynamic device tests vẫn pending.
