# LOG/session-122.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-121 commit 951bfee; complete R-121 by promoting exact data-only `3D990` dismiss-block exception behavior from LSDA/raw ARM64. Per user workflow, commit locally but do not push._

## R-121 — evidence source

Reviewed:
- `3D990.c`;
- raw ARM64 for `3D990` from the first arm64 FAT slice;
- Mach-O LSDA `0x1147A0`;
- existing evidence-safe `DDDismissHostMirror` state/IPC half.

The first arm64 FAT slice begins at file offset `0x4000`.

Mach-O maps:
- `3D990 -> LSDA 0x1147A0`.

Decoded call-site table:
- `0x3D990..0x3D9F0` -> no landing pad;
- `0x3D9F0..0x3DA28` -> landing `0x3DC1C`, action 5;
- `0x3DA28..0x3DA9C` -> no landing pad;
- `0x3DA9C..0x3DAD4` -> landing `0x3DC24`, action 5;
- `0x3DAD4..0x3DAFC` -> no landing pad;
- `0x3DAFC..0x3DB14` -> landing `0x3DC20`, action 0;
- `0x3DB1C..0x3DB50` -> landing `0x3DC04`, action 5;
- `0x3DB74..0x3DBA0` -> landing `0x3DBB0`, action 5;
- `0x3DBA0..0x3DBC8` -> no landing pad;
- `0x3DBC8..0x3DBCC` -> landing `0x3DC20`, action 0;
- `0x3DBCC..0x3DC38` -> no landing pad.

The function mixes expected typed catches with cleanup-only/action-0 unwind entries. R-121 keeps these paths distinct.

## Primary hosted-controller teardown catch

Before the protected range:
- the primary hosted-controller object from ivar `+8` is retained in `x20`;
- the original ivar is set to nil and its old value released;
- therefore the primary controller ivar has already been cleared before protected private teardown begins.

Protected range `0x3D9F0..0x3DA28` covers:
- `view` send;
- retain-autoreleased view;
- `removeFromSuperview`;
- `respondsToSelector:invalidate`;
- optional `invalidate` send.

Landing flow:
- `0x3DC1C -> 0x3DC24`;
- compare catch discriminator with expected type 1;
- expected type begin/end-catches;
- branch directly to `0x3DB14`, the bridge-off phase.

Exact expected semantics:
- swallow locally;
- skip the rest of primary private teardown;
- skip creation/clearing/teardown of the two secondary controller captures;
- skip normal private-object cleanup between the private teardown and bridge-off phase;
- continue bridge-off publication.

State-ordering metadata:
- `primaryControllerIvarWasAlreadyCleared = YES`;
- `secondaryControllerIvarsWereAlreadyCleared = NO`;
- `normalPrivateTeardownCleanupWouldBeBypassed = YES`.

The runtime descriptor does not mutate any real ivars or ownership.

## Secondary hosted-controller teardown catch

Before the secondary loop begins:
- both secondary controller ivars (`+24` and `+32`) are retained into stack captures;
- both corresponding ivars are set to nil and their old references released;
- the primary controller ivar was already cleared earlier.

Each loop iteration additionally retains the current controller into `x23` before entering the protected range.

Protected range `0x3DA9C..0x3DAD4` covers:
- `view` send;
- retain-autoreleased view;
- `removeFromSuperview`;
- `respondsToSelector:invalidate`;
- optional `invalidate` send.

Landing `0x3DC24` uses the same expected typed catch as the primary path and branches directly to `0x3DB14`.

Exact expected semantics:
- swallow;
- abandon the rest of the secondary-controller loop;
- bypass normal secondary/current-controller release cleanup and the later primary-controller release;
- continue bridge-off publication.

State-ordering metadata:
- primary controller ivar already cleared = YES;
- both secondary controller ivars already cleared = YES;
- normal private teardown cleanup bypassed = YES.

R-121 records only ordering/control-flow metadata, not an intentional leak or real ownership change.

## Private cleanup/release propagation

