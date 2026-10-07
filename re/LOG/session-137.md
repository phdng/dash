# LOG/session-137.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-136 commit `89152f3`; decode and promote exact data-only `38E14` keypane-hide-gap parser exception behavior, verify, and commit locally without pushing._

## Start state

- Branch: `chore/reconstruction-build-ci`.
- HEAD: `89152f3`.
- Working tree: clean.
- Branch synchronized with origin at session start.
- User explicitly confirmed session-136 macOS CI/compiler GREEN.

## Target

- Function: `sub_38E14`.
- LSDA: `0x1142DC`.
- Role: parse `/var/tmp/duodash_ab_keypane_hidegap`.

Reviewed:
- `decompile/38E14.c`;
- raw ARM64 `0x38E14..0x38EF8`;
- Mach-O LSDA bytes at `0x1142DC`.

## Normal behavior

The function:
1. reads `/var/tmp/duodash_ab_keypane_hidegap` as an UTF-8 NSString;
2. starts with fallback `71.0`;
3. if the string is nonempty, obtains its UTF-8 pointer;
4. parses using `strtod`;
5. accepts the parsed value only when:
   - value <= 200.0;
   - value >= 0.0;
   - parsing consumed at least one character;
6. otherwise keeps `71.0`;
7. explicitly releases the retained NSString;
8. returns the selected gap.

## Exact LSDA call-site table

Decoded entries:

1. `0x38E14..0x38E34` -> no landing.
2. `0x38E34..0x38E50` -> landing `0x38ED4`, action 5.
3. `0x38E50..0x38E58` -> landing `0x38ED8`, action 5.
4. `0x38E58..0x38E6C` -> no landing.
5. `0x38E6C..0x38E70` -> landing `0x38ED8`, action 5.
6. `0x38E70..0x38E7C` -> no landing.
7. `0x38E7C..0x38E88` -> landing `0x38ED0`, action 5.
8. `0x38E88..0x38EF8` -> no landing.

Landing aliases:
- `0x38ED0 -> 0x38ED8`;
- `0x38ED4 -> 0x38ED8`.

Common typed catch `0x38ED8`:
- compares discriminator with expected type;
- expected:
  - begin catch;
  - end catch;
  - load normal default `71.0` into `d8`;
  - branch to return epilogue `0x38EB4`;
- nonmatching:
  - resume unwind at `0x38EF4`.

No local retry, alternate file read, or reason probe exists.

## Protected site 1 — file read + retain

`0x38E34..0x38E50` covers:
- `+[NSString stringWithContentsOfFile:encoding:error:]`;
- retain-autoreleased return.

Important boundary:
- `mov x19,x0` is at `0x38E50`, immediately outside the protected range.

Expected exception:
- is swallowed;
- returns default `71.0`;
- does not continue length/UTF8/parse work.

Because the retained result is not yet committed into the cleanup register before the protected range ends, R-136 does not claim an established explicit x19-release bypass for this site.

## Protected site 2 — length

`0x38E50..0x38E58`:
- commits retained NSString into `x19`;
- sends `length`.

Expected exception:
- is swallowed;
- returns `71.0`;
- skips normal explicit release `0x38EAC`.

Therefore:
- retained string definitely existed before the protected call;
- its normal local release can be bypassed.

## Unprotected retainAutorelease gap

`0x38E58..0x38E6C` has no landing pad.

It contains:
- load of default `71.0`;
- branch for zero length;
- `objc_retainAutorelease(x19)`;
- setup immediately before `UTF8String`.

If an exception occurs here:
- no local catch converts it to `71.0`;
- it propagates.

This gap is represented explicitly by:
- `DDKeyPaneHideGapExceptionSiteRetainAutoreleaseGap`;
- retained string already committed;
- retain-autorelease may already have started;
- exception propagates.

## Protected site 3 — UTF8String

`0x38E6C..0x38E70` covers:
- `UTF8String`.

At entry:
- x19 retained string is already committed;
- retainAutorelease returned successfully.

Expected exception:
- swallowed;
- forced default `71.0`;
- explicit x19 release at `0x38EAC` is bypassed.

## Protected site 4 — strtod

`0x38E7C..0x38E88` covers:
- end-pointer setup;
- `strtod`.

At entry:
- retained string remains committed;
- UTF8 pointer is nonnull.

Expected exception:
- swallowed;
- forced default `71.0`;
- explicit x19 release is bypassed.

The subsequent numeric validation is unprotected.

## Unprotected validation and cleanup

`0x38E88..0x38EF8` has no local landing.

