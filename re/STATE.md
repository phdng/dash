# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-098 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-29 (session-098): GitHub Actions session-097 (`398d0d5`) đã xanh theo user. Executable target thêm data-only 40FF4 exception continuation được xác nhận bằng Mach-O LSDA + ARM64: original-callback throw bị swallow, reuse exact 41BA0 bounded reason-probe rồi quay lại post-original foreground gate nếu probe hoàn tất; throw từ 41CBC hoặc mutable-settings class/kind/selector/setForeground range bị swallow và skip phần foreground còn lại; nested 41BA0 throw thì resume unwind. Không synthesize/catch exception, invoke original/private selectors, mutate foreground, reason read hay probe-counter mutation.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-098):
- R-097 data-only 40FF4 exception continuation: original-callback catch→existing 41BA0 probe→resume post-original foreground evaluation; route/mutable-settings catches→swallow+skip remaining foreground forcing.

## CURRENT TASK:
- R-097 hoàn tất local; commit-only handoff. User sẽ tự push và báo compiler green/pass trước khi R-098 bắt đầu.

## NEXT TASK:
- Sau compiler xanh, R-098 inspect `41138` LSDA/raw-ARM64 exception behavior qua pre-original route/identity extraction, original callback và post-callback destroy routing; chỉ promote data-only continuation/probe/outcome metadata, không invoke private identity/30960/DDz2/slot-clear side effects, synthesize exceptions hay mutate globals. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-098):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-098.md`.

## TEST STATUS:
Session-097 GitHub Actions build GREEN (`398d0d5`, user-confirmed). Session-098 local verifier + py_compile PASS trước docs/log finalization; `git diff --check` sẽ chạy trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit; user tự push và báo compiler result. Dynamic device tests vẫn pending.
