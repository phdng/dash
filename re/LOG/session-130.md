# LOG/session-130.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-129 commit `877e143`; decode and promote exact data-only `3AE50` evictFromPhoneThen exception behavior from Mach-O LSDA/raw ARM64 plus callback helpers, verify, and commit locally without pushing._

## Start state

- Branch: `chore/reconstruction-build-ci`.
- HEAD at session start: `877e143`.
- Working tree: clean.
- Local tracking ref still reported branch ahead 1; no push performed by assistant.
- User explicitly confirmed the session-129 compiler/CI build was green.

## Target

Next earlier LSDA-bearing function from the previous handoff:
- `3AE50 -> LSDA 0x114424`.
- Identity: `-[DDz2 evictFromPhoneThen:]`.

Reviewed:
- `decompile/3AE50.c`;
- callback helpers `3F088.c`, `3F164.c`, `3F170.c`;
- raw ARM64 `0x3AE50..0x3B2D8`;
- Mach-O LSDA bytes at `0x114424`.

The first arm64 FAT slice begins at file offset `0x4000`.

## Callback wrapper semantics

The retained fallback wrapper is built around `sub_3F088`.

`3F088`:
- reads a shared byref delivered flag;
- if the flag is already set, returns without invoking the user callback;
- otherwise sets the flag first;
- if a user callback exists:
  - invokes it immediately when already on the main thread;
  - otherwise dispatches that callback to the main queue.

Therefore the wrapper is a one-shot delivery gate shared by:
- direct fallback calls in `evictFromPhoneThen:`;
- request completion callback helper `3F164`;
- 2-second timeout helper `3F170`;
- the common exception catch fallback.

Importantly, the delivered flag is set before the first callback-related Objective-C call (`+[NSThread isMainThread]`) and before direct callback or dispatch.

## Exact LSDA call-site table

Decoded 25 entries:

1. `0x3AE50..0x3AEE4` -> no landing.
2. `0x3AEE4..0x3AF00` -> landing `0x3B2C0`, action 0.
3. `0x3AF00..0x3AF14` -> no landing.
4. `0x3AF14..0x3AF50` -> landing `0x3B2C0`, action 0.
5. `0x3AF50..0x3AF6C` -> no landing.
6. `0x3AF6C..0x3AF78` -> landing `0x3B270`, action 5.
7. `0x3AF78..0x3AF88` -> landing `0x3B278`, action 5.
8. `0x3AF9C..0x3AFE0` -> landing `0x3B274`, action 5.
9. `0x3AFE4..0x3AFFC` -> landing `0x3B268`, action 5.
10. `0x3B00C..0x3B04C` -> landing `0x3B264`, action 5.
11. `0x3B04C..0x3B07C` -> no landing.
12. `0x3B07C..0x3B08C` -> landing `0x3B264`, action 5.
13. `0x3B08C..0x3B09C` -> no landing.
14. `0x3B09C..0x3B0A4` -> landing `0x3B278`, action 5.
15. `0x3B0AC..0x3B0B4` -> landing `0x3B274`, action 5.
16. `0x3B0B4..0x3B108` -> no landing.
17. `0x3B108..0x3B110` -> landing `0x3B268`, action 5.
18. `0x3B158..0x3B164` -> landing `0x3B26C`, action 5.
19. `0x3B164..0x3B1B0` -> no landing.
20. `0x3B1B0..0x3B1C0` -> landing `0x3B25C`, action 5.
21. `0x3B1C0..0x3B228` -> no landing.
22. `0x3B228..0x3B248` -> landing `0x3B260`, action 5.
23. `0x3B248..0x3B29C` -> no landing.
24. `0x3B29C..0x3B2A4` -> landing `0x3B2B4`, action 0.
25. `0x3B2A4..0x3B2D8` -> no landing.

Summary:
- 12 action-5 typed ranges;
- 3 action-0 cleanup ranges;
- 10 no-landing ranges.

## Early action-0 behavior

### 0x3AEE4..0x3AF00

Covers:
- default file manager acquisition;
- `fileExistsAtPath:/var/tmp/duodash_ab_noevict`.

Landing `0x3B2C0` performs byref block-object disposal then resumes unwind.

No typed swallow is attempted.

### 0x3AF14..0x3AF50

Depending on branch, covers:
- the direct one-shot fallback invocation for the no-evict path;
- second default-file-manager acquisition;
- `duodash_ab_evict_skipfrontmost` file probe;
- frontmost-phone identity check through `3EDFC`.

This range is also action 0.

Consequences:
- file/probe/frontmost exceptions propagate;
- if the early direct fallback wrapper itself throws, there is no local typed retry;
- byref state is disposed before unwind.

Because the fallback wrapper sets its delivered gate before callback-related throwing work, a callback exception here can propagate with the delivered gate already set.

## Action-5 per-site mapping

