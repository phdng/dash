# LOG/session-124.md
_Date: 2026-10-06. Objective: continue on explicit user instruction from clean HEAD `9f5e535` and complete R-123 by promoting the already-scouted exact data-only `3CC44` spikeHostSlots landscape-coordination exception behavior. Per established workflow, commit locally but do not push._

## Start state

- Branch: `chore/reconstruction-build-ci`.
- HEAD at session start: `9f5e535`.
- Working tree: clean.
- Branch was `ahead 1` of origin at session start; the assistant did not push.
- Session-123 had already decoded `3CC44 -> LSDA 0x11468C` and raw ARM64 continuation behavior in `LOG/session-123.md`; R-123 uses that persisted evidence rather than inventing a new private contract.

## R-123 — exact landscape exception continuation

The LSDA action-5 landing stubs:
- `0x3D4BC`
- `0x3D4C0`
- `0x3D4C4`
- `0x3D4C8`
- `0x3D4CC`
- `0x3D4D0`
- `0x3D4D4`
- `0x3D4D8`
- `0x3D4DC`

all converge on common typed catch `0x3D4E0`.

For the expected catch discriminator:
- begin catch;
- clear only parsed landscape orientation `qword_163D58` at `0x3D4EC`;
- end catch;
- branch to `0x3D21C`.

At `0x3D21C`, the zero parsed orientation enters the original normal fallback-orientation path, which resolves orientation with `3DFC8(0)`, stores the result into the active orientation state, then continues normal slot creation/hosting.

The reconstruction does **not** call `3DFC8`; it reports this as data-only continuation metadata.

## Late state-persistence distinction

Accepted landscape state is written before some later protected operations:
- `0x3D16C`: parsed orientation;
- `0x3D174..0x3D17C`: swap;
- `0x3D180..0x3D18C`: cswap;
- `0x3D190..0x3D194`: rotation.

When a later action-5 protected operation throws the expected type, common catch `0x3D4E0` clears only parsed orientation. It does not roll back the already-written swap/cswap/rotation values.

R-123 therefore distinguishes:
- typed catch before auxiliary state commit;
- typed catch after auxiliary state commit;
- action-0 cleanup/unwind.

For a late typed catch, the resolver explicitly reports that swap, cswap, and rotation remain committed.

## Action-0 and nonmatching behavior

Action-0 cleanup ranges do not use the local typed fallback continuation; they resume unwind/propagate.

For every typed action-5 site, a nonmatching catch discriminator branches to `0x3D4F8` and resumes unwind.

The resolver therefore reports:
- expected typed catch -> swallow + clear parsed orientation + normal fallback-orientation continuation + continue hosting;
- nonmatching typed catch -> resume unwind;
- action-0 cleanup -> propagate/unwind.

## Promoted runtime contract

Added:
- `DDSpikeHostSlotsLandscapeExceptionSite`:
  - `TypedBeforeAuxStateCommit`;
  - `TypedAfterAuxStateCommit`;
  - `ActionZeroCleanup`;
- `DDSpikeHostSlotsLandscapeExceptionOutcome`;
- `DDResolveSpikeHostSlotsLandscapeExceptionOutcome(site)`.

Expected typed sites set:
- `shouldSwallowException = YES`;
- `shouldClearParsedLandscapeOrientation = YES`;
- `shouldResolveFallbackOrientation = YES`;
- `shouldContinueHosting = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

Late typed site additionally sets:
- `swapStateWouldRemainCommitted = YES`;
- `crossSwapStateWouldRemainCommitted = YES`;
- `rotationStateWouldRemainCommitted = YES`.

Action-zero cleanup sets:
- `exceptionWouldPropagate = YES`.

Unknown/None site returns an all-false outcome.

## Explicit exclusions

R-123 does not:
- read, create, unlink, open, write, close, or stat landscape coordination files;
- mutate parsed orientation, swap, cswap, rotation, active orientation, hosting, or other globals;
- invoke `3DFC8`;
- create or host slots;
- invoke `sub_372CC` or other private hooks;
- synthesize or catch Objective-C/foreign exceptions;
- invoke begin-catch/end-catch/resume-unwind machinery.

## Files changed

- `re/RECONSTRUCTION/ReconstructionRuntime.h`
- `re/RECONSTRUCTION/ReconstructionRuntime.m`
- `scripts/verify_reconstruction.py`
- `re/RECONSTRUCTION/BUILD.md`
- `re/RECONSTRUCTION/COVERAGE.md`
- `re/TESTS.md`
- `re/TODO.md`
- `re/STATE.md`
- `re/LOG/session-124.md`

## Verification

After the runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final verifier, CatDesk standard verification status, and `git diff --check` are run immediately before commit.

## Next

After the user pushes the local batch and confirms compiler green:
- enumerate the next earlier LSDA-bearing function before `3CC44`;
- promote only evidence-safe data-only exception/continuation metadata when the binary contract is exact;
- keep private calls and mutation excluded unless separately proven.

Known unresolved items remain:
- `73E8` / `80D0` bounds;
- full `7E908` blacklist/numerics;
- jailbroken-device runtime smoke testing.
