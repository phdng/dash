# LOG/session-101.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-100 commit 7262e2e; complete R-100 by decoding `41730` LSDA/raw-ARM64 exception behavior and promoting only evidence-safe data-only continuation/probe/unwind outcomes. Per user workflow, commit locally but do not push._

## R-100 — evidence source

Reviewed:
- `41730.c`;
- raw ARM64 for `41730` from the first arm64 FAT slice;
- Mach-O `__unwind_info` / `__gcc_except_tab` mapping;
- existing R-085 to-apps yield-vs-swallow decision;
- existing `41BA0` bounded reason-probe contract.

The first arm64 FAT slice begins at file offset `0x4000`.

`__unwind_info` maps:
- `41730` -> LSDA `0x114DAC`.

The decoded call-site table is:
- `0x41730..0x41784` -> no landing pad;
- `0x41784..0x41788` -> `0x41B84`, action 5;
- `0x417D0..0x417DC` -> `0x41B24`, action 5;
- `0x417E0..0x417F4` -> `0x41B18`, action 5;
- `0x417FC..0x41820` -> `0x41B20`, action 5;
- `0x4182C..0x41838` -> `0x41B14`, action 5;
- `0x41838..0x41854` -> no landing pad;
- `0x41854..0x41864` -> `0x41B10`, action 5;
- `0x41898..0x418B8` -> `0x41B70`, action 5;
- `0x418BC..0x418E0` -> `0x41B6C`, action 5;
- `0x418EC..0x41908` -> `0x41B74`, action 5;
- `0x4190C..0x4191C` -> `0x41B78`, cleanup/action 0;
- `0x41928..0x4193C` -> `0x41B0C`, action 5;
- `0x41958..0x41974` -> `0x41B1C`, action 5;
- `0x41974..0x419AC` -> `0x41B78`, cleanup/action 0;
- `0x419AC..0x419D0` -> no landing pad;
- `0x419D0..0x419E4` -> `0x41AF0`, action 5;
- `0x419E4..0x419EC` -> `0x41B78`, cleanup/action 0;
- `0x419EC..0x419F8` -> `0x41B1C`, action 5;
- `0x41A00..0x41A14` -> `0x41AD4`, action 5;
- `0x41A14..0x41A1C` -> `0x41B78`, cleanup/action 0;
- `0x41A1C..0x41A28` -> `0x41AB8`, action 5;
- `0x41A28..0x41A60` -> `0x41B78`, cleanup/action 0;
- `0x41A68..0x41A74` -> `0x41B28`, action 5;
- `0x41A74..0x41A7C` -> `0x41B78`, cleanup/action 0;
- `0x41A7C..0x41B40` -> no landing pad;
- `0x41B40..0x41B44` -> `0x41B78`, cleanup/action 0;
- `0x41B44..0x41B4C` -> no landing pad;
- `0x41B4C..0x41B50` -> `0x41B60`, cleanup/action 0;
- `0x41B50..0x41B58` -> `0x41B78`, cleanup/action 0;
- `0x41B58..0x41BA0` -> no landing pad.

## Pre-yield / private enumeration exceptions

The action-5 ranges before the side-effect sequence cover:
- configured non-CarPlay host-slot presence checks;
- `toApplicationSceneEntities` capability/read;
- `allObjects` capability/read;
- `SBDeviceApplicationSceneEntity` class lookup;
- fast-enumeration calls and mutation/class checks;
- per-entity `application` capability/read;
- private bundle-identifier resolution through `3EFD4`;
- `3E4A8` non-CarPlay-host matching;
- later enumeration batches;
- `NSFileManager defaultManager` / `/var/tmp/duodash_ab_toapps_swallow` existence probe.

Their small landing pads all converge at `0x41B84`.

Raw ARM64 at `0x41B84`:
1. verifies the expected catch type;
2. begins catch;
3. ends catch;
4. branches to `0x41A60`, the hooked original-callback path.

Therefore protected pre-yield/private-enumeration/toggle exceptions:
- are swallowed;
- abandon the custom to-apps path;
- call the original callback.

The reconstruction does not reproduce any private entity traversal.

## Cleanup-only regions

Several release/cleanup regions use action-0 landing `0x41B78` rather than a typed catch.

That landing preserves the active exception and resumes unwind through the exception runtime. These ranges include cleanup during:
- nonmatching entity iteration;
- swallow-toggle early-return release path;
- DDz2/DDz1 temporary release paths;
- final matched-identity/entity cleanup;
- original-callback catch cleanup.

These exceptions are not converted into fallback-to-original behavior by `41730`.

Promoted generic outcome:
- `DDToAppsYieldExceptionSiteCleanup` -> `ResumeUnwind`;
- `shouldSwallowException = NO`.

## DDz2 dismiss exception

After a matched destination with swallow-file disabled, the original sets `byte_163EC0 = 1` and begins the yield side-effect sequence.

Protected range `0x419D0..0x419E4` covers:
- `+[DDz2 shared]`;
- retained return handling;
- `dismiss`.

Landing `0x41AF0`:
1. verifies/begins/ends the typed catch;
2. branches to `0x419EC`.

`0x419EC` is the cpdisconnect notification stage.

Therefore a DDz2 dismiss exception:
- is swallowed;
- does not abort the yield sequence;
- resumes with cpdisconnect, then hide/log/cleanup if those later operations succeed.