### Workspace class lookup

`0x3AF6C..0x3AF78`
- `objc_getClass("SBMainWorkspace")`.

`0x3AF78..0x3AF88`
- `objc_getClass("SBHomeScreenEntity")`.

Expected exception:
- common typed catch;
- invoke one-shot fallback wrapper;
- skip remaining eviction work;
- final cleanup.

### Workspace preparation

`0x3AF9C..0x3AFE0`
- `SBMainWorkspace sharedInstance` + retain-autoreleased;
- capability checks for `createRequestWithOptions:`;
- capability checks for `executeTransitionRequest:`.

If a retained workspace object already exists before the throw, common catch bypasses its normal local release path.

### Transition request creation

`0x3AFE4..0x3AFFC`
- `createRequestWithOptions:0`;
- retain-autoreleased request.

Expected catch invokes fallback and exits through final cleanup without continuing request setup/execution.

Retained transition intermediates may have their normal local releases bypassed.

### Application-context preparation

`0x3B00C..0x3B04C`
- `SBHomeScreenEntity respondsToSelector:entity`;
- optional `entity` getter + retain;
- request capability check for `modifyApplicationContext:`.

Expected catch invokes fallback then final cleanup.

### Application-context mutation

`0x3B07C..0x3B08C`
- `modifyApplicationContext:` send with the `3F100` activating-entity block.

The normal captured-entity release begins at `0x3B08C`, immediately after the protected range.

Expected catch skips all remaining request work and may bypass normal releases of retained transition intermediates.

### Protected direct fallback invocations

Three normal failure paths directly invoke the one-shot wrapper:

- `0x3B09C..0x3B0A4`: required private classes missing;
- `0x3B0AC..0x3B0B4`: workspace missing or required selectors unsupported;
- `0x3B108..0x3B110`: transition request creation returned nil.

All three direct calls are action 5.

For an expected Objective-C exception emitted from inside `3F088`:
- the wrapper's delivered gate has already been set;
- common catch invokes the same wrapper again;
- the second wrapper invocation sees the gate and returns without invoking the user callback again.

Thus the catch retries the wrapper call structurally, but does not duplicate the underlying user completion.

### Completion-selector probe

`0x3B158..0x3B164`
- probes the selected completion API:
  - older CoreFoundation: `setCompletionBlock:` first;
  - newer CoreFoundation: `addCompletionHandler:` first;
  - then alternate selector if needed.

At this point:
- no completion block has yet been installed;
- no 2-second timeout has yet been scheduled;
- transition execution has not started.

Expected catch invokes fallback immediately and exits.

### Completion-handler installation

`0x3B1B0..0x3B1C0`
- sends the selected completion setter/adder with a block using helper `3F164`.

The 2-second timeout is scheduled only after this range.

Because an Objective-C setter/add-completion send may perform side effects before throwing, the resolver records:
- completion handler may already have been installed.

Expected catch invokes fallback and exits; if an installed completion fires later, it shares the same one-shot wrapper gate.

### Execute transition or immediate fallback

`0x3B228..0x3B248` covers:
- `executeTransitionRequest:`;
- branch on whether completion-handler setup succeeded;
- when no completion handler is armed, immediate direct fallback wrapper invocation.

If a completion API was successfully installed:
- helper `3F164` already wraps the same one-shot fallback;
- a 2-second timeout using helper `3F170` has already been scheduled before `0x3B228`;
- catch fallback can set the shared delivered gate;
- later completion/timeout wrapper invocations then no-op.

If no completion API was available:
- no timeout is scheduled;
- after transition execution returns, the code directly invokes fallback;
- if that direct fallback throws after setting the gate, the catch's fallback invocation is gate-suppressed.

The protected range can therefore fail:
- during transition execution, before callback delivery;
- after transition execution, during immediate fallback delivery.

The resolver conservatively records:
- completion handler may already be installed;
- timeout fallback may already be scheduled;
- transition execution may have started;
- catch fallback may already be gate-suppressed, depending on where the exception arose.

## Common typed catch 0x3B278

Landing stubs:
- `0x3B25C`;
- `0x3B260`;
- `0x3B264`;
- `0x3B268`;
- `0x3B26C`;
- `0x3B270`;
- `0x3B274`;

all converge at `0x3B278`.

Expected discriminator:
- save exception;
- begin catch;
- retain caught object;
- load the one-shot fallback wrapper invoke pointer;
- call wrapper at `0x3B29C..0x3B2A4`;
- release caught object;
- end catch;
- branch to `0x3B0BC`.

At `0x3B0BC`, final outer cleanup:
- releases the retained fallback block;
- releases retained callback capture;
- disposes byref delivered state;
- releases the extra retained callback;
- returns.

All remaining eviction/request/transition logic is skipped.

Nonmatching discriminator:
- skips begin-catch;
- reaches byref cleanup at `0x3B2C4`;
- resumes unwind at `0x3B2D0`.

