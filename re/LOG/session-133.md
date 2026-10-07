# LOG/session-133.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-132 commit `5b20ca6`; decode and promote exact data-only `39B70` slide-animation exception behavior, verify, and commit locally without pushing._

## Start state

- Branch: `chore/reconstruction-build-ci`.
- HEAD: `5b20ca6`.
- Working tree: clean.
- Local tracking ref still reported ahead of origin; assistant did not fetch/push.
- User explicitly confirmed session-132 macOS CI/compiler GREEN.

## Target

- Function: `sub_39B70`.
- LSDA: `0x11439C`.
- Role: slide animation setup after the pre-slide `39D4C` predicate.

Reviewed:
- `decompile/39B70.c`;
- `decompile/3A004.c`;
- `decompile/3A034.c`;
- raw ARM64 `0x39B70..0x39D4C`;
- Mach-O LSDA `0x11439C`.

## Exact LSDA table

Decoded 5 entries:

1. `0x39B70..0x39CA4` -> no landing.
2. `0x39CA4..0x39CC8` -> landing `0x39CFC`, action 5.
3. `0x39CC8..0x39D1C` -> no landing.
4. `0x39D1C..0x39D2C` -> landing `0x39D3C`, action 0.
5. `0x39D2C..0x39D4C` -> no landing.

The only typed protected range is the UIView animation call.

## State committed before the protected animation call

Raw ARM64 before `0x39CA4` establishes:

- host object and split object are present;
- slide-in-progress byte `byte_163C98` is checked clear;
- `39D4C("before the slide")` returned false;
- `byte_163C98 = 1` is written at `0x39BCC..0x39BD0`;
- current generation `qword_163CE8` is captured;
- `dispatch_time(DISPATCH_TIME_NOW, 1s)` is computed;
- a main-queue `dispatch_after` block using helper `3A004` is already scheduled;
- split view `qword_163C68` is retained;
- host view `qword_163C78` bounds are read;
- target center is fully computed:
  - x = host-bounds width * 0.5;
  - y = host-bounds height - key-pane height * scale * 0.5;
- animation block helper `3A034` is built with:
  - retained split view;
  - precomputed center x/y.

Thus none of the above state is rolled back by the local animation catch.

## 1-second follow-up helper 3A004

`3A004` captures the generation value present when the slide starts.

At fire time it calls:
- `39D4C("1 s after the slide")`

only if:
- captured generation == current `qword_163CE8`;
- host `qword_163C78` is still non-null.

It does not itself clear `byte_163C98`; R-132 records only that the follow-up was already scheduled before the protected animation call.

## Animation block helper 3A034

`3A034` simply loads:
- captured target center;
- captured split view;

and sends:
- `setCenter:`.

Therefore the protected UIView animation call may execute the same center mutation through its animation block before the outer class method itself throws.

R-132 conservatively records:
- animation may already have started / block side effects may already have occurred before the exception.

## Expected typed catch

Landing `0x39CFC`:
- compare discriminator against expected type;
- expected:
  - begin catch;
  - retain caught object;
  - load retained split view;
  - load precomputed center `d8/d9`;
  - directly send `setCenter:` at `0x39D28`;
  - release caught object;
  - end catch;
  - branch to `0x39CD0`.

At `0x39CD0`:
- release primary retained split view `x20`;
- release retained input argument `x19`;
- return.

Thus the exact expected-exception continuation is:
- swallow the UIView animation exception;
- directly attempt target-center application;
- preserve normal primary-view/input cleanup;
- return.

## Local animation-capture release bypass

Normal successful animation-call continuation starts at `0x39CC8`:
- load retained animation-block capture from stack;
- release that capture;
- then release the primary split-view retain and input argument.

Expected catch instead jumps to `0x39CD0`.

Therefore:
- the normal local release at `0x39CC8` of the retained animation-block capture is bypassed;
- primary split-view release and input release still occur.

This is recorded only as local control-flow lifetime metadata.

## Catch-internal direct-setter exception

The direct catch fallback:
- `0x39D1C..0x39D2C` -> landing `0x39D3C`, action 0.

