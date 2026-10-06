# LOG/session-079.md
_Date: 2026-10-06. Objective: continue after session-078 GitHub Actions build GREEN; promote only complete pure geometry/orientation decisions around 3F5C0/3257C/400D0 without private scene/view mutation._

## R-076 — pure geometry consumers

### 3257C lscape transform plan
Directly re-read `3257C.c` and cross-checked `32290.c`, `400D0.c`, `40C5C.c`, `40DA8.c`, `4138C.c`.

Recovered exact landscape-specific transform inside 3257C:
- branch applies only when slot index <= 2, accepted landscape override is active, hosted bid at that slot is non-empty, and both native + target slot dimensions are positive;
- scale is computed from **unswapped** native dimensions:
  `min(slotWidth/nativeWidth, slotHeight/nativeHeight)`;
- `cswap` affects bounds dimensions only:
  - off: bounds = nativeWidth × nativeHeight
  - on: bounds = nativeHeight × nativeWidth
- transform begins as uniform scale;
- if rotation != 0, rotate that scaled transform by `rotationDegrees * 3.14159265 / 180.0`;
- center = midpoint of the target slot rectangle.

Promoted:
- `DDHostLandscapeGeometryPlan` (data only).
- `DDComputeHostLandscapeGeometryPlan(...)`.

No UIView, CALayer or CGAffineTransform object is created by the reconstruction helper.

Important distinction:
- session-078 `swap` changes scene-layout width/height before private layout calls.
- `cswap` in 3257C changes **container bounds**, not the scale denominator inputs.
- `rotation` affects the transform after scaling.

### 3E9A8 scene-geometry gate
Direct read `3E9A8.c`.

Recovered:
- cached int begins in unresolved state;
- first evaluation stores inverse existence of `/var/tmp/duodash_ab_noscenegeom`;
- later calls reuse the cached result.

Promoted:
- `DDSceneGeometryUpdatesEnabled()` with first-read memoization.

### 3F5C0 boundary
Direct reads:
- `3F5C0.c`
- block `3F7C8.c`
- settings block `3F990.c`

The executor is intentionally **not** promoted:
- requires private scene object;
- probes `updateSettingsWithBlock:` type encoding;
- dispatches private settings mutation on main queue;
- uses host generation + reentrancy/counter state;
- private block sets frame and possibly interface orientation.

Only complete pure decisions surrounding it are represented in the runtime.

## R-077 — pane settings orientation decision

Direct reads:
- `41C24.c`
- `3E534.c`
- `3F75C.c`
- `3FAF8.c`
- `3FB54.c` / `3FFC0.c` for aux-match meaning.

### 41C24 generation-scoped state
When cached generation differs from current host generation:
- refresh retry/counter state (private executor scope);
- read `/var/tmp/duodash_ab_nopaneorient`;
- store its existence into the pane-orientation-disable flag;
- clear private per-slot applied flags.

Promoted evidence-safe subset:
- lazy generation comparison against reconstruction host generation;
- exact generation-scoped `duodash_ab_nopaneorient` file read.

### 3E534 capability probe
Exact memoized runtime check:
- lookup private `UIApplicationSceneSettings`;
- return true iff class exists and has ivar `_interfaceOrientation`.

Promoted:
- `DDSceneSettingsHasInterfaceOrientationIvar()`.
- Runtime introspection only; no private framework hard-link.

### 3F75C + 3FAF8 pure orientation choice
Recovered decision:
1. if generation-scoped nopaneorient flag is set => return 0;
2. if landscape override active => return 0;
3. if UIApplicationSceneSettings has `_interfaceOrientation` ivar => return 0;
4. candidate orientation:
   - aux orientation when caller has already established the scene is the aux bundle and aux orientation is nonzero;
   - otherwise current hosted orientation;
5. return candidate only when 1..4; else 0.

Promoted:
- `DDResolvePaneSettingsOrientation(isAuxScene, auxOrientation)`.

The helper deliberately takes `isAuxScene` as an input. Determining that value in the original walks private scene/client identity objects through `3FBC8`; that object graph is not guessed.

## R-078 investigation — aux state boundary

Directly read:
- `3C368.c` createAuxSceneForBid:native:orient:
- `3C808.c` teardownAuxScene
- `3E590.c` capability check
- `3E428.c` aux generation/cache reset
- `3C918.c` / `3C934.c` getters
- `3ECD0.c` method-signature helper

Recoverable pure rules:
- reject empty bid, native width/height < 1, existing aux VC, or disallowed app;
- for requested orientation 3/4 when UIApplicationSceneSettings lacks direct ivar support:
  - if FBScene updateSettingsWithBlock + UIMutableApplicationSceneSettings setInterfaceOrientation capability is unavailable:
    orientation becomes 0 and native size is portrait-normalized min×max;
- after private `SBApplicationController applicationWithBundleIdentifier:` returns a valid app, original stores aux bid/size/orientation and refreshes aux generation/toggles;
- teardown clears aux bid/size/orientation after private view/controller teardown.

Not promoted in session-079:
- original state is installed **only after** the private application lookup succeeds.
- installing aux state before that lookup would change semantics.
- no private SBApplicationController / scene/view creation was introduced.

Queued as R-078 for the next CI-green session, preserving that post-application-lookup boundary.

## Verification
- `python scripts/verify_reconstruction.py` PASS.
- `python -m py_compile scripts/verify_reconstruction.py` PASS.
- `git diff --check` PASS (Windows LF/CRLF warnings only).
- CatDesk standard verifier = NOT_CONFIGURED, expected for this Theos-only repo without Cargo.toml/package.json/Python project manifest.

Session-078 GitHub Actions build was GREEN per user. Session-079 Objective-C runtime-introspection + geometry-plan changes require the next pushed macOS CI compiler run.

## Next
R-078 after CI green:
- model only the aux normalization/capability/state boundary whose contract is exact;
- preserve the requirement that aux state is committed only after original private application lookup succeeds;
- do not instantiate SBApplicationController, SBDeviceApplicationSceneEntity, SBAppViewController, or aux view objects;
- continue to keep 73E8/80D0 and full 7E908 unresolved until missing contracts are recovered.
