# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-145 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-76 (session-145): GitHub Actions session-144 (`01d2a46`) đã xanh theo user. Executable target thêm data-only `374C4` keypane rectangle-forward exception outcome từ LSDA `0x11413C` + raw ARM64. Một action-5 range `0x374FC..0x3751C` bao candidate CGRect helper `376DC` + `CGRectIsNull`. Caller rectangle vẫn nằm ở `d9/d8/d10/d11`; candidate chỉ được adopt sau protected range. Expected catch swallow rồi jump `0x3755C`, giữ original rectangle, bỏ candidate adoption + positive `dword_162EF0` decrement, vẫn gọi `off_163C58`, rồi cleanup input. Null-check site ghi candidate đã acquire; helper site không overclaim. Unprotected/nonmatching propagate/unwind. Không geometry/callback execution, counter mutation, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-145):
- R-144 data-only 374C4 keypane rectangle-forward exception outcome: one typed range→preserve original caller rectangle+skip candidate adoption/counter decrement+still forward through off_163C58+normal cleanup; null-check candidate-acquired timing, unprotected propagation and nonmatching unwind recorded.

## CURRENT TASK:
- R-144 hoàn tất local; commit-only handoff. User confirmed session-144 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-145 batch, R-145: inspect `37398 -> 0x114114` (`setCenter:` landscape wrapper). Exact 5-entry table has typed `0x373CC..0x373D0 -> 0x374A8` (`37640`), typed `0x373D0..0x373EC -> 0x374AC` (`376DC` candidate + `CGRectIsNull`), typed `0x373FC..0x37428 -> 0x374A4` (`CGRectGetMidX/MidY`), then unprotected tail. All aliases converge typed catch `0x374AC`, whose expected path begin/end-catches and jumps to `0x37468` before calling `off_163C50`. Important evidence gap: early protected ranges can throw before this function locally assigns `d10/d11`, yet catch continuation forwards those registers; registration/caller inspection has not established their source. Resolve this register-state question before promoting any fallback-midpoint claim. Later midX/midY site can be mapped separately with stronger local initialization evidence. Next earlier LSDA-bearing function is `37284 -> 0x114100`. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-145):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-145.md`.

## TEST STATUS:
Session-144 GitHub Actions build GREEN (`01d2a46`, user-confirmed). Session-145 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
