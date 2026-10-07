# LOG/session-118.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-117 commit ecfc20c; complete R-117 by promoting exact data-only `3E670` aux settings-preparation exception behavior from LSDA/raw ARM64. Per user workflow, commit locally but do not push._

## R-117 — evidence source

Reviewed:
- `3E670.c`;
- raw ARM64 for `3E670` from the first arm64 FAT slice;
- Mach-O LSDA `0x114880`;
- existing aux settings preparation/state-machine contracts around `3E670`, `3EA0C`, and `3EB9C`.

The first arm64 FAT slice begins at file offset `0x4000`.

Mach-O maps:
- `3E670 -> LSDA 0x114880`.

Decoded call-site table:
- `0x3E670..0x3E6CC` -> no landing pad;
- `0x3E6CC..0x3E6D8` -> landing `0x3E990`, action 7;
- `0x3E728..0x3E744` -> landing `0x3E988`, action 5;
- `0x3E76C..0x3E788` -> landing `0x3E984`, action 5;
- `0x3E788..0x3E7B8` -> no landing pad;
- `0x3E7B8..0x3E884` -> landing `0x3E98C`, action 5;
- `0x3E884..0x3E9A8` -> no landing pad.

Small landing stubs:
- `0x3E984 -> 0x3E990`;
- `0x3E988 -> 0x3E990`;
- `0x3E98C -> 0x3E990`.

All protected sites therefore share one typed catch continuation.

## Common typed catch `0x3E990`

Raw ARM64:
- `0x3E990`: compare catch discriminator with expected value 1;
- expected value:
  - begin catch at `0x3E998`;
  - end catch at `0x3E99C`;
  - branch to `0x3E944`;
- nonmatching value:
  - branch to `0x3E9A4`;
  - resume unwind.

`0x3E944` is the final outer cleanup path for the three retained function arguments:
- release `x21`;
- release `x20`;
- release `x19`;
- restore registers/return.

Thus every expected protected exception:
- is swallowed locally;
- skips all remaining aux settings preparation/scheduling work;
- enters final outer cleanup;
- performs no retry or alternate preparation path.

## Site 1 — initial aux/helper gate

Protected range:
- `0x3E6CC..0x3E6D8` -> common catch `0x3E990`.

Raw ARM64 covers:
- configured aux-bundle/string length helper call;
- subsequent `3E534` gate helper call.

Expected exception here:
- swallows;
- skips desired/current settings comparison and all private update preparation;
- proceeds directly to outer cleanup.

## Site 2 — current frame read

Protected range:
- `0x3E728..0x3E744` -> landing `0x3E988` -> common catch.

Raw ARM64 covers:
- `respondsToSelector:frame`;
- optional `frame` send.

Expected exception:
- swallows;
- skips the current orientation read/comparison;
- skips all later private update preparation/scheduling;
- enters outer cleanup.

No synthetic frame fallback is promoted for the exception case because the original catch does not rejoin at the normal CGRectZero fallback; it exits the preparation function.

## Site 3 — current orientation read

Protected range:
- `0x3E76C..0x3E788` -> landing `0x3E984` -> common catch.

Raw ARM64 covers:
- `respondsToSelector:interfaceOrientation`;
- optional `interfaceOrientation` send.

Expected exception:
- swallows;
- skips current-settings equality evaluation and all later update preparation;
- enters outer cleanup.

## Site 4 — late update preparation

Protected range:
- `0x3E7B8..0x3E884` -> landing `0x3E98C` -> common catch.

This range begins after the function has already retained a working object copy:
- `0x3E7A8`: move input object to x0;
- `0x3E7AC`: retain;
- `0x3E7B0`: store retained result in `x22`.

The protected work then covers:
- repeated configured aux-bundle length check;
- geometry/update gate including `3E9A8`;
- reentrancy/in-flight/attempt-limit gates around the surrounding logic;
- `respondsToSelector:updateSettingsWithBlock:`;
- runtime class lookup;
- `class_getInstanceMethod`;
- method type-encoding fetch ending at `0x3E880`.

