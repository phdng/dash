# LOG/session-121.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-120 commit 344479f; complete R-120 by promoting exact data-only `3DD4C` bundle-normalization application-validation exception behavior from LSDA/raw ARM64. Per user workflow, commit locally but do not push._

## R-120 — evidence source

Reviewed:
- `3DD4C.c`;
- raw ARM64 for `3DD4C` from the first arm64 FAT slice;
- Mach-O LSDA `0x1147EC`;
- existing host-slot canonicalization mirror that reproduces non-NSString/duplicate normalization without private application-controller traversal.

The first arm64 FAT slice begins at file offset `0x4000`.

Mach-O maps:
- `3DD4C -> LSDA 0x1147EC`.

Decoded call-site table:
- `0x3DD4C..0x3DDB0` -> no landing pad;
- `0x3DDB0..0x3DDBC` -> landing `0x3DFA8`, action 5;
- `0x3DDBC..0x3DEF4` -> no landing pad;
- `0x3DEF4..0x3DF0C` -> landing `0x3DF54`, action 5;
- `0x3DF0C..0x3DFC8` -> no landing pad.

Only the application-controller lookup and per-item application lookup have local typed catches.

## Early application-controller lookup

Before this protected range:
- input bundle array and CarPlay flags are retained;
- validation is entered only when `a3` requests application validation;
- runtime class lookup for `SBApplicationController` is outside the protected range.

Protected range `0x3DDB0..0x3DDBC` covers:
- `+[SBApplicationController sharedInstance]` send at `0x3DDB0`;
- retain-autoreleased-return handling ending at `0x3DDBC`.

Landing `0x3DFA8`:
- compare catch discriminator with expected value 1;
- expected type:
  - begin catch;
  - end catch;
  - set controller register `x22 = nil`;
  - restore saved requested count from stack;
  - branch to `0x3DDC8`;
- nonmatching type:
  - branch `0x3DFC4`;
  - resume unwind.

### Expected continuation

At `0x3DDC8` the original executes `respondsToSelector:applicationWithBundleIdentifier:` against the controller value.

Because the catch forced controller nil:
- the Objective-C send to nil safely produces false;
- the helper follows the normal no-validation-controller path;
- canonicalization still constructs the mutable output array and processes every requested item.

Thus expected early-catch semantics are:
- swallow locally;
- treat application validation controller as unavailable;
- continue canonicalization rather than returning nil/failing the operation.

### Important unprotected capability nuance

The `respondsToSelector:applicationWithBundleIdentifier:` operation itself at `0x3DDC8..0x3DDD4` is outside both LSDA protected ranges.

Therefore when the controller is genuinely non-nil and that capability operation throws, `3DD4C` has no local catch for it; the exception propagates.

R-120 deliberately models only the two observed local catch continuations rather than claiming the whole validation stage is protected.

## Per-item application lookup

Normal loop work before the protected app lookup has already:
- selected the raw bundle-array item when present;
- type-checked it as NSString, replacing non-string values with the empty constant;
- retained that candidate;
- replaced duplicate non-empty candidates with the empty constant;
- read the parallel CarPlay flag for the same index;
- checked candidate length and controller presence.

Only when candidate is non-empty, controller is non-nil, and the item is not CarPlay UI does the private validation call occur.

Protected range `0x3DEF4..0x3DF0C` covers:
- `applicationWithBundleIdentifier:` private send at `0x3DF00`;
- retain-autoreleased-return handling ending at `0x3DF0C`.

Landing `0x3DF54`:
- compare catch discriminator with expected value 1;
- expected type:
  - begin catch;
  - end catch;
  - restore saved requested count;
  - branch to `0x3DF28`;
- nonmatching type:
  - branch `0x3DFC4`;
  - resume unwind.

## Per-item expected continuation preserves sanitized candidate

The normal success path after the private app lookup is:
- if returned app is nil, release current candidate and replace it with empty string;
- release returned app;
- then reach `0x3DF28`, add current candidate to the output array, release current candidate/raw item, increment index, and continue loop.

The expected catch jumps directly to `0x3DF28`.

Therefore on protected per-item lookup exception:
- the returned-app nil test is skipped;
- the current candidate in `x27` is left unchanged;
- that already sanitized/deduplicated candidate is still added to output;
- loop cleanup/index increment still run;
- remaining items continue normally.

This is not equivalent to treating the app as missing; the original preserves the candidate specifically because the catch rejoins after the app-validation replacement branch.

## Promoted runtime contract

Added:
- `DDBundleNormalizationExceptionSite` with:
  - `ApplicationControllerLookup`;
  - `PerItemApplicationLookup`;
- `DDBundleNormalizationExceptionOutcome`;
- `DDResolveBundleNormalizationExceptionOutcome(site)`.