## cpdisconnect exception — stuck yield-in-progress edge

Protected range `0x419EC..0x419F8` includes:
- construction of `com.sensetechlab.appbridge.cpdisconnect`;
- `notify_post`.

Its landing `0x41B1C` immediately branches into the common typed catch at `0x41B84`, which ends the catch and jumps to the original callback at `0x41A60`.

Critically, the normal `byte_163EC0 = 0` clear is later at `0x41A30`. This catch bypasses it.

Therefore a cpdisconnect exception:
- is swallowed;
- skips DDz1 hide and yield-log side effects;
- calls original;
- leaves the original yield-in-progress byte set.

The reconstruction records this as `yieldInProgressWouldRemainSet = YES`; it does not mutate any byte.

## DDz1 hide exception

Protected range `0x41A00..0x41A14` covers:
- `+[DDz1 shared]`;
- retained return handling;
- `hide`.

Landing `0x41AD4` ends the typed catch and branches to `0x41A1C`, the yield-log call.

Therefore a hide exception:
- is swallowed;
- skips only the remainder of hide itself;
- continues at the yield-log side effect;
- later reaches normal cleanup/reset if no further exception occurs.

## Yield-log exception

Protected range `0x41A1C..0x41A28` covers `sub_4D0F4("to-apps yield")`.

Landing `0x41AB8` ends the typed catch and branches to `0x41A28`, the cleanup sequence.

Therefore a yield-log exception:
- is swallowed;
- resumes at cleanup;
- reaches the normal `byte_163EC0 = 0` clear at `0x41A30` if cleanup proceeds normally.

## Original-callback exception

The indirect hooked original callback is exactly:
- `0x41A68..0x41A74` -> landing `0x41B28`, action 5.

Landing behavior:
1. verifies expected catch type;
2. begins catch;
3. retains the caught exception;
4. calls existing `41BA0(exception)` at `0x41B4C`;
5. releases the retained exception;
6. ends catch;
7. branches to `0x41A74`, normal final cleanup/return.

Therefore an original-callback exception:
- is swallowed;
- original is not retried;
- the existing bounded reason-probe contract applies;
- after a normal probe completion, only final cleanup/return occurs.

## Nested reason-probe exception

The `41BA0` call itself is protected separately:
- `0x41B4C..0x41B50` -> landing `0x41B60`, cleanup/action 0.

Raw ARM64 at `0x41B60` ends the outer catch and then resumes unwind.

Therefore the original-callback exception path reaches cleanup/return only if `41BA0` completes normally.

## Promoted runtime contract

Added:
- `DDToAppsYieldExceptionSite`
  - None
  - PreYieldRouting
  - DismissSideEffect
  - DisconnectSideEffect
  - HideSideEffect
  - YieldLogSideEffect
  - OriginalCallback
  - Cleanup
- `DDToAppsYieldExceptionContinuation`
  - None
  - CallOriginal
  - ContinueYieldSideEffects
  - ContinueYieldCleanup
  - CleanupReturn
  - ResumeUnwind
- `DDToAppsYieldExceptionOutcome`
- `DDResolveToAppsYieldExceptionOutcome(site, currentProbeCount, reasonSelectorSupported)`.

Outcomes:
- PreYieldRouting -> swallow + CallOriginal;
- DismissSideEffect -> swallow + ContinueYieldSideEffects;
- DisconnectSideEffect -> swallow + CallOriginal + `yieldInProgressWouldRemainSet = YES`;
- HideSideEffect -> swallow + ContinueYieldSideEffects;
- YieldLogSideEffect -> swallow + ContinueYieldCleanup;
- OriginalCallback -> swallow + CleanupReturn + existing `DDResolveExceptionReasonProbeDecision` + nested-probe-unwind metadata;
- Cleanup -> ResumeUnwind without swallow.

## Explicit exclusions

R-100 does not:
- synthesize Objective-C exceptions;
- call begin-catch/end-catch;
- invoke `toApplicationSceneEntities`, `allObjects`, entity `application`, or private bundle traversal;
- enumerate `SBDeviceApplicationSceneEntity` objects;
- invoke DDz2 dismiss;
- post cpdisconnect;
- invoke DDz1 hide;
- call `4D0F4`;
- call or suppress the original callback;
- invoke `41BA0` or read exception `reason`;
- mutate `byte_163EC0` or any other global;
- intercept or resume unwind.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — 421CC

`421CC` already has the R-086 data-only `_otherSettings` flag-clear eligibility contract.

`__unwind_info` maps:
- `421CC` -> LSDA `0x114ECC`.

Its call-site table is small:
- `0x421CC..0x421E8` -> no landing pad;
- `0x421E8..0x42234` -> landing `0x42250`, action 5;
- `0x42234..0x42268` -> no landing pad.

Raw ARM64 shows the protected range covers private `_otherSettings` resolution, capability check, and `_setFlag:0 forSetting:6` send. Landing `0x42250` catches/swallow and branches directly to normal outer-object cleanup at `0x4223C`; there is no `41BA0` reason probe.

## Next

R-101 after compiler green:
- promote the exact `421CC` data-only private-settings exception swallow/cleanup outcome;
- keep private ivar access/setter invocation, exception synthesis, settings/global mutation, and any invented diagnostics excluded.
