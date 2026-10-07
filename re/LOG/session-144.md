# LOG/session-144.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-143 commit `6734571`; decode and promote exact data-only `375B8` keypane center-adjustment exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `6734571`.
- Working tree clean.
- User confirmed session-143 macOS CI/compiler GREEN.
- Local tracking ref still reported ahead 1 at session start; assistant did not fetch/push.

## Target
- Function: `sub_375B8`.
- LSDA: `0x11415C`.
- Role: invoke pre-geometry callback, retain a working view, run geometry helpers, and optionally read/reapply the view center.

## Exact LSDA table
1. `0x375B8..0x375EC` -> no landing.
2. `0x375EC..0x37610` -> landing `0x37628`, action 5.
3. `0x37610..0x37640` -> no landing.

The single protected range begins only after:
- initial input retain returned;
- indirect pre-geometry callback through `off_163C60` returned;
- second retain returned;
- the working retained view was committed to `x19`.

## Raw ARM64 ordering
Relevant flow:

```
375C8  objc_retain(input) -> x20
375D8  args
375DC  blr off_163C60
375E0  mov x0,x20
375E4  objc_retain
375E8  mov x19,x0

375EC  bl 37640
375F0  mov x0,x19
375F4  bl 376DC
375F8  bl CGRectIsNull
375FC  if null -> 37610
37600  mov x0,x19
37604  bl center
37608  mov x0,x19
3760C  bl setCenter:

37610  mov x0,x19
37614  objc_release
37618  mov x0,x19
...
37624  tail objc_release

37628  cmp w1,#1
3762C  b.ne 3763C
37630  objc_begin_catch
37634  objc_end_catch
37638  b 37618
3763C  resume unwind
```

## Expected catch continuation
Expected action-5 exception:
- begin catch;
- end catch;
- branch directly to `0x37618`.

Consequences:
- remaining protected geometry work is abandoned;
- normal release at `0x37614` is bypassed;
- final retained-view release at `0x37624` still runs;
- function returns after final cleanup.

Nonmatching type resumes unwind at `0x3763C`.

No catch-time geometry retry or rollback exists.

## Pre-protected ordering
Because the LSDA range starts at `0x375EC`:
- the indirect `off_163C60` callback definitely returned before every protected call;
- the second retained ownership in x19 is definitely committed before every protected call.

R-143 records this explicitly rather than treating catch behavior as if the whole helper were rolled back.

## Semantic site 1 — geometry helpers
This site covers:
- `37640`;
- `376DC`;
- `CGRectIsNull`.

If expected exception occurs here:
- no center getter has completed;
- `setCenter:` is not reached;
- catch skips the rest of the protected range;
- one normal retained-view release is bypassed;
- final retained-view cleanup still runs.

No center mutation is asserted.

## Semantic site 2 — center getter
The center getter is reached only after:
- helper `37640` returned;
- geometry helper `376DC` returned;
- `CGRectIsNull` returned false.

If `center` throws:
- `setCenter:` has not run;
- catch skips the setter;
- no center write is asserted;
- final retained-view cleanup still runs.

## Semantic site 3 — center setter
`setCenter:` is reached only after the center getter returned successfully.

If the setter throws:
- the getter definitely completed;
- setter side effects may already have occurred before exception propagation;
- catch performs no rollback of center;
- catch skips to final retained-view cleanup.

R-143 therefore marks center-write persistence only for this site.

## Promoted runtime contract
Added:
- `DDKeyPaneCenterAdjustmentExceptionSite`:
  - `GeometryHelpers`;
  - `CenterGetter`;
  - `CenterSetter`;
  - `UnprotectedRange`.
- `DDKeyPaneCenterAdjustmentExceptionOutcome`.
- `DDResolveKeyPaneCenterAdjustmentExceptionOutcome(site)`.

All typed semantic sites:
- `shouldSwallowException = YES`;
- skip remaining geometry work;
- pre-geometry callback definitely completed before protected call;
- retained working view definitely committed before protected call;
- first normal retained-view release could be bypassed;
- final retained-view cleanup continues;
- nonmatching type resumes unwind.

Center setter site additionally:
- center getter definitely completed before protected call;
- center could already have applied before exception.

Unprotected:
- propagates.

## Explicit exclusions
R-143 does not:
- call `off_163C60`;
- execute helpers `37640` / `376DC`;
- query live CGRect state;
- call UIView `center` / `setCenter:`;
- mutate real ownership;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` are run immediately before commit.

## Scout for next batch — 374C4
Next earlier LSDA-bearing function:
- `374C4 -> LSDA 0x11413C`.

Exact table:
1. `0x374C4..0x374FC` -> no landing.
2. `0x374FC..0x3751C` -> `0x375A0`, action 5.
3. `0x3751C..0x375B8` -> no landing.

Protected range covers:
- loading caller width/height into arguments;
- candidate rectangle helper `376DC`;
- storing candidate x/y/width/height into d15/d14/d13/d12;
- `CGRectIsNull`.

Expected typed catch at `0x375A0`:
- begin/end catch;
- branch to `0x3755C`.

At `0x3755C`, the function forwards through `off_163C58`.

Important ordering:
- caller rectangle remains preserved in d9/d8/d10/d11;
- candidate rectangle is copied into those forwarding registers only later at `0x3754C..0x37558`, outside the protected range;
- counter decrement logic for `dword_162EF0` is also outside the protected range and skipped by catch.

Therefore expected protected exception:
- keeps caller-supplied rectangle;
- skips candidate adoption;
- skips retry/counter decrement;
- still calls `off_163C58` with the original rectangle;
- then performs final input cleanup.

Nonmatching type resumes unwind at `0x375B4`.

R-144 should split candidate-helper vs CGRectIsNull sites only if needed for exact helper timing; both share the same original-rectangle forwarding continuation.

## Scout after R-144 — 37398
Next earlier LSDA-bearing function:
- `37398 -> LSDA 0x114114`.

Exact 5-entry table:
1. `0x37398..0x373CC` -> no landing.
2. `0x373CC..0x373D0` -> `0x374A8`, action 5.
3. `0x373D0..0x373EC` -> `0x374AC`, action 5.
4. `0x373FC..0x37428` -> `0x374A4`, action 5.
5. `0x37428..0x374C4` -> no landing.

All landing aliases converge the typed catch at `0x374AC`, whose expected path jumps to `0x37468`, forwarding a fallback midpoint through `off_163C50`.

R-145 should map:
- pre-helper `37640`;
- candidate CGRect helper + null test;
- CGRectGetMidX/MidY protected range;
- caller midpoint vs candidate midpoint fallback state;
- whether the positive `dword_162EF0` decrement is skipped/preserved by catch.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
