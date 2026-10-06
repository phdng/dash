# LOG/session-082.md
_Date: 2026-10-06. Objective: continue after session-081 GitHub Actions build GREEN; promote only pure post-identity scene routing from 400D0/4138C while keeping 3FBC8 private identity traversal and all settings/layout executors out of the buildable runtime._

## R-081 — post-identity scene routing

Directly read:
- `400D0.c`
- `4138C.c`
- `3FBC8.c`
- `3FFC0.c`

Cross-checked exact routing helpers:
- `41CBC.c`
- `41E08.c`
- `3FB54.c`
- `3E4A8.c`

Also inspected the next adjacent consumers for handoff:
- `41D80.c`
- `41E94.c`
- `40514.c`
- `41138.c`

## 3FBC8 boundary

`3FBC8` is the private identity resolver. It probes several object graphs, including:
- `clientProcess -> bundleIdentifier`;
- `sceneHandle/_definition/clientIdentity -> bundleIdentifier`;
- `application -> bundleIdentifier`;
- scene identifier/string fallbacks against configured hosted bids / aux state.

Those traversals depend on private scene/client object contracts and are intentionally **not** reconstructed.

R-081 APIs therefore accept an already-resolved `NSString *bundleIdentifier` from the caller.

## 3FFC0 exact aux match

`3FFC0` is pure once identity is known:
- candidate identity length must be nonzero;
- current aux bundle length must be nonzero;
- result is exact `isEqualToString:`.

Promoted:
- `DDBundleIdentifierMatchesAux(bundleIdentifier)`.

No substring/fuzzy identity inference is performed.

## 400D0 routing

`400D0` first requires active hosting and `41CBC` acceptance.

After identity has been supplied:
- `41CBC` accepts a configured **non-CarPlay** hosted slot or aux;
- `41E08` maps only configured **non-CarPlay** hosted bids to slot indices 0..2;
- if no host slot maps, `3FB54 -> 3FFC0` identifies aux.

Therefore the exact post-identity precedence is:

1. non-CarPlay host slot;
2. aux;
3. no route.

Promoted:
- `DDResolveFBSUpdateIdentityRoute(bundleIdentifier)`.

The returned descriptor is data-only:
- `DDSceneIdentityRouteHostSlot` with slot index;
- `DDSceneIdentityRouteAux`;
- `DDSceneIdentityRouteNone`.

The later `3F5C0` / `3E670` private settings/layout calls are not invoked.

## 4138C routing

`4138C` differs materially from `400D0`.

Its first hosted-slot loop checks:
- configured bid has nonzero length;
- exact equality with supplied identity.

It does **not** test the per-slot CarPlay flag in that loop.

Only if no configured host slot matches does it test aux through `3FFC0`.

Therefore the exact post-identity precedence is:

1. any configured host slot, including CarPlay-flagged slots;
2. aux;
3. no route.

Promoted:
- `DDResolveAVCSceneHandleIdentityRoute(bundleIdentifier)`.

The later branch that reads scene settings `isForeground` and conditionally increments the private counter remains outside this pure routing descriptor.

## Shared configured-slot matcher

Added an internal configured-slot matcher parameterized by whether CarPlay-flagged slots are allowed.

This is also reused by the existing active non-CarPlay host lookup so the runtime no longer carries two subtly different implementations of the same slot equality loop.

## Fidelity notes

Important distinction preserved:
- `400D0/41E08`: exclude CarPlay host slots.
- `4138C` first slot loop: include CarPlay host slots.

Host-slot match takes precedence over aux when both could theoretically name the same bundle.

No new private selectors, scene traversal, `FBSSceneSettingsDiff`, `updateSettingsWithBlock:`, or layout mutation were introduced.

## Next

R-082 after CI green:
- inspect pure size/orientation routing around `41D80/41E94/40514`;
- use caller-supplied identity/settings snapshots only;
- promote only complete data decisions;
- do not synthesize `FBSSceneSettingsDiff`, private settings mutation, or scene executors.
