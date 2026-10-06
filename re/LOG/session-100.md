# LOG/session-100.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-099 commit 3887d1d; complete R-099 by decoding `4138C` LSDA/raw-ARM64 exception behavior and promoting only data-only continuation/probe/unwind outcomes. Per user workflow, commit locally but do not push._

## R-099 — evidence source

Reviewed:
- `4138C.c`;
- raw ARM64 for `4138C` from the first arm64 FAT slice;
- Mach-O `__unwind_info` / `__gcc_except_tab` mapping;
- existing R-092 `4138C` update-routing and original-suppression decisions;
- existing `41BA0` bounded reason-probe contract.

The first arm64 FAT slice begins at file offset `0x4000`.

`__unwind_info` maps:
- `4138C` -> LSDA `0x114D2C`.

The decoded call-site table is:
- `0x4138C..0x413FC` -> no landing pad;
- `0x413FC..0x41420` -> landing `0x41640`, action 5;
- `0x4142C..0x41430` -> landing `0x4163C`, action 5;
- `0x41430..0x41440` -> landing `0x41638`, action 5;
- `0x41440..0x41448` -> landing `0x41648`, action 5;
- `0x4145C..0x41470` -> landing `0x4164C`, action 5;
- `0x41484..0x4148C` -> landing `0x41648`, action 5;
- `0x41498..0x414BC` -> landing `0x41630`, action 5;
- `0x41534..0x41540` -> landing `0x41648`, action 5;
- `0x41548..0x4155C` -> landing `0x41630`, action 5;
- `0x4155C..0x41578` -> no landing pad;
- `0x41578..0x4159C` -> landing `0x41634`, action 5;
- `0x415AC..0x415C8` -> landing `0x4162C`, action 5;
- `0x415CC..0x415E4` -> landing `0x41628`, action 5;
- `0x415E4..0x41684` -> no landing pad;
- `0x41684..0x4169C` -> landing `0x416EC`, action 7;
- `0x4169C..0x4170C` -> no landing pad;
- `0x4170C..0x41710` -> landing `0x41720`, cleanup/action 0;
- `0x41710..0x41730` -> no landing pad.

## Initial scene lookup exception

Protected range `0x413FC..0x41420` covers the initial scene-object capability/read path:
- `respondsToSelector:scene`;
- the private `scene` send;
- retain-autoreleased-return-value handling.

Its landing pad `0x41640` routes to the catch body at `0x416D4`.

Raw ARM64 there:
1. verifies the expected catch type;
2. begins catch;
3. ends catch;
4. branches to `0x4167C`, the original-callback path.

Therefore an exception while obtaining the scene:
- is swallowed;
- skips all custom update routing;
- skips foreground-based suppression evaluation;
- calls the original callback.

## Update-routing exceptions

The following protected ranges all converge on the common catch at `0x4164C` (some through tiny branch landing pads):
- `0x4142C..0x41430`: `41C24` pane-orientation/nopane probe;
- `0x41430..0x41440`: first `3FBC8` identity resolution + retain;
- `0x41440..0x41448`: identity length check;
- `0x4145C..0x41470`: configured-slot length/equality checks;
- `0x41484..0x4148C`: aux identity check through `3FFC0`;
- `0x41498..0x414BC`: aux scene-settings capability/read path;
- `0x41534..0x41540`: private host update boundary `3F5C0`;
- `0x41548..0x4155C`: private aux update boundary `3E670`.

The common catch at `0x4164C`:
1. verifies expected catch type;
2. begins catch;
3. ends catch;
4. tests saved scene object `x24`;
5. when scene exists, branches to `0x41570`, the foreground-suppression evaluation stage;
6. when scene is absent, falls through cleanup and then `0x4167C`, the original callback.

Therefore any protected update-routing exception:
- is swallowed;
- abandons the remaining update route;
- does not retry the private update operation;
- if scene exists, still evaluates whether the original callback should be suppressed;
- if scene is absent, calls original directly.

This includes exceptions thrown by the private `3F5C0` and `3E670` boundaries. The reconstruction records only the continuation choice and never invokes either helper.

## Suppression-decision exceptions