If fallback `setCenter:` throws:
- setter side effect may already have partially/fully applied before the throw;
- landing preserves nested exception;
- calls `objc_end_catch`;
- resumes unwind at `0x39D44`.

There is no second local typed swallow and no fallback retry.

## Nonmatching type

At `0x39D00..0x39D04`:
- nonmatching discriminator branches to shared resume-unwind tail `0x39D44`.

## Promoted runtime contract

Added:
- `DDSlideAnimationExceptionSite`:
  - `UIViewAnimationCall`;
  - `CatchFallbackCenterSetter`;
  - `UnprotectedRange`.
- `DDSlideAnimationExceptionOutcome`.
- `DDResolveSlideAnimationExceptionOutcome(site)`.

For the protected UIView animation call:
- swallow expected exception;
- slide flag already set;
- 1-second follow-up already scheduled;
- target center already computed;
- animation may already have started;
- direct center fallback should be attempted;
- retained animation-capture release can be bypassed;
- primary retained split-view/input cleanup still runs;
- nonmatching type resumes unwind.

For catch fallback setter:
- slide flag/follow-up/target remain committed;
- direct setter may have applied before nested throw;
- active catch ends;
- nested exception propagates.

Unprotected:
- propagates.

## Explicit exclusions

R-132 does not:
- write `byte_163C98`;
- schedule dispatch work;
- invoke `3A004`;
- call UIView animation APIs;
- invoke `setCenter:`;
- mutate live views;
- alter real retain/release ownership;
- synthesize/catch exceptions;
- execute unwind runtime machinery.

## Verification

After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final project verification and `git diff --check` are run immediately before commit.

## Scout for next batch — 39954

Direct Mach-O `__unwind_info` enumeration shows the next earlier LSDA-bearing function below `39B70`:
- `39954 -> LSDA 0x11435C`.
- No LSDA-bearing function exists between `39954` and `39B70`.

Identity:
- recursive helper `sub_39954(view, depth)`;
- depth limit <= 4;
- makes a view transparent/nonopaque;
- recursively traverses subviews using fast enumeration.

Decoded LSDA call-site table:

1. `0x39954..0x399A0` -> no landing.
2. `0x399A0..0x399BC` -> `0x39AB4`, action 5.
3. `0x399BC..0x399C4` -> no landing.
4. `0x399C4..0x399D0` -> `0x39AB4`, action 5.
5. `0x399DC..0x39A00` -> `0x39AAC`, action 5.
6. `0x39A24..0x39A3C` -> `0x39AC0`, action 5.
7. `0x39A48..0x39A5C` -> `0x39ABC`, action 5.
8. `0x39A64..0x39A74` -> `0x39AB0`, action 0.
9. `0x39A74..0x39AD4` -> no landing.

Action-5 mapping:
- `0x399A0..0x399BC`: clearColor acquisition + `setBackgroundColor:`;
- `0x399C4..0x399D0`: `setOpaque:NO`;
- `0x399DC..0x39A00`: `subviews` + initial fast-enumeration batch;
- `0x39A24..0x39A3C`: enumeration-mutation check + recursive child call;
- `0x39A48..0x39A5C`: next fast-enumeration batch.

Stubs `0x39AAC`, `0x39AB4`, `0x39ABC` converge at common typed catch `0x39AC0`.

Expected type:
- begin catch;
- end catch;
- branch directly to `0x39A6C` final input-view release and return.

Consequences to map in R-133:
- already-applied transparency writes are not rolled back;
- remaining recursion/sibling traversal is abandoned;
- normal retained enumerator/subviews-array cleanup at `0x39A64` can be bypassed depending on site;
- an exception propagated from a recursive child call can be caught by the parent's protected recursion range and terminate the parent traversal;
- action-0 cleanup range `0x39A64..0x39A74` resumes unwind instead of local swallow.

R-133 should distinguish:
- background-color setter possible side effect;
- opaque setter definite prior background write + possible opaque write;
- subviews/enumerator retained-object timing;
- recursive child propagation and parent swallow/abort semantics.

Known unresolved remain:
- `73E8` / `80D0` bounds;
- full `7E908` blacklist/numerics;
- jailbroken-device smoke testing.
