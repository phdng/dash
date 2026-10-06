# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-072 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-3 (session-072): GitHub Actions session-071 batch đã xanh. Executable target hiện thêm read-only 7764C liveness probe (libproc) và pure 7E63C/7EEDC integer validation/self-healing bên cạnh role/prefs/cache/notify/logical-evict runtime trước đó. 30 synthesis modules còn lại vẫn giữ APPROXIMATION/UNKNOWN rõ ràng.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-072):
- R-061 7764C liveness probe + libproc; R-062 7E63C/7EEDC integer validator/self-healing; verifier/docs updated.

## CURRENT TASK:
- Chờ compiler gate cho session-072 changes; local structural checks đã xanh.

## NEXT TASK:
- Sau khi push, GitHub Actions build current runtime. Nếu xanh, R-063 đọc 73E8/80D0/8154/81EC và chỉ promote numeric cache-reader wrappers có bounds/default args recoverable; không đoán args bị decompiler làm mất. Artifact mới vẫn cần cho P0-3, Q-09/Q-10/Q-12/Q-13 và dynamic verify.

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

## FILES CHANGED (session-072):
- Sửa: `Makefile`, `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-072.md`.

## TEST STATUS:
Session-071 GitHub Actions build GREEN (user-confirmed). Session-072 local verifier + py_compile + `git diff --check` pass. Current Objective-C/libproc edits need next macOS CI run; dynamic device tests vẫn pending.
