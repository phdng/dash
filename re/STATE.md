# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-151 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-82 (session-151): GitHub Actions session-150 (`43a6ef8`) đã xanh theo user. Executable target thêm data-only `36E00` display-bounds zero-fallback exception outcome từ LSDA `0x11409C` + raw ARM64. Một action-5 range `0x36E18..0x36E2C` bao UIScreen mainScreen+retain, x19 commit và bounds; range kết thúc trước d8/d9 bounds capture. Expected catch swallow rồi jump `0x36E60`, force `0.0`; runtime tách pre-x19 screen acquisition khỏi post-x19 bounds read, chỉ bounds-site ghi retained-screen release bypass. Bounds dimensions không được commit trên caught path. Nonmatching unwind `0x36E94`; unprotected tail propagate. Không UIScreen lookup/bounds execution, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-151):
- R-150 data-only 36E00 display-bounds zero-fallback exception outcome: one typed range→forced `0.0`; exact pre/post x19 UIScreen ownership, retained-screen release bypass, uncommitted/ignored bounds dimensions, unprotected propagation and nonmatching unwind recorded.

## CURRENT TASK:
- R-150 hoàn tất local; commit-only handoff. User confirmed session-150 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-151 batch, R-151: inspect `369E8 -> 0x114058`, layout-area/preferences-notify helper. Exact 9-entry table: typed `0x36A20..0x36A24 -> 0x36DE0`; typed `0x36C64..0x36C7C -> 0x36DDC`; typed `0x36CC0..0x36CE0 -> 0x36DEC`; typed `0x36CFC..0x36D1C -> 0x36DD8`; typed `0x36D28..0x36D2C -> 0x36DEC`; action-0 `0x36D30..0x36D40 -> 0x36DE8`; typed `0x36D40..0x36D94 -> 0x36DEC`; action-0 `0x36D94..0x36DA4 -> 0x36DE8`; final tail unprotected. Common typed catch `0x36DEC` swallows expected type and jumps final cleanup; aliases `0x36DD8/36DDC` route into it, while `0x36DE0` has an extra discriminator-zero branch before unwind. Map retained label/status strings, global qword_163AE8 store timing, preferences writes/synchronize, Darwin-notify creation/post, and action-0 cleanup unwind precisely. Next earlier LSDA-bearing function is `365D4 -> 0x113FFC`. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-151):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-151.md`.

## TEST STATUS:
Session-150 GitHub Actions build GREEN (`43a6ef8`, user-confirmed). Session-151 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
