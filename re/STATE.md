# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-103 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-34 (session-103): GitHub Actions session-102 (`d7fd24d`) đã xanh theo user. Executable target thêm data-only `41F50` private scene-settings mutation exception outcome được xác nhận bằng LSDA `0x114E8C` + raw ARM64: bốn typed protected ranges quanh `_frame`/`_foreground` ivar lookup/diagnostic/offset, force-IO/orientation repair (`42124`/`9C3BC`/nested `421CC`) và final foreground-offset resolution đều catch/swallow tại `0x4210C` rồi nhảy `0x420C8`, bỏ toàn bộ private mutation/control còn lại và bypass `dword_162F34` failure-budget decrement trước normal return. Không 41BA0 reason-probe, không synthesize/catch exception, invoke private ivar APIs/writes/diagnostics/helpers, hay mutate counters/settings.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-103):
- R-102 data-only 41F50 exception outcome: all typed private-settings catches→swallow, skip remaining mutation/control and failure-budget decrement, then normal final retain/cleanup/return; no reason probe.

## CURRENT TASK:
- R-102 hoàn tất local; commit-only handoff. User sẽ tự push và báo compiler green/pass trước khi R-103 bắt đầu.

## NEXT TASK:
- Sau compiler xanh, R-103 decode `400D0` LSDA `0x114AD8` + raw ARM64 exception behavior qua host/aux identity routing, scene/settings reads, frame/orientation decision paths, private `3F5C0`/`3E670`, và các continuation/cleanup tương ứng; chỉ promote data-only continuation/probe/unwind outcomes, không invoke private traversal/executors/side effects hay mutate counters/globals. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-103):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-103.md`.

## TEST STATUS:
Session-102 GitHub Actions build GREEN (`d7fd24d`, user-confirmed). Session-103 local verifier + py_compile PASS trước docs/log finalization; `git diff --check` sẽ chạy trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit; user tự push và báo compiler result. Dynamic device tests vẫn pending.
