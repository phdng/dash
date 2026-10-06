# LOG/session-104.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-103 commit 1dc3ce7; complete R-103 by decoding `400D0` LSDA/raw-ARM64 exception behavior and promoting only evidence-safe data-only continuation/probe/unwind outcomes. Per user workflow, commit locally but do not push._

## R-103 — evidence source

Reviewed:
- `400D0.c`;
- raw ARM64 for `400D0` from the first arm64 FAT slice;
- Mach-O `__unwind_info` / `__gcc_except_tab` mapping;
- existing R-081 identity-routing contract;
- existing R-089 frame/orientation update-gate contract;
- existing `41BA0` bounded reason-probe contract.

The first arm64 FAT slice begins at file offset `0x4000`.

`__unwind_info` maps:
- `400D0` -> LSDA `0x114AD8`.

Decoded call-site table:
- `0x400D0..0x4014C` -> no landing pad;
- `0x4014C..0x4018C` -> landing `0x40478`, action 7;
- `0x4018C..0x4019C` -> no landing pad;
- `0x4019C..0x401C8` -> landing `0x4040C`, action 7;
- `0x401C8..0x401D8` -> no landing pad;
- `0x401D8..0x40204` -> landing `0x403F0`, action 7;
- `0x40204..0x4020C` -> no landing pad;
- `0x4020C..0x40210` -> landing `0x403EC`, action 7;
- `0x40210..0x40218` -> landing `0x403E8`, action 5;
- `0x40284..0x40290` -> landing `0x40428`, action 5;
- `0x40294..0x402A0` -> landing `0x403E4`, action 5;
- `0x402A0..0x402E4` -> no landing pad;
- `0x402E4..0x402FC` -> landing `0x40428`, action 5;
- `0x402FC..0x40318` -> no landing pad;
- `0x40318..0x40364` -> landing `0x40428`, action 5;
- `0x40364..0x40390` -> no landing pad;
- `0x40390..0x403A8` -> landing `0x40438`, action 7;
- `0x403A8..0x40458` -> no landing pad;
- `0x40458..0x4045C` -> landing `0x4046C`, cleanup/action 0;
- `0x4045C..0x4049C` -> no landing pad.

## Pre-settings preparation catch

Protected range `0x4014C..0x4018C` covers:
- `41CBC` route eligibility;
- `41E94` adjusted size resolution;
- `3FAF8` orientation resolution;
- nested `41F50` private scene-settings mutation;
- retain-autoreleased-return handling for the returned settings object.

Landing `0x40478` enters the common typed catch at `0x4047C`.

Expected exception type:
- begin catch;
- end catch;
- branch to `0x40388`, the original callback setup.

Therefore any escaping exception from this preparation stage:
- is swallowed;
- abandons all custom settings/update routing;
- calls the original callback.

This includes an exception escaping `41F50`; exceptions already swallowed internally by the R-102 `41F50` catch never reach this outer catch.

## Scene `settings` catch — continue at `mutableSettings`

Protected range `0x4019C..0x401C8` covers:
- `respondsToSelector:settings`;
- private/public `settings` send;
- retain-autoreleased-return handling;
- nested `421CC` flag-clear helper.

Landing `0x4040C`:
- verifies expected catch type;
- begins/ends catch;
- branches to `0x401D0`.

`0x401D0` starts the `mutableSettings` selector stage.

Therefore a scene-settings exception:
- is swallowed;
- skips only the remainder of the scene-`settings` stage;
- still evaluates the `mutableSettings` path;
- does not jump directly to original.

## `mutableSettings` catch — continue at post-settings routing

Protected range `0x401D8..0x40204` covers:
- `respondsToSelector:mutableSettings`;
- `mutableSettings` send;
- retain-autoreleased-return handling;
- nested `421CC` flag-clear helper.

Landing `0x403F0`:
- verifies expected catch type;
- begins/ends catch;
- branches to `0x4020C`.

`0x4020C` is the `41C24` post-settings routing stage.

Therefore a mutable-settings exception:
- is swallowed;
- skips only the remainder of the mutable-settings stage;
- continues with post-settings routing/update decisions.

## Post-settings routing / frame / orientation / executor catches

All of the following protected ranges converge through tiny branch landings into the common typed catch at `0x40428`:

- `0x4020C..0x40210` — `41C24` pane-orientation/nopane routing;
- `0x40210..0x40218` — `41E08` non-CarPlay host-slot mapping;
- `0x40284..0x40290` — current settings `frame` capability check;
- `0x40294..0x402A0` — current `frame` selector read;
- `0x402E4..0x402FC` — desired orientation via `3F75C` and current orientation via `3FA90`;
- `0x40318..0x40364` — aux detection via `3FB54`, aux update executor `3E670`, and host-slot update executor `3F5C0`.

The common catch at `0x40428`:
- verifies expected exception type;
- branches to `0x40484`;
- begins/ends catch;
- branches to `0x40388`, the original callback setup.

