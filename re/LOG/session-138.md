# LOG/session-138.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-137 commit `954d26d`; decode and promote exact data-only `38B0C` display-scale width-cap exception behavior, verify, and commit locally without pushing._

## Start state

- Branch: `chore/reconstruction-build-ci`.
- HEAD: `954d26d`.
- Working tree: clean.
- User explicitly confirmed session-137 macOS CI/compiler GREEN.

## Target

- Function: `sub_38B0C(view)`.
- LSDA: `0x11428C`.
- Role: start with a bounds-derived dimension from the input view, then try to derive a valid display scale in [1,4]. When scale is valid, cap the original dimension by `800.0 / scale`; otherwise preserve the original dimension.

Reviewed:
- `decompile/38B0C.c`;
- raw ARM64 `0x38B0C..0x38CE8`;
- Mach-O LSDA bytes at `0x11428C`.

## Normal flow

The function:
1. retains the input view;
2. reads `bounds`, saving the original dimension in `d8`;
3. retains the input view a second time;
4. obtains a display object through `34250`;
5. looks up `FBSDisplayConfiguration`;
6. constructs a configuration for the display;
7. prefers direct `scale` when supported and in [1,4];
8. otherwise retains `view.window`, reads its bounds dimension, releases the window, and may derive scale from `pixelSize / windowDimension`;
9. releases display/config/intermediates;
10. if valid scale > 0 and `800/scale < original`, returns the cap; otherwise returns the original bounds-derived value.

## Exact LSDA call-site table

Decoded 12 entries:

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

Landing aliases `0x38CBC`, `0x38CC0`, `0x38CC4`, `0x38CC8`, and `0x38CCC` all branch to common typed catch `0x38CD0`.

## Common typed catch

At `0x38CD0`:
- compare discriminator with expected type;
- expected:
  - begin catch;
  - end catch;
  - branch to `0x38C58`;
- nonmatching:
  - resume unwind at `0x38CE4`.

The expected path at `0x38C58`:
- releases the input-view retain held in x19;
- releases the second input-view retain held in x19;
- returns `d8`, the original bounds-derived dimension.

Therefore every expected protected exception:
- abandons the rest of display/config/window/pixelSize probing;
- skips the `800.0 / scale` cap;
- returns original bounds dimension;
- still performs the two input-view releases.

## Site 1 — display acquisition

`0x38B3C..0x38B48`:
- call `34250`;
- retain-autoreleased display.

The protected range ends before `mov x20,x0`.

Expected catch therefore:
- returns original bounds dimension;
- does not assert a committed display retain in x20;
- runs input cleanup.

## Site 2 — display committed / class lookup

`0x38B48..0x38B58`:
- `mov x20,x0`;
- runtime lookup of `FBSDisplayConfiguration`.

At entry, retained display is committed to x20.

Expected catch:
- bypasses normal display release;
- returns original bounds dimension.

## Site 3 — configuration construction

`0x38B60..0x38B84`:
- allocate `FBSDisplayConfiguration`;
- `initWithCADisplay:isMainDisplay:`;
- retain-autoreleased result.

The committed config register `x21` is assigned only at `0x38B84`, immediately outside the protected range.

Thus:
- retained display x20 is definitely committed;
- config allocation/init may already have started;
- a temporary config object may exist;
- the normal temporary config release at `0x38B88` can be bypassed;
- R-137 does not claim a committed x21 config before the throw.

## Site 4 — scale capability probe

`0x38B9C..0x38BA8`:
- `respondsToSelector:scale`.

By this point:
- retained display x20 committed;
- retained configuration x21 committed.

Expected catch can bypass both normal releases and returns original bounds dimension.

## Site 5 — scale getter

`0x38BAC..0x38BB8`:
- direct `scale` getter.

Same ownership state as site 4:
- display committed;
- config committed.

If the getter returns normally with 1..4, the normal path uses that scale. If it throws the expected type, catch abandons the cap and returns original bounds dimension.

## Site 6 — window bounds fallback

`0x38BD4..0x38BEC`:
- obtain `inputView.window`;
- retain-autoreleased window;
- commit window to x22;
- read window `bounds`.

At throw:
- display x20 committed;
- configuration x21 committed;
- retained window x22 is also committed before the bounds call.

Expected catch skips:
- window release at `0x38BF0`;
- later config/display releases;

and returns original bounds dimension.

## Site 7 — pixelSize capability probe

