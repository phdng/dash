# LOG/session-134.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-133 commit `0cdbf25`; decode and promote exact data-only `39954` recursive view-transparency exception behavior, verify, and commit locally without pushing._

## Start state

- Branch: `chore/reconstruction-build-ci`.
- HEAD: `0cdbf25`.
- Working tree: clean.
- Branch synchronized with origin at session start.
- User explicitly confirmed session-133 macOS CI/compiler GREEN.

## Target

- Function: `sub_39954(view, depth)`.
- LSDA: `0x11435C`.
- Role: recursively make a view tree transparent/nonopaque to depth <= 4.

Reviewed:
- `decompile/39954.c`;
- raw ARM64 `0x39954..0x39AD4`;
- Mach-O LSDA bytes at `0x11435C`.

## Normal behavior

When input view is non-null and depth <= 4:

1. retain input view;
2. obtain `+[UIColor clearColor]`;
3. `setBackgroundColor:clearColor`;
4. release retained clearColor;
5. `setOpaque:NO`;
6. fetch/retain `subviews`;
7. fast-enumerate children;
8. recursively call `39954(child, depth+1)`;
9. release retained subviews array;
10. release retained input view.

Depth > 4 or nil input skips transparency/traversal and proceeds to final input cleanup.

## Exact LSDA call-site table

Decoded 9 entries:

1. `0x39954..0x399A0` -> no landing.
2. `0x399A0..0x399BC` -> landing `0x39AB4`, action 5.
3. `0x399BC..0x399C4` -> no landing.
4. `0x399C4..0x399D0` -> landing `0x39AB4`, action 5.
5. `0x399DC..0x39A00` -> landing `0x39AAC`, action 5.
6. `0x39A24..0x39A3C` -> landing `0x39AC0`, action 5.
7. `0x39A48..0x39A5C` -> landing `0x39ABC`, action 5.
8. `0x39A64..0x39A74` -> landing `0x39AB0`, action 0.
9. `0x39A74..0x39AD4` -> no landing.

Landing aliases:
- `0x39AAC -> 0x39AC0`;
- `0x39ABC -> 0x39AC0`;
- `0x39AB4` routes action-selector 1 into `0x39AC0`;
- `0x39AB0` resumes unwind.

Common expected typed catch `0x39AC0`:
- compare discriminator with expected type;
- begin catch;
- end catch;
- branch directly to `0x39A6C`.

At `0x39A6C`:
- release retained input view;
- return.

Thus expected typed exceptions abort all remaining traversal but preserve final input cleanup.

## Protected site 1 — background-color setup

`0x399A0..0x399BC` covers:
- `+[UIColor clearColor]`;
- retain-autoreleased clearColor;
- `setBackgroundColor:`.

If the setter itself throws:
- background color may already have changed before the exception.

The normal clearColor release is immediately after the protected range at `0x399BC`.

Expected catch jumps to `0x39A6C`, so:
- retained clearColor release can be bypassed;
- opaque setter is skipped;
- all subview traversal is skipped;
- input view is still released.

R-133 records background write as possible, not definite, because exceptions earlier in the protected range can occur before the setter side effect.

## Protected site 2 — opaque setter

`0x399C4..0x399D0` covers:
- `setOpaque:NO`.

This site is reached only after:
- clearColor/background setter returned successfully;
- clearColor retained object was released normally.

Therefore:
- background transparency is definitely applied before this protected call;
- opaque state may already have changed before a setter exception.

Expected catch aborts subview traversal and continues final input cleanup.

## Protected site 3 — subviews / initial enumeration

`0x399DC..0x39A00` covers:
- `subviews`;
- retain-autoreleased subviews array;
- initial `countByEnumeratingWithState:objects:count:`.

This site is reached only after:
- background setter completed;
- opaque setter completed.

Thus both parent-view transparency writes are definitely applied.

If the subviews array was already retained before the throw:
- its normal release at `0x39A64` is bypassed by the catch jump.

Expected catch:
- aborts child traversal before/within the first batch;
- final-releases the input view.

## Protected site 4 — enumeration mutation / recursive child

`0x39A24..0x39A3C` covers:
- `objc_enumerationMutation` if mutation is detected;
- loading current child;
- recursive `39954(child, depth+1)`.

At this point:
- background and opaque writes on the current parent definitely completed;
- the subviews array is retained.

A matching exception escaping the recursive child call can reach the parent LSDA protected call site.

The parent then:
- swallows the matching exception;
- aborts all remaining sibling traversal;
- skips normal subviews-array release;
- final-releases only the current input view.

Consequently:
- descendants may already have been partially made transparent before the child exception escaped;
- parent does not roll those writes back;
- parent does not continue with later siblings.

R-133 models this explicitly as possible child partial mutation plus parent swallow/abort semantics.

## Protected site 5 — next enumeration batch

