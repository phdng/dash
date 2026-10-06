# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-083 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-14 (session-083): executable target thêm pure identity size/orientation/settings decisions quanh 41D80/41E94/3FAF8/40514. Raw ARM64 xác nhận 41D80/41E94 trả cặp double dù decompiler type sai: native size ưu tiên host slot non-CarPlay rồi aux; aux orientation 3/4 portrait-normalize khi width>height; non-aux dùng exact landscape-swap gate. 40514 snapshot/diff decisions được promote data-only; FBSSceneSettingsDiff/private ivar/settings mutation vẫn explicit gap.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-083):
- R-082 raw-ARM64-confirmed identity native/adjusted size, raw 3FAF8 orientation, and pure 40514 direct-repair/snapshot/diff-clear decisions.

## CURRENT TASK:
- Chờ compiler gate cho session-083 changes; final local structural checks chạy sau tracking/log update.

## NEXT TASK:
- Sau compiler xanh, R-083 inspect remaining pure callback rewrites `40C5C/40DA8/40F0C`: dimension substitution + orientation equality. `40FF4` private setForeground mutation chỉ được represent bằng caller-driven decision descriptor nếu contract đủ; không invoke private setter. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-083):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-083.md`.

## TEST STATUS:
Last explicitly recorded GitHub Actions compiler green remains session-081. Session-082 is already committed/pushed at `89dc8cb` and accepted by user; this workspace has no independent CI-status surface. Session-083 local verifier + py_compile + `git diff --check` PASS after final docs/log edits; CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Current Objective-C pure-decision helpers need next macOS CI run; dynamic device tests vẫn pending.
