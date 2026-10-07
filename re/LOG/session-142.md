# LOG/session-142.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-141 commit `b45bfb2`; decode and promote exact data-only `37A7C` keyboard-lost recovery summary exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `b45bfb2`.
- Working tree clean.
- User confirmed session-141 macOS CI/compiler GREEN.
- Local tracking ref still reported ahead 1; assistant did not fetch/push.

## Target
- Function: `sub_37A7C`.
- LSDA: `0x11418C`.
- Role: keyboard-lost recovery / marker and rebuild coordination.

## Exact LSDA table
1. `0x37A7C..0x37AD0` -> no landing.
2. `0x37AD0..0x37AEC` -> landing `0x37C20`, action 5.
3. `0x37AEC..0x37C40` -> no landing.

The one protected range covers:
- `+[DDz2 shared]`;
- retain-autoreleased DDz2;
- `keyPaneSceneSummary`;
- retain-autoreleased summary.

## Expected catch continuation
At `0x37C20`:
- compare discriminator with expected type;
- expected:
  - begin catch;
  - end catch;
  - load static fallback summary `&stru_146AD8` into x20;
  - branch to `0x37B18`;
- nonmatching:
  - resume unwind at `0x37C3C`.

This catch does **not** return from the function.

`0x37B18` is the normal recovery continuation:
- obtain `NSFileManager defaultManager`;
- test `/var/tmp/duodash_ab_nokprecover`;
- if recovery is allowed, compare keyboard-loss generations;
- either log the repeated loss or copy the current keypane state and attempt rebuild;
- later release x20 and input x19.

Therefore expected summary-acquisition exceptions are converted into a fallback scene-summary value and the existing recovery path continues.

## Semantic site 1 — DDz2 shared acquisition
Relevant raw order:
- `0x37AD0`: call `+[DDz2 shared]`;
- `0x37AD8`: retain-autoreleased return;
- `0x37ADC`: `mov x21,x0`.

The commit to x21 occurs only after the shared/retain calls.

If the expected exception occurs before x21 commit:
- catch selects fallback scene summary;
- marker/rebuild flow continues;
- no committed retained controller x21 is asserted;
- DDz2 acquisition/retain may already have started;
- any temporary DDz2 local cleanup can be bypassed because catch jumps directly to `0x37B18`.

R-141 records only temporary acquisition/release-bypass timing here.

## Semantic site 2 — keyPaneSceneSummary acquisition
Relevant raw order:
- x21 already contains retained DDz2;
- `0x37AE0`: `keyPaneSceneSummary`;
- `0x37AE8`: retain-autoreleased summary;
- `0x37AEC`: `mov x22,x0`, immediately outside protected range.

At this site:
- retained DDz2 x21 is definitely committed before the protected call;
- expected catch jumps over the normal DDz2 release at `0x37B10..0x37B14`;
- the later marker-flow setup overwrites x21 with retained NSFileManager, so the DDz2 local release is bypassed;
- summary acquisition/retain may already have started before the exception;
- x22 is not guaranteed committed because its assignment is outside the protected range;
- a temporary retained summary can therefore exist without reaching the normal x22 release at `0x37B08`.

R-141 records:
- retained controller definitely committed;
- controller release can be bypassed;
- temporary summary acquisition may have started;
- temporary summary cleanup can be bypassed.

## Unprotected paths
Outside `0x37AD0..0x37AEC` there is no local LSDA landing.

This includes:
- main-thread predicate and global/keypane gates;
- non-main-thread dispatch_async path;
- NSFileManager marker test;
- generation comparison;
- logging;
- current keypane copy;
- rebuild attempt;
- later releases.

Exceptions from those paths propagate normally.

## Promoted runtime contract
Added:
- `DDKeyboardLostRecoveryExceptionSite`:
  - `SharedControllerAcquisition`;
  - `SceneSummaryAcquisition`;
  - `UnprotectedRange`.
- `DDKeyboardLostRecoveryExceptionOutcome`.
- `DDResolveKeyboardLostRecoveryExceptionOutcome(site)`.

Both typed semantic sites:
- `shouldSwallowException = YES`;
- `shouldUseFallbackSceneSummary = YES`;
- `shouldContinueMarkerAndRebuildFlow = YES`;
- nonmatching type resumes unwind.

Shared-controller site:
- temporary controller acquisition may have started;
- temporary controller cleanup can be bypassed.

Scene-summary site:
- retained controller definitely committed;
- controller release can be bypassed;
- temporary scene-summary acquisition may have started;
- temporary scene-summary cleanup can be bypassed.

Unprotected:
- propagates.

## Explicit exclusions
R-141 does not:
- call DDz2;
- obtain a live scene summary;
- test NSFileManager markers;
- execute logging or rebuild helpers;
- mutate recovery generations;
- mutate real ownership;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` are run immediately before commit.

## Scout for next batch — 37924
Next earlier LSDA-bearing function:
- `37924 -> LSDA 0x114178`.
- Role: forward CarPlay UI status to DDz1.

Exact table:
1. `0x3793C..0x37958` -> `0x37968`, action 1.
2. `0x37958..0x37978` -> no landing.

Raw protected flow:
- `+[DDz1 shared]`;
- retain-autoreleased DDz1;
- commit retained DDz1 to x19 at `0x37948`;
- load block/context fields `gen` and `ok`;
- send `noteCarPlayUIStatus:gen:ok:`.

Landing `0x37968`:
- `objc_begin_catch`;
- restore frame;
- tail `objc_end_catch`.

There is no discriminator test: action 1 is catch-all.

R-142 should split:
- DDz1 shared acquisition: exception may happen before x19 commit; no committed DDz1 release-bypass claim.
- status callback send: x19 retained DDz1 definitely committed; catch returns immediately and skips normal tail release at `0x37958..0x37964`; callback side effects may already have occurred before throw.

Unprotected tail propagates.

## Scout after R-142 — 375B8
The next earlier LSDA-bearing function is:
- `375B8 -> LSDA 0x11415C`.

Exact table:
1. `0x375B8..0x375EC` -> no landing.
2. `0x375EC..0x37610` -> `0x37628`, action 5.
3. `0x37610..0x37640` -> no landing.

Protected range covers:
- helper `37640`;
- helper `376DC`;
- `CGRectIsNull`;
- optional `center` getter;
- optional `setCenter:`.

Expected typed catch:
- begin/end-catch;
- jump directly to `0x37618`;
- perform remaining retained-input cleanup;
- no geometry rollback.

Thus a setter exception may occur after center was already changed; earlier geometry helper exceptions skip center mutation entirely.
Nonmatching type resumes unwind at `0x3763C`.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
