# LOG/session-120.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-119 commit 3ac49b3; complete R-119 by promoting exact data-only `3E02C` scene/settings diagnostic-summary exception behavior from LSDA/raw ARM64/export metadata. Per user workflow, commit locally but do not push._

## R-119 — evidence source

Reviewed:
- `3E02C.c`;
- raw ARM64 for `3E02C` from the first arm64 FAT slice;
- Mach-O LSDA `0x114818`;
- export pointer/memory metadata for CFString object `0x147C18`.

The first arm64 FAT slice begins at file offset `0x4000`.

Mach-O maps:
- `3E02C -> LSDA 0x114818`.

Decoded call-site table:
- `0x3E02C..0x3E05C` -> no landing pad;
- `0x3E05C..0x3E080` -> landing `0x3E27C`, action 5;
- `0x3E090..0x3E0B4` -> landing `0x3E278`, action 5;
- `0x3E0C4..0x3E0E8` -> landing `0x3E274`, action 5;
- `0x3E0F0..0x3E0FC` -> landing `0x3E268`, action 5;
- `0x3E0FC..0x3E10C` -> landing `0x3E264`, action 5;
- `0x3E10C..0x3E130` -> landing `0x3E26C`, action 5;
- `0x3E130..0x3E1B0` -> no landing pad;
- `0x3E1B0..0x3E23C` -> landing `0x3E270`, action 5;
- `0x3E23C..0x3E29C` -> no landing pad.

Landing stubs `0x3E264`, `0x3E268`, `0x3E26C`, `0x3E270`, `0x3E274`, and `0x3E278` all branch to common typed catch `0x3E27C`.

## Exact fallback CFString

Raw ARM64 expected catch:
- `0x3E27C`: compare catch discriminator with expected value 1;
- `0x3E284`: begin catch;
- `0x3E288`: end catch;
- `0x3E28C`: load CFString object at image address `0x147C18`;
- `0x3E294`: branch to final outer return path `0x3E174`.

Export metadata resolves:
- `0x147C18 -> cfstr_Threw`;
- backing string pointer `0xBB6A9`;
- exact ASCII literal `"threw"`;
- length 5.

The runtime contract represents this as enum `DDSceneDiagnosticSummaryFallbackThrew` instead of storing an Objective-C object pointer inside the C outcome struct. This keeps the descriptor compile-safe/data-only while preserving the exact fallback identity.

## Common expected-catch behavior

For every protected site:
- swallow the expected exception locally;
- abandon all remaining diagnostic-summary construction;
- select fallback summary `"threw"`;
- branch directly to `0x3E174`;
- release only the retained outer input object at the final return path;
- no retry, reason probe, diagnostic counter, or alternate summary source.

A nonmatching catch discriminator branches to `0x3E298` and resumes unwind.

## Site 1 — sceneHandle resolution

Protected range:
- `0x3E05C..0x3E080`.

Covers:
- `respondsToSelector:sceneHandle`;
- optional `sceneHandle` send;
- retain-autoreleased handling.

At the start of this protected range no intermediate scene object has yet been retained into a stable local register. Therefore the descriptor records:
- guaranteed retained-intermediate release bypass count = 0.

The outer retained input is still released by final cleanup.

## Site 2 — nested scene resolution

Protected range:
- `0x3E090..0x3E0B4`.

The previously resolved sceneHandle is already retained in `x20` before this site starts.

Normal no-scene/success cleanup eventually releases `x20` before final return. The catch jumps directly to `0x3E174`, bypassing that intermediate release.

Descriptor:
- guaranteed bypass count = 1.

## Site 3 — nested settings resolution

Protected range:
- `0x3E0C4..0x3E0E8`.

Before this site starts:
- `x20` = retained sceneHandle;
- `x21` = retained scene.

Expected catch bypasses both normal intermediate releases and goes directly to outer-input cleanup.

Descriptor:
- guaranteed bypass count = 2.

## Site 4 — selector construction

Protected ranges:
- `0x3E0F0..0x3E0FC` for `NSSelectorFromString("isForeground")`;
- `0x3E0FC..0x3E10C` for `NSSelectorFromString("deactivationReasons")`.

Before either selector-construction site starts:
- sceneHandle `x20` is retained;
- scene `x21` is retained;
- settings `x22` is retained.

Selectors themselves are not retained ObjC intermediates requiring release.

Descriptor for both selector ranges:
- guaranteed bypass count = 3.

## Site 5 — foreground probe/getter

Protected range:
- `0x3E10C..0x3E130`.

Covers:
- `3E29C(settings, isForegroundSelector)` type probe;
- optional `isForeground` getter.

At entry, the same three scene/settings intermediates are definitely retained. The foreground summary string retain occurs later outside this protected range, so it is not counted as guaranteed prior state.

Descriptor:
- guaranteed bypass count = 3.

## Site 6 — deactivation probe and formatting

Protected range:
- `0x3E1B0..0x3E23C`.

