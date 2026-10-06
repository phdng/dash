# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-05 session-069 (function-level reconstruction — STEADY STATE)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
STEADY STATE (từ session-069): static reconstruction hoàn tất trong điều kiện artifacts hiện có — 11 function records (INFERRED) + 30 synthesis files (APPROXIMATION) + ledger/COMPARISON/COVERAGE đầy đủ; integrity audit pass (LOG 68/68, artifacts 42/42). Chỉ mở scope mới khi có artifacts mới (device jailbroken / decompile thêm / entitlements / MITM captures).

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT (FINAL): mọi subsystem chính có behavioral model CONFIRMED; tàn dư liệt kê đóng ở OPEN_QUESTIONS + LOG-011 (không mở rộng nếu không có artifacts mới).

## LAST COMPLETED TASK (session-069):
- Integrity audit (LOG/artifacts/TESTS) + R-004 superseded + R-056 steady-state declaration.

## CURRENT TASK:
STANDBY — không session routine nữa. Mở session mới chỉ khi: (a) artifacts mới, (b) user yêu cầu verify/sửa cụ thể, (c) phát hiện inconsistency trong audit.

## NEXT TASK:
- Chờ artifacts mới (device / decompile / entitlements / MITM) để mở: P0-3 raw asm, P1 4C34 record, TESTS dynamic, Q-09/Q-10/Q-12/Q-13.

## BLOCKERS:
- P0-3 blocked (raw asm 27E20). Không device. Git local-only. Tàn dư đóng ở LOG-011.

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

## FILES CHANGED (session-069):
- Mới: `LOG/session-069.md`.
- Sửa: TODO (R-004 superseded, R-056), STATE (steady-state).

## TEST STATUS:
Static asserts session-002..004 pass (TESTS.md). Dynamic + build vẫn pending (không device/toolchain).
