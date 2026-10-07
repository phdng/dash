# LOG/session-125.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-124 commit `6dcbcb9`; identify the immediately preceding LSDA-bearing function before `3CC44`, promote its exact evidence-safe exception continuation, verify, and commit locally without pushing._

## Start state

- Branch: `chore/reconstruction-build-ci`.
- HEAD at session start: `6dcbcb9`.
- Working tree: clean.
- Branch was synchronized with origin at session start.
- User confirmed the session-124 macOS CI/compiler build was green.

## LSDA enumeration

Direct `__unwind_info` enumeration for the first arm64 FAT slice shows the immediately preceding exception-bearing functions below `3CC44`:

- `3C808 -> LSDA 0x11466C`;
- `3C368 -> LSDA 0x1145D8`;
- `3C1F0 -> LSDA 0x1145B8`;
- `3BBF0 -> LSDA 0x114538`.

Therefore R-124 targets `3C808` first.

The first arm64 FAT slice begins at file offset `0x4000`.

## R-124 — 3C808 teardownAuxScene exception behavior

Reviewed:
- `decompile/3C808.c`;
- raw ARM64 `0x3C808..0x3C908`;
- Mach-O LSDA `0x11466C`;
- existing evidence-safe `DDClearAuxSceneMirror` state half from R-078/session-080.

Decoded LSDA call-site table:
- `0x3C808..0x3C858` -> no landing pad;
- `0x3C858..0x3C894` -> landing `0x3C8F0`, action 5;
- `0x3C894..0x3C908` -> no landing pad.

There is exactly one local typed catch.

## Ordering before the protected range

Normal ARM64 ordering:

- `0x3C81C`: read `self->_auxVC`;
- if controller is absent, aux bundle length is checked and a completely empty teardown returns early;
- `0x3C838`: retain current `self->_auxVC` into `x19`;
- `0x3C840`: load current ivar;
- `0x3C844`: set `self->_auxVC = nil`;
- `0x3C848`: release the old ivar value.

Therefore the private controller ivar has already been cleared before entering the only typed protected range.

## Protected private-view teardown

Protected range `0x3C858..0x3C894` covers:

- `view` send on the retained aux controller;
- retain-autoreleased handling for the returned view;
- `removeFromSuperview`;
- `respondsToSelector:invalidate`;
- optional `invalidate`.

Normal flow releases the retained view at `0x3C894`, immediately after the protected range.

Landing `0x3C8F0`:

- compare catch discriminator with expected value 1;
- expected type -> begin catch;
- end catch;
- branch to `0x3C89C`;
- nonmatching type -> `0x3C904` resume unwind.

The expected catch therefore skips:
- any remaining private view teardown;
- the normal retained-view release at `0x3C894`.

The release bypass is conditional on a view having been retained before the throw, so the promoted metadata is “could be bypassed”, not “guaranteed leaked”.

## Expected continuation at 0x3C89C

The catch rejoins at the aux state-reset block:

- load old aux bundle from `qword_163D70`;
- clear `qword_163D70`;
- release old aux bundle;
- store `CGSizeZero` into `xmmword_163DD0`;
- clear aux orientation `qword_163DE0`;
- call `sub_3E428` to refresh aux generation/settings state;
- release retained aux controller `x19`;
- return.

Thus an expected private teardown exception:

- is swallowed locally;
- does not restore the already-cleared `_auxVC` ivar;
- skips the rest of private view removal/invalidation;
- still clears aux bundle/native size/orientation state;
- still executes the existing `3E428` generation-state refresh;
- still reaches final retained-controller cleanup.

All ranges outside `0x3C858..0x3C894` have no local landing pad and exceptions propagate.

## Promoted runtime contract

Added:

- `DDAuxSceneTeardownExceptionSite`:
  - `PrivateViewTeardown`;
  - `UnprotectedRange`;
- `DDAuxSceneTeardownExceptionOutcome`;
- `DDResolveAuxSceneTeardownExceptionOutcome(site)`.

Private-view site reports:

- `shouldSwallowException = YES`;
- `auxControllerIvarWasAlreadyClearedBeforeCatch = YES`;
- `shouldSkipRemainingPrivateTeardown = YES`;
- `shouldContinueAuxStateReset = YES`;
- `shouldRefreshAuxGenerationState = YES`;
- `retainedViewReleaseCouldBeBypassed = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

Unprotected site reports:

- `exceptionWouldPropagate = YES`.

Unknown/None site returns an all-false outcome.

The existing live mirror `DDClearAuxSceneMirror` is unchanged; R-124 only adds exception-continuation metadata.

## Explicit exclusions

R-124 does not:

- access or mutate the real `DDz2._auxVC` ivar;
- call `view`, `removeFromSuperview`, `respondsToSelector:`, or `invalidate`;
- clear live aux globals through the exception resolver;
- call private scene/controller APIs;
- retain/release live private view/controller objects;
- synthesize or catch Objective-C/foreign exceptions;
- invoke begin-catch/end-catch/resume-unwind runtime machinery.

## Verification

After runtime/verifier edit:

- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final verifier, CatDesk verification status, and `git diff --check` are run immediately before commit.

## Scout for next batch — 3C368

Direct unwind enumeration shows:

- `3C368 -> LSDA 0x1145D8`.

Existing decompile/raw ARM64 tail already shows landing stubs `0x3C7AC..0x3C7BC` converging at common catch `0x3C7C0`.

At that catch:
- expected discriminator 1 begins catch;
- calls `[DDz2 teardownAuxScene]`;
- releases the caught exception object;
- ends catch;
- branches to `0x3C3D8`, the nil-return path;
- nonmatching discriminator resumes unwind at `0x3C800`.

R-125 should decode the exact `3C368` call-site table before promotion so each protected private scene-creation range can be mapped precisely to the common teardown-and-return-nil continuation.

## Next

After the user pushes the session-125 batch and confirms compiler green:
- R-125: decode/promote exact `3C368` exception ranges against LSDA `0x1145D8`;
- preserve data-only scope;
- do not instantiate private SpringBoard scene/controller objects or invoke teardown from the resolver.

Known unresolved items remain:
- `73E8` / `80D0` bounds;
- full `7E908` blacklist/numerics;
- jailbroken-device runtime smoke testing.
