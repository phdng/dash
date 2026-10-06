# LOG/session-108.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-107 commit 68714ab; complete R-107 by promoting exact data-only `3F990` mutation exception continuations from LSDA/raw ARM64. Per user workflow, commit locally but do not push._

## R-107 — evidence source

Reviewed:
- `3F990.c`;
- raw ARM64 for `3F990` from the first arm64 FAT slice;
- Mach-O LSDA index and `__gcc_except_tab` mapping;
- existing R-090 `DDResolveFBSSceneSettingsMutationPlan` normal-path contract.

The first arm64 FAT slice begins at file offset `0x4000`.

Mach-O maps:
- `3F990 -> LSDA 0x1149D4`.

Decoded call-site table:
- `0x3F990..0x3F9BC` -> no landing pad;
- `0x3F9BC..0x3F9E4` -> landing `0x3FA78`, action 7;
- `0x3F9EC..0x3FA04` -> landing `0x3FA64`, action 7;
- `0x3FA08..0x3FA30` -> landing `0x3FA60`, action 5;
- `0x3FA30..0x3FA90` -> no landing pad.

## Frame path — swallow, then continue orientation stage

Protected range `0x3F9BC..0x3F9E4` covers:
- `respondsToSelector:setFrame:`;
- optional private/public `setFrame:` send with `{0,0,targetWidth,targetHeight}`.

Landing `0x3FA78`:
- compares the catch discriminator with the expected value;
- expected type begins and ends catch;
- branches to `0x3F9E4`.

`0x3F9E4` is not cleanup. It is the beginning of the orientation path (`desiredOrientation` check, runtime setter-signature validation, current-orientation read, optional orientation set).

Therefore an expected frame-path exception:
- is swallowed;
- does not retry `setFrame:`;
- skips the remaining frame operation;
- still evaluates the orientation mutation path.

Promoted outcome:
- `shouldSwallowException = YES`;
- `shouldContinueOrientationAfterCatch = YES`.

If the landing discriminator is not the expected catch type, `0x3FA78` branches to `0x3FA8C`, which resumes unwind.

## Orientation setter-signature path — swallow, cleanup/return

Protected range `0x3F9EC..0x3FA04` covers:
- runtime class lookup for the settings object;
- `3ECD0` validation of the `setInterfaceOrientation:` method signature.

Landing `0x3FA64`:
- verifies expected catch type;
- expected type begins/ends catch;
- branches to `0x3FA4C`, final settings-object release/return cleanup.

Therefore an expected exception in the setter-signature path:
- is swallowed;
- orientation mutation is abandoned;
- function returns through final cleanup;
- no orientation-change by-reference fields are recorded.

## Current-orientation / setter path — same cleanup catch

Protected range `0x3FA08..0x3FA30` covers:
- `3FA90` current-orientation read;
- comparison against desired orientation;
- optional `setInterfaceOrientation:` send.

Landing `0x3FA60` is only a branch to the same common catch at `0x3FA64`.

Therefore an expected exception in the current-orientation/setter path:
- is swallowed;
- skips the by-reference writes at `0x3FA30..0x3FA48` that would record previous orientation and orientation-changed=1;
- goes directly to final cleanup/return.

Promoted outcome:
- `shouldSwallowException = YES`;
- `shouldContinueCleanupAfterCatch = YES`.

As with the frame catch, a nonmatching catch discriminator branches to `0x3FA8C` and resumes unwind.

## By-reference mutation fidelity

Normal-path by-reference writes are outside the protected orientation range:
- `0x3FA30..0x3FA38` records previous/current orientation;
- `0x3FA3C..0x3FA48` records the orientation-changed flag.

Because the protected range ends at `0x3FA30`, an exception from `3FA90` or `setInterfaceOrientation:` reaches the catch before either by-reference write runs.

R-107 does not mutate these captures; it only records the cleanup continuation.

## Promoted runtime contract

Added:
- `DDFBSSceneSettingsMutationExceptionSite`
  - None
  - FramePath
  - OrientationPath
- `DDFBSSceneSettingsMutationExceptionOutcome`
- `DDResolveFBSSceneSettingsMutationExceptionOutcome(site)`.

### FramePath
- `shouldSwallowException = YES`;
- `shouldContinueOrientationAfterCatch = YES`;
- `shouldContinueCleanupAfterCatch = NO`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

### OrientationPath
- `shouldSwallowException = YES`;
- `shouldContinueOrientationAfterCatch = NO`;
- `shouldContinueCleanupAfterCatch = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

## Explicit exclusions

R-107 does not:
- synthesize or catch exceptions;
- execute landing-pad runtime APIs;
- perform Objective-C class/method lookup;
- invoke `respondsToSelector:setFrame:`;
- invoke `setFrame:`;
- invoke `3ECD0`;
- invoke `3FA90`;
- invoke `setInterfaceOrientation:`;
- mutate settings objects;
- mutate the by-reference previous-orientation or orientation-changed captures;
- intercept/resume unwind.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — `3FA90`

Mach-O maps:
- `3FA90 -> LSDA 0x114A00`.

Decoded call-site table:
- `0x3FA90..0x3FAB0` -> no landing pad;
- `0x3FAB0..0x3FACC` -> landing `0x3FAD4`, action 1;
- `0x3FACC..0x3FAF8` -> no landing pad.

Raw ARM64 shows the protected range covers exactly:
- `respondsToSelector:interfaceOrientation`;
- conditional `interfaceOrientation` selector send.

Expected catch at `0x3FAD4`:
- begins/ends catch;
- falls to `0x3FADC`;
- sets return orientation to zero;
- releases the retained object and returns.

Thus the next evidence-safe contract is:
- expected interface-orientation exception -> swallow + forced zero return;
- no selector retry or reason probe;
- nonmatching exception/catch behavior should be confirmed and represented only as unwind metadata.

## Next

R-108 after compiler green:
- promote exact `3FA90` swallow/forced-zero/unwind outcome from LSDA `0x114A00` + raw ARM64;
- keep selector invocation, exception synthesis, object mutation, and unwind execution excluded.
