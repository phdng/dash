# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-100 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-31 (session-100): GitHub Actions session-099 (`3887d1d`) đã xanh theo user. Executable target thêm data-only `4138C` sceneHandle exception outcome được xác nhận bằng LSDA `0x114D2C` + raw ARM64: initial scene lookup throw bị swallow rồi fallback original; update-routing/private `3F5C0`/`3E670` throw bị swallow, skip phần update còn lại và rejoin suppression nếu scene còn tồn tại, ngược lại gọi original; suppression-decision throw bị swallow rồi gọi original; original-callback throw bị swallow, reuse exact 41BA0 bounded reason-probe, không retry và đi cleanup; nested 41BA0 throw resume unwind. Không synthesize/catch exception, invoke private selectors/executors/original callback, reason read hay mutate counters.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-100):
- R-099 data-only 4138C exception outcome: initial scene catch→original; update-routing/private-executor catches→suppression continuation if scene exists else original; suppression catches→original; original-callback catch→existing 41BA0 probe→cleanup/no retry.

## CURRENT TASK:
- R-099 hoàn tất local; commit-only handoff. User sẽ tự push và báo compiler green/pass trước khi R-100 bắt đầu.

## NEXT TASK:
- Sau compiler xanh, R-100 decode `41730` LSDA/raw-ARM64 exception behavior quanh destination-entity enumeration, non-CarPlay host matching, yield/dismiss/cpdisconnect/hide side effects, swallow-vs-original routing và original callback; chỉ promote data-only continuation/probe/unwind outcomes, không invoke private entity traversal/side effects/original callback, synthesize exceptions hay mutate globals. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-100):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-100.md`.

## TEST STATUS:
Session-099 GitHub Actions build GREEN (`3887d1d`, user-confirmed). Session-100 local verifier + py_compile PASS trước docs/log finalization; `git diff --check` sẽ chạy trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit; user tự push và báo compiler result. Dynamic device tests vẫn pending.