Normal non-exception cleanup of this retained working object occurs at:
- `0x3E93C`: move `x22` to x0;
- `0x3E940`: release;
- then fall into final outer cleanup at `0x3E944`.

The expected catch instead jumps directly from `0x3E9A0` to `0x3E944`.

Therefore for a late protected exception:
- the normal `x22` release at `0x3E93C..0x3E940` is bypassed;
- final outer cleanup still releases the three original retained arguments;
- no later capability/signature/dispatch work runs.

R-117 records this only as control-flow/lifetime metadata. It does not intentionally retain, leak, or release a real runtime object.

## Nonmatching catch discriminator

Every protected site funnels to the same common catch. A nonmatching discriminator branches to `0x3E9A4` and resumes unwind.

Promoted metadata:
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

No foreign/nonmatching exception is synthesized, and no unwind machinery is executed by the reconstruction.

## Promoted runtime contract

Added:
- `DDAuxSettingsPreparationExceptionSite` with:
  - `InitialAuxGate`;
  - `CurrentFrameRead`;
  - `CurrentOrientationRead`;
  - `LateUpdatePreparation`;
- `DDAuxSettingsPreparationExceptionOutcome`;
- `DDResolveAuxSettingsPreparationExceptionOutcome(site)`.

For all four valid sites:
- `shouldSwallowException = YES`;
- `shouldSkipRemainingPreparation = YES`;
- `shouldContinueFinalOuterCleanup = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

Late site only:
- `retainedWorkingObjectReleaseWouldBeBypassed = YES`.

Unknown/None site returns an all-false outcome.

## Explicit exclusions

R-117 does not:
- invoke private selectors such as `frame`, `interfaceOrientation`, or `updateSettingsWithBlock:`;
- execute runtime class/method/type-encoding APIs;
- call `3E9A8` as part of private preparation;
- dispatch or execute blocks;
- retain/release live private working objects;
- synthesize/catch Objective-C or foreign exceptions;
- execute begin-catch/end-catch/resume-unwind runtime APIs;
- mutate aux counters, attempt counts, in-flight/reentrancy/applied flags, geometry, or other globals.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — `3E33C`

Mach-O maps:
- `3E33C -> LSDA 0x114860`.

Decoded call-site table:
- `0x3E33C..0x3E3C8` -> no landing pad;
- `0x3E3C8..0x3E3EC` -> landing `0x3E3F4`, action 5;
- `0x3E3EC..0x3E428` -> no landing pad.

### Unprotected `sceneIfExists` path

Raw ARM64 before `0x3E3C8` includes:
- `NSSelectorFromString("sceneIfExists")`;
- `respondsToSelector:`;
- `object_getClass`;
- `class_getInstanceMethod`;
- `method_getReturnType` and return-type validation;
- when valid, `sceneIfExists` selector send and retain-autoreleased handling.

None of those calls are inside a local LSDA protected range for `3E33C`.

Therefore exceptions in this primary `sceneIfExists` path propagate out of the helper rather than using the local catch.

### Protected fallback `scene` path

Protected range `0x3E3C8..0x3E3EC` covers:
- `respondsToSelector:scene`;
- optional `scene` send;
- retain-autoreleased handling.

Landing `0x3E3F4`:
- compare catch discriminator with expected value 1;
- expected type begin/end-catches;
- fall through to `0x3E404`;
- set resolved scene result to nil;
- release retained input and return nil.

Nonmatching type:
- branch `0x3E424`;
- resume unwind.

R-118 can therefore model the complete helper exception distinction compactly:
- primary `sceneIfExists` path exception -> propagate/resume unwind;
- fallback `scene` protected exception -> swallow + nil result;
- nonmatching fallback catch type -> resume unwind.

## Next

R-118 after compiler green:
- promote exact `3E33C` primary-path propagation vs fallback-scene typed-catch nil-result behavior;
- keep selector construction/invocation, runtime method-signature inspection, real scene object lifetime effects, exception synthesis, and unwind execution excluded.
