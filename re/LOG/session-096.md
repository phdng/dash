# LOG/session-096.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-095 commit 8db179c; complete R-095 by mapping 40C5C/40DA8 Mach-O exception call-site tables to their exact operations and promoting only data-only exception outcomes. Per user workflow, commit locally but do not push._

## R-095 — evidence source

Reviewed:
- `40C5C.c`
- `40DA8.c`
- raw ARM64 for both functions
- Mach-O `__unwind_info`
- Mach-O `__gcc_except_tab` LSDA entries

The first FAT slice is arm64 and begins at file offset `0x4000`.

`__unwind_info` maps:
- `40C5C` -> LSDA `0x114C40`
- `40DA8` -> LSDA `0x114C6C`

The call-site tables decode to:

### 40C5C

- `0x40C98..0x40CA0` -> landing `0x40D64`, action 7
  - this range contains the `41CBC` route-eligibility call.
- `0x40CC8..0x40CD0` -> landing `0x40D60`, action 5
  - this range contains the `41D80` native-size-resolution call.
- `0x40D30..0x40D48` -> landing `0x40D78`, action 7
  - this range contains the original callback indirect call.
- all other listed ranges have no landing pad.

### 40DA8

- `0x40DE8..0x40DF0` -> landing `0x40EC8`, action 7
  - `41CBC` route-eligibility call.
- `0x40E18..0x40E20` -> landing `0x40EC4`, action 5
  - `41D80` native-size-resolution call.
- `0x40E90..0x40EAC` -> landing `0x40EDC`, action 7
  - original callback indirect call.
- all other listed ranges have no landing pad.

This removes ambiguity about which operation each catch belongs to.

## Route/native-size exception behavior

For both callbacks, the route and native-size landing pads converge on the same catch body.

Raw ARM64:
- validates catch selector/type with `cmp w1,#1`;
- calls Objective-C begin-catch;
- calls end-catch;
- resumes at the normal original-callback path.

Therefore an exception from either:
- `41CBC`, or
- `41D80`

is:
- caught;
- swallowed;
- not diagnosed through EA8/EB0;
- followed by a call to the original callback.

The reconstruction expresses this as:
- `shouldSwallowException = YES`;
- `shouldCallOriginalAfterCatch = YES`;
- no diagnostic increment.

## Original-callback exception behavior

The original callback call-site has a distinct landing pad.

For `40C5C`:
- diagnostic counter is `qword_163EA8`.

For `40DA8`:
- diagnostic counter is `qword_163EB0`.

Both landing pads:
- begin catch;
- load the unsigned 64-bit diagnostic count;
- compare it to 9;
- increment only when current count <=9;
- end catch;
- continue after the original callback call, so the original is not retried.

Exact bounded behavior:
- count 0..9 -> next count = current + 1;
- count >=10 -> unchanged;
- maximum value reached by this increment path is 10.

The thrown exception is swallowed.

## Promoted runtime contract

Added:
- `DDSceneCallbackExceptionSite`
  - None
  - RouteEligibility
  - NativeSizeResolution
  - OriginalCallback
- `DDSceneCallbackExceptionOutcome`
- `DDResolveSceneCallbackExceptionOutcome(site, diagnosticCount)`

For RouteEligibility / NativeSizeResolution:
- swallow = YES;
- call original after catch = YES;
- diagnostic unchanged.

For OriginalCallback:
- swallow = YES;
- do not call/retry original;
- increment diagnostic only when unsigned count <=9.

The helper is intentionally counter-identity-neutral:
- caller supplies `qword_163EA8` state for 40C5C;
- caller supplies `qword_163EB0` state for 40DA8.

## Explicit exclusions

R-095 does not:
- synthesize Objective-C exceptions;
- perform begin-catch/end-catch;
- invoke `41CBC`;
- invoke `41D80`;
- invoke the original callback;
- increment EA8/EB0 globals;
- reproduce exception runtime personality/type matching.

## Scout for next batch — 40F0C

Reviewed `40F0C.c`, raw ARM64, and LSDA.

Observed:
- LSDA range covering route/orientation work lands in a catch that swallows then falls back to the original callback.
- LSDA range covering the original callback lands in a separate catch.
- that original-callback catch retains the caught exception, calls existing `41BA0`, releases it, ends catch, and forces result to 0/false.
- `41BA0` itself already has a data-only probe-budget decision in the reconstruction.

## Next

R-096 after compiler green:
- promote only the data-only 40F0C exception outcome;
- route/orientation exception => fallback to original;
- original-callback exception => pending existing 41BA0 reason-probe + forced false result;
- do not synthesize exceptions, invoke original/private helpers, or read exception reason directly.
