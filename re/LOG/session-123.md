# LOG/session-123.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-122 commit afd88df; complete R-122 by promoting exact data-only `3D704` convert-slot-to-CarPlay exception behavior from LSDA/raw ARM64. Per user workflow, commit locally but do not push._

## R-122 — evidence source

Reviewed:
- `3D704.c`;
- raw ARM64 for `3D704` from the first arm64 FAT slice;
- Mach-O LSDA `0x114774`;
- existing evidence-safe `DDConvertHostSlotToCarPlayUI` state/IPC half.

The first arm64 FAT slice begins at file offset `0x4000`.

Mach-O maps:
- `3D704 -> LSDA 0x114774`.

Decoded call-site table:
- `0x3D704..0x3D7AC` -> no landing pad;
- `0x3D7AC..0x3D7E8` -> landing `0x3D890`, action 5;
- `0x3D7E8..0x3D7FC` -> no landing pad;
- `0x3D7FC..0x3D828` -> landing `0x3D87C`, action 5;
- `0x3D828..0x3D8A8` -> no landing pad.

The helper has exactly two local typed catches: one around private hosted-view teardown and one around copied-bundle bridge-off publication.

## Admission and state established before protected work

Before either protected range the original has already evaluated:
- `[NSThread isMainThread]`;
- slot index `< 3`;
- hosted slot count greater than index;
- slot is not already marked CarPlay UI.

When all gates pass:
- hosted bundle for the slot is copied into `x21`;
- slot-specific private controller ivar is retained into `x22`;
- slot-specific ivar offset is resolved from index.

The function's return value remains the precondition result (`YES` once these gates pass), even if a protected exception is later swallowed.

## Private hosted-view teardown catch

Protected range:
- `0x3D7AC..0x3D7E8` -> landing `0x3D890`, action 5.

Raw ARM64 covers:
- controller `view` send;
- retain-autoreleased view into `x24`;
- `removeFromSuperview`;
- `respondsToSelector:invalidate`;
- optional `invalidate` send.

Landing `0x3D890`:
- compare catch discriminator with expected value 1;
- expected type begin/end-catches;
- branch to `0x3D7F0`;
- nonmatching type -> `0x3D8A4` resume unwind.

### Expected continuation at `0x3D7F0`

The catch rejoins **before** the slot-specific private controller ivar clear:
- load current controller ivar;
- set ivar to nil;
- release old ivar value.

Then normal flow continues:
- copied hosted bundle `length` is checked;
- if non-empty, split bridge-off `89D8(... shouldBridge=0, isSplit=1 ...)` remains eligible;
- copied bundle is written back into the hosted-bundle slot;
- the slot CarPlay flag is set to `1`;
- retained controller/bundle cleanup runs;
- function returns the earlier admission result.

Therefore an expected private teardown exception:
- is swallowed locally;
- skips only the remaining private view/remove/invalidate operations;
- does **not** prevent controller ivar clear;
- does **not** prevent the bridge-off phase from being attempted;
- does **not** prevent hosted-bundle/CarPlay conversion state commit.

Promoted data-only metadata:
- `shouldContinueControllerIvarClear = YES`;
- `shouldContinueBridgeOffPhase = YES`;
- `shouldCommitHostedBundleState = YES`;
- `shouldSetCarPlayFlag = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

No real private ivar or host global is changed by the resolver.

## Bridge-off publication catch

Protected range:
- `0x3D7FC..0x3D828` -> landing `0x3D87C`, action 5.

Raw ARM64 covers:
- copied bundle `length`;
- optional `89D8(bundle, shouldBridge=0, orientation=qword_162F08, isSplit=1, width=0, height=0)`.

The slot-specific private controller ivar was already cleared immediately before this range at `0x3D7F0..0x3D7F8`.

Landing `0x3D87C`:
- compare catch discriminator with expected value 1;
- expected type begin/end-catches;
- branch to `0x3D828`;
- nonmatching type -> `0x3D8A4` resume unwind.

### Expected continuation at `0x3D828`

The catch rejoins exactly at the state-commit block:
- old hosted-bundle slot value is loaded;
- copied bundle is stored into the hosted-bundle slot;
- copied bundle is retained for cleanup ordering;
- old slot value is released;
- CarPlay flag byte for the slot is set to `1`;
- controller/bundle cleanup runs.

Thus an expected publish exception:
- swallows the failed bridge-off publication;
- does not retry `89D8`;
- still commits the copied hosted bundle;
- still sets the slot CarPlay flag;
- occurs only after the private controller ivar has already been cleared.

Promoted metadata:
- `controllerIvarWasAlreadyClearedBeforeCatch = YES`;
- `shouldCommitHostedBundleState = YES`;
- `shouldSetCarPlayFlag = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

## Promoted runtime contract

Added:
- `DDConvertSlotToCarPlayExceptionSite`:
  - `PrivateHostedViewTeardown`;
  - `BridgeOffPublish`;