## Catch-internal fallback throw

Catch fallback call:
- `0x3B29C..0x3B2A4` -> landing `0x3B2B4`, action 0.

If this fallback wrapper throws:
- landing preserves nested exception;
- calls `objc_end_catch`;
- continues through byref cleanup;
- resumes unwind.

There is no second typed catch/retry.

## Possible retained-intermediate release bypass

Common typed catch jumps directly to final outer cleanup `0x3B0BC`, bypassing the normal late cleanup sequence for transition intermediates around `0x3B248..0x3B258`.

Depending on site/throw timing, already-retained workspace/request/entity or related transition intermediates may therefore bypass their normal local release instructions.

The resolver records only:
- `retainedTransitionIntermediatesReleaseCouldBeBypassed`.

It does not claim a guaranteed leak or emulate ARC/unwind ownership.

## Promoted runtime contract

Added:
- `DDEvictFromPhoneExceptionSite`:
  - `WorkspaceClassLookup`;
  - `WorkspacePreparation`;
  - `TransitionRequestCreation`;
  - `ApplicationContextPreparation`;
  - `ApplicationContextMutation`;
  - `ProtectedFallbackInvocation`;
  - `CompletionSelectorProbe`;
  - `CompletionHandlerInstall`;
  - `ExecuteTransitionOrFallback`;
  - `EarlyProbeOrBypassCleanup`;
  - `CatchFallback`;
  - `UnprotectedRange`.
- `DDEvictFromPhoneExceptionOutcome`.
- `DDResolveEvictFromPhoneExceptionOutcome(site)`.

All typed sites:
- swallow expected exception;
- invoke fallback wrapper from catch;
- skip remaining eviction work;
- continue final cleanup;
- nonmatching type resumes unwind.

Protected fallback invocation additionally:
- records that throwing callback work occurs after one-shot gate set;
- records catch fallback can be suppressed by that gate.

Completion-handler install / final execute sites:
- record possible already-installed handler.

Final execute site:
- records possible already-scheduled 2-second timeout;
- records possible transition execution start;
- records possible gate-suppressed catch fallback.

Early action-0:
- propagate after byref cleanup.

Catch fallback action-0:
- end active catch;
- byref cleanup;
- propagate.

Unprotected:
- propagate.

## Explicit exclusions

R-129 does not:
- read no-evict/skip-frontmost files;
- query SpringBoard workspace/entity classes;
- construct or mutate transition requests;
- execute transition requests;
- install real completion handlers;
- schedule dispatch timers;
- invoke the real fallback/user callback;
- mutate the byref delivered gate in live code;
- retain/release live private transition objects through the resolver;
- synthesize/catch exceptions;
- execute catch/unwind runtime machinery.

## Verification

After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final project verifier, CatDesk verification status, and `git diff --check` are run immediately before commit.

## Scout for next batch — 3A0D0

Direct parsing of Mach-O `__unwind_info` LSDA index entries shows the immediately preceding LSDA-bearing function below `3AE50`:
- `3A0D0 -> LSDA 0x114404`.

No LSDA-bearing function exists between `3A0D0` and `3AE50`.

Identity:
- `sub_3A0D0`;
- split-host geometry update using `DDz1 shared`, `splitHostView`, frame/center changes, and geometry synchronization helpers.

LSDA `0x114404` has exactly three call-site entries:

1. `0x3A0D0..0x3A1F4` -> no landing.
2. `0x3A1F4..0x3A254` -> landing `0x3A2A8`, action 5.
3. `0x3A254..0x3A2C0` -> no landing.

Protected range `0x3A1F4..0x3A254` includes:
- host view `setFrame:`;
- split/center computation;
- hosted split object `setCenter:`;
- `38E14` query;
- `39260` geometry synchronization.

Expected catch `0x3A2A8`:
- checks expected discriminator;
- begin/end-catches;
- jumps directly to `0x3A254` final retained-view cleanup.

Thus a protected geometry exception:
- is swallowed;
- skips all remaining geometry work after the throw;
- preserves writes already completed before the throw;
- still releases the retained split host view on the normal cleanup path.

Nonmatching type:
- resumes unwind at `0x3A2BC`.

R-130 should map exact partial-write persistence within the protected range, especially:
- whether host view frame was already applied;
- whether split-view center was already applied;
- whether final geometry synchronization had already started/completed.

## Next

After the user confirms compiler green for session-130:
- R-130: decode/promote exact `3A0D0 -> LSDA 0x114404` partial geometry-write exception continuation;
- preserve already-applied frame/center writes by site/timing;
- keep real UI mutation and geometry helper execution excluded.

Known unresolved:
- `73E8` / `80D0` bounds;
- full `7E908` blacklist/numerics;
- jailbroken-device runtime smoke testing.