Three protected ranges map through `0x41640` to the catch that calls original:
- `0x41578..0x4159C`: scene `settings` capability/read;
- `0x415AC..0x415C8`: settings `isForeground` capability/read;
- `0x415CC..0x415E4`: second `3FBC8` identity resolution plus `3E4A8` non-CarPlay-host match.

Therefore an exception while deciding foreground suppression:
- is swallowed;
- suppression is abandoned;
- the original callback is called.

The normal suppression diagnostic counter `qword_163EB8` is not incremented by these catch paths; its bounded behavior remains modeled only by the existing normal-path `DDResolveAVCSceneHandleCallbackDecision` contract.

## Original-callback exception

The indirect original callback is exactly the protected range:
- `0x41684..0x4169C` -> landing `0x416EC`, action 7.

Raw ARM64 landing behavior:
1. verifies expected catch type;
2. begins catch;
3. retains the caught exception;
4. calls existing `41BA0(exception)` at `0x4170C`;
5. releases the retained exception;
6. ends catch;
7. branches to normal cleanup at `0x4169C`.

Therefore an original-callback exception:
- is swallowed;
- original is not retried;
- the existing `DDResolveExceptionReasonProbeDecision` contract applies;
- after normal probe completion, execution performs only normal cleanup/return.

There is no forced alternate callback result because `4138C` is void.

## Nested reason-probe exception

The `41BA0` call itself is protected separately:
- `0x4170C..0x41710` -> cleanup landing `0x41720`.

Raw ARM64 at `0x41720`:
- preserves the newly thrown exception;
- ends the outer catch;
- resumes unwind.

Thus original-callback cleanup after the probe is conditional on `41BA0` completing normally.

## Promoted runtime contract

Added:
- `DDAVCSceneHandleExceptionSite`
  - None
  - InitialSceneLookup
  - UpdateRouting
  - SuppressionDecision
  - OriginalCallback
- `DDAVCSceneHandleExceptionOutcome`
- `DDResolveAVCSceneHandleExceptionOutcome(site, scenePresent, currentProbeCount, reasonSelectorSupported)`.

InitialSceneLookup outcome:
- `shouldSwallowException = YES`;
- `shouldSkipRemainingUpdateRouting = YES`;
- `shouldCallOriginalAfterCatch = YES`.

UpdateRouting outcome:
- `shouldSwallowException = YES`;
- `shouldSkipRemainingUpdateRouting = YES`;
- `shouldContinueSuppressionEvaluationAfterCatch = scenePresent`;
- `shouldCallOriginalAfterCatch = !scenePresent`.

SuppressionDecision outcome:
- `shouldSwallowException = YES`;
- `shouldCallOriginalAfterCatch = YES`.

OriginalCallback outcome:
- `shouldSwallowException = YES`;
- `shouldApplyReasonProbeDecision = YES`;
- `reasonProbeDecision = DDResolveExceptionReasonProbeDecision(...)`;
- `probeExceptionWouldResumeUnwind = YES`;
- no original retry.

## Explicit exclusions

R-099 does not:
- synthesize Objective-C exceptions;
- call begin-catch/end-catch;
- invoke private `scene`, `settings`, or `isForeground` selectors;
- invoke `41C24`, `3FBC8`, `3FFC0`, `3E4A8`, `3F5C0`, or `3E670`;
- call or suppress the original callback;
- invoke `41BA0` or read exception `reason`;
- mutate `dword_162F1C`, `qword_163EB8`, or `qword_163EA0`;
- intercept or resume unwind.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — 41730

`41730` already has the R-085 data-only to-apps yield-vs-swallow decision, but its exception continuations have not yet been modeled.

`__unwind_info` maps:
- `41730` -> LSDA `0x114DAC`.

The LSDA call-site table is substantially larger than the adjacent callbacks and contains multiple typed catches and cleanup-only regions across destination-entity enumeration and to-apps side-effect paths. It should be decoded as a separate batch rather than folded into R-099.

## Next

R-100 after compiler green:
- decode `41730` LSDA/raw-ARM64 exception behavior across destination-entity enumeration, non-CarPlay host matching, yield/dismiss/cpdisconnect/hide side effects, swallow-vs-original routing, and the original callback;
- promote only evidence-safe data-only continuation/probe/unwind outcomes;
- keep private entity traversal, all side effects, the original callback, exception synthesis, and global mutation excluded.
