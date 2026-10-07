# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-118 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-49 (session-118): GitHub Actions session-117 (`ecfc20c`) đã xanh theo user. Executable target thêm data-only `3E670` aux settings-preparation exception outcome được xác nhận bằng LSDA `0x114880` + raw ARM64: four protected ranges for initial aux gate, current frame/orientation reads, and late executor-preparation all funnel into common typed catch `0x3E990`; expected discriminator catch/swallow then jumps final outer cleanup `0x3E944`, nonmatching discriminator `0x3E9A4` resume unwind. Late-preparation range begins after retained working object `x22`; catch bypasses its normal release at `0x3E93C`. Không invoke private selectors/runtime methods, dispatch, change real object lifetime, synthesize/catch exception hay mutate globals.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-118):
- R-117 data-only 3E670 exception outcome: four aux-preparation protected sites→common catch swallow+final outer cleanup; nonmatching type→unwind; late site bypasses normal retained-working-object release.

## CURRENT TASK:
- R-117 hoàn tất local; commit-only handoff. User sẽ tự push và báo compiler green/pass trước khi R-118 bắt đầu.

## NEXT TASK:
- Sau compiler xanh, R-118 promote exact `3E33C` LSDA `0x114860`: `sceneIfExists` construction/capability/signature/send path has no local landing pad and propagates; fallback `scene` capability/send range catches/swallow and forces nil; nonmatching type→resume unwind. Chỉ data-only propagate-vs-swallow/nil/unwind metadata, không selector construction/invocation, method-signature inspection hay live scene lifetime effects. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-118):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-118.md`.

## TEST STATUS:
Session-117 GitHub Actions build GREEN (`ecfc20c`, user-confirmed). Session-118 local verifier + py_compile PASS trước docs/log finalization; `git diff --check` sẽ chạy trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit; user tự push và báo compiler result. Dynamic device tests vẫn pending.
