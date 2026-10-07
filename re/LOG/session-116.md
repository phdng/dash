# LOG/session-116.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-115 commit f5fdd32; complete R-115 by promoting exact data-only `3EB9C` aux settings-mutation exception behavior from LSDA/raw ARM64. Per user workflow, commit locally but do not push._

## R-115 — evidence source

Reviewed:
- `3EB9C.c`;
- raw ARM64 for `3EB9C` from the first arm64 FAT slice;
- Mach-O LSDA `0x1148D8`;
- existing aux settings state-machine contracts around `3EA0C/3E670`.

The first arm64 FAT slice begins at file offset `0x4000`.

Mach-O maps:
- `3EB9C -> LSDA 0x1148D8`.

Decoded call-site table:
- `0x3EB9C..0x3EBC8` -> no landing pad;
- `0x3EBC8..0x3EC34` -> landing `0x3EC58`, action 1;
- `0x3EC34..0x3EC64` -> no landing pad.

This function therefore has one protected region spanning both frame and orientation mutation work, followed by one unconditional local catch-all continuation.

## Normal mutation sequence

After retaining the supplied settings object, raw ARM64 performs the following when non-nil.

### Frame phase
- load `setFrame:` selector;
- `respondsToSelector:setFrame:`;
- when supported, send `setFrame:{0,0,width,height}` using captured width/height;
- only after the setter returns successfully, write `1` into the frame-applied byref at `0x3EBF0..0x3EBFC`.

### Orientation phase
- read captured desired orientation;
- skip orientation when desired orientation is zero;
- obtain runtime class for the settings object;
- call `3ECD0` to validate the `setInterfaceOrientation:` q/Q integer-setter signature;
- when supported, send `setInterfaceOrientation:`;
- only after the setter returns successfully, write `1` into the orientation-applied byref beginning at `0x3EC34`.

The orientation-applied write begins exactly at the end of the LSDA protected range.

## Catch-all landing `0x3EC58`

Raw ARM64:
- `0x3EC58`: begin catch;
- `0x3EC5C`: end catch;
- `0x3EC60`: branch to `0x3EC44`;
- `0x3EC44`: release retained settings object and return.

There is no catch-discriminator comparison at this landing. Therefore R-115 does not expose a nonmatching-catch branch for this helper.

Exact common continuation for every protected exception:
- swallow locally;
- skip all remaining mutation;
- release retained settings and return normally;
- no retry;
- no reason probe;
- no counter/global mutation.

## Frame-path exception timing

Frame-path protected calls are:
- `respondsToSelector:setFrame:`;
- optional `setFrame:` send.

The frame-applied byref write starts only after those calls return successfully.

Therefore if either protected frame call throws:
- the local catch swallows;
- the frame-applied write has not occurred as part of this invocation;
- orientation processing is skipped because catch jumps directly to cleanup;
- the orientation-applied write is also skipped.

This is represented by the frame exception site with:
- `frameAppliedWriteCouldHaveOccurredBeforeException = NO`;
- `orientationAppliedWriteWouldBeSkipped = YES`.

The outcome deliberately does not claim that an externally preexisting byref value becomes zero; the reconstruction helper performs no byref mutation.

## Orientation-path exception timing

Orientation-path protected calls/work are after the frame phase:
- runtime class lookup;
- `3ECD0` signature validation;
- optional `setInterfaceOrientation:` send.

By the time an orientation-path exception can occur, the earlier frame phase may already have successfully completed and written `1` to the frame-applied byref.

The catch does not restore or clear that earlier state.

Therefore:
- `frameAppliedWriteCouldHaveOccurredBeforeException = YES` for the orientation site;
- any already-recorded frame-applied state is preserved by the catch;
- the orientation-applied write at `0x3EC34` is not reached when the protected orientation setter throws;
- all remaining mutation is skipped and cleanup runs.

The `couldHaveOccurred` wording is intentional: if `setFrame:` was unsupported, the prior frame write did not occur. R-115 records ordering/persistence without inventing whether the normal frame phase actually succeeded.

## Promoted runtime contract

Added:
- `DDAuxSettingsMutationExceptionSite` with `FramePath` and `OrientationPath`;
- `DDAuxSettingsMutationExceptionOutcome`;
- `DDResolveAuxSettingsMutationExceptionOutcome(site)`.

