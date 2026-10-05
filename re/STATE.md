# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-05 session-011 (FINAL static)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
Session-011 FINAL static: DDz3 picker→host bridge (F-039) + cpuiGen lifecycle (F-040). Mọi subsystem chính đã có behavioral model. Tàn dư liệt kê đóng. Tag static-complete.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT (FINAL): mọi subsystem chính có behavioral model CONFIRMED; tàn dư liệt kê đóng ở OPEN_QUESTIONS + LOG-011 (không mở rộng nếu không có artifacts mới).

## LAST COMPLETED TASK (session-011):
- 2 subagents (DDz3 commit chain, cpuiGen trace) + persist 2 EVIDENCE + FINDINGS/BEHAVIOR/OPEN_QUESTIONS + FINAL verdict + tag.

## CURRENT TASK:
Checkpoint: tag + commit + STATE/TODO/LOG session-011 (đang làm).

## NEXT TASK (session-012, nếu có artifacts mới/yêu cầu):
1. Dynamic verify trên device (TESTS.md dynamic list).
2. Đào sâu tàn dư theo ưu tiên user.
3. RECONSTRUCTION code bodies (cần toolchain + scope).

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

## FILES CHANGED (session-011):
- Mới: `EVIDENCE/ddz3_commit.md`, `EVIDENCE/cpuigen_trace.md`, `LOG/session-011.md`.
- Sửa: FINDINGS (+F-039/F-040), BEHAVIOR (+B-29/B-30 + FINAL), OPEN_QUESTIONS (Q-11).

## TEST STATUS:
Static asserts session-002..004 pass (TESTS.md). Dynamic + build vẫn pending (không device/toolchain).
