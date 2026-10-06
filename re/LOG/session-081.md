# LOG/session-081.md
_Date: 2026-10-06. Objective: continue after session-080 GitHub Actions build GREEN; reconstruct the exact aux retry/settings state machine without invoking private auxSceneObject or updateSettingsWithBlock:._

## R-080 — aux retry/settings state machine

Directly re-read:
- `3C368.c`
- `3E428.c`
- `3E604.c`
- `3E670.c`
- `3EA0C.c`
- `3EB9C.c`

Also searched all direct references to:
- `byte_163E81`
- `byte_163DF8`
- `byte_163E9D`
- `dword_163E84`
- `dword_162F14`

No additional writers/transitions were found outside 3E428/3E670/3EA0C.

## 3C368 create-kick scheduling

After the private aux controller/view exists, original 3C368 schedules three main-queue callbacks only when:
- aux orientation is nonzero;
- `UIApplicationSceneSettings` does not expose direct `_interfaceOrientation` ivar support.

Recovered delays exactly from the code:
- 0.1 s
- 0.5 s
- 1.5 s

All three callbacks capture the current aux generation.

Promoted:
- `kDDAuxCreateKickRetryDelays = {0.1, 0.5, 1.5}`.
- `DDAuxCreateKickRetryDelays()`.
- `DDAuxCreateKickRetriesEnabled()`.

No private scheduler callback invokes auxSceneObject in the reconstruction.

## 3E428 reset semantics

Exact state reset on aux create-state commit and aux teardown:
- `generation++`;
- settings in-flight = 0;
- settings applied = 0;
- attempt count = 0;
- retry/budget counter = 10;
- refresh `swapEnabled = !exists(/var/tmp/duodash_kp_auxnoswap)`.

Important fidelity point:
- 3E428 does **not** write `byte_163E9D` (executor reentrancy).
- Initial implementation review caught this; reconstruction now preserves executor-reentrancy across generation refresh exactly instead of resetting it.

Promoted state:
- `gDDAuxSettingsInFlight`
- `gDDAuxSettingsApplied`
- `gDDAuxSettingsAttemptCount`
- `gDDAuxSettingsBudget`
- `gDDAuxSettingsExecutorReentrant`
- state exposure via `DDCurrentAuxSceneMirror()`.

## 3E604 retry callback gate

Before the original performs private `auxSceneObject` lookup:
- captured generation must equal current aux generation;
- settings-applied flag must still be false.

Promoted:
- `DDAuxCreateKickShouldRequestPrivateSceneObject(capturedGeneration)`.

The private object lookup itself remains outside the executable reconstruction.

## 3E670 attempt reservation

The existing session-080 helper already models the current-settings/applied early-out and desired settings plan.

After those early-outs, original 3E670 requires:
- scene-geometry gate enabled;
- executor reentrancy flag == 0;
- settings in-flight flag == 0.

Attempt/budget transitions:
1. If attempt count >= 8:
   - when budget >= 1, set budget directly to 0;
   - do not dispatch.
2. If attempt count < 8 but the private executor method/signature gate fails:
   - when budget >= 1, decrement budget by one;
   - do not dispatch.
3. If executor method/signature gate succeeds:
   - increment attempt count;
   - set in-flight = 1;
   - capture aux generation, desired frame/orientation, and attempt number;
   - original dispatches private executor block to main queue.

Promoted:
- `DDAuxSceneSettingsAttempt`.
- `DDBeginAuxSceneSettingsAttempt(settingsNeedUpdate, privateExecutorMethodSupported)`.
- exact attempt-cap and budget transitions.
- returned descriptor includes captured generation, attempt number, and desired settings plan.

The caller supplies the private executor capability result; reconstruction does not acquire or invoke the private scene object.

## 3EA0C executor-entry transition

Original async block:
- first compares captured generation to current generation;
- generation mismatch => total no-op;
- matching generation first clears in-flight;
- if executor-reentrancy is already active => stop;
- otherwise set executor-reentrancy = 1;
- invoke private `updateSettingsWithBlock:`;
- after the invocation returns, set applied = 1;
- if budget >= 1, decrement budget;
- clear executor-reentrancy.

Promoted as explicit two-phase caller-driven transitions:

### DDBeginAuxSceneSettingsApply(capturedGeneration)
- generation mismatch => NO, no state mutation;
- matching generation clears in-flight;
- if reentrancy already active => NO;
- otherwise acquires reentrancy and records the executing generation.

### DDCompleteAuxSceneSettingsApply(capturedGeneration)
- only succeeds for the matching active external execution;
- marks applied = YES;
- decrements budget when >= 1;
- clears the reentrancy/executing-generation state.

Critical safety/fidelity rule:
- reconstruction never calls `updateSettingsWithBlock:`;
- reconstruction never marks applied merely because an attempt was reserved;
- caller must call Complete only after the real/private invocation actually returned.

This matches original 3EA0C semantics where `byte_163DF8 = 1` is set after the updateSettingsWithBlock message returns, regardless of whether the inner 3EB9C frame/orientation setters were individually available.

## 3EB9C boundary

Direct read confirms the private mutation block:
- setFrame to `{0,0,width,height}` only when supported;
- if desired orientation nonzero and setter signature is valid, call setInterfaceOrientation:.

These actual settings-object mutations remain excluded.

## Other 3E670 callers

Directly reviewed:
- `400D0.c`
- `4138C.c`

They do not introduce additional writes to the aux retry/settings state variables. They supply private scene/current-settings objects and route into 3E670 based on scene identity/layout callbacks.

Therefore no scene-object traversal or private callback routing was promoted in R-080.

## Verification

- `python scripts/verify_reconstruction.py` PASS.
- `python -m py_compile scripts/verify_reconstruction.py` PASS.
- `git diff --check` PASS (Windows LF/CRLF warnings only).
- CatDesk standard verifier = NOT_CONFIGURED, expected for this Theos-only repo without Cargo.toml/package.json/Python project manifest.

Session-080 GitHub Actions build was GREEN per user. Session-081 Objective-C aux state-machine changes require the next pushed macOS CI compiler run.

## Next

R-081 after CI green:
- inspect post-identity routing in `400D0/4138C` plus exact helpers `3FBC8/3FFC0`;
- promote only pure bundle/slot/aux routing decisions when scene/bundle identity is supplied explicitly by the caller;
- do not reconstruct private scene/client identity traversal;
- do not call private settings/layout executors;
- keep 73E8/80D0 and full 7E908 unresolved until missing contracts are recovered.
