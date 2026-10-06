# LOG/session-105.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-104 commit bf38894; complete R-104 by decoding `40514` LSDA/raw-ARM64 exception behavior and promoting only evidence-safe data-only continuation/probe/unwind outcomes. Per user workflow, commit locally but do not push._

## R-104 — evidence source

Reviewed:
- `40514.c`;
- raw ARM64 for `40514` from the first arm64 FAT slice;
- Mach-O `__unwind_info` / `__gcc_except_tab` mapping;
- existing R-082 direct-orientation/snapshot/settingsDiff decisions;
- existing `41BA0` bounded reason-probe contract.

The first arm64 FAT slice begins at file offset `0x4000`.

`__unwind_info` maps:
- `40514` -> LSDA `0x114B58`.

Decoded call-site table:
- `0x40514..0x40588` -> no landing pad;
- `0x40588..0x405A8` -> landing `0x40A88`, action 7;
- `0x405AC..0x405C0` -> landing `0x40A7C`, action 5;
- `0x405C0..0x405CC` -> landing `0x40A78`, action 5;
- `0x405D8..0x40618` -> landing `0x40A84`, action 5;
- `0x40624..0x40630` -> landing `0x40A74`, action 5;
- `0x4063C..0x40648` -> landing `0x40A70`, action 5;
- `0x40654..0x40664` -> landing `0x40A6C`, action 5;
- `0x40668..0x40678` -> landing `0x40A54`, action 5;
- `0x4067C..0x40688` -> landing `0x40A50`, action 5;
- `0x40694..0x406C4` -> landing `0x40A84`, action 5;
- `0x406D4..0x40738` -> landing `0x40A5C`, action 5;
- `0x4075C..0x40790` -> landing `0x40A80`, action 5;
- `0x40794..0x407A0` -> landing `0x40A4C`, action 5;
- `0x407C0..0x407CC` -> landing `0x40A48`, action 5;
- `0x407DC..0x407E8` -> landing `0x40A44`, action 5;
- `0x40850..0x40870` -> landing `0x40A3C`, action 5;
- `0x40884..0x408A8` -> landing `0x40A68`, action 5;
- `0x408B4..0x408D0` -> landing `0x40A64`, action 5;
- `0x408D0..0x408EC` -> landing `0x40A60`, action 5;
- `0x40900..0x4090C` -> landing `0x40A40`, action 5;
- `0x4090C..0x40960` -> landing `0x40A58`, action 5;
- `0x40964..0x409B0` -> landing `0x40A38`, action 5;
- `0x409B0..0x409E8` -> no landing pad;
- `0x409E8..0x409FC` -> landing `0x40AA4`, action 7;
- `0x409FC..0x40AC4` -> no landing pad;
- `0x40AC4..0x40AC8` -> landing `0x40AD8`, cleanup/action 0;
- `0x40AC8..0x40AE8` -> no landing pad.

## One common custom-path catch

Every small custom-path landing from `0x40A38` through `0x40A84` is only a branch to `0x40A88`.

`0x40A88`:
1. preserves the thrown exception;
2. verifies the expected catch type;
3. begins catch;
4. ends catch;
5. branches to `0x409E0`, the original callback setup.

Therefore all protected custom-path exceptions have the same continuation:
- swallow;
- abandon the remaining custom settings/snapshot/diff work;
- call original.

There is no reason probe on this catch.

## Protected custom-path coverage

The common catch covers all protected calls in the custom branch, including:

### Initial eligibility/settings acquisition
- `41CBC` route eligibility;
- callback-object `settings` capability/read;
- raw desired orientation through `3FAF8`;
- `settingsDiff` capability/read;
- aux detection through `3FB54`.

### Aux snapshot before mutation
- `interfaceOrientation` capability/read;
- `frame` capability/read;
- `isForeground` capability/read.

### Non-aux direct repair
- `42124` force-interface-orientation decision;
- direct private integer repair through `9C3BC`.

### Diff fallback construction setup
- `mutableCopyWithZone:` capability/read;
- retained mutable copy;
- `setFrame:` capability/send on the copy.

### Aux mutation + snapshot after mutation
- adjusted size through `41E94`;
- nested private settings mutation through `41F50`;
- after-mutation `interfaceOrientation`, `frame`, and `isForeground` reads.

### Existing settingsDiff clear path
- callback-object `setSettingsDiff:` capability check;
- `setSettingsDiff:nil` send.

### Diagnostic reads after the bounded diff counter
- scene `settings` capability/read;
- current and scene-settings `interfaceOrientation` capability/read.

### FBSSceneSettingsDiff fallback path
- `objc_getClass("FBSSceneSettingsDiff")`;
- scene `settings` capability/read;
- class `diffFromSettings:toSettings:` capability/send;
- callback-object `setSettingsDiff:` capability/send with the constructed diff.

