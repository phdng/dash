# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-082 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-13 (session-082): GitHub Actions session-081 batch đã xanh. Executable target hiện thêm pure post-identity scene routing từ 400D0/4138C/41CBC/41E08/3FB54/3FFC0: 400D0 chỉ route host slot non-CarPlay trước aux; 4138C ưu tiên bất kỳ configured host slot trước aux. Caller phải supply bundle identity; private 3FBC8 traversal và settings/layout executors vẫn giữ explicit gap.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-082):
- R-081 pure post-identity routing descriptors for 400D0/4138C with exact non-CarPlay-vs-any-host-slot precedence and aux fallback.

## CURRENT TASK:
- Chờ compiler gate cho session-082 changes; final local structural checks chạy sau tracking/log update.

## NEXT TASK:
- Sau CI xanh, R-082 inspect pure size/orientation routing quanh 41D80/41E94/40514 với caller-supplied identity/settings snapshots; chỉ promote complete data decisions, không synthesize FBSSceneSettingsDiff/private settings mutation/scene executors. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-082):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-082.md`.

## TEST STATUS:
Session-081 GitHub Actions build GREEN (user-confirmed). Session-082 local verifier + py_compile + `git diff --check` PASS after final docs/log edits; CatDesk standard verifier = NOT_CONFIGURED (expected for this Theos-only repo without Cargo.toml/package.json/Python project manifest). Current Objective-C routing descriptors need next macOS CI run; dynamic device tests vẫn pending.