After the protected secondary teardown body, normal code releases:
- retained view/current-controller values;
- both stack-retained secondary captures;
- the retained primary controller.

This cleanup spans two LSDA behaviors:
- `0x3DAD4..0x3DAFC` has no local landing pad;
- `0x3DAFC..0x3DB14` has landing `0x3DC20`, action 0.

`0x3DC20` calls resume-unwind directly.

Therefore exceptions escaping this private cleanup are not locally swallowed. The reconstruction collapses this whole cleanup category into:
- `exceptionWouldPropagate = YES`.

No nonmatching typed-catch metadata is attached because this site is not an expected typed catch site.

## Slot-0 bridge-off publication catch

Bridge-off phase begins at `0x3DB14`.

Protected range `0x3DB1C..0x3DB50` covers:
- slot-0 hosted-bundle `length`;
- CarPlay-flag gate;
- optional `89D8(bundle, shouldBridge=0, orientation, isSplit=0, 0, 0)`.

Landing `0x3DC04`:
- when discriminator == expected type 1, begin/end-catch;
- branch to `0x3DB50`;
- nonmatching discriminator -> `0x3DC20` resume unwind.

`0x3DB50` initializes the slots 1/2 loop.

Exact expected semantics:
- swallow slot-0 publication exception;
- do not abandon dismiss;
- continue attempting bridge-off publication for slots 1 and 2.

Promoted fields:
- `shouldSwallowException = YES`;
- `shouldContinueLaterSlotPublications = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

## Slot-1/2 bridge-off publication catch

Protected range `0x3DB74..0x3DBA0` covers each later slot's:
- hosted-bundle `length`;
- CarPlay-flag gate;
- optional split `89D8(bundle, shouldBridge=0, orientation, isSplit=1, 0, 0)`.

Landing `0x3DBB0`:
- expected discriminator -> begin/end-catch -> branch `0x3DBA0`;
- nonmatching discriminator -> `0x3DC20` resume unwind.

`0x3DBA0` advances the loop state and either attempts the next later slot or exits the loop.

Exact expected semantics:
- swallow only the current later-slot publication exception;
- continue the slot loop.

Promoted fields:
- `shouldSwallowException = YES`;
- `shouldContinueSlotLoop = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

## Final resetHostingState propagation

After the slots 1/2 loop, `0x3DBC8` invokes `resetHostingState` on the captured DDz2 object.

Call-site entry:
- `0x3DBC8..0x3DBCC` -> `0x3DC20`, action 0.

Thus an exception escaping `resetHostingState`:
- is not swallowed by `3D990`;
- resumes/propagates unwind.

Promoted metadata:
- `exceptionWouldPropagate = YES`.

This distinction matters because an expected publish exception is swallowed, but a final reset exception aborts through unwind.

## Promoted runtime contract

Added:
- `DDDismissExceptionSite`:
  - `PrimaryPrivateTeardown`;
  - `SecondaryPrivateTeardown`;
  - `PrivateCleanupRelease`;
  - `SlotZeroBridgeOffPublish`;
  - `LaterSlotBridgeOffPublish`;
  - `ResetHostingState`;
- `DDDismissExceptionOutcome`;
- `DDResolveDismissExceptionOutcome(site)`.

Primary private teardown:
- swallow = YES;
- skip remaining private teardown = YES;
- continue bridge-off = YES;
- primary ivar already cleared = YES;
- secondary ivars already cleared = NO;
- normal private cleanup bypassed = YES;
- nonmatching typed catch -> resume unwind.

Secondary private teardown:
- swallow = YES;
- skip remaining private teardown = YES;
- continue bridge-off = YES;
- primary ivar already cleared = YES;
- secondary ivars already cleared = YES;
- normal private cleanup bypassed = YES;
- nonmatching typed catch -> resume unwind.

Slot 0 publish:
- swallow = YES;
- continue later slots = YES;
- nonmatching typed catch -> resume unwind.

Later-slot publish:
- swallow = YES;
- continue slot loop = YES;
- nonmatching typed catch -> resume unwind.

