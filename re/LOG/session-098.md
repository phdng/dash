# LOG/session-098.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-097 commit 398d0d5; complete R-097 by promoting only the data-only `40FF4` exception continuation/probe outcomes. Per user workflow, commit locally but do not push._

## R-097 — evidence source

Reviewed:
- `40FF4.c`;
- `41BA0.c`;
- raw ARM64 for `40FF4` from the first arm64 FAT slice;
- the `40FF4` Mach-O LSDA mapping scouted in session-097.

The `40FF4` LSDA call-site mapping is:
- original callback `0x41038..0x4104C` -> landing `0x410F4`;
- `41CBC` route eligibility `0x4105C..0x41064` -> landing `0x410D4`;
- mutable-settings class/kind/selector/setter path `0x41068..0x410B0` -> landing `0x410D8`;
- nested `41BA0` `0x41114..0x41118` -> cleanup landing `0x41128`.

## Original-callback exception continuation

Raw ARM64 at `0x410F4` confirms a distinct catch for the indirect original callback:
1. verify expected catch type;
2. begin catch;
3. retain the caught exception;
4. call `41BA0(exception)` at `0x41114`;
5. release the retained exception;
6. end catch;
7. branch to `0x4104C`, immediately after the original callback.

Therefore, when the original callback throws and the reason-probe path completes normally:
- the exception is swallowed;
- the original callback is not retried;
- the existing bounded `41BA0` reason-probe decision applies;
- execution resumes at the normal post-original hosting gate;
- `41CBC` and mutable-settings foreground eligibility may still be evaluated.

This is different from `40F0C`: there is no forced return value because `40FF4` is void and explicitly rejoins its post-original foreground path.

## Route / mutable-settings exceptions

Raw ARM64 shows `0x410D4` immediately joins the common catch body at `0x410D8`.

That catch:
- verifies the expected catch type;
- begins catch;
- ends catch;
- branches directly to cleanup at `0x410B0`.

The protected ranges cover:
- `41CBC` route eligibility; and
- `objc_getClass("UIMutableApplicationSceneSettings")`, kind-of-class checking, `respondsToSelector:setForeground:`, and the private `setForeground:` send.

Therefore a throw from either range is swallowed and the remaining foreground-forcing path is skipped. No reason-probe runs for these catches.

## Nested reason-probe exception

The `41BA0` call itself is protected separately.

Raw ARM64 at `0x41128`:
- preserves the newly thrown exception;
- ends the outer catch;
- resumes unwind through the exception runtime.

Therefore the post-original continuation is conditional on `41BA0` completing normally. A nested probe exception does not rejoin `0x4104C`.

## Promoted runtime contract

Added:
- `DDSceneForegroundExceptionSite`
  - None
  - OriginalCallback
  - RouteEligibility
  - MutableSettingsPath
- `DDSceneForegroundExceptionOutcome`
- `DDResolveSceneForegroundExceptionOutcome(site, currentProbeCount, reasonSelectorSupported)`.

OriginalCallback outcome:
- `shouldSwallowException = YES`;
- `shouldApplyReasonProbeDecision = YES`;
- `reasonProbeDecision = DDResolveExceptionReasonProbeDecision(...)`;
- `probeExceptionWouldResumeUnwind = YES`;
- `shouldContinueForegroundEvaluationAfterCatch = YES`.

RouteEligibility / MutableSettingsPath outcome:
- `shouldSwallowException = YES`;
- `shouldSkipRemainingForegroundForcing = YES`;
- no reason probe.

## Explicit exclusions

R-097 does not:
- synthesize Objective-C exceptions;
- call begin-catch/end-catch;
- invoke the original callback;
- invoke `41CBC`;
- perform runtime class/kind/selector probes;
- send `setForeground:`;
- invoke `41BA0`;
- read exception `reason`;
- mutate `qword_163EA0`;
- mutate foreground state;
- intercept or resume unwind.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final `git diff --check` and verifier rerun are required immediately before commit.

## Scout for next batch — 41138

Direct decompile + raw ARM64 show multiple exception landing pads around `41138`, including:
- a catch near `0x41320` that calls existing `41BA0` and then branches according to the saved pre-original gate state;
- cleanup/unwind paths near `0x41358` and `0x41364`;
- pre-original route/identity extraction, original callback, and post-callback destroy routing all remain candidates for exact LSDA mapping.

## Next

R-098 after compiler green:
- decode `41138` LSDA call-site ranges and map them to pre-original route/identity extraction, original callback, and post-callback destroy routing;
- promote only data-only continuation/probe/outcome metadata;
- keep private identity traversal, `30960`, slot clearing, DDz2 dismiss, exception synthesis, and global mutation excluded.
