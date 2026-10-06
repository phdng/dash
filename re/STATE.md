# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-06 session-106 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-37 (session-106): GitHub Actions session-105 (`9cef813`) đã xanh theo user. Executable target thêm data-only `40AE8` presentation-update exception outcome được xác nhận bằng LSDA `0x114C10` + raw ARM64: original-callback throw tại `0x40B40..0x40B54` bị swallow, reuse exact 41BA0 bounded reason-probe rồi nếu probe hoàn tất thì rejoin post-original evaluation tại `0x40B54`; nopresupdate file-manager probe `0x40B68..0x40B98` nằm trong no-landing-pad range nên exception propagate/resume unwind; `_updateFrameAndTransform` capability/send throw tại `0x40BB8..0x40BD4` bị swallow rồi cleanup; nested 41BA0 throw qua cleanup-only `0x40C4C` rồi resume unwind. Không file I/O, synthesize/catch exception, invoke private selector/original callback, reason read hay mutate globals.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-106):
- R-105 data-only 40AE8 exception outcome: original-callback catch→existing 41BA0 probe→post-original evaluation; file-probe range→propagate/unwind; `_updateFrameAndTransform` catch→swallow+cleanup; nested probe→unwind.

## CURRENT TASK:
- R-105 hoàn tất local; commit-only handoff. User sẽ tự push và báo compiler green/pass trước khi R-106 bắt đầu.

## NEXT TASK:
- Sau compiler xanh, R-106 audit/decode exact Mach-O unwind/LSDA exception behavior của private scene-settings executor `3F5C0` và dispatched block `3F7C8`, reconcile với các admission/slot-mark/counter descriptors hiện có; chỉ promote data-only continuation/counter-class/unwind metadata, không dispatch private selector/block, write slot/reentrancy/counters hay synthesize exceptions. 73E8/80D0 và full 7E908 vẫn unresolved; dynamic device verify vẫn cần.

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

## FILES CHANGED (session-106):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-106.md`.

## TEST STATUS:
Session-105 GitHub Actions build GREEN (`9cef813`, user-confirmed). Session-106 local verifier + py_compile PASS trước docs/log finalization; `git diff --check` sẽ chạy trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit; user tự push và báo compiler result. Dynamic device tests vẫn pending.
