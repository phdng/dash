# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-101 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-32 (session-101): GitHub Actions session-100 (`7262e2e`) đã xanh theo user. Executable target thêm data-only `41730` to-apps yield exception outcome được xác nhận bằng LSDA `0x114DAC` + raw ARM64: pre-yield/private enumeration/matching/toggle throw bị swallow rồi fallback original; DDz2 dismiss throw tiếp tục cpdisconnect; cpdisconnect throw nhảy original và bypass normal `byte_163EC0` clear nên yield-in-progress would remain set; DDz1 hide throw tiếp tục yield-log; yield-log throw tiếp tục cleanup/reset; cleanup-only throw resume unwind; original-callback throw bị swallow, reuse exact 41BA0 bounded reason-probe, không retry và cleanup/return; nested probe throw resume unwind. Không synthesize/catch exception, invoke private entity/side effects/original callback, reason read hay mutate globals.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-101):
- R-100 data-only 41730 exception outcome: pre-yield/entity/toggle catches→original; dismiss/hide/log catches preserve their exact continuation; cpdisconnect catch→original with stuck yield-in-progress metadata; cleanup-only→unwind; original-callback catch→existing 41BA0 probe→cleanup/no retry.

## CURRENT TASK:
- R-100 hoàn tất local; commit-only handoff. User sẽ tự push và báo compiler green/pass trước khi R-101 bắt đầu.

## NEXT TASK:
- Sau compiler xanh, R-101 decode `421CC` LSDA/raw-ARM64 exception behavior quanh private `_otherSettings` resolution và `_setFlag:forSetting:` capability/send; chỉ promote data-only swallow/cleanup outcome, không invoke private ivar access/setter, synthesize exceptions hay mutate settings/globals. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-101):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-101.md`.

## TEST STATUS:
Session-100 GitHub Actions build GREEN (`7262e2e`, user-confirmed). Session-101 local verifier + py_compile PASS trước docs/log finalization; `git diff --check` sẽ chạy trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit; user tự push và báo compiler result. Dynamic device tests vẫn pending.
