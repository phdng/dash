# LOG/session-097.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-096 commit 036e7f2; complete R-096 by promoting only the data-only 40F0C exception outcome and reusing the existing 41BA0 reason-probe decision. Per user workflow, commit locally but do not push._

## R-096 — evidence source

Reviewed:
- `40F0C.c`
- `41BA0.c`
- raw ARM64 for `40F0C`
- Mach-O `__gcc_except_tab` LSDA for `40F0C`

The LSDA call-site table for `40F0C` decodes as:

- `0x40F0C..0x40F3C` -> no landing pad
- `0x40F3C..0x40F50` -> landing `0x40F5C`, action 1
- `0x40F50..0x40F7C` -> no landing pad
- `0x40F7C..0x40F8C` -> landing `0x40FAC`, action 1
- `0x40F8C..0x40FCC` -> no landing pad
- `0x40FCC..0x40FD0` -> landing `0x40FE4`, cleanup/action 0
- `0x40FD0..0x40FF4` -> no landing pad

This maps catches to operations exactly.

## Decision-path exception

The protected range `0x40F3C..0x40F50` contains both:
- `sub_41CBC(scene)`;
- `sub_3FAF8(scene)`.

Therefore a throw from either route eligibility or orientation resolution uses the same landing pad `0x40F5C`.

Raw ARM64 at that landing pad:
- captures the exception;
- verifies the expected catch type;
- begins catch;
- ends catch;
- branches to the normal original-callback path at `0x40F74`.

Promoted outcome:
- swallow exception;
- call original after catch;
- no reason probe;
- no forced result.

## Original-callback exception

The protected range `0x40F7C..0x40F8C` is the indirect original callback call.

Its landing pad `0x40FAC`:
1. begins catch;
2. retains the caught exception object;
3. calls `sub_41BA0(exception)`;
4. releases the retained exception;
5. ends catch;
6. sets the hook result register to 0;
7. returns through normal cleanup.

Therefore, if the original callback throws and the probe path completes normally:
- the exception is swallowed;
- original is not retried;
- the caught exception uses the same 41BA0 bounded reason-probe behavior already modeled in reconstruction;
- final result is forced false.

The new outcome embeds `DDResolveExceptionReasonProbeDecision(currentProbeCount, reasonSelectorSupported)` rather than duplicating 41BA0 logic.

## Nested probe exception

The LSDA also covers the `41BA0` call itself:
- protected range `0x40FCC..0x40FD0`;
- landing `0x40FE4`;
- cleanup action only.

Raw ARM64 at `0x40FE4`:
- preserves the newly thrown exception;
- ends the outer catch;
- resumes unwind.

So forced-false is conditional on the reason-probe path completing normally.

The data-only outcome records:
- `probeExceptionWouldResumeUnwind = YES`;
- `shouldForceFalseResultAfterProbe = YES`.

It does not attempt to synthesize that nested exception.

## Promoted runtime contract

Added:
- `DDSceneOrientationExceptionSite`
  - None
  - DecisionPath
  - OriginalCallback
- `DDSceneOrientationExceptionOutcome`
- `DDResolveSceneOrientationExceptionOutcome(site, currentProbeCount, reasonSelectorSupported)`

DecisionPath:
- `shouldSwallowException = YES`;
- `shouldCallOriginalAfterCatch = YES`.

OriginalCallback:
- `shouldSwallowException = YES`;
- `shouldApplyReasonProbeDecision = YES`;
- `reasonProbeDecision = DDResolveExceptionReasonProbeDecision(...)`;
- `probeExceptionWouldResumeUnwind = YES`;
- `shouldForceFalseResultAfterProbe = YES`.

## Explicit exclusions

R-096 does not:
- synthesize Objective-C exceptions;
- call begin-catch/end-catch;
- invoke `41CBC`;
- invoke `3FAF8`;
- invoke the original callback;
- invoke `41BA0`;
- read exception `reason`;
- mutate `qword_163EA0`;
- intercept/resume unwind.

## Scout for next batch — 40FF4

Reviewed `40FF4.c`, raw ARM64, and LSDA.

The LSDA maps:
- original callback range `0x41038..0x4104C` -> landing `0x410F4`;
- `41CBC` range `0x4105C..0x41064` -> landing `0x410D4`;
- mutable-settings capability/setter range `0x41068..0x410B0` -> landing `0x410D8`;
- nested `41BA0` range `0x41114..0x41118` -> cleanup landing `0x41128`.

Visible behavior:
- original-callback exception is caught, run through 41BA0, then execution resumes after original and can still attempt foreground forcing;
- route/capability/setter exceptions are swallowed and skip the rest of foreground forcing;
- nested 41BA0 exception ends catch and resumes unwind.

## Next

R-097 after compiler green:
- promote only data-only 40FF4 continuation/probe outcomes;
- do not invoke original callback or private selectors;
- do not synthesize exceptions;
- do not mutate foreground state or the 41BA0 probe counter.
