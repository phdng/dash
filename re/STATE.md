# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-070 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE SCAFFOLD (session-070): static reconstruction vẫn đầy đủ như session-069, đồng thời đã có Theos target thật. Build target chỉ chứa phần compile-safe có evidence: role detect + SpringBoard startup + AppBridge prefs/cache/notify. 30 synthesis modules còn lại vẫn giữ APPROXIMATION/UNKNOWN rõ ràng, không bị fake-stub để qua compiler.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang mở. Mục tiêu là promote từng subsystem từ synthesis sang runtime compile-safe mà không bịa private contracts.

## LAST COMPLETED TASK (session-070):
- Thêm ReconstructionRuntime, Theos Makefile/control/filter, local verifier và GitHub Actions macOS build.

## CURRENT TASK:
- Làm compiler CI xanh, sau đó mở rộng runtime từng subsystem theo evidence.

## NEXT TASK:
- Chạy GitHub Actions “Build Reconstruction”; nếu xanh, ưu tiên prefs setters / notify fabric trước private UIKit/SpringBoard hooks. Artifact mới vẫn cần cho P0-3, Q-09/Q-10/Q-12/Q-13 và dynamic verify.

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

## FILES CHANGED (session-070):
- Mới: root Theos build files, `.github/workflows/build.yml`, `scripts/verify_reconstruction.py`, `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `RECONSTRUCTION/BUILD.md`, `LOG/session-070.md`.
- Sửa: `Tweak.x`, `DuoDashShared.h`, `.gitignore`, STATE/TODO/TESTS/COVERAGE.

## TEST STATUS:
Static asserts cũ vẫn pass. `python scripts/verify_reconstruction.py` pass trên workspace; Theos compiler build được giao cho GitHub Actions macOS; dynamic device tests vẫn pending.
