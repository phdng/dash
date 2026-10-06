# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-093 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-24 (session-093): GitHub Actions session-092 (`0dad59a`) đã xanh theo user. Executable target thêm data-only 4138C AVC sceneHandle decisions: update host route match mọi configured slot kể cả CarPlay, aux chỉ fallback khi không slot match; host scene+unmarked+width>0 tạo pending landscape-adjusted update, còn foreground=false original-callback suppression chỉ dành cho configured non-CarPlay host và count chỉ increment khi <=9. Không identity/settings selector, private executor, original callback hay counter mutation.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-093):
- R-092 data-only 4138C host/aux sceneHandle update routing plus foreground-based original-callback suppression/count descriptors.

## CURRENT TASK:
- R-092 hoàn tất local; commit-only handoff. User sẽ tự push và báo compiler green/pass trước khi R-093 bắt đầu.

## NEXT TASK:
- Sau compiler xanh, R-093 inspect `3F3F0` resize-to-private-scene path: exact attempt-count reset/general-counter floor plus probeScene result→landscape-adjusted `3F5C0` request; chỉ promote data-only post-resize counter normalization và scene-update descriptor, không invoke `probeSceneForSlot:`, `3F5C0`, hay mutate private counters. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-093):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-093.md`.

## TEST STATUS:
Session-092 GitHub Actions build GREEN (`0dad59a`, user-confirmed). Session-093 local verifier + py_compile + `git diff --check` PASS after final docs/log edits; CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit; user tự push và báo compiler result. Dynamic device tests vẫn pending.