Therefore an exception anywhere in these protected decision/executor ranges:
- is swallowed;
- abandons the remaining custom FBS update flow;
- calls original.

No private executor is retried.

## Counter side-effect fidelity

The normal host-slot path may decrement `dword_162F1C` before `3F5C0` at `0x4033C..0x4034C`.

That decrement range itself is outside the typed protected region, while the `3F5C0` call is inside `0x40318..0x40364`.

Therefore if the decrement already occurred and `3F5C0` subsequently throws, the catch does not roll the decrement back. R-103 deliberately does not model counter mutation or rollback; it only records the continuation to original.

Similarly, the no-size/no-aux decrement at `0x40368..0x4037C` is outside typed protection.

## Original-callback exception

The hooked original callback is exactly:
- `0x40390..0x403A8` -> landing `0x40438`, action 7.

Landing behavior:
1. verify expected catch type;
2. begin catch;
3. retain the caught exception;
4. call existing `41BA0(exception)` at `0x40458`;
5. release the retained exception;
6. end catch;
7. branch to `0x403A8`, normal argument/object cleanup and return.

Therefore an original-callback exception:
- is swallowed;
- does not retry original;
- reuses `DDResolveExceptionReasonProbeDecision`;
- after a normal probe completion, performs only normal cleanup/return.

## Nested reason-probe exception

The `41BA0` call itself is protected separately:
- `0x40458..0x4045C` -> landing `0x4046C`, cleanup/action 0.

Raw ARM64 at `0x4046C`:
- preserves the newly thrown exception;
- ends the outer catch;
- branches to the unwind/resume path at `0x40494`.

Thus original-callback cleanup after the probe is conditional on `41BA0` completing normally.

## Promoted runtime contract

Added:
- `DDFBSUpdateExceptionSite`
  - None
  - PreSettingsPreparation
  - SceneSettingsPath
  - MutableSettingsPath
  - RoutingDecisionOrExecution
  - OriginalCallback
- `DDFBSUpdateExceptionContinuation`
  - None
  - ContinueMutableSettings
  - ContinuePostSettingsRouting
  - CallOriginal
  - CleanupReturn
- `DDFBSUpdateExceptionOutcome`
- `DDResolveFBSUpdateExceptionOutcome(site, currentProbeCount, reasonSelectorSupported)`.

Outcomes:
- PreSettingsPreparation -> swallow + CallOriginal;
- SceneSettingsPath -> swallow + ContinueMutableSettings;
- MutableSettingsPath -> swallow + ContinuePostSettingsRouting;
- RoutingDecisionOrExecution -> swallow + CallOriginal;
- OriginalCallback -> swallow + CleanupReturn + existing reason-probe decision + nested-probe-unwind metadata.

## Explicit exclusions

R-103 does not:
- synthesize Objective-C exceptions;
- call begin-catch/end-catch;
- invoke `41CBC`, `41E94`, `3FAF8`, `41F50`, `421CC`, `41C24`, `41E08`, `3F75C`, `3FA90`, `3FB54`, `3E670`, or `3F5C0`;
- invoke `settings`, `mutableSettings`, or `frame` selectors;
- call the original callback;
- invoke `41BA0` or read exception `reason`;
- mutate `qword_163E00`, `dword_162F1C`, slot marks, scene settings, or any global state;
- intercept or resume unwind.

## Verification

Before final documentation pass:
- `python scripts/verify_reconstruction.py` -> PASS;
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS;
- CatDesk standard verifier -> `NOT_CONFIGURED` for this Theos-only repository.

Final verifier rerun plus `git diff --check` are required immediately before commit.

## Scout for next batch — 40514

`40514` already has several data-only size/orientation/settings snapshot contracts from earlier sessions, but its exception continuations have not yet been promoted.

Mach-O unwind mapping:
- `40514` -> LSDA `0x114B58`.

The decoded call-site table is substantially larger than `400D0` and contains:
- one early action-7 region;
- many action-5 typed regions across aux/private-settings work;
- a second late action-7 region near the callback path;
- cleanup-only action-0 regions, including a nested-catch cleanup near the end.

Representative ranges include:
- `0x40588..0x405A8` -> `0x40A88`, action 7;
- multiple action-5 ranges from `0x405AC` through `0x409B0` with distinct small branch landings;
- `0x409E8..0x409FC` -> `0x40AA4`, action 7;
- `0x40AC4..0x40AC8` -> `0x40AD8`, cleanup/action 0.

Because these ranges span snapshot preparation, private mutation, equality/diff work, executor paths, callback handling, and cleanup-only regions, `40514` should be decoded as its own batch.

## Next

R-104 after compiler green:
- decode `40514` LSDA `0x114B58` + raw ARM64 exactly across aux/private-settings snapshot mutation, equality/diff construction, private selector/executor paths, original callback handling, and cleanup-only regions;
- promote only evidence-safe data-only continuation/probe/unwind metadata;
- keep private scene/settings traversal, FBSSceneSettingsDiff construction, executors, side effects, counters/globals, and exception synthesis excluded.
