# LOG/session-117.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-116 commit 335f97d; complete R-116 by promoting exact data-only `3EA0C` aux private-executor exception behavior from LSDA/raw ARM64. Per user workflow, commit locally but do not push._

## R-116 — evidence source

Reviewed:
- `3EA0C.c`;
- raw ARM64 for `3EA0C` from the first arm64 FAT slice;
- Mach-O LSDA `0x1148B8`;
- existing aux settings state-machine and `3EB9C` mutation exception descriptors.

The first arm64 FAT slice begins at file offset `0x4000`.

Mach-O maps:
- `3EA0C -> LSDA 0x1148B8`.

Decoded call-site table:
- `0x3EA0C..0x3EADC` -> no landing pad;
- `0x3EADC..0x3EAEC` -> landing `0x3EB4C`, action 5;
- `0x3EAEC..0x3EB9C` -> no landing pad.

The only protected operation is the private executor send at `0x3EAE8`:
- receiver from captured scene/settings executor object;
- captured `updateSettingsWithBlock:` selector;
- retained mutation block argument.

## State already established before the protected send

Before entering `0x3EADC..0x3EAEC`, matching generation/reentrancy admission has already:
- cleared the in-flight byte;
- rejected an already-reentrant invocation;
- set reentrancy active;
- constructed two byref capture cells;
- retained the mutation block and a copy for the private executor send.

Therefore catch behavior must be interpreted relative to a state where reentrancy is already active.

## Normal successful return

After the private send returns normally, raw ARM64 performs:
- release of the retained executor argument block copy;
- `byte_163DF8 = 1` settings-applied mark at `0x3EAF4..0x3EAF8`;
- decrement `dword_162F14` only when its signed current value is >=1;
- release outer retained mutation block;
- clear reentrancy at `0x3EB18`;
- dispose both byref captures;
- return.

The applied write is outside and immediately after the protected range, so a throwing private send never reaches it.

## Expected typed catch `0x3EB4C`

Raw ARM64:
- save exception object;
- compare discriminator with expected value 1;
- begin catch;
- read `dword_162F14`;
- decrement/store only when current value is positive;
- end catch;
- branch to `0x3EB18`;
- clear reentrancy;
- dispose both byref captures;
- return.

Exact expected-catch semantics:
- swallow locally;
- do not mark settings applied;
- decrement the failure/budget counter only when positive;
- preserve a zero/negative counter unchanged;
- clear reentrancy;
- dispose both byref captures;
- no retry of the private executor.

The reconstruction does not execute any of these side effects; it reports only their next-state metadata.

## Nonmatching catch discriminator

For a nonmatching catch type:
- branch from `0x3EB54` to `0x3EB7C`;
- dispose the first byref capture;
- dispose the second byref capture;
- pass the saved exception to resume-unwind at `0x3EB98`.

This path bypasses:
- the expected-catch `dword_162F14` decrement;
- `0x3EB18` reentrancy clear;
- the normal settings-applied write.

Therefore nonmatching metadata is:
- resume unwind = YES;
- dispose captures = YES;
- clear reentrancy = NO;
- decrement failure counter = NO.

This preserves the subtle raw-binary behavior that reentrancy would remain set while unwinding from a nonmatching type.

## Promoted runtime contract

Added:
- `DDAuxSettingsExecutorExceptionOutcome`;
- `DDResolveAuxSettingsExecutorExceptionOutcome(currentFailureCounter)`.

Expected typed-path fields:
- `shouldSwallowException = YES`;
- `settingsAppliedWriteWouldBeSkipped = YES`;
- `shouldDecrementFailureCounter = currentFailureCounter > 0`;
- `nextFailureCounter = currentFailureCounter - 1` only when positive, otherwise unchanged;
- `shouldClearReentrantState = YES`;
- `shouldDisposeByrefCaptures = YES`.