Private cleanup and resetHostingState:
- propagate/resume unwind only.

Unknown/None site returns an all-false outcome.

## Relationship to DDDismissHostMirror

The existing `DDDismissHostMirror` reconstructs only the evidence-safe state/IPC half:
- bridge-off each non-CarPlay hosted bid;
- slot0 non-split, slots1/2 split;
- reset reconstruction host mirror afterward.

It intentionally owns no private hosted controllers/views. R-121 does not change that boundary. The exception resolver only describes how the original `3D990` would continue if protected private teardown or publish operations threw.

## Explicit exclusions

R-121 does not:
- access/clear real DDz2 hosted-controller ivars;
- invoke `view`, `removeFromSuperview`, or `invalidate`;
- retain/release live private controllers/views;
- invoke `89D8` as exception simulation;
- invoke real `resetHostingState`;
- mutate host mirror state as an exception side effect;
- synthesize/catch Objective-C or foreign exceptions;
- execute begin-catch/end-catch/resume-unwind runtime APIs.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — `3D704`

Direct unwind enumeration maps:
- `3D704 -> LSDA 0x114774`.

Decoded call-site table:
- `0x3D704..0x3D7AC` -> no landing pad;
- `0x3D7AC..0x3D7E8` -> landing `0x3D890`, action 5;
- `0x3D7E8..0x3D7FC` -> no landing pad;
- `0x3D7FC..0x3D828` -> landing `0x3D87C`, action 5;
- `0x3D828..0x3D8A8` -> no landing pad.

### Private hosted-view teardown catch

Normal preconditions already passed before the protected range:
- main-thread gate;
- physical slot <3;
- hosted slot count > index;
- slot is not already CarPlay UI;
- hosted bundle was copied into `x21`;
- slot-specific private controller was retained into `x22`.

Protected range `0x3D7AC..0x3D7E8` covers:
- controller `view` send;
- retain-autoreleased view;
- `removeFromSuperview`;
- `respondsToSelector:invalidate`;
- optional `invalidate` send.

Landing `0x3D890`:
- expected type begin/end-catches;
- branch to `0x3D7F0`;
- nonmatching -> `0x3D8A4` resume unwind.

`0x3D7F0` clears the slot-specific private controller ivar and releases its old value.

Then normal flow continues:
- if copied bundle is non-empty, attempt split bridge-off `89D8`;
- write copied bundle back into global hosted-bundle slot;
- retain/release state around that replacement;
- set per-slot CarPlay flag to 1;
- release retained private controller and bundle copy;
- return the original precondition result.

Thus expected private-teardown exception semantics are:
- swallow;
- skip only the remaining private view teardown operations;
- still clear controller ivar;
- still attempt bridge-off publication;
- still commit hosted-bundle/CarPlay flag conversion state.

R-122 should expose these only as data-only continuation/state-commit metadata.

### Bridge-off publish catch

Protected range `0x3D7FC..0x3D828` covers:
- copied bundle `length`;
- optional split `89D8(bundle, shouldBridge=0, orientation, isSplit=1, 0, 0)`.

Landing `0x3D87C`:
- expected type begin/end-catches;
- branch to `0x3D828`;
- nonmatching -> `0x3D8A4` resume unwind.

`0x3D828` begins the state commit:
- swap copied bundle into hosted-bundle global slot;
- set slot CarPlay flag = 1;
- cleanup retained private controller/bundle.

Therefore expected bridge-off exception semantics are:
- swallow;
- skip failed publication only;
- still commit slot conversion state.

## Next

R-122 after compiler green:
- promote `3D704` private-teardown catch -> continue controller-clear + publish-attempt + bundle/CarPlay state commit;
- promote bridge-off publish catch -> continue bundle/CarPlay state commit;
- both nonmatching types -> resume unwind;
- keep private view/controller operations, `89D8`, live ivar/global mutation, real object lifetime effects, exception synthesis, and unwind execution excluded.
