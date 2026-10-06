# LOG/session-099.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-098 commit 35823bf; complete R-098 by decoding `41138` LSDA/raw-ARM64 exception behavior and promoting only data-only continuation/probe/unwind outcomes. Per user workflow, commit locally but do not push._

## R-098 — evidence source

Reviewed:
- `41138.c`;
- raw ARM64 for `41138` from the first arm64 FAT slice;
- Mach-O `__unwind_info` / `__gcc_except_tab` mapping;
- existing R-084 destroy-routing contract and existing `41BA0` reason-probe contract.

The first arm64 FAT slice begins at file offset `0x4000`.

`__unwind_info` maps:
- `41138` -> LSDA `0x114CF8`.

The LSDA call-site table decodes to:
- `0x41138..0x4118C` -> no landing pad;
- `0x4118C..0x411F0` -> landing `0x41364`, action 5;
- `0x411F0..0x41214` -> no landing pad;
- `0x41214..0x41228` -> landing `0x41320`, action 5;
- `0x41228..0x41340` -> no landing pad;
- `0x41340..0x41344` -> landing `0x41358`, cleanup/action 0;
- `0x41344..0x4138C` -> no landing pad.

This maps the exception regions to pre-original routing, the original callback, post-callback destroy routing, and nested `41BA0` cleanup exactly.

## Pre-original route / identity exception

The protected range `0x4118C..0x411F0` contains the active-host route and private identity preparation work:
- primary `41CBC` route check;
- secondary `41CBC` fallback route check;
- primary `3FBC8` identity extraction and length test;
- secondary `3FBC8` fallback identity extraction when the primary identity is empty.

Raw ARM64 at landing `0x41364`:
1. verifies the expected catch type;
2. begins catch;
3. ends catch;
4. restores the selected identity register with the saved fallback register (`mov x22, x26`);
5. branches to `0x4120C`, the normal original-callback setup.

The destroy-routing prepared flag (`w25`) is not cleared by this catch. Therefore the catch preserves whatever gate state had already been established at the throw site.

Promoted semantics:
- swallow the exception;
- restore the saved identity state;
- preserve caller-supplied `destroyRoutingPrepared` state;
- still call the original callback;
- if the original later returns normally, prepared destroy routing remains eligible.

No private identity object is reconstructed by the data-only helper.

## Original-callback exception

The protected range `0x41214..0x41228` is the indirect original callback call.

Landing `0x41320`:
1. verifies the expected catch type;
2. begins catch;
3. retains the caught exception;
4. calls existing `41BA0(exception)` at `0x41340`;
5. releases the retained exception;
6. ends catch;
7. tests the saved destroy-routing prepared flag (`w25`);
8. if prepared, branches to `0x4122C` and executes post-callback destroy routing;
9. otherwise branches to normal cleanup at `0x412EC`.

Therefore an original-callback throw:
- is swallowed;
- does not retry the original callback;
- reuses the exact existing `DDResolveExceptionReasonProbeDecision` contract;
- continues destroy routing only when the saved pre-original gate was prepared.

## Nested reason-probe exception

The `41BA0` call itself is protected separately:
- `0x41340..0x41344` -> cleanup landing `0x41358`.

Raw ARM64 at `0x41358`:
- preserves the newly thrown exception;
- ends the outer catch;
- resumes unwind.

So post-callback continuation is conditional on `41BA0` completing normally.

## Post-callback destroy-routing exception

The entire `0x41228..0x41340` range has no landing pad in `41138`.

That range includes the existing post-callback destroy behavior:
- selected-identity length and aux matching;
- `30960` aux-destroyed notice path;
- split-host slot equality/count logic and slot clear;
- DDz2 `shared` / `dismiss` path.

An exception from that range is therefore not swallowed by a `41138` catch and propagates/resumes unwind out of this function.

The reconstruction records only this unwind outcome. It does not execute any of those side effects.

## Promoted runtime contract

Added:
- `DDSceneDestroyExceptionSite`
  - None
  - PreOriginalRouting
  - OriginalCallback
  - PostCallbackDestroyRouting
- `DDSceneDestroyExceptionOutcome`
- `DDResolveSceneDestroyExceptionOutcome(site, destroyRoutingPrepared, currentProbeCount, reasonSelectorSupported)`.

PreOriginalRouting outcome:
- `shouldSwallowException = YES`;
- `shouldCallOriginalAfterCatch = YES`;
- `shouldRestoreSavedIdentityAfterCatch = YES`;
- `preservesPreparedDestroyRoutingState = YES`;
- `shouldContinuePreparedDestroyRoutingAfterOriginal = destroyRoutingPrepared`.

OriginalCallback outcome:
- `shouldSwallowException = YES`;
- `shouldApplyReasonProbeDecision = YES`;
- `reasonProbeDecision = DDResolveExceptionReasonProbeDecision(...)`;
- `probeExceptionWouldResumeUnwind = YES`;
- `preservesPreparedDestroyRoutingState = YES`;
- `shouldContinuePreparedDestroyRoutingAfterOriginal = destroyRoutingPrepared`.

PostCallbackDestroyRouting outcome:
- `exceptionWouldResumeUnwind = YES`;
- no swallow and no reason probe.

## Explicit exclusions

R-098 does not:
- synthesize Objective-C exceptions;
- call begin-catch/end-catch;
- invoke the original callback;
- invoke `41CBC` or `3FBC8`;
- recover private identity objects;
- invoke `41BA0` or read exception `reason`;
- mutate `qword_163EA0`;
- call `30960`;
- clear host slots;
- call DDz2 `shared` / `dismiss`;
- intercept or resume unwind.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — 4138C

`4138C` already has data-only host/aux update-routing and foreground-based original-callback suppression contracts from R-092, but its exception regions have not yet been mapped into runtime outcomes.

Its unwind index maps `4138C` to LSDA `0x114D2C`.

## Next

R-099 after compiler green:
- decode `4138C` LSDA/raw-ARM64 call-site ranges around scene/settings/identity update routing, private `3F5C0`/`3E670` boundaries, foreground suppression decisions, and the original callback;
- promote only data-only continuation/counter/probe/unwind metadata;
- do not invoke private selectors/executors, the original callback, synthesize exceptions, or mutate counters.
