# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-071 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-2 (session-071): GitHub Actions phase-1 build đã xanh. Executable target hiện có role detect + SpringBoard startup + AppBridge publish, exact-ish prefs setters (746C/84D8/637E8/836C), 29198-safe Darwin reload trio, 85CDC CFBoolean-only semantics và prefs-only logical evict 85B8. 30 synthesis modules còn lại vẫn giữ APPROXIMATION/UNKNOWN rõ ràng.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-071):
- R-058 prefs setters + notify reload fabric; R-059 logical evict 85B8; R-060 exact cache readers + keypane/font-floor pure-pref helpers; verifier mở rộng cho runtime contracts.

## CURRENT TASK:
- Chuẩn bị compiler gate cho session-071 changes, rồi tiếp tục R-060 cache readers / pure prefs helpers.

## NEXT TASK:
- Sau khi push, GitHub Actions build lại current runtime. Nếu xanh, R-061 đánh giá 7764C liveness probe cho compile-safe promotion (snapshot/filter + pid/path checks, libproc nếu contract sạch); SpringBoard/private consumers vẫn giữ ngoài. Artifact mới vẫn cần cho P0-3, Q-09/Q-10/Q-12/Q-13 và dynamic verify.

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

## FILES CHANGED (session-071):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `DuoDashShared.h`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-071.md`.

## TEST STATUS:
Phase-1 GitHub Actions build GREEN (user-confirmed). Session-071 local verifier + py_compile + `git diff --check` pass; standard `verify_project` reports NOT_CONFIGURED because this is a Theos repo without Cargo/package.json/Python manifest. Current Objective-C edits need next macOS CI run; dynamic device tests vẫn pending.