Although these ranges have both action 7 and action 5 entries in LSDA, raw ARM64 proves they converge to the same catch body and continuation.

## Normal-path counter/state side effects are not rolled back

The function increments `qword_163E18` before entering the protected custom path. A later caught exception does not roll that increment back.

Likewise the normal path may decrement `dword_162F38` before later diagnostic/FBSSceneSettingsDiff work. If a protected call after that decrement throws, the common catch falls back to original and does not restore the counter.

R-104 does not model either mutation or rollback; the promoted contract records only the continuation.

## Original-callback exception

The indirect original callback is exactly:
- `0x409E8..0x409FC` -> landing `0x40AA4`, action 7.

Landing behavior:
1. verify expected catch type;
2. begin catch;
3. retain the caught exception;
4. call existing `41BA0(exception)` at `0x40AC4`;
5. release the retained exception;
6. end catch;
7. branch to `0x409FC`, final argument/object cleanup and return.

Therefore an original-callback exception:
- is swallowed;
- original is not retried;
- applies the existing `DDResolveExceptionReasonProbeDecision` contract;
- continues final cleanup only if the probe completes normally.

## Nested reason-probe exception

The `41BA0` call is protected separately:
- `0x40AC4..0x40AC8` -> landing `0x40AD8`, cleanup/action 0.

Raw ARM64 at `0x40AD8`:
- preserves the newly thrown exception;
- ends the outer catch;
- falls into the unwind/resume path at `0x40AE0`.

Thus a nested reason-probe exception resumes unwind instead of reaching final cleanup.

## Promoted runtime contract

Added:
- `DDFBSSettingsCallbackExceptionSite`
  - None
  - CustomPath
  - OriginalCallback
- `DDFBSSettingsCallbackExceptionOutcome`
- `DDResolveFBSSettingsCallbackExceptionOutcome(site, currentProbeCount, reasonSelectorSupported)`.

CustomPath outcome:
- `shouldSwallowException = YES`;
- `shouldCallOriginalAfterCatch = YES`.

OriginalCallback outcome:
- `shouldSwallowException = YES`;
- `shouldApplyReasonProbeDecision = YES`;
- `probeExceptionWouldResumeUnwind = YES`;
- `shouldContinueCleanupAfterProbe = YES`;
- `reasonProbeDecision = DDResolveExceptionReasonProbeDecision(...)`;
- no original retry.

## Explicit exclusions

R-104 does not:
- synthesize Objective-C exceptions;
- call begin-catch/end-catch;
- invoke private scene/settings traversal;
- invoke `41CBC`, `3FAF8`, `3FB54`, `42124`, `9C3BC`, `41E94`, or `41F50`;
- read or write `settings`, `settingsDiff`, `frame`, `isForeground`, or `interfaceOrientation` through selectors;
- construct or invoke `FBSSceneSettingsDiff`;
- send `setFrame:` or `setSettingsDiff:`;
- call the original callback;
- invoke `41BA0` or read exception `reason`;
- mutate `qword_163E18`, `dword_162F38`, settings objects, or any global state;
- intercept or resume unwind.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — 40AE8

Mach-O unwind mapping:
- `40AE8` -> LSDA `0x114C10`.

Decoded call-site table:
- `0x40AE8..0x40B40` -> no landing pad;
- `0x40B40..0x40B54` -> landing `0x40C18`, action 1;
- `0x40B54..0x40BB8` -> no landing pad;
- `0x40BB8..0x40BD4` -> landing `0x40BFC`, action 1;
- `0x40BD4..0x40C38` -> no landing pad;
- `0x40C38..0x40C3C` -> landing `0x40C4C`, cleanup/action 0;
- `0x40C3C..0x40C5C` -> no landing pad.

Raw ARM64 already establishes three materially different outcomes:

1. Original callback (`0x40B40..0x40B54`) catch at `0x40C18`:
   - swallow;
   - retain exception;
   - call `41BA0`;
   - if probe completes, end catch and branch to `0x40B54`, continuing post-original evaluation rather than returning.

2. Post-original nopresupdate file-manager probe (`0x40B68..0x40B98`) lies inside a **no-landing-pad** range:
   - exceptions there propagate/resume unwind through `40AE8`;
   - they are not swallowed by this callback.

3. `_updateFrameAndTransform` capability/send (`0x40BB8..0x40BD4`) catch at `0x40BFC`:
   - swallow;
   - branch to normal cleanup `0x40BD4`;
   - no reason probe.

Nested `41BA0` throw:
- `0x40C38..0x40C3C` -> cleanup landing `0x40C4C` -> end catch + resume unwind.

## Next

R-105 after compiler green:
- promote the exact `40AE8` original-callback probe→post-original continuation, unprotected file-manager propagate/unwind behavior, and `_updateFrameAndTransform` catch→cleanup outcome;
- keep file I/O, private selector invocation, original callback invocation, exception synthesis, reason reads, and all global mutation excluded.
