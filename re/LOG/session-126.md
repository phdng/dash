# LOG/session-126.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-125 commit `123b913`; decode and promote exact data-only `3C368` aux-scene creation exception behavior from Mach-O LSDA/raw ARM64, verify, and commit locally without pushing._

## Start state

- Branch: `chore/reconstruction-build-ci`.
- HEAD at session start: `123b913`.
- Working tree: clean.
- Branch synchronized with origin.
- User confirmed the session-125 macOS CI/compiler build was green.

## Target selection

Persisted unwind enumeration from session-125 showed:

- `3C808 -> LSDA 0x11466C`;
- `3C368 -> LSDA 0x1145D8`;
- `3C1F0 -> LSDA 0x1145B8`;
- `3BBF0 -> LSDA 0x114538`.

R-124 completed `3C808`, so R-125 targets the immediately preceding LSDA-bearing function `3C368`.

Reviewed:
- `decompile/3C368.c`;
- raw ARM64 `0x3C368..0x3C808`;
- Mach-O LSDA bytes at `0x1145D8`;
- existing evidence-safe aux mirror/state-machine contracts from sessions 080-081;
- existing `3C808` teardown exception contract from R-124.

The first arm64 FAT slice begins at file offset `0x4000`.

## Exact LSDA call-site table

LSDA header:
- LPStart encoding: omitted;
- type-table encoding: `0x9B`;
- call-site encoding: ULEB128;
- call-site table length: `0x81` bytes.

Decoded entries:

1. `0x3C368..0x3C488` -> no landing pad.
2. `0x3C488..0x3C498` -> landing `0x3C7B4`, action 5.
3. `0x3C4A4..0x3C4C8` -> landing `0x3C7C0`, action 5.
4. `0x3C4C8..0x3C4F0` -> no landing pad.
5. `0x3C4F0..0x3C518` -> landing `0x3C7C0`, action 5.
6. `0x3C518..0x3C52C` -> no landing pad.
7. `0x3C52C..0x3C548` -> landing `0x3C7C0`, action 5.
8. `0x3C548..0x3C558` -> no landing pad.
9. `0x3C558..0x3C57C` -> landing `0x3C7B8`, action 5.
10. `0x3C57C..0x3C594` -> no landing pad.
11. `0x3C594..0x3C5B0` -> landing `0x3C7AC`, action 5.
12. `0x3C5B0..0x3C5BC` -> no landing pad.
13. `0x3C5BC..0x3C5E4` -> landing `0x3C7BC`, action 5.
14. `0x3C5E4..0x3C608` -> no landing pad.
15. `0x3C608..0x3C650` -> landing `0x3C7BC`, action 5.
16. `0x3C658..0x3C6AC` -> landing `0x3C7B0`, action 5.
17. `0x3C6AC..0x3C750` -> no landing pad.
18. `0x3C750..0x3C758` -> landing `0x3C7B8`, action 5.
19. `0x3C760..0x3C768` -> landing `0x3C7BC`, action 5.
20. `0x3C770..0x3C778` -> landing `0x3C7B0`, action 5.
21. `0x3C778..0x3C7E0` -> no landing pad.
22. `0x3C7E0..0x3C7E8` -> landing `0x3C7F8`, action 0.

All action-5 landing stubs:
- `0x3C7AC`;
- `0x3C7B0`;
- `0x3C7B4`;
- `0x3C7B8`;
- `0x3C7BC`;

branch to common typed catch `0x3C7C0`.

## Protected creation work

The twelve action-5 ranges cover distinct phases of the private aux creation flow.

### Application lookup

`0x3C488..0x3C498`:
- `SBApplicationController sharedInstance`;
- retain-autoreleased handling.

`0x3C4A4..0x3C4C8`:
- `applicationWithBundleIdentifier:`;
- retain-autoreleased handling;
- branch based on whether an application was found.

### Post-application state/file preparation

`0x3C4F0..0x3C518`:
- `3E428` generation-state refresh after aux bid/native/orientation commit;
- default file-manager acquisition;
- first file-flag probe (`duodash_kp_noauxsid`).

`0x3C52C..0x3C548`:
- second default file-manager acquisition;
- second file-flag probe (`duodash_kp_noapplydiff`).

### Private entity/controller construction

`0x3C558..0x3C57C`:
- allocate `SBDeviceApplicationSceneEntity`;
- `initWithApplicationForMainDisplay:`;
- retain-autoreleased handling.

`0x3C594..0x3C5B0`:
- `NSUUID UUID`;
- retain UUID;
- `UUIDString`;
- retain resulting string.

`0x3C5BC..0x3C5E4`:
- allocate `SBAppViewController`;
- `initWithIdentifier:andApplicationSceneEntity:`;
- retain-autoreleased handling.

### Private controller configuration / view acquisition

`0x3C608..0x3C650`:
- capability probe + optional `setIgnoresOcclusions:`;
- capability probe + optional `setAutomatesLifecycle:`.

`0x3C658..0x3C6AC`:
- `view` send + retain-autoreleased view;
- capability probe + optional `setRequestedMode:2`;
- view-presence branch;
- initial orientation/update capability gate.

