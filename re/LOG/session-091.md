# LOG/session-091.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-090 commit 3133026; complete R-090 by promoting only data-only 3F5C0 executor admission/method-signature decisions and 3ECD0/3F990 private mutation plans. Per user workflow, commit locally but do not push._

## R-090 — 3F5C0 private executor admission

Directly reviewed:
- `3F5C0.c`
- `3F990.c`
- `3F7C8.c`
- `3ECD0.c`
- `3FA90.c`

Raw ARM64 cross-check was used for `3F5C0/3F990/3ECD0`.

Exact 3F5C0 admission ordering:

1. Scene object and dimensions:
   - object must be non-null;
   - width must be strictly > 0;
   - height must be strictly > 0.
   - Using strict positive checks also preserves ARM64 behavior for NaN: NaN is rejected.

2. Reentrant executor:
   - original `byte_163E9B == 1` stops admission;
   - it attempts to decrement the general failure counter `dword_162F1C`.

3. Attempt cap:
   - `dword_163E88 < 13` is required;
   - count >=13 stops admission and attempts to decrement `dword_162F20`.

4. Capability gate:
   - scene geometry helper must be enabled;
   - scene object must respond to `updateSettingsWithBlock:`.
   - failure here is silent with no diagnostic counter.

5. Method-signature gate:
   - runtime instance method must exist;
   - method type encoding must exist;
   - first encoding byte must be `v`;
   - full encoding must contain `@?`.
   - failure attempts to decrement `dword_162F24`.

6. Dispatch-eligible:
   - only the fully accepted path increments `dword_163E88`;
   - then it resolves desired orientation, captures generation/size/selector/slot data, and dispatches a main-queue block.

Promoted:
- `DDFBSSceneSettingsExecutorAdmissionKind`;
- `DDFBSSceneSettingsExecutorCounterKind`;
- `DDFBSSceneSettingsExecutorDecision`;
- `DDPrivateUpdateSettingsMethodSignatureSupported(...)`;
- `DDResolveFBSSceneSettingsExecutorDecision(...)`.

The decision reports eligibility, rejection class, counter class, and whether the original would increment the attempt count. It never mutates any counter or dispatches.

## R-090 — 3ECD0 void-integer setter signature

Exact 3ECD0 rule:
- method exists;
- Objective-C method argument count is exactly 3;
- return type first byte is `v`;
- argument index 2 first type byte is `q` or `Q`.

The original implements q/Q acceptance with:
`(argumentType[0] & 0xDF) == 'Q'`.

Promoted:
- `DDPrivateVoidIntegerSetterSignatureSupported(...)`.

No class/method runtime lookup is performed by the helper.

## R-090 — 3F990 in-block mutation plan

Exact frame behavior:
- if mutable settings object is nil, no action;
- otherwise, if it responds to `setFrame:`, the original sets frame to `{0,0,targetWidth,targetHeight}`;
- this frame action is independent of orientation mutation.

Exact orientation behavior:
- desired orientation must be nonzero;
- class must pass the 3ECD0 q/Q setter signature gate for `setInterfaceOrientation:`;
- current orientation comes from 3FA90 semantics;
- current orientation must be nonzero;
- current orientation must differ from desired orientation.

Only then does the original:
- call `setInterfaceOrientation:`;
- record the previous/current orientation value into its by-reference capture;
- set an orientation-changed flag to 1.

Promoted:
- `DDFBSSceneSettingsMutationPlan`;
- `DDResolveFBSSceneSettingsMutationPlan(...)`.

The plan reports:
- pending frame set;
- target frame size;
- pending interface-orientation set;
- target orientation;
- previous orientation;
- whether the original would record the orientation-change flag.

## Explicit exclusions

R-090 does not:
- perform Objective-C class/method lookup;
- mutate attempt/failure counters;
- mutate executor reentrancy state;
- dispatch to the main queue;
- invoke `updateSettingsWithBlock:`;
- invoke retained blocks/private selectors;
- invoke `setFrame:`;
- invoke `setInterfaceOrientation:`;
- mutate scene/settings objects.

## Next

R-091 after compiler green:
- inspect `3F7C8` execution-generation/reentrancy gate;
- reconstruct post-invocation slot-mark and counter outcome as data-only decisions;
- do not invoke retained blocks/private selectors or mutate `byte_163E9B`, `word_163E98`, or counters.
