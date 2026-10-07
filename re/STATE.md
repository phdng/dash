# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-158 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-89 (session-158): GitHub Actions session-157 (`dde603e`) đã xanh theo user. Executable target thêm data-only `35FBC` splash-fade UIView-animation action-0 cleanup outcome từ LSDA `0x113F94` + raw ARM64. Một action-0 range `0x3606C..0x36084` bao duration/arguments + `+[UIView animateWithDuration:animations:completion:]`; trước range, animation/completion strong captures đã retain/commit và completion weak capture đã copy. Landing `0x360B4` giữ active exception, destroy copied weak capture rồi resume unwind `0x360C4`, không swallow. Normal strong-capture releases ngoài range bị bypass trên unwind path; animation side effects có thể đã apply trước throw. Unprotected paths propagate. Không live animation/capture/ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-158):
- R-157 data-only 35FBC splash-fade UIView-animation action-0 cleanup outcome: copied weak capture cleanup before resume unwind, precommitted strong capture lifetime/release bypass, possible animation side-effect persistence, and unprotected propagation recorded.

## CURRENT TASK:
- R-157 hoàn tất local; commit-only handoff. User confirmed session-157 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-158 batch, R-158: inspect `358F0 -> 0x113EDC`, large splash creation/preferences/image/dispatch pipeline. Exact LSDA call-site table has 29 entries, with protected action indices 5 plus initial action 7 and many unprotected gaps. Protected landing aliases `0x35F60/64/68/6C/70/74/78/7C/80` all converge at common discriminator `0x35F84`; expected type begin/end-catches and returns, nonmatching type resumes unwind at `0x35FB8`. Decode action-chain 7 separately before assigning semantics. Map NSFileManager no-splash gate, content-view/bounds, splash selection prefs/type parsing, image-path/image loading, view/image-view construction, global splash store, duration parsing, qword_163C30 timing, weak captures, and two dispatch_after blocks site-by-site without genericizing. After R-158, `35880 -> 0x113EC8` is an action-1 catch-all around opacity check + CATransaction begin/setDisableActions/setOpacity/commit. 73E8/80D0/full 7E908 and device smoke tests remain unresolved.

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

## FILES CHANGED (session-158):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-158.md`.

## TEST STATUS:
Session-157 GitHub Actions build GREEN (`dde603e`, user-confirmed). Session-158 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
