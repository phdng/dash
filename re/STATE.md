# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-122 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-53 (session-122): GitHub Actions session-121 (`951bfee`) đã xanh theo user. Executable target thêm data-only `3D990` dismiss-block exception outcome được xác nhận bằng LSDA `0x1147A0` + raw ARM64: primary/secondary private teardown typed catches swallow và jump bridge-off phase `0x3DB14`; primary catch sees only primary controller ivar already cleared, secondary catch sees all three already cleared and bypasses remaining private cleanup. Slot0 publish catch continues slots1/2; later-slot catch continues loop. Private cleanup path and final `resetHostingState` have no local swallow continuation and propagate/resume unwind. Không mutate private views/controllers/hosted ivars, invoke `89D8`, change real lifetime hay synthesize/catch exception.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-122):
- R-121 data-only 3D990 exception outcome: private teardown throws→swallow+continue bridge-off; slot publish throws→continue remaining publications; private cleanup/final reset throws→propagate, with controller-ivar ordering metadata.

## CURRENT TASK:
- R-121 hoàn tất local; commit-only handoff. User sẽ tự push và báo compiler green/pass trước khi R-122 bắt đầu.

## NEXT TASK:
- Sau compiler xanh, R-122 promote exact `3D704` LSDA `0x114774`: private hosted-view teardown throw→typed catch swallow rồi vẫn clear controller ivar + attempt bridge-off + commit bundle/CarPlay flag; bridge-off `89D8` throw→typed catch swallow rồi vẫn commit bundle/CarPlay flag; both nonmatching types→resume unwind. Chỉ data-only continuation/state-commit/unwind metadata, không remove/invalidate views, invoke `89D8` hay mutate live host/private state. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-122):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-122.md`.

## TEST STATUS:
Session-121 GitHub Actions build GREEN (`951bfee`, user-confirmed). Session-122 local verifier + py_compile PASS trước docs/log finalization; `git diff --check` sẽ chạy trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit; user tự push và báo compiler result. Dynamic device tests vẫn pending.