Covers:
- `3E29C(settings, deactivationReasonsSelector)`;
- optional deactivation getter;
- `+[NSString stringWithFormat:@"0x%llx"]`;
- final `+[NSString stringWithFormat:@"fg=%@ deact=%@"]`;
- retain-autoreleased handling for formatted strings.

At entry, sceneHandle/scene/settings are definitely retained, giving guaranteed bypass count 3.

Additional conditional intermediates may also already exist or be created before a later call in this same protected range throws:
- retained foreground display string in `x23` when the type probe succeeded;
- retained formatted deactivation string in `x25` when formatting completed.

The catch bypasses normal releases at `0x3E240..0x3E258`. Because those extra objects are conditional and depend on where within the protected range the exception occurs, the runtime exposes only:
- `additionalFormattedIntermediateReleaseCouldBeBypassed = YES`.

It does not invent an exact extra-count value.

## Promoted runtime contract

Added:
- `DDSceneDiagnosticSummaryExceptionSite` with six semantic sites;
- `DDSceneDiagnosticSummaryFallbackKind` with exact `FallbackThrew`;
- `DDSceneDiagnosticSummaryExceptionOutcome`;
- `DDResolveSceneDiagnosticSummaryExceptionOutcome(site)`.

For every valid site:
- `shouldSwallowException = YES`;
- `shouldReturnFallbackSummary = YES`;
- `fallbackKind = DDSceneDiagnosticSummaryFallbackThrew`;
- `shouldContinueFinalOuterCleanup = YES`;
- `nonmatchingCatchTypeWouldResumeUnwind = YES`.

Guaranteed intermediate-release-bypass counts:
- sceneHandle resolution = 0;
- scene resolution = 1;
- settings resolution = 2;
- selector construction = 3;
- foreground probe = 3;
- diagnostic formatting = 3.

Final formatting additionally sets:
- `additionalFormattedIntermediateReleaseCouldBeBypassed = YES`.

Unknown/None site returns an all-false/None outcome.

## Explicit exclusions

R-119 does not:
- traverse live sceneHandle/scene/settings objects;
- invoke `respondsToSelector:` or private selectors;
- invoke `3E29C`;
- invoke `NSString stringWithFormat:`;
- retain/release or intentionally leak live private objects;
- synthesize/catch Objective-C or foreign exceptions;
- execute begin-catch/end-catch/resume-unwind runtime APIs.

Lifetime fields describe original control flow only.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — `3DD4C`

Direct `__unwind_info` LSDA enumeration shows the immediately preceding exception-bearing function:
- `3DD4C -> LSDA 0x1147EC`.

Decoded call-site table:
- `0x3DD4C..0x3DDB0` -> no landing pad;
- `0x3DDB0..0x3DDBC` -> landing `0x3DFA8`, action 5;
- `0x3DDBC..0x3DEF4` -> no landing pad;
- `0x3DEF4..0x3DF0C` -> landing `0x3DF54`, action 5;
- `0x3DF0C..0x3DFC8` -> no landing pad.

### Early application-controller lookup catch

Protected range `0x3DDB0..0x3DDBC` covers:
- `+[SBApplicationController sharedInstance]` send;
- retain-autoreleased handling.

Landing `0x3DFA8`:
- compare discriminator with expected type 1;
- expected catch begin/end;
- set controller register `x22 = nil`;
- restore saved requested count;
- branch back to `0x3DDC8`.

At `0x3DDC8`, the normal `respondsToSelector:applicationWithBundleIdentifier:` test runs against nil, fails safely, and the function proceeds into array canonicalization with no validation controller.

Therefore expected early exception semantics:
- swallow;
- controller becomes nil;
- continue normal bundle canonicalization rather than returning/failing.

Nonmatching type -> `0x3DFC4` resume unwind.

### Per-item application lookup catch

Protected range `0x3DEF4..0x3DF0C` covers:
- `applicationWithBundleIdentifier:` send on the controller;
- retain-autoreleased handling for returned app.

Landing `0x3DF54`:
- compare discriminator with expected type 1;
- expected catch begin/end;
- restore saved requested count;
- branch to `0x3DF28`.

`0x3DF28` is the normal point that adds current sanitized candidate `x27` to the output array, releases candidate/original input intermediates, increments index, and continues the loop.

Therefore expected per-item exception semantics:
- swallow;
- preserve the already sanitized/deduplicated candidate string;
- skip only the app-existence validation for that item;
- still add the candidate to output;
- continue the remaining loop.

Nonmatching type -> common `0x3DFC4` resume unwind.

## Next

R-120 after compiler green:
- promote `3DD4C` two-site application-validation exception continuation metadata;
- early lookup catch -> controller nil + continue canonicalization;
- per-item lookup catch -> preserve candidate + add/continue loop;
- both nonmatching types -> resume unwind;
- keep SpringBoard controller/private selector invocation, live app lifetime effects, array mutation, exception synthesis, and unwind execution excluded.
