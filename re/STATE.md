# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-07 session-138 (buildable reconstruction phase)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
BUILDABLE RUNTIME PHASE-69 (session-138): GitHub Actions session-137 (`954d26d`) đã xanh theo user. Executable target thêm data-only `38B0C` display-scale width-cap exception outcome từ LSDA `0x11428C` + raw ARM64. Tám action-5 ranges quanh display acquisition, FBSDisplayConfiguration construction/scale probing, window-bounds fallback và pixelSize đều hội tụ catch `0x38CD0`: expected catch swallow rồi jump `0x38C58`, bỏ remaining display-scale probing/`800/scale` cap, release hai ownership của input view và trả original bounds-derived `d8`. Metadata tách pre-x20 display acquisition, committed display, in-progress config construction trước x21 commit, committed config, temporary retained window, và post-window pixelSize sites. Unprotected/nonmatching propagate/unwind. Không private display/config/window queries, scale computation, ownership mutation hay exception runtime.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-138):
- R-137 data-only 38B0C display-scale width-cap exception outcome: 8 typed ranges→swallow+original-bounds fallback+skip scale cap+input cleanup; site-aware display/config/window commit/release-bypass timing recorded; unprotected/nonmatching paths propagate/unwind.

## CURRENT TASK:
- R-137 hoàn tất local; commit-only handoff. User confirmed session-137 compiler green before this batch; assistant không push.

## NEXT TASK:
- Sau compiler xanh cho session-138 batch, R-138: inspect next earlier LSDA-bearing `3896C -> 0x114250` (`sub_3896C`, property-list file writer). Scout decoded 8 call-site entries: unprotected `0x3896C..0x389C4`; typed action-5 `0x389C4..0x389E0 -> 0x38AAC` around property-list serialization+retain; typed `0x389E8..0x38A00 -> 0x38A94` around `NSData writeToFile:options:error:`; typed `0x38A0C..0x38A6C -> 0x38A98` around defaultManager/permissions-dictionary/setAttributes; action-0 cleanup `0x38A6C..0x38A90 -> 0x38B08`; unprotected catch body `0x38A90..0x38AC0`; action-0 final argument cleanup `0x38AC0..0x38AD0 -> 0x38B08`; unprotected tail. Serialization/write exceptions converge to catch `0x38AAC` and return false; write range occurs after retained data x21 commit so data release may be bypassed. Attribute-phase expected catch `0x38A98` instead sets success `w22=1` and rejoins at `0x38A7C`, because data write already succeeded; depending on throw timing retained file-manager/dictionary releases may be bypassed, while retained data is still released at `0x38A88`. Nonmatching type and action-0 cleanup resume unwind. Split exact attribute sub-sites/ownership before promotion. 73E8/80D0 and full 7E908 remain unresolved; dynamic device verify still needed.

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

## FILES CHANGED (session-138):
- Sửa: `RECONSTRUCTION/ReconstructionRuntime.{h,m}`, `BUILD.md`, `COVERAGE.md`, `scripts/verify_reconstruction.py`, STATE/TODO/TESTS.
- Mới: `LOG/session-138.md`.

## TEST STATUS:
Session-137 GitHub Actions build GREEN (`954d26d`, user-confirmed). Session-138 `python scripts/verify_reconstruction.py` + `python -m py_compile scripts/verify_reconstruction.py` PASS sau runtime edit; sẽ rerun final verifier + `git diff --check` trước commit. CatDesk standard verifier remains NOT_CONFIGURED for this Theos-only repo. Per user workflow, assistant chỉ commit local; không push. Dynamic device tests vẫn pending.
