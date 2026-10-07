# LOG/session-155.md
_Date: 2026-10-07. Objective: continue from synced session-154 commit `2ca7d2a`; decode and promote exact data-only `3640C` `+[DDz1 carPlayConnected]` typed-false exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `2ca7d2a`.
- Working tree clean and synchronized with origin.
- User requested continuation; this turn did not explicitly confirm the CI result for session-154.

## Target
- Function: `+[DDz1 carPlayConnected]`.
- Address: `0x3640C`.
- LSDA: `0x113FD0`.
- Role: resolve AVExternalDevice, acquire current CarPlay external device, return whether that device is non-nil.

## Exact LSDA call-site table
1. `0x36418..0x3643C -> 0x3644C`, action 5.
2. `0x3643C..0x36474` -> no landing.

The function prefix `0x3640C..0x36418` is unprotected.

## Raw ARM64
```
36418  load "AVExternalDevice"
36420  objc_getClass
36424  cbz x0,3645C
36428  load currentCarPlayExternalDevice selector
36430  objc_msgSend
36438  retain-autoreleased return

3643C  cmp x0,#0
36440  cset w19,ne
36444  objc_release
36448  b 36460

3644C  cmp w1,#1
36450  b.ne 36470
36454  objc_begin_catch
36458  objc_end_catch
3645C  mov w19,#0
36460  mov x0,x19
...
36470  resume unwind
```

The protected range ends immediately before:
- device pointer null test;
- boolean commit to w19;
- normal device release.

## Normal false path
A null AVExternalDevice class is not an exception:
- `cbz x0,0x3645C`;
- w19 is forced false;
- no device acquisition occurs.

This control-flow false path is separate from the exception resolver.

## Expected typed catch
Expected action-5 exception:
- begin catch;
- end catch;
- fall through `0x3645C`;
- force `w19 = 0`;
- return false.

The catch does not:
- retry class lookup;
- retry device acquisition;
- inspect any partial device result;
- commit a device-derived boolean.

Nonmatching type resumes unwind at `0x36470`.

## Semantic site 1 — AVExternalDevice class lookup
Protected operation:
- `objc_getClass("AVExternalDevice")`.

If expected exception occurs:
- boolean result is definitely uncommitted;
- expected catch forces false;
- no current-device acquisition has started;
- no retained device ownership is asserted.

## Semantic site 2 — current device acquisition
This site covers:
- `currentCarPlayExternalDevice`;
- retain-autoreleased result.

If expected exception occurs:
- class lookup has already succeeded;
- boolean result is still uncommitted because `cmp/cset` start only at `0x3643C`, outside protection;
- device acquisition/retain may already have produced a temporary retained result;
- normal device release at `0x36444` is bypassed;
- catch forces false.

No committed local device register exists beyond the temporary x0 return value, so R-154 deliberately records temporary acquisition/release-bypass rather than a stronger retained-local claim.

## Unprotected paths
Exceptions in:
- function prologue;
- pointer comparison;
- boolean commit;
- normal release;
- epilogue/catch code

are outside the protected action-5 range and propagate according to normal runtime behavior.

## Promoted runtime contract
Added:
- `DDCarPlayConnectedExceptionSite`:
  - `ExternalDeviceClassLookup`;
  - `CurrentDeviceAcquisition`;
  - `UnprotectedRange`.
- `DDCarPlayConnectedExceptionOutcome`.
- `DDResolveCarPlayConnectedExceptionOutcome(site)`.

Both typed sites:
- swallow expected exception;
- return false;
- mark boolean result definitely uncommitted before catch;
- record nonmatching-type resume unwind.

Current-device acquisition additionally records:
- temporary device acquisition may have started;
- temporary-device release may be bypassed.

Unprotected:
- propagates.

## Explicit exclusions
R-154 does not:
- call `objc_getClass`;
- query `AVExternalDevice`;
- retain/release a real device;
- execute exception runtime or unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` run immediately before commit.

## Scout for next batch — 361C4
Next earlier LSDA-bearing function:
- `361C4 -> LSDA 0x113FBC`.
- Role: block helper sending `teardownWindow` then `buildShellIfNeeded`, storing the latter result byte into captured block state.

Exact table:
1. `0x361D8..0x361E4 -> 0x361FC`, action 1 catch-all.
2. `0x361E4..0x3620C` -> no landing.

Protected raw sequence:
```
361D8 teardownWindow
361DC load same target
361E0 buildShellIfNeeded
```

The protected range ends before:
```
361E4..361EC captured block-result byte store
```

Landing `0x361FC`:
- unconditional begin catch;
- restore frame;
- tail end catch;
- return.

Thus a covered exception:
- is swallowed;
- returns immediately;
- leaves captured result byte unmodified;
- can preserve teardown/build side effects already applied before throw.

No type discriminator/nonmatching branch exists.

## Scout after R-155 — 36158
Next earlier LSDA-bearing function:
- `36158 -> LSDA 0x113FA8`.

Exact table:
1. `0x3616C..0x36170 -> 0x361B8`, action 1 catch-all.
2. `0x36170..0x361C4` -> no landing.

The only protected instruction is `removeFromSuperview`.

Landing `0x361B8` unconditionally begin/end-catches and branches back to `0x36170`.

Therefore a removeFromSuperview exception:
- is swallowed;
- does **not** return;
- continues weak-owner acquisition;
- may clear matching owner slot;
- still sends `nudgePresent:@"splash.fade"`;
- still releases the weak-retained owner.

All later weak-owner/nudge work is unprotected and can propagate.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
