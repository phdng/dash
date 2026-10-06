# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-075 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-6 (session-075): GitHub Actions session-074 batch đã xanh. Executable target hiện thêm UIApp-side bundle-scoped IPC consumer từ 4CBDC + exact state/fontfloor/keypane parsing cache + active re-request/3s stale timeout + background teardown semantics. UIKit relayout/font mutation, key-probe/input mutation và SpringBoard 3F224 multi-slot response vẫn giữ explicit gap.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-075):
- R-068 UIApp consumer: 4CBDC evidence-safe wiring + 4407C/443FC/444C4 parser defaults + 445F8/447C0 stale-state timeout + 446E4 background semantics + 42F10 temp/legacy marker lookup.

## CURRENT TASK:
- Chờ compiler gate cho session-075 changes; local structural checks chạy sau final docs.

## NEXT TASK:
- R-069 SpringBoard onUIAppRequest 3F224 đang blocked vì thiếu exact per-slot render-size accessor cho slots 1/2. Sau CI xanh, ưu tiên tìm direct safe state bridge/accessor; nếu vẫn không có thì chuyển sang gap khác thay vì dùng slot-0 size cho mọi slot. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-075):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-075.md`.

## TEST STATUS:
Session-074 GitHub Actions build GREEN (user-confirmed). Session-075 local verifier + py_compile + `git diff --check` PASS after final tracking edits; CatDesk standard verifier = NOT_CONFIGURED (expected for Theos-only repo without Cargo/package.json/Python manifest). Current Objective-C observer/block/state-cache edits need next macOS CI run; dynamic device tests vẫn pending.
