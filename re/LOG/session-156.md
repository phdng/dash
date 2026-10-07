# LOG/session-156.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-155 commit `0be4c67`; decode and promote exact data-only `361C4` shell-rebuild block catch-all behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `0be4c67`.
- Working tree clean and synchronized with origin.
- User confirmed session-155 macOS CI/compiler GREEN.

## Target
- Function: `sub_361C4`.
- LSDA: `0x113FBC`.
- Role: block helper that calls `teardownWindow`, then `buildShellIfNeeded`, then stores the build result byte into captured block state.

## Exact LSDA
1. `0x361D8..0x361E4 -> 0x361FC`, action 1 catch-all.
2. `0x361E4..0x3620C` -> no landing.

The function prefix `0x361C4..0x361D8` is unprotected.

## Raw ARM64
```
361C4  prologue
361D0  mov x19,x0
361D4  ldr x0,[x0,#0x20]
361D8  teardownWindow
361DC  ldr x0,[x19,#0x20]
361E0  buildShellIfNeeded

361E4  ldr x8,[x19,#0x28]
361E8  ldr x8,[x8,#8]
361EC  strb w0,[x8,#0x18]
361F0  epilogue
361F8  ret

361FC  objc_begin_catch
36200  restore frame
36208  tail objc_end_catch
```

The protected range ends exactly before the captured result-byte store.

## Catch behavior
Action 1 is catch-all:
- no discriminator;
- no nonmatching-type path;
- covered exception is swallowed;
- function returns immediately from the catch landing.

The catch skips:
- loading captured byref storage;
- storing the build result byte;
- normal return path after that store.

Therefore the captured byte is not modified by this block when either protected send throws.

## Semantic site 1 — teardownWindow
Protected call:
- `teardownWindow`.

If it throws:
- catch-all swallows the exception;
- block returns immediately;
- captured result byte store is skipped;
- teardown may already have partially applied side effects before throw;
- `buildShellIfNeeded` is never reached.

No rollback or compensating teardown action exists locally.

## Semantic site 2 — buildShellIfNeeded
This site is reached only after `teardownWindow` returned normally.

If `buildShellIfNeeded` throws:
- teardown definitely completed before the protected call;
- catch-all swallows the exception;
- block returns immediately;
- captured result byte store is skipped;
- build side effects may already have partially applied before throw.

No retry or alternate build path exists locally.

## Unprotected tail
`0x361E4..0x3620C` is outside local exception protection.

The captured byte store and epilogue/catch code are therefore not covered by the action-1 landing.

Any exception there propagates according to normal runtime behavior.

## Promoted runtime contract
Added:
- `DDShellRebuildBlockExceptionSite`:
  - `TeardownWindowSend`;
  - `BuildShellIfNeededSend`;
  - `UnprotectedRange`.
- `DDShellRebuildBlockExceptionOutcome`.
- `DDResolveShellRebuildBlockExceptionOutcome(site)`.

Teardown site records:
- swallow any covered exception;
- immediate return;
- captured result-byte store skipped;
- teardown side effects may have applied.

Build site additionally records:
- teardown definitely completed before the call;
- build side effects may have applied.

Unprotected site:
- propagates.

There is intentionally no nonmatching-type field because LSDA action 1 is catch-all.

## Explicit exclusions
R-155 does not:
- invoke `teardownWindow`;
- invoke `buildShellIfNeeded`;
- mutate captured block state;
- execute exception runtime or unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` run immediately before commit.

## Scout for next batch — 36158
Next earlier LSDA-bearing function:
- `36158 -> LSDA 0x113FA8`.
- Role: remove a splash-like view, reconcile a weak owner slot, nudge presentation with `"splash.fade"`, then release the weak-retained owner.

Exact table:
1. `0x3616C..0x36170 -> 0x361B8`, action 1 catch-all.
2. `0x36170..0x361C4` -> no landing.

The protected range covers only:
```
3616C removeFromSuperview
```

Landing:
```
361B8 objc_begin_catch
361BC objc_end_catch
361C0 b 36170
```

Therefore a covered remove exception:
- is swallowed;
- does **not** return;
- resumes at weak-owner acquisition;
- can still clear a matching owner slot and release the old slot object;
- still sends `nudgePresent:@"splash.fade"`;
- still releases the weak-retained owner.

R-156 should record possible remove side effects before throw, guaranteed continuation after catch, owner-slot mutation timing, nudge timing, and unprotected later propagation.

## Scout after R-156 — 35FBC
Next earlier LSDA-bearing function:
- `35FBC -> LSDA 0x113F94`.
- Role: build animation/completion blocks around a target view and weak owner, then invoke `+[UIView animateWithDuration:animations:completion:]`.

Exact table:
1. `0x35FBC..0x3606C` -> no landing.
2. `0x3606C..0x36084 -> 0x360B4`, action 0.
3. `0x36084..0x360C8` -> no landing.

The action-0 range covers duration/block preparation immediately before and including the UIView animation call.

Landing `0x360B4`:
- preserves the active exception;
- destroys the copied weak capture via `objc_destroyWeak`;
- resumes unwind at `0x360C4`.

It does not swallow the exception.

R-157 should map:
- copied weak-capture lifetime;
- retained animation/completion captures;
- animation-call side effects before throw;
- action-0 weak cleanup before resume unwind;
- normal post-call weak/capture releases outside protection.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
