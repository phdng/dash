# LOG/session-114.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-113 commit b8e355d; complete R-113 by promoting exact data-only `3F3F0` post-resize publish exception continuation from LSDA/raw ARM64. Per user workflow, commit locally but do not push._

## R-113 — evidence source

Reviewed:
- `3F3F0.c`;
- raw ARM64 for `3F3F0` from the first arm64 FAT slice;
- Mach-O LSDA `0x114994`;
- existing R-094 `DDResolveHostSlotResizePrivateFollowup` normal post-resize descriptor.

The first arm64 FAT slice begins at file offset `0x4000`.

Mach-O maps:
- `3F3F0 -> LSDA 0x114994`.

Decoded call-site table:
- `0x3F3F0..0x3F4BC` -> no landing pad;
- `0x3F4BC..0x3F4D4` -> landing `0x3F5A8`, action 5;
- `0x3F4D4..0x3F5C0` -> no landing pad.

## Protected range is only the `89D8` publish

The accepted resize path has already passed:
- main-thread gate;
- slot index/count/active hosting gates;
- non-CarPlay slot gate;
- hosted bundle non-empty gate;
- width/height >=1 gates;
- raw slot-size write to `xmmword_163D90`.

Only after those writes does the protected range begin at `0x3F4BC`.

Raw ARM64 `0x3F4BC..0x3F4D4`:
- load bundle into x0;
- pass bridge-on/split arguments and accepted width/height;
- call `89D8` at `0x3F4D0`.

Therefore an exception from `89D8` occurs after the raw slot-size state has already been written. R-113 does not model or mutate that prior state; it only records the original continuation after the protected call.

## Expected typed catch `0x3F5A8`

Raw ARM64:
- `0x3F5A8`: compare catch discriminator with expected value 1;
- expected value:
  - begin catch at `0x3F5B0`;
  - end catch at `0x3F5B4`;
  - branch to `0x3F4D4`;
- nonmatching value:
  - branch to `0x3F5BC`;
  - resume unwind.

The important fidelity point is that `0x3F4D4` is **not cleanup**. It is the start of the normal post-publish follow-up.

Thus an expected `89D8` exception:
- is swallowed locally;
- does not retry the publish;
- does not roll back the already-stored raw slot size;
- continues all post-publish follow-up exactly as if `89D8` had returned normally.

## Post-publish follow-up that remains eligible

After rejoining at `0x3F4D4`, raw ARM64 performs:

### Attempt-count normalization
- read `dword_163E88`;
- if signed current >=1, store zero.

This is the same rule already exposed by `DDResolveHostSlotResizePrivateFollowup` as:
- `shouldResetAttemptCount`;
- `nextAttemptCount = 0`.

### General-counter floor
- read `dword_162F1C`;
- if signed current <=3, store 4.

Already represented data-only as:
- `shouldRaiseGeneralCounterFloor`;
- `nextGeneralCounter = 4`.

### Private scene probe
- obtain `+[DDz2 shared]`;
- call `probeSceneForSlot:` with the accepted slot index;
- release shared instance.

Already represented data-only as:
- `shouldProbePrivateScene = YES`.

### Possible private scene update
When a scene is returned:
- if accepted landscape state is active, apply the exact positive-dimension swap rule;
- call `3F5C0(scene, slot, targetWidth, targetHeight)`.

Already represented data-only through caller-supplied `privateScenePresent` as:
- `shouldRequestPrivateSceneUpdate`;
- `targetSize = DDApplyLandscapeSwapToSize(acceptedRawSize)`.

R-113 therefore needs no duplicate counter/scene-plan fields. The exception contract only records that these existing post-publish decisions remain reachable after the catch.

## Nonmatching catch discriminator

If the landing discriminator is not the expected typed catch:
- branch to `0x3F5BC`;
- runtime resume-unwind is invoked.

Promoted metadata:
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

The reconstruction does not synthesize foreign/nonmatching exceptions or execute unwind machinery.

## Promoted runtime contract

Added:
- `DDHostSlotResizePublishExceptionOutcome`;
- `DDResolveHostSlotResizePublishExceptionOutcome(void)`.

Exact constant outcome for the expected typed path:
- `shouldSwallowException = YES`;
- `shouldContinuePostPublishFollowup = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

No site enum is necessary because the LSDA has one protected range and one local expected continuation.

## Explicit exclusions

R-113 does not:
- synthesize or catch Objective-C/foreign exceptions;
- execute begin-catch/end-catch/resume-unwind runtime APIs;
- invoke `89D8`;
- mutate the accepted raw slot size;
- mutate `dword_163E88` or `dword_162F1C`;
- call `+[DDz2 shared]` or `probeSceneForSlot:`;
- invoke `3F5C0`;
- mutate scene settings or any other private/global state.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — `3EDFC`

Mach-O maps:
- `3EDFC -> LSDA 0x1148F4`.

Decoded call-site table:
- `0x3EDFC..0x3EE20` -> no landing pad;
- `0x3EE20..0x3EE2C` -> landing `0x3EEE4`, action 5;
- `0x3EE38..0x3EE60` -> landing `0x3EEE8`, action 5;
- `0x3EE64..0x3EE78` -> landing `0x3EEDC`, action 5;
- `0x3EE84..0x3EEA8` -> landing `0x3EEE0`, action 5;
- `0x3EEA8..0x3EF20` -> no landing pad.

The small landing stubs:
- `0x3EEDC -> 0x3EEE8`;
- `0x3EEE0 -> 0x3EEE8`;
- `0x3EEE4 -> 0x3EEE8`.

Common catch `0x3EEE8`:
- compare catch discriminator with expected value 1;
- expected value:
  - begin catch;
  - end catch;
  - fall to `0x3EEF8`;
  - set result false/zero;
  - release retained input bundle and return false;
- nonmatching value:
  - branch to `0x3EF1C`;
  - resume unwind.

Protected work spans the frontmost-phone identity test:
- runtime lookup of SpringBoard class;
- `sharedApplication` acquisition + capability check for `_accessibilityFrontMostApplication`;
- private frontmost-application send;
- `3EFD4(..., bundleIdentifier)` string extraction;
- returned string length and equality check against the requested bundle.

All expected protected exceptions therefore collapse to:
- swallow;
- return false (not frontmost);
- no retry or alternate lookup.

## Next

R-114 after compiler green:
- promote exact `3EDFC` protected frontmost-phone identity exception -> swallow + false return plus nonmatching-type unwind metadata;
- keep SpringBoard/private selector lookup, frontmost object traversal, `3EFD4`, exception synthesis, and unwind execution excluded.
