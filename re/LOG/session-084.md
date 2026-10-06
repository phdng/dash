# LOG/session-084.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-083 commit ffcd879; complete R-083 with pure callback rewrites only. Per user workflow, commit locally but do not push._

## R-083 — 40C5C / 40DA8 / 40F0C

Directly reviewed:
- `40C5C.c`
- `40DA8.c`
- `40F0C.c`
- `40FF4.c`
- `41CBC.c`
- `41D80.c`
- `3FAF8.c`

Reused previously reconstructed pure helpers:
- `DDResolveFBSUpdateIdentityRoute`
- `DDResolveIdentityNativeSize`
- `DDApplyLandscapeSwapToSize`
- `DDResolveIdentityRawSettingsOrientation`

## 40C5C / 40DA8 size rewrite

Both callbacks share the same pure argument rewrite:
1. hosting must be active;
2. original width and height must both be positive;
3. post-identity `41CBC` route must accept either a configured non-CarPlay host slot or aux;
4. resolve native size through `41D80`;
5. when accepted landscape override + swap is active and both resolved dimensions are positive, swap width/height;
6. substitute only when final resolved width and height are both positive;
7. otherwise preserve the original dimensions.

Promoted:
- `DDSceneCallbackSizeRewrite`
- `DDResolveSceneCallbackSizeRewrite(bundleIdentifier, originalSize)`

The descriptor carries:
- final size;
- `substituted` flag.

This makes the `40DA8` substitution condition explicit without reconstructing its private counter decrement.

## 40F0C orientation result rewrite

Exact post-identity behavior:
- when hosting is active and the `41CBC` route accepts the identity, return whether `3FAF8(identity) == requestedOrientation`;
- otherwise preserve the original implementation's boolean result.

Promoted:
- `DDResolveSceneOrientationEqualityResult(bundleIdentifier, requestedOrientation, originalResult)`.

## Explicit exclusions

Not promoted:
- `40DA8` private counter decrement;
- `40FF4` private `UIMutableApplicationSceneSettings setForeground:` mutation;
- private scene/client identity traversal.

## Next

R-084 after compiler green:
- inspect data-only `40FF4` foreground-force eligibility;
- inspect post-identity destroy routing in `41138`;
- promote decisions only, not `setForeground:`, dismiss, toast, or slot mutation side effects.