### Protected normal failure teardowns

The final three action-5 ranges are themselves normal failure-path calls to `teardownAuxScene`:

- `0x3C750..0x3C758`;
- `0x3C760..0x3C768`;
- `0x3C770..0x3C778`.

These occur on different private construction/view failure branches.

## Common typed catch 0x3C7C0

Raw ARM64:

- save exception object;
- compare catch discriminator with expected value 1;
- nonmatching -> `0x3C800` resume unwind;
- expected type:
  - begin catch;
  - retain caught object;
  - invoke `[DDz2 teardownAuxScene]`;
  - release caught object;
  - end catch;
  - branch to `0x3C3D8`.

`0x3C3D8` is the existing nil-return path.

Therefore every expected action-5 exception:

- is swallowed locally;
- requests aux-scene teardown;
- abandons all remaining creation work;
- exits through the function's nil-return path.

For the three action-5 ranges whose throwing operation was already a normal failure-path `teardownAuxScene` call, the common catch invokes `teardownAuxScene` again. This is an exact single catch-level teardown retry.

The resolver represents the retry distinction as metadata; it does not invoke teardown.

## Nested exception from teardown inside the catch

The catch-internal teardown send is itself covered by:

- `0x3C7E0..0x3C7E8` -> landing `0x3C7F8`, action 0.

At `0x3C7F8`:
- preserve nested exception;
- call `objc_end_catch`;
- continue to `0x3C800`;
- resume unwind.

Thus a teardown exception raised while handling the first expected exception:

- is not swallowed by another local typed catch;
- performs active-catch cleanup;
- propagates/resumes unwind.

This also prevents interpreting the catch-level teardown as an unbounded retry loop: the original performs at most the one retry induced by entry into the common catch.

## Unprotected ranges

All no-landing-pad ranges propagate normally.

R-125 exposes a generic unprotected-range propagation outcome rather than assigning invented behavior to individual unprotected calls.

## Promoted runtime contract

Added:

- `DDAuxSceneCreationExceptionSite`:
  - `ProtectedCreationWork`;
  - `ProtectedFailureTeardown`;
  - `CatchTeardown`;
  - `UnprotectedRange`;
- `DDAuxSceneCreationExceptionOutcome`;
- `DDResolveAuxSceneCreationExceptionOutcome(site)`.

For `ProtectedCreationWork`:
- `shouldSwallowException = YES`;
- `shouldInvokeTeardownFromCatch = YES`;
- `shouldSkipRemainingCreation = YES`;
- `shouldReturnNilScene = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

For `ProtectedFailureTeardown`, the same flags apply plus:
- `shouldRetryTeardownFromCatch = YES`.

For `CatchTeardown`:
- `shouldEndActiveCatchBeforeResumeUnwind = YES`;
- `exceptionWouldPropagate = YES`.

For `UnprotectedRange`:
- `exceptionWouldPropagate = YES`.

Unknown/None returns all false.

## Relationship to existing aux mirror

Existing reconstruction already has:
- `DDPrepareAuxSceneCandidate`;
- `DDCommitAuxSceneMirrorAfterApplicationLookup`;
- `DDClearAuxSceneMirror`;
- aux settings/retry state-machine descriptors.

R-125 does not wire the exception resolver into those state mutators. The resolver is descriptive data-only metadata for the original private control flow.

## Explicit exclusions

R-125 does not:

- query `SBApplicationController`;
- invoke `applicationWithBundleIdentifier:`;
- allocate or initialize `SBDeviceApplicationSceneEntity`;
- allocate/configure `SBAppViewController`;
- invoke private controller `view`, lifecycle setters, or requested-mode setters;
- invoke `teardownAuxScene`;
- mutate live aux controller ivars/globals/mirror state from the resolver;
- alter real object lifetime;
- synthesize/catch Objective-C or foreign exceptions;
- invoke begin-catch/end-catch/resume-unwind machinery.

## Verification

After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final verifier, CatDesk standard verification status, and `git diff --check` are run immediately before commit.

## Scout for next batch — 3C1F0

Direct unwind enumeration shows the next earlier LSDA-bearing function:
- `3C1F0 -> LSDA 0x1145B8`.

Decompiler identity:
- `-[DDz2 degradeSlot:bid:native:why:]`.

Normal decompile shows:
- retain selected hosted controller ivar;
- optional `viewIfLoaded`;
- remove view;
- optional `invalidate`;
- clear selected controller ivar;
- replace hosted-bid slot with empty string;
- create placeholder via `36E98`.

R-126 should decode the exact LSDA/raw ARM64 continuation before promoting any exception behavior, especially whether private teardown failure still reaches ivar/bid clear and placeholder creation.

## Next

After the user pushes session-126 and confirms compiler green:
- R-126: decode `3C1F0 -> LSDA 0x1145B8`;
- promote only evidence-safe data-only continuation/order metadata;
- keep private hosted controller/view mutation and placeholder creation out of the resolver.

Known unresolved items remain:
- `73E8` / `80D0` bounds;
- full `7E908` blacklist/numerics;
- jailbroken-device runtime smoke testing.
