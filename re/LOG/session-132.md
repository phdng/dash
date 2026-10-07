# LOG/session-132.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-131 commit `a951e33`; decode and promote exact data-only `39D4C` scene-layer-host predicate exception behavior, verify, and commit locally without pushing._

## Start state

- Branch: `chore/reconstruction-build-ci`.
- HEAD: `a951e33`.
- Working tree: clean.
- Local tracking ref reported branch ahead 1; assistant did not fetch/push.
- User explicitly confirmed session-131 macOS CI/compiler GREEN.

## Target

Direct unwind enumeration from the previous session identified:
- `39D4C -> LSDA 0x1143C8`.
- Identity: `sub_39D4C`.

Function role from decompile/raw ARM64:
- retain input reason/context argument;
- require host root/view state;
- retain the split/root view at `qword_163C70`;
- find class `_UISceneLayerHostContainerView`;
- breadth-first-ish scan of subviews through a mutable traversal array;
- when a matching layer-host container is found, read its bounds and convert them into the root view coordinate system;
- compute a local geometry predicate in `w23`;
- decrement `dword_162EF8` when signed-positive;
- only if the predicate remains true, proceed into orientation/rebuild gating and rotation-related notice/rebuild work.

Reviewed:
- `decompile/39D4C.c`;
- raw ARM64 `0x39D4C..0x3A004`;
- Mach-O LSDA bytes at `0x1143C8`.

## Exact LSDA call-site table

Decoded 8 entries:

1. `0x39D4C..0x39DA4` -> no landing.
2. `0x39DA4..0x39DD8` -> landing `0x39FE4`, action 5.
3. `0x39DE0..0x39E30` -> landing `0x39FE8`, action 5.
4. `0x39E30..0x39E40` -> no landing.
5. `0x39E40..0x39E48` -> landing `0x39FE8`, action 5.
6. `0x39E48..0x39F7C` -> no landing.
7. `0x39F7C..0x39F90` -> landing `0x39FE4`, action 5.
8. `0x39F90..0x3A004` -> no landing.

Landing `0x39FE4` is only a branch to the common typed catch at `0x39FE8`.

Thus there are exactly four local typed protected ranges.

## Protected range 1 — class/traversal-array setup

`0x39DA4..0x39DD8` covers:

- runtime class lookup for `_UISceneLayerHostContainerView`;
- creation of a mutable traversal array initialized with the retained root view;
- retain-autoreleased array result;
- initial array `count`.

Before this protected range:
- the root view at `qword_163C70` has already been retained into `x20`.

If an expected exception occurs:
- common catch forces predicate false;
- normal root-view release at `0x39E68` is bypassed;
- if the traversal array had already been created/retained before the throw, its normal release at `0x39FC0` is also bypassed.

The resolver records these as possible local release bypasses only; it does not claim a guaranteed process-level leak.

## Protected range 2 — traversal step

`0x39DE0..0x39E30` covers:

- `objectAtIndexedSubscript:` on the traversal array;
- retain-autoreleased current candidate;
- candidate-vs-root comparison;
- kind-of-class check against `_UISceneLayerHostContainerView`;
- for nonmatching candidates, fetch `subviews`;
- retain-autoreleased subviews array;
- append subviews into the traversal array.

Normal candidate/subviews releases begin at `0x39E30`, immediately outside the protected range.

Therefore an expected exception in this range may bypass:
- root-view release;
- traversal-array release;
- current-candidate release;
- retained subviews release.

Catch still forces predicate false and continues to the post-scan path.

## Protected range 3 — traversal count refresh

`0x39E40..0x39E48` covers the traversal array `count` refresh.

At this point:
- the current candidate and any retained subviews from the iteration were already released by `0x39E30..0x39E3C`;
- the root view and traversal array are still retained.

An expected exception therefore:
- can bypass root-view/traversal-array releases;
- does not need current-candidate/subviews release-bypass metadata for this site.

## Protected range 4 — candidate geometry read

When a scanned candidate is of the target private class, control branches to `0x39F7C`.

`0x39F7C..0x39F90` covers:
- candidate `bounds`;
- `convertRect:toView:` using the retained root view.

The candidate is retained in `x23` before entering this range.

Normal path after the protected region:
- uses converted geometry to compute a local predicate;
- releases the candidate at `0x39FB0`;
- later releases the traversal array and root view.

Expected exception may therefore bypass:
- root-view release;
- traversal-array release;
- current-candidate release.

The geometry read itself may already have partly executed before the exception, so the resolver records that timing but no mutation (these are read/conversion operations).

## Common typed catch

Raw tail:

- `0x39FE4`: branch to `0x39FE8`.
- `0x39FE8`: compare discriminator with expected value 1.
- expected:
  - begin catch;
  - end catch;
  - `mov w23,#0`;
  - branch to `0x39E70`.
- nonmatching:
  - resume unwind at `0x3A000`.

No reason probe, retry, traversal restart, or alternate geometry path is invoked.

## Exact continuation after catch

At `0x39E70`:

- load `dword_162EF8`;
- compute current-1;
- store the decremented value only when the result is not negative.

Thus the original still attempts the same signed-positive post-scan counter decrement after an expected catch:
- current >= 1 -> decrement;
- current <= 0 -> no store.

The data-only resolver records only that this decrement evaluation remains pending; it does not mutate the global counter.

Immediately afterward:

- `cbz w23, 0x39EDC`.

Because catch forced `w23=0`, the function skips all downstream predicate-true work.

Skipped after expected catch:

- dispatch-once initialization for `qword_163D10`;
- `byte_163D08 == 1` orientation/rebuild enable check;
- default file manager acquisition;
- `/var/tmp/duodash_ab_nokporient` probe;
- rotation state comparison between `qword_162F00` and `qword_163D18`;
- `37CBC("rebuild — card rotated")`;
- card-length checks;
- `37C48("rebuild failed")`;
- `37C48("card rotated twice")`.

The expected-catch path reaches `0x39EDC`:
- sets return value false;
- releases the retained input argument in `x19`;
- returns.

Therefore the exact continuation is:

expected exception
→ swallow
→ force scan predicate false
→ still evaluate signed-positive counter decrement
→ suppress all rotation/rebuild gating/actions
→ final input cleanup
→ return false.

## Promoted runtime contract

Added:
- `DDSceneLayerHostPredicateExceptionSite`:
  - `ClassAndTraversalArraySetup`;
  - `TraversalStep`;
  - `TraversalCountRefresh`;
  - `CandidateGeometryRead`;
  - `UnprotectedRange`.
- `DDSceneLayerHostPredicateExceptionOutcome`.
- `DDResolveSceneLayerHostPredicateExceptionOutcome(site)`.

All four typed sites record:
- `shouldSwallowException = YES`;
- `shouldForcePredicateFalse = YES`;
- `shouldAttemptPostScanCounterDecrement = YES`;
- `shouldSkipRotationRebuildEvaluation = YES`;
- `shouldContinueInputCleanup = YES`;
- `shouldReturnFalse = YES`;
- root-view release could be bypassed;
- traversal-array release could be bypassed;
- nonmatching discriminator would resume unwind.

Traversal-step additionally:
- current-candidate release could be bypassed;
- retained-subviews release could be bypassed.

Candidate-geometry-read additionally:
- current-candidate release could be bypassed;
- candidate geometry read could already have started before the throw.

Unprotected range:
- propagates.

## Explicit exclusions

R-131 does not:
- call `NSClassFromString`;
- allocate/traverse mutable arrays;
- inspect private scene-layer-host views;
- invoke `bounds` or `convertRect:toView:`;
- mutate `dword_162EF8`;
- run dispatch-once;
- read `duodash_ab_nokporient`;
- invoke rebuild or notice helpers;
- change real object lifetimes;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification

After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final project verification and `git diff --check` are run immediately before commit.

## Scout for next batch — 39B70

Direct unwind enumeration identifies the next earlier LSDA-bearing function:
- `39B70 -> LSDA 0x11439C`.
- Identity: `sub_39B70`, slide animation setup.

Decompile/raw flow:
- retain input;
- require host objects and slide flag clear;
- call `39D4C("before the slide")`;
- when predicate says slide may proceed:
  - set `byte_163C98 = 1`;
  - capture `qword_163CE8`;
  - schedule a 1-second dispatch-after block `3A004`;
  - retain the split object at `qword_163C68`;
  - read host bounds and compute target center `d8/d9`;
  - construct animation block `3A034`;
  - invoke `+[UIView animateWithDuration:delay:options:animations:completion:]`.

LSDA `0x11439C` decodes to five entries:

1. `0x39B70..0x39CA4` -> no landing.
2. `0x39CA4..0x39CC8` -> landing `0x39CFC`, action 5.
3. `0x39CC8..0x39D1C` -> no landing.
4. `0x39D1C..0x39D2C` -> landing `0x39D3C`, action 0.
5. `0x39D2C..0x39D4C` -> no landing.

The single action-5 range is exactly the UIView animation call.

Expected catch at `0x39CFC`:
- begin catch;
- retain caught object;
- directly invoke `setCenter:` on the retained split object using already-computed `d8/d9`;
- release caught exception;
- end catch;
- rejoin normal object cleanup at `0x39CD0`.

Thus an animation exception falls back to direct center mutation instead of abandoning the slide.

The catch-internal fallback `setCenter:` call at `0x39D1C..0x39D2C` is action 0:
- if it throws, landing `0x39D3C` ends the active catch;
- resume unwind at `0x39D44`.

R-132 should additionally map:
- the pre-animation persisted state `byte_163C98 = 1`;
- the already-scheduled 1-second `3A004` timeout/reset block;
- whether bounds/target-center computation is complete before the protected animation call (raw ARM64 says yes);
- direct fallback setter partial-write semantics if it itself throws.

Known unresolved remain:
- `73E8` / `80D0` bounds;
- full `7E908` blacklist/numerics;
- jailbroken-device smoke testing.
