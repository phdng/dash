# LOG/session-085.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-084 commit 4933e59; complete R-084 with data-only 40FF4 foreground eligibility and 41138 post-identity destroy routing. Per user workflow, commit locally but do not push._

## R-084 — 40FF4 foreground eligibility

Directly reviewed:
- `40FF4.c`
- `41CBC.c`
- `3FBC8.c`
- `3FFC0.c`

Exact post-original-callback gate:
1. hosting active;
2. 41CBC accepts the scene identity (configured non-CarPlay host or exact aux);
3. `UIMutableApplicationSceneSettings` class exists;
4. supplied settings object is kind of that class;
5. settings object responds to `setForeground:`.

Promoted:
- `DDShouldForceMutableSceneForeground(bundleIdentifier, mutableSettingsClassAvailable, settingsIsMutableApplicationSceneSettings, foregroundSetterSupported)`.

The caller supplies the runtime class/kind/setter capability results. The reconstruction never sends `setForeground:`.

## R-084 — 41138 destroy routing

Directly reviewed:
- `41138.c`
- `3AE3C.c` to confirm `byte_163DC0 == isSplitHosting`;
- `30960.c` to keep its UI/log execution outside the runtime.

### Outer gate

41138 enters special post-callback routing only when hosting is active and either callback object passes 41CBC.

The reconstruction accepts already-resolved:
- primary bundle identity;
- secondary bundle identity.

No private 3FBC8 scene/client traversal is reproduced.

### Identity precedence

A subtle original behavior is preserved:
- either primary or secondary may satisfy the 41CBC gate;
- after the gate, a non-empty primary identity is selected even if only the secondary identity made the gate true;
- secondary identity is used only when primary is empty.

### Decision routes

After the original callback:
1. exact selected aux identity -> `AuxDestroyedNotice`;
2. otherwise when not split-hosting -> `DismissHost`;
3. when split-hosting, count exact selected-identity matches against all three configured slot bundle IDs;
4. exactly one match -> `ClearHostSlot(slotIndex)`;
5. zero or multiple matches -> `DismissHost`.

The slot count intentionally ignores CarPlay flags because 41138 compares all three configured bundle IDs directly.

Promoted:
- `DDSceneDestroyDecisionKind`;
- `DDSceneDestroyDecision`;
- `DDResolveSceneDestroyDecision(primaryBundleIdentifier, secondaryBundleIdentifier)`.

## Explicit exclusions

R-084 does not:
- traverse private scene/client identity objects;
- call `setForeground:`;
- call `30960`;
- clear a host slot;
- call DDz2 `dismiss`;
- recreate any private settings or scene executor.

## Next

R-085 after compiler green:
- inspect `41730` to-apps yield gating;
- accept caller-supplied destination bundle candidates and swallow-toggle state;
- promote pure host-state/candidate-match/yield decisions only;
- do not reconstruct `SBDeviceApplicationSceneEntity` enumeration or invoke dismiss/cpdisconnect/hide/log side effects.
