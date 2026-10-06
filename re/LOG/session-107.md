# LOG/session-107.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-106 commit dc9c07f; complete R-106 by auditing exact Mach-O unwind/LSDA exception behavior for `3F5C0` and dispatched block `3F7C8`, reconciling it with the existing data-only executor admission/invocation descriptors. Per user workflow, commit locally but do not push._

## R-106 — evidence source

Reviewed:
- `3F5C0.c`;
- `3F7C8.c`;
- raw ARM64 for both functions from the first arm64 FAT slice;
- Mach-O LSDA index around `3F3F0..400D0`;
- session-091 normal `3F5C0` executor admission/counter-class reconstruction;
- session-092 normal/exception `3F7C8` generation/reentrancy, slot-mark, and counter descriptors.

The first arm64 FAT slice begins at file offset `0x4000`.

## Mach-O LSDA index — `3F5C0` has no local entry

Raw LSDA-index pairs around the executor region are:
- `0x3E02C -> 0x114818`;
- `0x3E33C -> 0x114860`;
- `0x3E670 -> 0x114880`;
- `0x3EA0C -> 0x1148B8`;
- `0x3EB9C -> 0x1148D8`;
- `0x3EDFC -> 0x1148F4`;
- `0x3EFD4 -> 0x114924`;
- `0x3F100 -> 0x114948`;
- `0x3F224 -> 0x114960`;
- `0x3F3F0 -> 0x114994`;
- `0x3F7C8 -> 0x1149B4`;
- `0x3F990 -> 0x1149D4`;
- `0x3FA90 -> 0x114A00`;
- `0x3FBC8 -> 0x114A18`.

There is no LSDA entry for `3F5C0`, nor for its adjacent helper `3F75C`.

This is consistent with the raw function body: `3F5C0` contains no local exception landing-pad path. Objective-C/runtime/helper exceptions therefore unwind out to the caller.

## `3F5C0` propagated-exception stages

The raw ARM64 confirms the existing admission order and exposes the important non-rollback boundary.

### Before attempt-count increment

Before `dword_163E88++`, possible call boundaries include:
- `3E9A8` scene-geometry gate;
- `respondsToSelector:updateSettingsWithBlock:`;
- class/method lookup;
- method type-encoding lookup;
- signature substring search.

Because there is no local LSDA/catch:
- any exception escaping this stage propagates/resumes unwind to the caller;
- `dword_163E88` has not yet been incremented by this invocation.

Promoted site:
- `DDFBSSceneSettingsExecutorExceptionSiteOuterBeforeAttemptIncrement`;
- `exceptionWouldResumeUnwind = YES`.

### After attempt-count increment

Raw ARM64:
- `0x3F6A8`: load `dword_163E88`;
- `0x3F6AC`: add 1;
- `0x3F6B0`: store updated attempt count;
- only then call `3F75C` at `0x3F6B8` and build/retain/dispatch the execution block.

Subsequent call boundaries include:
- `3F75C` desired-orientation resolution;
- retaining the scene object into the block capture;
- `dispatch_async`.

Again, there is no local catch.

Therefore an exception after `dword_163E88++`:
- propagates/resumes unwind;
- does not roll back the increment already stored in `dword_163E88`.

Promoted site:
- `DDFBSSceneSettingsExecutorExceptionSiteOuterAfterAttemptIncrement`;
- `exceptionWouldResumeUnwind = YES`;
- `attemptCountWouldRemainIncremented = YES`.

No attempt counter is mutated by the reconstruction.

## `3F7C8` LSDA

Mach-O maps:
- `3F7C8 -> LSDA 0x1149B4`.

Decoded call-site table:
- `0x3F7C8..0x3F890` -> no landing pad;
- `0x3F890..0x3F8A0` -> landing `0x3F940`, action 5;
- `0x3F8A0..0x3F990` -> no landing pad.

Thus the only locally protected operation is exactly the private selector invocation:
- load scene object / selector / retained mutation block;
- `objc_msgSend(scene, selector, block)` at `0x3F89C`.

Block construction/retention before the call and all normal post-call slot/counter cleanup after it are outside LSDA protection.

## Expected typed catch at `0x3F940`

Raw ARM64:
- `0x3F940`: preserve thrown object;
- `0x3F944`: compare landing selector/type discriminator with 1;
- expected type enters catch at `0x3F94C`;
- `0x3F954`: load `dword_162F2C`;
- `0x3F95C`: `subs current, current, #1`;
- `0x3F960`: if result < 0, skip store;
- `0x3F964`: otherwise store decremented value;
- `0x3F968`: end catch;
- `0x3F96C`: branch to `0x3F8F4`.

`0x3F8F4` is the shared entered-path cleanup:
- clear `byte_163E9B` reentrancy state;
- dispose the two by-reference captures;
- return.

The typed exception path skips:
- slot mark at `0x3F8A8..0x3F8C0`;
- normal OrientationChanged/General counter selection;
- normal selected-counter decrement.

