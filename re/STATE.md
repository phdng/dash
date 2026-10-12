# STATE.md — DuoDash iOS Tweak Reconstruction
_Last updated: 2026-10-11 session-401 (portable 269FC dock geometry oracle CI tests)_

## PROJECT:
Tái hiện behavior-equivalent của iOS tweak **DuoDash-STL-1.0** (SenseTechLab, (c)2026) — CarPlay dual-pane AppBridge + HUD + Unified Keyboard + License + Perf tweaks. Artifacts: `DuoDash.dylib` (3087248B, 4018 funcs), `DuoDash.app` (`com.sensetechlab.duodash`), `DuoDashKey.app` (`com.sensetechlab.duodashkey`), `DuoDashPrefs.bundle` (`com.sensetechlab.duodash.prefs`).

## CURRENT STATUS:
Session-401 adds executable portable Python geometry-vector oracle for 269FC dock-covered expansion, covering four edges and exact adjacency/usable containment tolerance boundaries. The `build.yml` workflow now runs these Python tests before the compiled macOS Objective-C smoke and watches the new script for push/PR triggers. Executed Python tests PASS (2 test methods), structural verifier PASS (30 modules), git diff --check PASS on Windows local workspace. Objective-C macOS smoke, Theos arm64 and physical CarPlay remain unverified.

Session-400 adds a pure-data `DDHostDockCoverageReason` adapter combining original 269FC early exit reasons with adjacent strip matching and expanded usable-rect containment. It distinguishes no-exit, no-strip-published, no-window, already-inside, strip-not-adjacent, outside-usable and covered; output CGRect changes only on covered. Extended Objective-C smoke to test each branch and unchanged output on rejected decisions; verifier export registry updated. Local reconstruction verifier (30 modules) and git diff PASS; native macOS smoke, Theos arm64 and CarPlay hardware remain unverified.

Session-399 corrected an invalid regression fixture introduced in Session-398: the purported accepted left-side dock occupied x=20 while the provided usable bounds inset(-1) only reached x=38. Updated the valid fixture to usable x=21 (expanded minimum x=20), and added rejected x=21.1 (expanded minimum x=20.1) with unchanged output. Local structural verifier (30 modules) and diff PASS. Compiled macOS Objective-C smoke, Theos arm64 and CarPlay hardware unverified.

Session-398 adds macOS Objective-C smoke assertions for 269FC covered dock geometry tolerance boundaries: exactly 2pt adjacency, >2pt rejection, containment within usable rectangle expanded by 1pt and unchanged output on rejection. Structural verifier (30 modules) and git diff --check PASS locally; compiled macOS Objective-C smoke, Theos arm64 and CarPlay device remain unverified.

Session-397 ports the source-evidenced 269FC final `covered` geometry gate: extend candidate CGRect toward an adjacent dock on left/right/top/bottom, then require containment within `CGRectInset(carPlayUsableBounds,-1,-1)`. Added `DDHostDockCoveredExpandedBounds` to compiled HostFlowAdapter.m and public header. Smoke covers four orientations, rejected usable-bounds overflow and unchanged output. Local verifier (30 modules), py_compile and git diff PASS. No private UI operation; macOS Objective-C executable, Theos arm64 and device tests unconfirmed.

Session-396 ports a bounded pure-data classification from original `269FC.c`: dock spanning candidate window with <=2pt edge adjacency is marked left/right/top/bottom by `DDHostDockAdjacentEdge`. The helper refuses nonfinite, empty and already-inside rectangles. It does not perform the final extended-rectangle check against CarPlay usable bounds and does not authorize live UI hosting. Smoke tests and structural verifier updated; local verifier, py_compile and diff PASS. macOS Objective-C runtime, Theos arm64 and device tests unconfirmed.

Session-395 directly ports the early reason gates from original `DuoDash.dylib_export_for_ai/decompile/269FC.c` into `DDHostDockCoverageEarlyReason`. The helper orders no-exit, no-strip-published, no-window, and already-inside (candidate CGRect expanded 2pt), returning nil when further adjacency/covered checks are required. Test-only macOS smoke and structural verifier extended. Local verifier (30 modules), Python py_compile and diff PASS. Private dock notification acquisition, later coverage geometry, compiled macOS smoke, Theos arm64 and live CarPlay are unverified.

