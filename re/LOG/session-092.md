# LOG/session-092.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-091 commit 22ba993; complete R-091 by promoting only data-only 3F7C8 generation/reentrancy admission and post-invocation slot-mark/counter outcomes. Per user workflow, commit locally but do not push._

## R-091 — 3F7C8 execution admission

Directly reviewed:
- `3F7C8.c`
- `3F990.c`
- `3F5C0.c`

Raw ARM64 for `3F7C8` was used to confirm the decompiler and recover the exception-only counter path.

Exact entry gate:
- captured generation at block +40 must equal current host generation `qword_163DC8`;
- executor reentrancy bit `byte_163E9B & 1` must be clear;
- stale generation returns silently;
- matching generation while already reentrant returns silently;
- accepted entry sets the reentrancy byte to 1 before building/invoking the retained mutation block.

Promoted:
- `DDFBSSceneSettingsExecutionAdmissionKind`;
- `DDFBSSceneSettingsExecutionAdmission`;
- `DDResolveFBSSceneSettingsExecutionAdmission(capturedGeneration, currentGeneration, executorReentrant)`.

The descriptor reports whether the original would enter the private invocation and whether it would enter reentrant state. It never mutates the original byte.

## R-091 — normal invocation outcome

After `updateSettingsWithBlock:` returns normally:

1. Slot mark:
- slot index is loaded as an unsigned 64-bit value;
- values 0, 1, 2 write byte value 1 into `word_163E98 + slot`;
- values >2 do not write;
- a negative signed input therefore also does not qualify when interpreted unsigned.

2. Counter selection:
- the by-reference orientation-changed flag is read;
- changed !=0 selects `dword_162F28`;
- changed ==0 selects `dword_162F1C`;
- the selected counter is decremented only when positive.

3. Cleanup:
- retained block is released;
- `byte_163E9B` is cleared;
- by-reference captures are disposed.

Promoted data-only result:
- slot mark eligibility;
- slot index;
- counter class;
- whether the caller should attempt a counter decrement;
- whether the caller should clear reentrant state.

## R-091 — exception outcome

Raw ARM64 exposes an exception handler at the private-selector invocation:
- begin catch;
- decrement `dword_162F2C` when positive;
- end catch;
- do not execute the normal slot-mark path;
- clear `byte_163E9B`;
- dispose captures and return.

Promoted:
- `DDFBSSceneSettingsInvocationCounterException`;
- `DDResolveFBSSceneSettingsInvocationOutcome(slotIndex, invocationThrewException, orientationChanged)`.

For exception=true:
- `shouldMarkSlot = NO`;
- counter class = Exception;
- counter-decrement attempt = YES;
- reentrant clear = YES.

For a normal return:
- mark only unsigned slot 0..2;
- choose OrientationChanged or General counter;
- counter-decrement attempt = YES;
- reentrant clear = YES.

## Explicit exclusions

R-091 does not:
- retain or invoke the inner mutation block;
- call `updateSettingsWithBlock:`;
- send any private selector;
- catch or synthesize Objective-C exceptions;
- mutate `byte_163E9B`;
- mutate `word_163E98`;
- mutate `dword_162F1C`, `dword_162F28`, or `dword_162F2C`.

## Scout for next batch

Reviewed `4138C.c`.

Useful next pure boundary:
- host identity path may request a `3F5C0` update only when a scene exists, slot mark is clear, and slot width is positive, with accepted landscape swap applied;
- aux identity path may request `3E670` using the scene settings;
- after routing, if scene settings exist, support `isForeground`, report foreground=false, and the identity is a configured non-CarPlay host, the original suppresses its original callback and increments a bounded counter (<=9 before increment).

## Next

R-092 after compiler green:
- inspect `4138C` sceneHandle host/aux update routing and foreground-based original-callback suppression;
- promote only caller-supplied scene/identity/settings/foreground decisions plus update descriptors;
- do not invoke `3F5C0`, `3E670`, identity traversal, settings selectors, or suppress/call the original callback.