Common fields for both sites:
- `shouldSwallowException = YES`;
- `shouldSkipRemainingMutation = YES`;
- `shouldContinueCleanupAfterCatch = YES`;
- `orientationAppliedWriteWouldBeSkipped = YES`.

Site-specific field:
- frame path: `frameAppliedWriteCouldHaveOccurredBeforeException = NO`;
- orientation path: `frameAppliedWriteCouldHaveOccurredBeforeException = YES`.

Unknown/None site returns an all-false outcome.

## Relationship to aux apply state

The original outer executor `3EA0C` decides whether the private `updateSettingsWithBlock:` invocation itself returned or threw. Its `applied` global transition is separate from the two byref flags captured by the `3EB9C` mutation block.

R-115 therefore does not change:
- `DDBeginAuxSceneSettingsApply`;
- `DDCompleteAuxSceneSettingsApply`;
- attempt count/budget state;
- applied/reentrant globals.

Those outer-executor exception semantics belong to `3EA0C` and are scoped to R-116.

## Explicit exclusions

R-115 does not:
- synthesize or catch Objective-C/foreign exceptions;
- execute begin-catch/end-catch runtime APIs;
- invoke `respondsToSelector:setFrame:`;
- invoke `setFrame:`;
- perform runtime class lookup for settings;
- invoke `3ECD0`;
- invoke `setInterfaceOrientation:`;
- write either byref flag;
- mutate settings, aux globals, counters, budgets, or reentrancy state.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — `3EA0C`

Mach-O maps:
- `3EA0C -> LSDA 0x1148B8`.

Decoded call-site table:
- `0x3EA0C..0x3EADC` -> no landing pad;
- `0x3EADC..0x3EAEC` -> landing `0x3EB4C`, action 5;
- `0x3EAEC..0x3EB9C` -> no landing pad.

The only protected call is the private executor send:
- receiver from block capture `+0x20`;
- selector from block capture `+0x48`;
- retained mutation block argument;
- `objc_msgSend(receiver, selector, block)` at `0x3EAE8`.

Before the protected send, matching generation has already:
- cleared `byte_163E81` in-flight state;
- rejected an already-reentrant executor;
- set `byte_163E9D = 1` reentrancy state;
- constructed two byref flags and retained block captures.

### Normal return path

After a successful private executor return:
- release the retained argument block copy;
- set `byte_163DF8 = 1` (settings applied);
- decrement `dword_162F14` when current >=1;
- release the retained outer mutation block;
- clear `byte_163E9D = 0`;
- dispose both byref captures;
- return.

### Expected typed catch `0x3EB4C`

Raw ARM64:
- save exception object;
- compare discriminator with expected value 1;
- begin catch;
- decrement `dword_162F14` only when current >=1;
- end catch;
- branch to `0x3EB18`;
- clear `byte_163E9D = 0`;
- dispose both byref captures;
- return.

Notably, the expected catch skips the normal applied-state write at `0x3EAF8`.

Therefore expected private-executor exception semantics are:
- swallow;
- do **not** mark settings applied;
- decrement the failure/budget counter only when positive/current >=1;
- clear reentrancy;
- dispose both byref captures;
- return normally.

### Nonmatching catch discriminator

For a nonmatching type:
- branch to `0x3EB7C`;
- dispose both byref captures;
- pass the saved exception to resume-unwind at `0x3EB98`.

This path does **not** pass through `0x3EB18`, so it does not clear `byte_163E9D`.

It also skips the expected-catch decrement block, so `dword_162F14` is not decremented on the nonmatching path.

This mirrors the nearby `3F7C8` subtlety where nonmatching unwind cleanup does not necessarily restore reentrancy state.

## Next

R-116 after compiler green:
- promote exact `3EA0C` expected private-executor catch outcome: swallow + no applied mark + bounded counter decrement + reentrancy clear + capture disposal;
- expose nonmatching type as capture-dispose + resume-unwind without reentrancy clear/counter decrement;
- keep private executor/block invocation, real capture lifetime changes, global mutation, exception synthesis, and unwind execution excluded.
