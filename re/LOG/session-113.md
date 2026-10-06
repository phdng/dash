# LOG/session-113.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-112 commit d64bf5e; complete R-112 by promoting exact data-only `3F224` `onUIAppRequest:` exception behavior from LSDA/raw ARM64. Per user workflow, commit locally but do not push._

## R-112 — evidence source

Reviewed:
- `3F224.c` (`-[CNABHostUIAppResponder onUIAppRequest:]`);
- raw ARM64 for `3F224` from the first arm64 FAT slice;
- Mach-O LSDA `0x114960`;
- the existing compile-safe host UI-app responder/mirror path in `ReconstructionRuntime.m`.

The first arm64 FAT slice begins at file offset `0x4000`.

Mach-O maps:
- `3F224 -> LSDA 0x114960`.

Decoded call-site table:
- `0x3F224..0x3F248` -> no landing pad;
- `0x3F248..0x3F26C` -> landing `0x3F350`, action 5;
- `0x3F26C..0x3F294` -> no landing pad;
- `0x3F294..0x3F29C` -> landing `0x3F34C`, action 5;
- `0x3F2B8..0x3F2D4` -> landing `0x3F354`, action 5;
- `0x3F310..0x3F324` -> landing `0x3F348`, action 5;
- `0x3F324..0x3F36C` -> no landing pad.

## One common request catch

Raw ARM64 shows:
- `0x3F348 -> 0x3F354`;
- `0x3F34C -> 0x3F354`;
- `0x3F350 -> 0x3F354`.

Common catch `0x3F354`:
- compare catch discriminator with expected value 1;
- expected type:
  - begin catch at `0x3F35C`;
  - end catch at `0x3F360`;
  - branch to `0x3F32C`;
- nonmatching type:
  - branch to `0x3F368`;
  - resume unwind.

`0x3F32C` is the final retained request-argument cleanup/return path. Therefore every expected protected exception abandons all remaining custom request processing and returns normally after cleanup.

There is no reason probe, retry, diagnostic counter, alternate slot fallback, or later `89D8` attempt after the catch.

## Protected request stages

### Request userInfo / bundle extraction

Protected range:
- `0x3F248..0x3F26C` -> landing `0x3F350` -> common catch.

Raw ARM64 covers:
- request/notification `userInfo` retrieval;
- retain-autoreleased handling;
- `objectForKeyedSubscript:@"bundleIdentifier"`;
- retain-autoreleased bundle result.

Expected exception here:
- is swallowed;
- skips bundle-length gating;
- skips host-slot scan;
- skips final UI-app-state request/publish;
- jumps directly to final cleanup.

### Candidate bundle length gate

Protected range:
- `0x3F294..0x3F29C` -> landing `0x3F34C` -> common catch.

It covers the candidate bundle `length` call that gates slot matching.

Expected exception here:
- is swallowed;
- skips the slot scan and final request dispatch;
- goes to final cleanup.

### Host-slot string matching

Protected range:
- `0x3F2B8..0x3F2D4` -> common catch `0x3F354`.

It covers the per-slot loop operations:
- configured host bundle `length`;
- CarPlay-slot exclusion check around those calls;
- candidate `isEqualToString:` against the configured host bundle.

Expected exception here:
- aborts the remaining slot scan;
- does not try later slots;
- skips final request dispatch;
- goes to final cleanup.

### Final `89D8` request/state publication

Protected range:
- `0x3F310..0x3F324` -> landing `0x3F348` -> common catch.

It covers the final call:
- `89D8(bundle, 1, qword_162F08, byte_163DC0, width, height)`
when a matched slot supplied positive width.

Expected exception from `89D8`:
- is swallowed;
- is not retried;
- jumps directly to final cleanup/return.

## Nonmatching catch discriminator

For every protected range, a nonmatching discriminator at common catch `0x3F354` branches to `0x3F368` and resumes unwind.

Promoted metadata:
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

The reconstruction does not synthesize foreign/nonmatching exceptions or execute unwind machinery.

## Promoted runtime contract

Added:
- `DDHostUIAppRequestExceptionOutcome`;
- `DDResolveHostUIAppRequestExceptionOutcome(void)`.

Exact constant outcome for the expected typed path:
- `shouldSwallowException = YES`;
- `shouldContinueCleanupAfterCatch = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

A site enum is unnecessary because all protected request ranges converge on the same common catch and final-cleanup continuation.

## Relationship to the existing compile-safe responder

The reconstruction already has `DDConsumeHostUIAppRequestUserInfo`, which consumes a caller-visible dictionary safely against the host mirror and publishes via `DDPostUIAppState` only for a matched non-CarPlay slot with positive width.

R-112 does not change that normal path and does not wrap it in synthetic exception handling. It only adds the original binary's data-only exception continuation descriptor for evidence and higher-level testing.

## Explicit exclusions

R-112 does not:
- synthesize or catch Objective-C/foreign exceptions;
- execute begin-catch/end-catch/resume-unwind runtime APIs;
- read a live notification/request `userInfo` through the original private path;
- invoke `objectForKeyedSubscript:` as part of the original callback;
- traverse private host-slot globals/strings;
- invoke original `89D8`;
- mutate host-slot sizes, flags, orientation, split state, cached UI settings, or other globals.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — `3F3F0`

Mach-O maps:
- `3F3F0 -> LSDA 0x114994`.

Decoded call-site table:
- `0x3F3F0..0x3F4BC` -> no landing pad;
- `0x3F4BC..0x3F4D4` -> landing `0x3F5A8`, action 5;
- `0x3F4D4..0x3F5C0` -> no landing pad.

The only protected range is exactly the `89D8` publish call after the resize mirror has already accepted/stored the new slot size.

Raw ARM64 landing `0x3F5A8`:
- compare catch discriminator with expected value 1;
- expected type:
  - begin catch;
  - end catch;
  - branch back to `0x3F4D4`;
- nonmatching type:
  - branch to `0x3F5BC`;
  - resume unwind.

`0x3F4D4` is the beginning of the post-publish follow-up, not cleanup:
- normalize `dword_163E88` attempt count to zero when current >=1;
- floor `dword_162F1C` general counter to 4 when current <=3;
- obtain `DDz2 shared`;
- call `probeSceneForSlot:`;
- if a scene exists, apply accepted landscape size swap and call `3F5C0`.

Thus an expected `89D8` exception:
- is swallowed;
- publish is not retried;
- all post-publish counter normalization and scene/private-update follow-up remains eligible.

## Next

R-113 after compiler green:
- promote exact `3F3F0` `89D8` catch -> continue post-publish follow-up plus nonmatching-type unwind metadata;
- keep `89D8`, private DDz2 scene probe, `3F5C0`, counter/global mutation, exception synthesis, and unwind execution excluded.