Session-394 adds `DDHostTrimFallbackCarPlayBoundsForDockState`, the source-evidenced 23D94 fallback measured-dock branch: shell empty/under 40pt or outside the expanded usable bounds causes dock clipping to start from carPlayUsableBounds. The helper composes 83FC packed dock decoding with 26654 edge stripping, with no private notification or UI mutation. Smoke covers missing, undersized and outside shell, valid shell rejection and invalid state; local verifier, Python compile and diff PASS. macOS Objective-C smoke, Theos arm64 CI and real CarPlay still unconfirmed.

Session-393 expands Objective-C smoke assertions for `DDHostTrimUsableBoundsForDock` with direct clipped CGRect cases: dock overhang outside usable area, inclusive 2pt near-edge tolerance, exact 40pt residual success and sub-40pt residual rejection preserving output. Local structural verifier (30 modules) and diff PASS; macOS compiled smoke, Theos arm64 and CarPlay device remain unverified.

Session-392 expands Objective-C smoke coverage of source-derived 83FC -> 26654 integration: packed right/top/bottom dock state must produce exactly the same trimmed CGRect as the direct dock CGRect path, and packed non-edge dock must reject without changing caller output. Uses portable C CGRect arrays in Foundation-only macOS harness. Local reconstruction verifier (30 modules), py_compile and diff PASS; compiled smoke, Theos arm64 and physical CarPlay device still unverified.

Session-391 composes the source-derived packed dock notification decoder (83FC) with edge strip classification/clipping (26654) through `DDHostTrimUsableBoundsForDockState`, a pure-data adapter accepting caller-fed 64-bit dock state and usable CGRect. Atomic fail-closed output semantics and macOS smoke assertions added, structural verifier updated. Local reconstruction verifier (30 modules), py_compile, and diff PASS. No private notification subscription or live host UI mutations; compiled macOS, Theos arm64, and CarPlay device still unverified.

Session-390 hardens the compiled 26654 dock edge classifier against nonfinite CGRect origins and dimensions before CoreGraphics intersection. It adds Objective-C smoke regressions for dock overhang, inclusive 2pt edge tolerance, >=40pt surviving width threshold, and NaN/infinity input. Local reconstruction verifier (30 modules), Python syntax and git diff PASS; compiled macOS Objective-C smoke, iOS arm64 Theos and device testing remain unconfirmed.

Session-389 adds DDHostTrimUsableBoundsForDock to reconstruct the remaining CGRect after subtracting a valid dock edge strip, using the evidenced 26654 edge classification and CGRectIntersection. It rejects non-edge, outside and degenerate dock areas without modifying output. Test-only smoke covers left/right/top/bottom and rejected cases. Structural verifier, Python syntax and git diff PASS; macOS Objective-C, Theos arm64 and device CarPlay tests remain unconfirmed. This helper is decision-only and does not mutate live host UI.

Session-388 ports the documented edge-strip classification logic from `DuoDash.dylib_export_for_ai/decompile/26654.c` into DDHostDockEdgeLabel on compiled HostFlowAdapter.m. It intersects caller-fed dock and usable CGRects, checks 2pt edge tolerances and 40pt remaining width/height thresholds, and returns left/right/top/bottom/not-an-edge-strip/strip-outside-area/degenerate labels. Added macOS smoke cases and adjusted verifier return-type matching to include NSString *. Local verifier, py_compile and diff PASS; no runtime dock geometry mutations. macOS Objective-C, Theos arm64 and CarPlay device unverified.

Session-387 ports the pure-data 64-bit dock-rect notification decoder from original `DuoDash.dylib_export_for_ai/decompile/83FC.c` into `DDHostDecodeDockRectState`. Fields are four unsigned 16-bit values (x/y/width/height) in units of one-tenth point, from high to low bits. Rejects empty/invalid width or height; output pointer optional and unchanged on failure. Smoke regression and verifier export contract added; local structural verifier/diff PASS. Does not register or read system notifications yet; macOS compiled smoke, Theos arm64 and CarPlay device remain unverified.

Session-386 ports the 23D94 CGRect containment calculation (CGRectInset usable CarPlay bounds by -1pt and CGRectContainsRect shell bounds) as `DDHostGeometryIsCarPlaySubrectForRects` using caller-fed CGRects, composing with Session-385 threshold logic. Adds smoke tests for valid/invalid positions, inclusive 1pt boundary, undersized shell, and rejects nonfinite/empty rectangles. Local structural verifier/diff PASS; macOS Objective-C execution, Theos arm64 and real device hosting unverified.

