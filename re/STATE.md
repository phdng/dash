# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-081 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-12 (session-081): GitHub Actions session-080 batch đã xanh. Executable target hiện thêm exact aux retry/settings state machine từ 3C368/3E604/3E670/3EA0C: 0.1/0.5/1.5 retry descriptors, generation/applied/in-flight/attempt/budget state, 8-attempt cap, và explicit two-phase external apply completion. Private aux scene lookup/updateSettings invocation vẫn giữ explicit gap.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-081):
- R-080 exact aux create-kick retry metadata + 3E428/3E604/3E670/3EA0C state machine with explicit external executor begin/complete transition.

## CURRENT TASK:
- Chờ compiler gate cho session-081 changes; final local structural checks chạy sau tracking/log update.

## NEXT TASK:
- Sau CI xanh, R-081 inspect post-identity routing quanh 400D0/4138C + 3FBC8/3FFC0; chỉ promote pure bundle/slot/aux routing decisions khi caller đã supply identity, không reconstruct private scene/client traversal và không gọi settings/layout executor. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-081):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-081.md`.

## TEST STATUS:
Session-080 GitHub Actions build GREEN (user-confirmed). Session-081 local verifier + py_compile + `git diff --check` PASS after final docs/log edits; CatDesk standard verifier = NOT_CONFIGURED (expected for this Theos-only repo without Cargo.toml/package.json/Python project manifest). Current Objective-C aux state-machine edits need next macOS CI run; dynamic device tests vẫn pending.
