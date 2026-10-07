# LOG/session-145.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-144 commit `01d2a46`; decode and promote exact data-only `374C4` keypane rectangle-forward exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `01d2a46`.
- Working tree clean and synchronized with origin.
- User confirmed session-144 macOS CI/compiler GREEN.

## Target
- Function: `sub_374C4`.
- LSDA: `0x11413C`.
- Role: obtain a candidate keyboard-host rectangle, optionally adopt it when non-null, conditionally decrement geometry budget, then forward a rectangle through `off_163C58`.

## Exact LSDA call-site table
1. `0x374C4..0x374FC` -> no landing.
2. `0x374FC..0x3751C` -> landing `0x375A0`, action 5.
3. `0x3751C..0x375B8` -> no landing.

The one protected range covers:
- preparing width/height arguments from the caller rectangle;
- calling candidate helper `376DC`;
- moving candidate x/y/width/height into `d15/d14/d13/d12`;
- `CGRectIsNull`.

## Caller vs candidate register state
At function entry:
- caller x -> `d9`;
- caller y -> `d8`;
- caller width -> `d10`;
- caller height -> `d11`.

Candidate values returned by `376DC` are copied into:
- candidate x -> `d15`;
- candidate y -> `d14`;
- candidate width -> `d13`;
- candidate height -> `d12`.

Crucially, candidate values do not replace the caller forwarding registers until the later unprotected block:

```
3754C  fmov d9,d15
37550  fmov d8,d14
37554  fmov d10,d13
37558  fmov d11,d12
```

Thus throughout the protected range, caller rectangle remains intact in `d9/d8/d10/d11`.

## Expected catch continuation
Common typed catch at `0x375A0`:
- compares discriminator with expected type;
- expected:
  - begin catch;
  - end catch;
  - branch to `0x3755C`;
- nonmatching:
  - resume unwind at `0x375B4`.

At `0x3755C`:
- load `off_163C58`;
- pass retained input and selector/context;
- move `d9/d8/d10/d11` into the four CGRect argument registers;
- call the forwarding callback;
- perform final retained-input cleanup.

Therefore an expected protected exception:
- does not return early;
- preserves the caller rectangle;
- skips candidate rectangle adoption;
- skips all candidate-difference checks;
- skips the positive `dword_162EF0` decrement path;
- still invokes `off_163C58` with the original caller rectangle;
- then performs normal cleanup.

The forward callback itself is outside the protected range; exceptions there propagate normally.

## Semantic site 1 — candidate geometry helper
This site covers the `376DC` acquisition path.

If expected exception occurs:
- candidate rectangle is not guaranteed complete;
- catch forwards the untouched caller rectangle;
- no counter decrement occurs;
- final cleanup continues.

No candidate-complete claim is made.

## Semantic site 2 — candidate null check
This site starts after `376DC` returned and all four candidate components were committed to `d15/d14/d13/d12`.

If `CGRectIsNull` throws:
- candidate rectangle was definitely acquired;
- it still has not been adopted into forwarding registers;
- catch forwards the original caller rectangle;
- counter decrement is skipped;
- cleanup continues.

## Retained input timing
Input is retained at `0x374F4` and committed to `x20` at `0x374F8`, before the protected range begins.

The catch continuation does not bypass final input cleanup: it joins the same forwarding path that ends in the normal `objc_release(x20)` tail.

R-144 therefore records committed input and cleanup continuation, not a local release leak.

## Promoted runtime contract
Added:
- `DDKeyPaneRectangleForwardExceptionSite`:
  - `CandidateGeometryHelper`;
  - `CandidateNullCheck`;
  - `UnprotectedRange`.
- `DDKeyPaneRectangleForwardExceptionOutcome`.
- `DDResolveKeyPaneRectangleForwardExceptionOutcome(site)`.

Both typed sites:
- swallow expected exception;
- forward original caller rectangle;
- skip candidate adoption;
- skip geometry-counter decrement;
- still invoke forward callback;
- continue final input cleanup;
- input retain definitely committed;
- nonmatching type resumes unwind.

Null-check site additionally:
- candidate rectangle definitely acquired before protected call.

Unprotected:
- propagates.

## Explicit exclusions
R-144 does not:
- call `376DC`;
- execute `CGRectIsNull`;
- mutate `dword_162EF0`;
- invoke `off_163C58`;
- mutate real retain/release ownership;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` are run immediately before commit.

## Scout for next batch — 37398
Next earlier LSDA-bearing function:
- `37398 -> LSDA 0x114114`.
- Registered by `sub_372CC` as the landscape wrapper for `_UIKeyboardLayerHostView -setCenter:`.

Exact table:
1. `0x37398..0x373CC` -> no landing.
2. `0x373CC..0x373D0` -> `0x374A8`, action 5.
3. `0x373D0..0x373EC` -> `0x374AC`, action 5.
4. `0x373FC..0x37428` -> `0x374A4`, action 5.
5. `0x37428..0x374C4` -> no landing.

Landing aliases `0x374A4` and `0x374A8` branch to common typed catch `0x374AC`.

Expected typed catch:
- begin catch;
- end catch;
- branch to `0x37468`;
- then call `off_163C50`;
- final retained-input cleanup follows.

Protected range identities:
- `0x373CC..0x373D0`: helper `37640`;
- `0x373D0..0x373EC`: candidate CGRect helper `376DC`, candidate component stores, `CGRectIsNull`;
- `0x373FC..0x37428`: `CGRectGetMidX` + `CGRectGetMidY`.

### Important unresolved register-state question
The function saves caller center arguments into:
- `d9 = incoming d0`;
- `d8 = incoming d1`.

The eventual forward path at `0x37468` copies:
- `d10 -> d9`;
- `d11 -> d8`;
then calls `off_163C50`.

However:
- local assignment `d10 = caller x`, `d11 = caller y` happens only in the normal `CGRectIsNull` branch at `0x373F0..0x373F4`;
- local candidate-midpoint assignment to d10/d11 occurs in the later `CGRectGetMidX/MidY` path;
- the first two protected ranges can throw before either local assignment.

Inspection of the swizzle-registration function `372CC` establishes only that `37398` is registered as the `setCenter:` wrapper; it does not establish a special source for incoming d10/d11.

Therefore R-145 must **not** promote an early-catch fallback-midpoint claim until the source/validity of d10/d11 is resolved from stronger evidence (trampoline ABI, caller register setup, or other binary evidence).

The third protected range can be analyzed separately because midpoint computation has partially/fully progressed locally; exact d10/d11 assignment boundary must be mapped per call.

Nonmatching type resumes unwind at `0x374C0`.

## Scout after R-145
Next earlier LSDA-bearing function:
- `37284 -> LSDA 0x114100`.
- Decompile: obtain `+[DDz1 shared]`, send `dropSplashIfOverdue`, release.
- Full LSDA/catch routing remains to be decoded after R-145.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