Application-controller lookup site:
- `shouldSwallowException = YES`;
- `shouldContinueCanonicalization = YES`;
- `shouldForceApplicationControllerNil = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

Per-item application lookup site:
- `shouldSwallowException = YES`;
- `shouldContinueCanonicalization = YES`;
- `shouldPreserveSanitizedCandidate = YES`;
- `shouldAddCandidateAndContinueLoop = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

Unknown/None site returns an all-false outcome.

## Relationship to the existing reconstruction

The existing host-slot mirror already performs evidence-safe string canonicalization:
- non-NSString input -> empty string;
- duplicate non-empty candidate -> empty string;
- order preserved.

It intentionally does not query SpringBoard application existence.

R-120 does not add that private query. It only documents the original exception continuation that would apply around the two protected application-validation calls.

## Explicit exclusions

R-120 does not:
- query `SBApplicationController`;
- invoke `sharedInstance`;
- invoke `applicationWithBundleIdentifier:`;
- perform private application existence validation;
- retain/release live application objects;
- mutate a live normalization array as part of exception simulation;
- synthesize/catch Objective-C or foreign exceptions;
- execute begin-catch/end-catch/resume-unwind runtime APIs.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — `3D990`

Direct unwind-index enumeration maps:
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

### First hosted-controller teardown catch

Protected range `0x3D9F0..0x3DA28` covers:
- hosted controller `view` send + retain-autoreleased result;
- `removeFromSuperview`;
- `respondsToSelector:invalidate`;
- optional `invalidate` send.

Landing `0x3DC1C` branches into common typed catch `0x3DC24`.

Expected catch at `0x3DC24`:
- begin/end catch;
- branch directly to `0x3DB14`, start of the bridge-off phase.

Therefore a protected exception during first hosted-controller teardown:
- is swallowed;
- skips all remaining private hosted-controller teardown work;
- continues bridge-off state publication.

The first hosted-controller ivar had already been cleared before entering the protected range; secondary controller ivars have not yet been processed when this early catch fires. R-121 should expose only ordering/skip metadata, not mutate those ivars.

### Secondary hosted-controller teardown catch

Protected range `0x3DA9C..0x3DAD4` covers the same `view`/remove/capability/invalidate operations inside the two-entry secondary controller loop.

Its landing is already common catch `0x3DC24`.

Expected exception:
- swallow;
- jump to `0x3DB14`;
- skip the rest of the private controller loop and normal private teardown cleanup;
- continue bridge-off publication.

By this point both secondary controller ivars were already copied/cleared before the loop. Again, R-121 should expose only control-flow/lifetime metadata, not recreate private object ownership.

### Cleanup-only release range

`0x3DAFC..0x3DB14` covers release cleanup after the private controller loop.

Its landing `0x3DC20` immediately resumes unwind and has action 0, not a local typed swallow continuation.

R-121 should treat an exception there as propagation/unwind-only metadata.

### Slot-0 bridge-off publication catch

Protected range `0x3DB1C..0x3DB50` covers:
- hosted bundle length test for slot 0;
- when non-empty/non-CarPlay, `89D8(... shouldBridge=0, isSplit=0 ...)` publication.

Landing `0x3DC04`:
- expected discriminator 1 -> begin/end catch -> branch `0x3DB50`;
- all other/no matching types -> `0x3DC20` resume unwind.

`0x3DB50` begins the slot 1/2 loop.

Therefore expected slot-0 exception:
- swallow;
- skip only the remainder of slot-0 publish operation;
- continue attempting slots 1 and 2.

### Slot-1/2 bridge-off publication catch

Protected range `0x3DB74..0x3DBA0` covers each later slot's bundle length test and optional split `89D8(... shouldBridge=0, isSplit=1 ...)` publication.

Landing `0x3DBB0`:
- expected discriminator 1 -> begin/end catch -> branch `0x3DBA0`;
- nonmatching -> `0x3DC20` resume unwind.

`0x3DBA0` advances to the next slot / exits the loop.

Therefore expected later-slot exception:
- swallow;
- continue the slot loop rather than abandoning dismiss.

### Final resetHostingState propagation

Final call:
- `0x3DBC8`: `resetHostingState`.

Its call-site entry lands at `0x3DC20` with action 0.

Thus an exception escaping `resetHostingState` is not swallowed locally; it resumes/propagates unwind.

## Next

R-121 after compiler green:
- promote site-aware `3D990` dismiss exception outcomes;
- first/secondary private teardown catches -> skip remaining private teardown + continue bridge-off phase;
- slot0 publish catch -> continue later slots;
- later-slot publish catch -> continue loop;
- cleanup-only release and final reset exceptions -> propagate/resume unwind;
- keep private view/controller mutation, `89D8` publication, hosted-ivar mutation, real lifetime effects, exception synthesis, and unwind execution excluded.
