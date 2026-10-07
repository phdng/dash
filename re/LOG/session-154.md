# LOG/session-154.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-153 commit `fbf3b4f`; promote exact data-only outer catch-all behavior for `365A8`, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `fbf3b4f`.
- Working tree clean and synchronized with origin.
- User confirmed session-153 macOS CI/compiler GREEN.

## Target
- Function: `sub_365A8`.
- LSDA: `0x113FE8`.
- Role: invoke `sub_365D4(CFSTR("display.changed"), YES)`.

## Exact LSDA call-site table
1. `0x365B0..0x365C0 -> 0x365C8`, action 1 catch-all.
2. `0x365C0..0x365D4` -> no landing.

The function prefix `0x365A8..0x365B0` is unprotected.

## Raw ARM64
```
365A8  stp x29,x30,[sp,#-0x10]!
365AC  mov x29,sp
365B0  adrp x0,...          ; "display.changed"
365B4  add  x0,x0,...
365B8  mov  w1,#1
365BC  bl   sub_365D4
365C0  restore frame
365C4  ret

365C8  objc_begin_catch
365CC  restore frame
365D0  tail objc_end_catch
```

Action 1 has no type discriminator and no nonmatching path.

## Exact outer behavior
If an exception escapes `sub_365D4` through the protected range:
- the outer wrapper catches any exception;
- begin/end-catch runs;
- wrapper returns immediately;
- no alternate retry or fallback call is made;
- no wrapper-owned inner object exists to release;
- no rollback or compensation is performed.

The outer wrapper therefore does not erase side effects already performed by `sub_365D4` before the escaping exception.

Those inner effects remain described by R-152:
- display/FBS probing;
- geometry globals;
- resolution/quality globals;
- preferences writes/synchronize;
- Darwin notification behavior;
- retained-local release timing.

R-153 deliberately does not duplicate those inner site semantics.

## Unprotected paths
No landing covers:
- prefix before `0x365B0`;
- normal epilogue `0x365C0..0x365C4`;
- catch body itself.

Exceptions in unprotected wrapper code propagate according to normal runtime behavior.

## Promoted runtime contract
Added:
- `DDDisplayChangedWrapperExceptionSite`:
  - `InnerDisplayConfigurationCall`;
  - `UnprotectedRange`.
- `DDDisplayChangedWrapperExceptionOutcome`.
- `DDResolveDisplayChangedWrapperExceptionOutcome(site)`.

Inner-call site:
- `shouldSwallowAnyException = YES`;
- `shouldReturnImmediately = YES`;
- `innerDisplayConfigurationCouldHaveAppliedSideEffectsBeforeException = YES`.

Unprotected range:
- `exceptionWouldPropagate = YES`.

There is intentionally no nonmatching-type field because this is action-1 catch-all.

## Explicit exclusions
R-153 does not:
- execute `sub_365D4`;
- reconstruct R-152 inner site routing;
- mutate display/global/preferences/notification state;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` run immediately before commit.

## Scout for next batch — 3640C
Next earlier LSDA-bearing function:
- `3640C -> LSDA 0x113FD0`.
- Role: `+[DDz1 carPlayConnected]`.

Exact table:
1. `0x36418..0x3643C -> 0x3644C`, action 5.
2. `0x3643C..0x36474` -> no landing.

Protected range covers:
- `objc_getClass("AVExternalDevice")`;
- class-null branch;
- `currentCarPlayExternalDevice`;
- retain-autoreleased device result.

The range ends at `0x3643C`, before:
- pointer-null comparison;
- boolean result commit to w19;
- normal device release.

Expected typed catch at `0x3644C`:
- begin/end-catch;
- continue at `0x3645C`;
- force result false.

Nonmatching type resumes unwind at `0x36470`.

R-154 should split:
- class lookup;
- current-device acquisition/retain.

The acquisition site can throw before any boolean result is committed and before normal retained-device release.

## Scout after R-154 — 361C4
Next earlier LSDA-bearing function:
- `361C4 -> LSDA 0x113FBC`.

Decoded table:
1. `0x361D8..0x361E4 -> 0x361FC`, action 1 catch-all.
2. `0x361E4..0x3620C` -> no landing.

Protected sequence:
- `teardownWindow`;
- load same target;
- `buildShellIfNeeded`.

The protected range ends before:
```
361E4..361EC  store buildShellIfNeeded result byte into captured block state
```

Catch landing `0x361FC` unconditionally begin/end-catches and returns.

Thus a covered exception:
- swallows any exception;
- returns immediately;
- skips the block-result byte store;
- can preserve any teardown/build side effect that occurred before throw.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