Exact expected-catch semantics:
- swallow the private invocation exception;
- never mark the slot;
- counter class = Exception (`dword_162F2C`);
- decrement that counter only when its signed current value is >0;
- clear executor reentrancy;
- dispose invocation captures;
- return through the normal block epilogue.

The pre-existing R-091 `DDResolveFBSSceneSettingsInvocationOutcome(... invocationThrewException=YES ...)` already represented the broad counter class/no-slot/clear-reentrant shape. R-106 adds exact LSDA-derived positive-only next-counter state and the catch/unwind distinctions without changing that older API.

## Nonmatching catch type / foreign exception path

When the landing discriminator is not the expected typed catch:
- branch from `0x3F948` to `0x3F970`;
- dispose both by-reference captures (`0x3F970..0x3F984`);
- resume unwind via `0x3F988..0x3F98C`.

Critically this path does **not** pass through `0x3F8F4`, so it does not clear `byte_163E9B` before resuming unwind.

Promoted metadata for the private-invocation site:
- `nonmatchingCatchTypeWouldResumeUnwind = YES`;
- `nonmatchingCatchTypeWouldClearReentrantState = NO`;
- invocation captures are still disposed.

This distinction is evidence-only metadata; the reconstruction does not create foreign exceptions or execute landing pads.

## Promoted runtime contract

Added:
- `DDFBSSceneSettingsExecutorExceptionSite`
  - None
  - OuterBeforeAttemptIncrement
  - OuterAfterAttemptIncrement
  - PrivateInvocation
- `DDFBSSceneSettingsExecutorExceptionOutcome`
- `DDResolveFBSSceneSettingsExecutorExceptionOutcome(site, currentExceptionCounter)`.

### OuterBeforeAttemptIncrement
- `shouldSwallowException = NO`;
- `exceptionWouldResumeUnwind = YES`;
- no attempt-increment non-rollback flag.

### OuterAfterAttemptIncrement
- `shouldSwallowException = NO`;
- `exceptionWouldResumeUnwind = YES`;
- `attemptCountWouldRemainIncremented = YES`.

### PrivateInvocation — expected typed catch
- `shouldSwallowException = YES`;
- `shouldMarkSlot = NO`;
- `counterKind = DDFBSSceneSettingsInvocationCounterException`;
- `shouldDecrementExceptionCounter = currentExceptionCounter > 0`;
- `nextExceptionCounter = currentExceptionCounter - 1` only when decrementing, otherwise unchanged;
- `shouldClearReentrantState = YES`;
- `shouldDisposeInvocationCaptures = YES`.

### PrivateInvocation — nonmatching catch type metadata
- `nonmatchingCatchTypeWouldResumeUnwind = YES`;
- `nonmatchingCatchTypeWouldClearReentrantState = NO`.

## Explicit exclusions

R-106 does not:
- synthesize or catch Objective-C/foreign exceptions;
- invoke `3E9A8`, `3F75C`, runtime method lookup, selector dispatch, or `dispatch_async`;
- retain/invoke the `3F990` mutation block;
- invoke `updateSettingsWithBlock:`;
- mark `word_163E98` slots;
- set/clear `byte_163E9B`;
- mutate `dword_163E88`, `dword_162F1C`, `dword_162F20`, `dword_162F24`, `dword_162F28`, or `dword_162F2C`;
- dispose actual by-reference captures;
- intercept/resume unwind.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — `3F990`

Mach-O maps:
- `3F990 -> LSDA 0x1149D4`.

Decoded call-site table:
- `0x3F990..0x3F9BC` -> no landing pad;
- `0x3F9BC..0x3F9E4` -> landing `0x3FA78`, action 7;
- `0x3F9EC..0x3FA04` -> landing `0x3FA64`, action 7;
- `0x3FA08..0x3FA30` -> landing `0x3FA60`, action 5;
- `0x3FA30..0x3FA90` -> no landing pad.

Raw ARM64 already establishes:

1. Frame path `0x3F9BC..0x3F9E4`:
   - `respondsToSelector:setFrame:` + optional `setFrame:`;
   - catch at `0x3FA78` swallows then branches back to `0x3F9E4`;
   - orientation processing still runs after a frame-path exception.

2. Orientation signature path `0x3F9EC..0x3FA04`:
   - class lookup + `3ECD0` signature check;
   - catch at `0x3FA64` swallows and branches to final cleanup `0x3FA4C`.

3. Current orientation / setter path `0x3FA08..0x3FA30`:
   - `3FA90` current-orientation read and optional `setInterfaceOrientation:`;
   - landing `0x3FA60` branches into the same catch at `0x3FA64`;
   - swallow + cleanup/return.

No `41BA0` probe appears in this function.

## Next

R-107 after compiler green:
- promote exact `3F990` frame-path catch→continue orientation and orientation-path catch→cleanup outcomes;
- keep runtime lookup/private setter invocation, settings/byref mutation, exception synthesis, and landing-pad execution excluded.
