# LOG/session-090.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-089 commit 3b22754; complete R-089 with data-only 3FA90 current-interface-orientation read eligibility and 400D0 post-frame/orientation update gating. Per user workflow, commit locally but do not push._

## R-089 — 3FA90 current interface-orientation read

Directly reviewed:
- `3FA90.c`
- `400D0.c`
- `3F75C.c`
- `41E08.c`

Exact 3FA90 behavior:
- retain the supplied settings object;
- if the object exists and responds to `interfaceOrientation`, read and return it;
- otherwise return nil/zero.

Promoted only as data:
- `DDResolveCurrentInterfaceOrientation(settingsObjectPresent, interfaceOrientationSelectorSupported, currentOrientation)`.

The supplied orientation is returned only when both booleans are true; otherwise the result is exactly zero. No selector is sent by the reconstruction helper.

## R-089 — 400D0 post-frame/orientation update gate

This batch covers only the branch that decides whether the original would request `3F5C0` after:
- callback/identity routing already succeeded;
- target dimensions/orientation were already resolved;
- 41F50/private-ivar handling already ran.

Promoted:
- `DDFBSSceneSettingsUpdateReason`
  - None
  - SlotNotMarked
  - FrameWidthMismatch
  - OrientationMismatch
- `DDFBSSceneSettingsUpdateDecision`
- `DDResolveFBSSceneSettingsUpdateDecision(...)`.

### Exact ordering

1. Target width <= 0:
   - no host-scene update request from this branch.
   - The original separately routes aux/no-size behavior and counters; those are out of scope here.

2. Target width > 0 and per-slot mark is false:
   - request update immediately.
   - Reason: `SlotNotMarked`.
   - The original also decrements a private counter before the call when possible; counter mutation remains excluded.

3. Marked slot:
   - obtain current frame width if `frame` is supported;
   - otherwise use CGRectZero width, exactly 0.
   - if `abs(currentWidth - targetWidth) > 0.5`, request update.
   - Reason: `FrameWidthMismatch`.

4. Width already within tolerance:
   - resolve desired orientation through the existing 3F75C-equivalent path;
   - desired orientation 0 -> no update;
   - obtain current orientation through 3FA90 semantics;
   - current orientation 0 -> no update;
   - only nonzero current orientation different from nonzero desired orientation requests update.
   - Reason: `OrientationMismatch`.

Therefore unsupported/missing current orientation is treated as unknown, not as a mismatch.

## Target-size detail

The descriptor carries the resolved target size because the original 3F5C0 call receives both width and height. The decision gate itself only rejects target width <= 0; the downstream private executor has its own stricter width/height validation and is not invoked here.

## Explicit exclusions

R-089 does not:
- invoke `interfaceOrientation`;
- invoke `frame`;
- mutate per-slot mark state;
- decrement `dword_162F1C`;
- invoke `3F5C0`;
- invoke `updateSettingsWithBlock:`;
- mutate any private scene/settings object.

## Next

R-090 after compiler green:
- inspect `3F5C0` private executor admission/type-encoding gate;
- inspect `3F990` in-block frame/orientation mutation decisions;
- promote only data-only capability/method-signature/mutation plans;
- do not dispatch main queue or invoke `updateSettingsWithBlock:`, `setFrame:`, or `setInterfaceOrientation:`.