`0x39A48..0x39A5C` covers:
- another `countByEnumeratingWithState:objects:count:` call.

This site can only be reached after:
- one previous non-empty enumeration batch has completed fully.

Therefore:
- background + opaque writes are definitely applied;
- at least one batch of children has already been processed;
- subviews array is retained;
- some descendants may already have been recursively mutated.

Expected catch:
- swallows;
- aborts later batches/siblings;
- can bypass subviews-array release;
- final-releases the input view.

## Action-0 cleanup range

`0x39A64..0x39A74` covers:
- release retained subviews array;
- release retained input view.

Its LSDA action is 0 with landing `0x39AB0`:
- no local typed swallow;
- resume unwind.

R-133 exposes this only as cleanup-unwind propagation metadata.

## Unprotected ranges

All no-landing ranges propagate normally.

## Promoted runtime contract

Added:
- `DDRecursiveTransparencyExceptionSite`:
  - `BackgroundColorSetup`;
  - `OpaqueSetter`;
  - `InitialSubviewsEnumeration`;
  - `RecursiveChildStep`;
  - `NextEnumerationBatch`;
  - `CleanupUnwind`;
  - `UnprotectedRange`.
- `DDRecursiveTransparencyExceptionOutcome`.
- `DDResolveRecursiveTransparencyExceptionOutcome(site)`.

All five typed sites:
- swallow expected exception;
- abort remaining traversal;
- continue final input cleanup;
- nonmatching catch type resumes unwind.

Site-sensitive metadata:
- background setup:
  - background may have applied;
  - retained clearColor release may be bypassed.
- opaque setter:
  - background definitely applied;
  - opaque may have applied.
- initial enumeration:
  - background + opaque definitely applied;
  - retained subviews-array release may be bypassed.
- recursive child step:
  - same definite writes;
  - subviews-array release may be bypassed;
  - child exception may be swallowed by parent;
  - child/descendant mutations may already have occurred.
- next enumeration batch:
  - same definite writes;
  - subviews-array release may be bypassed;
  - a prior enumeration batch definitely completed.

Cleanup action-0:
- resume unwind;
- propagate.

Unprotected:
- propagate.

## Explicit exclusions

R-133 does not:
- call `+[UIColor clearColor]`;
- invoke `setBackgroundColor:` or `setOpaque:`;
- fetch or enumerate live subviews;
- recurse into live views;
- mutate live transparency;
- alter real retain/release ownership;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification

After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final project verification and `git diff --check` are run immediately before commit.

## Scout for next batch — 39884

Direct Mach-O `__unwind_info` enumeration shows the next earlier LSDA-bearing function:
- `39884 -> LSDA 0x114330`.
- No LSDA-bearing function exists between `39884` and `39954`.

Identity:
- `sub_39884`;
- top-level transparency wrapper for:
  - host view `qword_163C78`;
  - split view `qword_163C68`;
  - recursive root `qword_163C70`.

Decoded LSDA call-site entries:

1. `0x39884..0x398A8` -> no landing.
2. `0x398A8..0x398C4` -> `0x3993C`, action 1.
3. `0x398C4..0x398D0` -> no landing.
4. `0x398D0..0x39904` -> `0x3993C`, action 1.
5. `0x39904..0x39910` -> no landing.
6. `0x39910..0x3992C` -> `0x3993C`, action 1.

Landing `0x3993C`:
- `objc_begin_catch`;
- function epilogue;
- tail to `objc_end_catch`.

There is no discriminator test: these are local catch-all ranges.

Range mapping:

### 0x398A8..0x398C4
- host clearColor acquisition/retain;
- host `setBackgroundColor:`.

Catch-all return means:
- host background may already have changed;
- host opaque setter is skipped;
- split transparency and recursive root traversal are skipped.

### 0x398D0..0x39904
- host `setOpaque:NO`;
- split clearColor acquisition/retain;
- split `setBackgroundColor:`.

If host opaque throws:
- host background definitely applied;
- host opaque may have applied;
- split work not reached.

If split background path throws:
- host background + opaque definitely applied;
- split background may have applied;
- split opaque + root recursion are skipped.

This broad protected range therefore needs sub-site timing inside one LSDA range.

### 0x39910..0x3992C
- split `setOpaque:NO`;
- optional recursive `39954(qword_163C70,0)`.

If split opaque throws:
- host transparency is complete;
- split background is definitely applied;
- split opaque may have applied;
- root recursion not reached.

If recursive `39954` throws:
- host + split background/opaque writes are all definitely complete;
- root subtree may have been partially mutated before propagation;
- catch-all swallows and returns.

R-134 should promote site-aware catch-all metadata rather than only a single generic outcome.

Known unresolved remain:
- `73E8` / `80D0` bounds;
- full `7E908` blacklist/numerics;
- jailbroken-device smoke testing.