- `DDConvertSlotToCarPlayExceptionOutcome`;
- `DDResolveConvertSlotToCarPlayExceptionOutcome(site)`.

Private-teardown site:
- swallow = YES;
- continue controller-ivar clear = YES;
- continue bridge-off phase = YES;
- commit hosted-bundle state = YES;
- set CarPlay flag = YES;
- nonmatching catch type -> resume unwind.

Bridge-off-publish site:
- swallow = YES;
- controller ivar already cleared before catch = YES;
- commit hosted-bundle state = YES;
- set CarPlay flag = YES;
- nonmatching catch type -> resume unwind.

Unknown/None site returns an all-false outcome.

## Relationship to existing conversion mirror

`DDConvertHostSlotToCarPlayUI` already reconstructs the evidence-safe state/IPC half of `3D704`:
- main-thread/slot-count gate;
- copied hosted bundle;
- optional bridge-off publish;
- preserve bundle in slot;
- set CarPlay flag.

It intentionally owns no private hosted controller/view. R-122 therefore adds only exception-continuation descriptors and does not alter the live mirror's normal behavior.

## Explicit exclusions

R-122 does not:
- access or clear real DDz2 controller ivars;
- invoke `view`, `removeFromSuperview`, or `invalidate`;
- invoke `89D8` as exception simulation;
- write live hosted-bundle globals or CarPlay flags through the resolver;
- retain/release live private controllers/views;
- synthesize/catch Objective-C or foreign exceptions;
- execute begin-catch/end-catch/resume-unwind runtime APIs.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — `3CC44`

Direct `__unwind_info` LSDA enumeration shows the next earlier exception-bearing function:
- `3CC44 -> LSDA 0x11468C`.

No existing reconstruction log/doc had promoted this function's LSDA behavior.

The call-site table contains many action-0 cleanup/unwind ranges plus multiple action-5 typed ranges during landscape-file coordination/parsing and a cold tripped-file write path.

All action-5 landing stubs (`0x3D4BC`, `0x3D4C0`, `0x3D4C4`, `0x3D4C8`, `0x3D4CC`, `0x3D4D0`, `0x3D4D4`, `0x3D4D8`, `0x3D4DC`) branch to common typed catch `0x3D4E0`.

### Common typed catch `0x3D4E0`

Raw ARM64:
- compare catch discriminator with expected value 1;
- nonmatching -> `0x3D4F8` resume unwind;
- expected type:
  - begin catch;
  - clear `qword_163D58` (parsed landscape orientation) at `0x3D4EC`;
  - end catch;
  - branch to `0x3D21C`.

At `0x3D21C`:
- load parsed landscape orientation;
- when zero, call `3DFC8(0)` for fallback orientation;
- store resolved orientation into `qword_162F08`;
- continue normal slot creation/hosting flow.

Thus every expected typed catch has the same high-level result:
- swallow;
- invalidate only the parsed landscape orientation;
- fall back through normal orientation resolution;
- continue hosting rather than abandoning the request.

### Action-0 ranges

Several LSDA entries land directly at `0x3D4F8`, action 0, or have no landing pad. These are cleanup/unwind behavior only; they do not use the local expected-type swallow continuation.

R-123 should expose action-0/nonmatching paths as unwind/propagation metadata, not as swallowed landscape parse failures.

### Late state-persistence nuance

Successful landscape parsing commits state before later protected file/hook operations:
- `0x3D16C`: parsed orientation -> `qword_163D58`;
- `0x3D174..0x3D17C`: swap flag -> `byte_163E80`;
- `0x3D180..0x3D18C`: cswap flag -> `byte_163D60`;
- `0x3D190..0x3D194`: rotation -> `qword_163D68`.

Later typed protected ranges include the inflight-file open/write/close path and `sub_372CC` call.

If one of those later operations throws the expected type:
- common catch clears `qword_163D58` only;
- previously written swap/cswap/rotation values are **not** rolled back;
- `0x3D21C` then falls back orientation via `3DFC8(0)` while those auxiliary landscape fields remain as already written.

This must be represented as ordering/persistence metadata only; the reconstruction should not mutate these globals as part of the resolver.

### Cold tripped-file path

The protected range `0x3D488..0x3D4A8` is reached from the foreign-inflight PID branch at `0x3CF80` before the later normal logging loop changes `x19`; on this cold path the common catch's global-page register usage remains consistent. Expected failure still clears parsed orientation and returns to the same fallback-orientation continuation.

## Next

R-123 after compiler green:
- promote common expected typed catch -> clear parsed landscape orientation + continue fallback orientation/hosting;
- expose nonmatching/action-0 paths as resume-unwind/propagate metadata;
- distinguish late post-state-commit catches so swap/cswap/rotation persistence is explicit;
- keep landscape file IO, globals, `3DFC8`, slot creation, `sub_372CC`, private hooks, exception synthesis, and unwind execution excluded.