Nonmatching fields:
- `nonmatchingCatchTypeWouldResumeUnwind = YES`;
- `nonmatchingCatchTypeWouldClearReentrantState = NO`;
- `nonmatchingCatchTypeWouldDecrementFailureCounter = NO`;
- `nonmatchingCatchTypeWouldDisposeByrefCaptures = YES`.

The implementation uses explicit field assignments rather than positional initialization so the expected-vs-nonmatching semantics remain auditable.

## Relationship to R-115

`3EA0C` owns the outer private executor send and outer applied/reentrancy/capture lifetime.

The block passed to that executor invokes `3EB9C`, whose own local catch-all may swallow frame/orientation setter exceptions and return normally. If `3EB9C` catches internally, the outer private executor call can still return normally and the normal `3EA0C` applied path remains eligible.

R-116 only describes exceptions escaping the private executor send itself into `3EA0C`'s LSDA range.

## Explicit exclusions

R-116 does not:
- invoke `updateSettingsWithBlock:`;
- execute or retain real mutation blocks/captures;
- synthesize or catch Objective-C/foreign exceptions;
- execute begin-catch/end-catch/resume-unwind runtime APIs;
- write settings-applied/reentrancy globals;
- decrement real counters;
- dispose real byref captures.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

An intermediate verifier check initially expected an explicit `outcome.settingsAppliedWriteWouldBeSkipped` assignment while the first implementation used a positional initializer. The resolver was changed to explicit field assignments and the verifier then passed; no runtime semantic change was needed.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — `3E670`

Mach-O maps:
- `3E670 -> LSDA 0x114880`.

Decoded protected ranges:
- `0x3E6CC..0x3E6D8` -> landing `0x3E990`, action 7;
- `0x3E728..0x3E744` -> landing `0x3E988`, action 5;
- `0x3E76C..0x3E788` -> landing `0x3E984`, action 5;
- `0x3E7B8..0x3E884` -> landing `0x3E98C`, action 5.

Small landing stubs `0x3E984`, `0x3E988`, and `0x3E98C` branch to common catch `0x3E990`.

Common typed catch:
- compare discriminator with expected value 1;
- expected type begin/end-catches then branches to `0x3E944` final outer cleanup;
- nonmatching type branches to `0x3E9A4` and resumes unwind.

### Protected stage 1 — initial aux gates
`0x3E6CC..0x3E6D8` covers the configured aux-bundle length/helper gate including the call to `3E534`.

Expected exception skips all remaining current-settings/update preparation and goes to final cleanup.

### Protected stage 2 — current frame read
`0x3E728..0x3E744` covers `frame` capability and optional frame read from current settings.

Expected exception skips orientation comparison and all later update scheduling/preparation.

### Protected stage 3 — current orientation read
`0x3E76C..0x3E788` covers `interfaceOrientation` capability and optional read.

Expected exception skips comparison and all later update preparation.

### Protected stage 4 — late update preparation
`0x3E7B8..0x3E884` spans:
- repeated configured aux-bundle length check;
- geometry/update-enabled gate including `3E9A8`;
- updateSettingsWithBlock: capability check;
- runtime class/method lookup;
- method type-encoding fetch through `0x3E880`.

The retained working object copy `x22` is created at `0x3E7AC`, before this protected range.

Normal late-path cleanup releases `x22` at `0x3E93C` before final outer cleanup.

The expected catch instead jumps directly to `0x3E944`, bypassing `0x3E93C`. Therefore a late protected exception does not execute that normal `x22` release.

R-117 should expose this only as data-only lifetime/continuation metadata; it should not attempt to retain/leak/release any real object.

## Next

R-117 after compiler green:
- promote exact `3E670` site-aware protected catch outcome;
- all expected sites swallow and jump to final outer cleanup;
- nonmatching type resumes unwind;
- late-preparation site additionally records that the normal retained-working-object release is bypassed;
- keep private selector/runtime method lookup, dispatch scheduling, counters/globals, exception synthesis, and real object lifetime changes excluded.