This region includes:
- range checks against 0 and 200;
- consumed-input check;
- select parsed value vs default;
- explicit release of x19;
- return epilogue;
- catch tail itself.

Exceptions in ordinary unprotected code propagate.

## Promoted runtime contract

Added:
- `DDKeyPaneHideGapExceptionSite`:
  - `FileRead`;
  - `LengthRead`;
  - `UTF8StringRead`;
  - `NumericParse`;
  - `RetainAutoreleaseGap`;
  - `OtherUnprotectedRange`.
- `DDKeyPaneHideGapExceptionOutcome`.
- `DDResolveKeyPaneHideGapExceptionOutcome(site)`.

All four typed sites:
- `shouldSwallowException = YES`;
- `shouldReturnDefaultGap = YES`;
- `defaultGap = 71.0`;
- nonmatching discriminator resumes unwind.

Length/UTF8/parse sites additionally:
- retained string definitely committed before protected call;
- explicit local retained-string release could be bypassed.

File-read site:
- no retained-string cleanup bypass is asserted.

RetainAutorelease gap:
- retained string already committed;
- retainAutorelease may have started;
- exception propagates.

Other unprotected:
- propagates.

## Explicit exclusions

R-136 does not:
- read the gap file;
- create/read NSString contents;
- call `UTF8String`;
- call `strtod`;
- mutate retain/release ownership;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification

After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final project verification and `git diff --check` are run immediately before commit.

## Scout for next batch — 38B0C

Direct Mach-O unwind enumeration shows the next earlier LSDA-bearing function:
- `38B0C -> LSDA 0x11428C`.
- It immediately precedes `38E14`.

Identity:
- `sub_38B0C(view)`;
- derives a dimension from input view bounds, then attempts to obtain a valid display scale (1..4) using `FBSDisplayConfiguration`;
- if valid, caps the original dimension by `800.0 / scale`;
- if display/config/scale probing fails normally, returns the original bounds dimension.

Exact LSDA call-site table:

1. `0x38B0C..0x38B3C` -> no landing.
2. `0x38B3C..0x38B48` -> `0x38CCC`, action 5.
3. `0x38B48..0x38B58` -> `0x38CC8`, action 5.
4. `0x38B60..0x38B84` -> `0x38CD0`, action 5.
5. `0x38B84..0x38B9C` -> no landing.
6. `0x38B9C..0x38BA8` -> `0x38CD0`, action 5.
7. `0x38BAC..0x38BB8` -> `0x38CC0`, action 5.
8. `0x38BD4..0x38BEC` -> `0x38CC4`, action 5.
9. `0x38BEC..0x38C00` -> no landing.
10. `0x38C00..0x38C0C` -> `0x38CC4`, action 5.
11. `0x38C24..0x38C30` -> `0x38CBC`, action 5.
12. `0x38C30..0x38CE8` -> no landing.

All action-5 landing stubs converge at common typed catch `0x38CD0`.

Expected catch:
- begin catch;
- end catch;
- branch to `0x38C58`;
- release the two input-view ownerships held in x19;
- return original bounds-derived value from d8.

Thus expected display-scale exceptions:
- abandon remaining display/config/window/pixel-size probing;
- do not apply the 800/scale cap;
- return original bounds dimension.

Nonmatching type:
- resumes unwind at `0x38CE4`.

### R-137 ownership timing to map

- `0x38B3C..0x38B48` display acquisition+retain:
  - ends before `mov x20,x0`;
  - no established committed display cleanup bypass.
- `0x38B48..0x38B58`:
  - display x20 committed before class lookup;
  - expected catch can bypass display release.
- `0x38B60..0x38B84`:
  - display committed;
  - FBSDisplayConfiguration allocation/init/retain in progress;
  - temporary allocated config may exist before x21 commit.
- `0x38B9C..0x38BA8` and `0x38BAC..0x38BB8`:
  - retained display + retained configuration are committed;
  - catch can bypass both normal releases.
- `0x38BD4..0x38BEC`:
  - window acquisition/retain + bounds;
  - display/config committed;
  - retained window may also be present before throw.
- `0x38C00..0x38C0C` and `0x38C24..0x38C30`:
  - temporary window was already released;
  - display/config remain retained;
  - catch bypasses those normal releases.

R-137 should promote:
- typed exception -> original-bounds fallback;
- exact display/config/window ownership timing;
- unprotected cleanup/tail propagation;
- nonmatching unwind.

Known unresolved remain:
- `73E8` / `80D0` bounds;
- full `7E908` blacklist/numerics;
- jailbroken-device smoke testing.
