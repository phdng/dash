# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-121 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-52 (session-121): GitHub Actions session-120 (`344479f`) đã xanh theo user. Executable target thêm data-only `3DD4C` bundle-normalization exception outcome được xác nhận bằng LSDA `0x1147EC` + raw ARM64: early protected `SBApplicationController sharedInstance` send/retain lands at typed catch `0x3DFA8`, expected discriminator catch/swallow then force controller nil and resume canonicalization `0x3DDC8`; per-item `applicationWithBundleIdentifier:` send/retain lands at typed catch `0x3DF54`, expected discriminator catch/swallow then rejoin `0x3DF28`, preserving sanitized candidate for add/continue loop. Both nonmatching types `0x3DFC4` resume unwind. Không query private controller/selectors, retain live apps, mutate arrays hay synthesize/catch exception.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-121):
- R-120 data-only 3DD4C exception outcome: early controller lookup throw→swallow+controller nil+continue canonicalization; per-item app lookup throw→swallow+preserve candidate+add/continue loop; nonmatching types→resume unwind.

## CURRENT TASK:
- R-120 hoàn tất local; commit-only handoff. User sẽ tự push và báo compiler green/pass trước khi R-121 bắt đầu.

## NEXT TASK:
- Sau compiler xanh, R-121 promote exact `3D990` LSDA `0x1147A0`: private hosted-controller teardown catches→swallow+skip remaining private teardown+continue bridge-off phase; slot0 publish catch→continue slots1/2; slot1/2 publish catch→continue loop; cleanup-only/final reset exceptions→resume/propagate unwind. Chỉ data-only continuation/propagation/lifetime metadata, không remove/invalidate views, invoke `89D8`, mutate hosted ivars hay reset real host state. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-121):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-121.md`.

## TEST STATUS:
Session-120 GitHub Actions build GREEN (`344479f`, user-confirmed). Session-121 local verifier + py_compile PASS trước docs/log finalization; `git diff --check` sẽ chạy trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit; user tự push và báo compiler result. Dynamic device tests vẫn pending.