Session-385 inspects original `DuoDash.dylib_export_for_ai/decompile/23D94.c` and ports only the evidence-safe `carplay-subrect` branch condition: nonempty >=40pt shell, caller-verified containment in usable CarPlay bounds expanded 1pt, and shell smaller than usable dimensions by over 1pt on either axis. Added `DDHostGeometryIsCarPlaySubrect` to compiled header/source with smoke boundary checks; verifier/diff PASS. Private dock measurement, sub_26654, sub_269FC and entire host geometry calculation remain unimplemented.

Session-384 directly ports the pure-data geometry mismatch predicate of original `DuoDash.dylib_export_for_ai/decompile/22D64.c`, used by 218D8 and 208F4, as DDHostDisplayGeometryMismatch. Caller supplies actual shell bounds, saved shell dimensions, CarPlay display size and calculated dimensions from private sub_23D94. The 40-point saved-shell threshold and 1-point comparisons are preserved. Test smoke cases and structural verifier were updated; local checks PASS. Private acquisition/23D94, CI arm64 and device tests are outstanding.

Session-383 adds DDHostPreparedSlotsAndFlagsMatch combining only directly evidenced 218D8:213–295 conditions: normalized vs hosted BIDs, active first slot dimensions, and prepared-vs-hosted CarPlay UI flags. Mac smoke regression cases ensure each independent gate can reject. Structural verifier registers new public helper. Local reconstruction verifier/diff PASS. Additional private guards sub_22D64 and controller state not incorporated; Objective-C macOS CI, Theos arm64 and CarPlay device tests unconfirmed.

Session-382 directly ported the prepared-vs-hosted CarPlay UI flag comparison from original DuoDash dylib decompile/218D8.c:264–295 into DDHostPreparedCarPlayFlagsMatch (DuoDashShared.h/HostFlowAdapter.m), without speculating about private sub_22E40. Test-only macOS smoke now covers exact matches, missing flags, ignored trailing entries, mismatch, and malformed/zero-count inputs. Structural verifier updated; local verifier and git diff PASS. This helper remains opt-in and does not perform UI hosting. macOS Objective-C and Theos arm64 CI unconfirmed.

Session-381 hardens scripts/verify_reconstruction.py with explicit guards for both macOS arm64 Objective-C object compilation steps, the arm64 link target, lipo architecture validation, Foundation/CoreFoundation and Theos build invocation. Local verifier and diff PASS; macOS Objective-C executable/link and iOS arm64 CI outcomes remain unconfirmed.

## CURRENT PHASE:
Phase 1-4 static HOÀN TẤT; Phase 5 buildability đang promote từng evidence-safe subsystem vào runtime mà không bịa private contracts.

## LAST COMPLETED TASK (session-398):
- Added exact adjacency and expanded usable-bounds tolerance tests for 269FC covered geometry.

## CURRENT TASK:
- Continue bounded Phase-5 evidence-safe helper promotions after user-confirmed green CI. No speculative private-hook wiring. Assistant không push.

## NEXT TASK:
- Continue the `218D8` toggle slice only where constants are exact. `paneratio` still contains unresolved `&stru_20+18` fallback metadata, so do not promote it until that constant is recovered. HUD/BLE and A2720 remain insufficiently evidenced for exact promotion. Jailbroken-device smoke tests remain unresolved.

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

## FILES CHANGED (sessions 375–377, uncommitted):
- Sửa: `re/RECONSTRUCTION/HostFlowAdapter.m`, `re/RECONSTRUCTION/DuoDashShared.h`, `re/STATE.md`.
- Mới: `re/LOG/session-361.md`, `re/LOG/session-362.md`, `re/LOG/session-363.md`, `re/LOG/session-364.md`, `re/LOG/session-365.md`, `re/LOG/session-366.md`, `re/LOG/session-367.md`, `re/LOG/session-368.md`, `re/LOG/session-369.md`, `re/LOG/session-370.md`, `re/LOG/session-371.md`, `re/LOG/session-372.md`, `re/LOG/session-373.md`, `re/LOG/session-375.md`, `re/LOG/session-376.md`, `re/LOG/session-377.md`. Earlier sessions 346–350 already in HEAD at this session start.
- Prior sessions 335–342 are in the current clean HEAD observed at session start.

## TEST STATUS:
Theos arm64 CI GREEN was last explicitly confirmed through session-312. Session-381 structural local checks PASS (Objective-C tests not executed locally): reconstruction verifier and git diff --check (LF/CRLF warnings only). New Objective-C code is not locally compiled; arm64 CI unconfirmed. Assistant không push.
