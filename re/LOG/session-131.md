# LOG/session-131.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-130 commit `35f2bd9`; decode and promote exact data-only `3A0D0` split-host geometry exception continuation, verify, and commit locally without pushing._

## Start state

- Branch: `chore/reconstruction-build-ci`.
- HEAD: `35f2bd9`.
- Working tree: clean.
- Branch synchronized with origin.
- User confirmed session-130 macOS CI/compiler GREEN.

## Target

Direct Mach-O unwind enumeration shows the immediately preceding LSDA-bearing function below `3AE50`:
- `3A0D0 -> LSDA 0x114404`.

Identity:
- `sub_3A0D0`;
- split-host geometry update using `DDz1 shared`, `splitHostView`, host frame/center mutation, `38E14` gap read, and `39260` final geometry synchronization.

Reviewed:
- `decompile/3A0D0.c`;
- `decompile/38E14.c`;
- `decompile/39260.c`;
- raw ARM64 around `0x3A0D0..0x3A2C0`;
- Mach-O LSDA bytes at `0x114404`.

## Exact LSDA table

LSDA call-site table has exactly three entries:

1. `0x3A0D0..0x3A1F4` -> no landing.
2. `0x3A1F4..0x3A254` -> landing `0x3A2A8`, action 5.
3. `0x3A254..0x3A2C0` -> no landing.

Thus the function has exactly one local typed protected region.

## Protected geometry range

Raw ARM64 `0x3A1F4..0x3A254`:

- `0x3A1F4..0x3A1FC`: host view `setFrame:`.
- `0x3A200..0x3A230`: derive split-center coordinates from orientation/layout globals.
- `0x3A230..0x3A234`: split/host object `setCenter:`.
- `0x3A238`: call `38E14`, which reads/parses `/var/tmp/duodash_ab_keypane_hidegap` and returns a bounded gap value.
- `0x3A23C..0x3A24C`: prepare persisted geometry inputs.
- `0x3A250`: call `39260`, a substantial UI synchronization routine that updates key-pane/split subviews, frames, colors, centers, and related presentation state.

## Catch continuation

Landing `0x3A2A8`:
- compare catch discriminator with expected type;
- expected -> begin catch, end catch, branch to `0x3A254`;
- nonmatching -> resume unwind at `0x3A2BC`.

At `0x3A254`:
- the retained split-host view in `x19` is released;
- normal epilogue follows.

Expected exceptions therefore:
- are swallowed locally;
- skip all geometry work remaining after the throw;
- do not roll back prior setter/helper side effects;
- still execute final retained-view cleanup.

## Site-aware partial-write persistence

The LSDA has one broad protected range, but raw instruction order permits exact site-sensitive metadata.

### Host frame setter

If `setFrame:` throws:
- no later protected geometry call has been reached;
- Objective-C setter side effects may have occurred before the throw;
- host frame is therefore **possibly applied**, not definitely applied;
- split center and final synchronization have not been reached.

### Split center setter

If `setCenter:` throws:
- `setFrame:` returned normally first;
- host frame is therefore **definitely applied**;
- center mutation may have occurred before the throw;
- gap read/final sync have not been reached.

### Gap read `38E14`

If `38E14` throws:
- both `setFrame:` and `setCenter:` returned normally;
- host frame and split center are **definitely applied**;
- final `39260` synchronization has not started.

### Final geometry synchronization `39260`

If `39260` throws:
- frame setter returned;
- center setter returned;
- gap read returned;
- frame and center are therefore **definitely applied**;
- `39260` itself may have already performed some internal UI synchronization before throwing.

The reconstruction records that final synchronization **could have started/partially applied**; it does not invent exact internal rollback semantics.

## Promoted runtime contract

Added:
- `DDSplitHostGeometryExceptionSite`:
  - `HostFrameSetter`;
  - `SplitCenterSetter`;
  - `GapRead`;
  - `FinalGeometrySync`;
  - `UnprotectedRange`.
- `DDSplitHostGeometryExceptionOutcome`.
- `DDResolveSplitHostGeometryExceptionOutcome(site)`.

Typed sites share:
- `shouldSwallowException = YES`;
- `shouldSkipRemainingGeometryWork = YES`;
- `shouldContinueRetainedViewCleanup = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

Site-sensitive persistence:
- frame setter -> `hostFrameCouldHaveAppliedBeforeException`;
- center setter -> `hostFrameDefinitelyAppliedBeforeProtectedCall` + `splitCenterCouldHaveAppliedBeforeException`;
- gap read -> definite frame + definite center;
- final sync -> definite frame + definite center + `finalGeometrySyncCouldHaveStartedBeforeException`.

Unprotected range:
- `exceptionWouldPropagate = YES`.

## Explicit exclusions

R-130 does not:
- invoke `setFrame:` or `setCenter:`;
- read the gap file;
- invoke `38E14` or `39260`;
- mutate live views;
- model hidden rollback not present in control flow;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification

After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final project verifier + `git diff --check` are rerun immediately before commit.

## Scout for next batch — 39D4C

Direct Mach-O `__unwind_info` enumeration shows the next earlier LSDA-bearing function:
- `39D4C -> LSDA 0x1143C8`.
- Identity: `sub_39D4C`, scene-layer-host-container search / geometry predicate feeding rotation/rebuild decisions.

Decoded LSDA call-site entries:

1. `0x39D4C..0x39DA4` -> no landing.
2. `0x39DA4..0x39DD8` -> `0x39FE4`, action 5.
3. `0x39DE0..0x39E30` -> `0x39FE8`, action 5.
4. `0x39E30..0x39E40` -> no landing.
5. `0x39E40..0x39E48` -> `0x39FE8`, action 5.
6. `0x39E48..0x39F7C` -> no landing.
7. `0x39F7C..0x39F90` -> `0x39FE4`, action 5.
8. `0x39F90..0x3A004` -> no landing.

Landing `0x39FE4` branches to common typed catch `0x39FE8`.

Expected catch:
- begin/end catch;
- force local predicate register `w23 = 0`;
- branch to `0x39E70`.

Nonmatching:
- resume unwind at `0x3A000`.

R-131 should map each protected range against:
- layer-host-container traversal;
- bounds/convertRect geometry predicate computation;
- any late file/rotation helper protected work;
- exact cleanup and downstream rebuild gating after predicate is forced false.

Known unresolved remain:
- `73E8` / `80D0` bounds;
- full `7E908` blacklist/numerics;
- jailbroken-device smoke testing.
