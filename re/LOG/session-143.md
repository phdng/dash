# LOG/session-143.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-142 commit `13e2a56`; decode and promote exact data-only `37924` CarPlay UI-status callback catch-all behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `13e2a56`.
- Working tree clean.
- Branch synchronized with origin at session start.
- User confirmed session-142 macOS CI/compiler GREEN.

## Target
- Function: `sub_37924`.
- LSDA: `0x114178`.
- Role: obtain shared DDz1 and forward captured CarPlay UI status/generation/ok fields.

## Exact LSDA table
The call-site table contains two entries:
1. `0x3793C..0x37958 -> 0x37968`, action 1.
2. `0x37958..0x37978` -> no landing.

The function prefix `0x37924..0x3793C` is also outside the protected range.

Action 1 is catch-all here.

## Raw ARM64
Relevant sequence:

```
3793C  bl    +[DDz1 shared]
37944  bl    objc_retainAutoreleasedReturnValue
37948  mov   x19,x0
3794C  ldp   x2,x3,[x20,#0x20]
37950  ldrb  w4,[x20,#0x30]
37954  bl    noteCarPlayUIStatus:gen:ok:
37958  mov   x0,x19
3795C  restore frame
37964  b     objc_release

37968  bl    objc_begin_catch
3796C  restore frame
37974  b     objc_end_catch
```

There is no catch discriminator test.

Therefore every exception covered by `0x3793C..0x37958`:
- is swallowed;
- skips the normal DDz1 release tail;
- returns immediately after `objc_end_catch`.

## Semantic site 1 — shared DDz1 acquisition
Protected operations before `mov x19,x0`:
- `+[DDz1 shared]`;
- retain-autoreleased result.

If an exception occurs here:
- catch-all swallows it;
- function returns immediately;
- no committed retained DDz1 x19 is guaranteed;
- DDz1 lookup/retain work may already have started;
- temporary DDz1 cleanup can be bypassed.

R-142 records only:
- catch-all swallow;
- immediate return;
- temporary controller acquisition may have started;
- temporary controller release could be bypassed.

## Semantic site 2 — status callback send
At `0x37948` retained DDz1 is committed to x19.

The function then loads captured values from the callback context:
- generation/context field at +0x20/+0x28;
- boolean ok field at +0x30;

and sends:
- `noteCarPlayUIStatus:gen:ok:` at `0x37954`.

If that callback throws:
- retained DDz1 x19 definitely existed before the call;
- the catch skips the normal release tail `0x37958..0x37964`;
- any callback side effects that occurred before the exception are not rolled back;
- the wrapper returns immediately.

No retry, alternate notification, reason probe, or cleanup callback exists locally.

## Unprotected paths
No landing covers:
- function prologue/prefix before `0x3793C`;
- normal x19 release/tail after `0x37958`;
- catch body itself.

Exceptions in those regions propagate normally.

## Promoted runtime contract
Added:
- `DDCarPlayUIStatusCallbackExceptionSite`:
  - `SharedControllerAcquisition`;
  - `StatusCallbackSend`;
  - `UnprotectedRange`.
- `DDCarPlayUIStatusCallbackExceptionOutcome`.
- `DDResolveCarPlayUIStatusCallbackExceptionOutcome(site)`.

Shared acquisition:
- `shouldSwallowAnyException = YES`;
- `shouldReturnImmediately = YES`;
- temporary controller acquisition may have started;
- temporary controller release could be bypassed.

Callback send:
- catch-all swallow + immediate return;
- retained controller definitely committed;
- retained-controller release could be bypassed;
- callback side effects could already have applied before exception.

Unprotected:
- propagates.

The outcome intentionally has no nonmatching-type field because action 1 has no type discriminator path.

## Explicit exclusions
R-142 does not:
- call `+[DDz1 shared]`;
- invoke `noteCarPlayUIStatus:gen:ok:`;
- mutate callback/global state;
- alter real retain/release ownership;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final standard verifier and `git diff --check` are run immediately before commit.

## Scout for next batch — 375B8
Next earlier LSDA-bearing function:
- `375B8 -> LSDA 0x11415C`.

Exact table:
1. `0x375B8..0x375EC` -> no landing.
2. `0x375EC..0x37610 -> 0x37628`, action 5.
3. `0x37610..0x37640` -> no landing.

Protected range:
- call helper `37640`;
- call geometry helper `376DC`;
- `CGRectIsNull`;
- when non-null, `center` getter;
- `setCenter:`.

Expected typed catch at `0x37628`:
- compare discriminator;
- begin catch;
- end catch;
- branch to `0x37618`;
- skip all remaining protected geometry work;
- perform remaining retained-input cleanup;
- return.

Nonmatching type resumes unwind at `0x3763C`.

R-143 should split:
- pre-center geometry helper failure:
  - no center setter reached;
- center getter failure:
  - no center setter completed;
- center setter failure:
  - center mutation may already have applied before throw;
  - catch performs no rollback.

## Scout after R-143 — 374C4
The next earlier LSDA-bearing function is:
- `374C4 -> LSDA 0x11413C`.

Decoded table:
1. `0x374C4..0x374FC` -> no landing.
2. `0x374FC..0x3751C -> 0x375A0`, action 5.
3. `0x3751C..0x375B8` -> no landing.

Decompile shows this helper:
- obtains a candidate CGRect through `376DC`;
- compares its origin against caller coordinates with a 0.25 tolerance;
- decrements `dword_162EF0` when the origin materially changed and the counter is positive;
- forwards either candidate or caller rectangle via function pointer `off_163C58`.

R-144 should map the single typed range and whether the catch preserves caller rectangle vs candidate rectangle/counter effects before the final callback.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