`0x38C00..0x38C0C`:
- `respondsToSelector:pixelSize`.

The temporary window was already released at `0x38BF4`.

At this site:
- display committed;
- config committed;
- no live retained-window claim.

Expected catch can bypass display/config releases and returns original bounds dimension.

## Site 8 — pixelSize getter

`0x38C24..0x38C30`:
- direct `pixelSize` getter.

Same ownership state as site 7:
- display/config committed;
- temporary window already released.

Expected catch abandons derived scale and returns original bounds dimension.

## Promoted runtime contract

Added:
- `DDDisplayScaleCapExceptionSite`;
- `DDDisplayScaleCapExceptionOutcome`;
- `DDResolveDisplayScaleCapExceptionOutcome(site)`.

All eight typed sites:
- swallow expected exception;
- return original bounds dimension;
- skip display-scale cap;
- continue two input-view releases;
- nonmatching type resumes unwind.

Site-aware metadata distinguishes:
- display not yet committed vs committed;
- temporary config construction vs committed config;
- retained window only during the window-bounds range;
- possible local release bypasses.

Unprotected ranges:
- propagate.

## Explicit exclusions

R-137 does not:
- call `34250`;
- look up or construct `FBSDisplayConfiguration`;
- query `scale`, `window`, `bounds`, or `pixelSize`;
- calculate or apply a live display cap;
- mutate retain/release ownership;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification

After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final project verification and `git diff --check` are run immediately before commit.

## Scout for next batch — 3896C

Direct unwind order identifies the next earlier LSDA-bearing function:
- `3896C -> LSDA 0x114250`.
- Identity: property-list file writer used by rebuild/state helpers.

Normal flow:
- retain property-list object and path;
- require nonnull object + nonempty path;
- serialize property list to NSData;
- write data atomically/options `536870913`;
- after successful write, obtain default NSFileManager;
- create permissions dictionary using `NSFilePosixPermissions`;
- apply file attributes;
- return success.

Exact LSDA table:

1. `0x3896C..0x389C4` -> no landing.
2. `0x389C4..0x389E0` -> `0x38AAC`, action 5.
3. `0x389E8..0x38A00` -> `0x38A94`, action 5.
4. `0x38A0C..0x38A6C` -> `0x38A98`, action 5.
5. `0x38A6C..0x38A90` -> `0x38B08`, action 0.
6. `0x38A90..0x38AC0` -> no landing.
7. `0x38AC0..0x38AD0` -> `0x38B08`, action 0.
8. `0x38AD0..0x38B0C` -> no landing.

### Serialization range

`0x389C4..0x389E0`:
- property-list serialization;
- retain-autoreleased NSData.

Ends before `mov x21,x0`.

Expected catch at `0x38AAC`:
- begin/end catch;
- force return flag false;
- continue final argument cleanup.

No committed x21 data release-bypass should be asserted for this earliest site.

### Write range

`0x389E8..0x38A00`:
- `NSData writeToFile:options:error:`.

At entry:
- retained NSData x21 is committed.

Landing `0x38A94` aliases failure catch `0x38AAC`.

Expected catch:
- returns false;
- jumps past normal retained-data release at `0x38A88`;
- final argument cleanup still runs.

### Attribute range

`0x38A0C..0x38A6C` begins only after write returned success.

Covers:
- defaultManager acquisition/retain;
- permissions dictionary creation/retain;
- `setAttributes:ofItemAtPath:error:`.

Expected catch `0x38A98`:
- begin/end catch;
- branch to `0x38A7C`;
- force success flag true;
- release retained data x21 at `0x38A88`;
- final argument cleanup.

Thus an exception while applying attributes does **not** negate the successful file write.

Depending on sub-site timing:
- retained NSFileManager and/or permissions dictionary normal releases can be bypassed.

### Action-0 cleanup

`0x38A6C..0x38A90` covers attribute intermediates/data cleanup and success flag setup.
`0x38AC0..0x38AD0` covers final path/property-list releases.

Exceptions there:
- are not locally swallowed;
- resume unwind via `0x38B08`.

R-138 should split the attribute range into:
- file-manager acquisition;
- permissions dictionary construction;
- setAttributes call;

and record exact manager/dictionary ownership timing while preserving:
- serialization/write exception -> false;
- post-write attribute exception -> true.

Known unresolved remain:
- `73E8` / `80D0` bounds;
- full `7E908` blacklist/numerics;
- jailbroken-device smoke testing.
