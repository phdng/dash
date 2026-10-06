# LOG/session-086.md
_Date: 2026-10-06. Objective: continue after user-confirmed GREEN for session-085 commit e70ff19; complete R-085 by extracting only the data-only 41730 to-apps yield gate. Per user workflow, commit locally but do not push._

## R-085 — 41730 to-apps yield decision

Directly reviewed:
- `41730.c`
- `3E4A8.c`

Also checked nearby post-settings helpers to choose the next evidence-safe batch:
- `42124.c`
- `421CC.c`
- `41BA0.c`
- `403E4.c`
- `40A38.c`

## Exact pre-enumeration gate

The original 41730 only enters its to-apps scan when:
1. host mirror state is active;
2. a configured non-CarPlay host slot exists;
3. the internal to-apps yield reentrancy flag is not set;
4. the private callback object can expose destination application scene entities.

The reconstruction keeps only the data-only state that can be supplied without private scene objects:
- current host mirror state is read from the reconstruction mirror;
- caller supplies whether a yield is already in progress;
- caller supplies already-extracted destination bundle identifiers.

A successful destination match against a non-CarPlay configured host slot inherently proves the original “at least one non-CarPlay host slot exists” gate.

## Destination identity matching

Original `3E4A8` matching is exact:
- candidate identity must be non-empty;
- a configured slot bundle ID must be non-empty;
- the slot must not be flagged CarPlay UI;
- candidate bundle ID must equal the slot bundle ID.

The pure helper reuses:
- `DDConfiguredHostSlotIndexForBundleIdentifier(bundleIdentifier, NO)`.

Candidates are consumed in caller-provided order, corresponding to the already-resolved identities from the private enumeration boundary. The first match determines the decision and matched slot index.

## Swallow vs yield

After the first matching destination, 41730 tests:
- `/var/tmp/duodash_ab_toapps_swallow`.

The caller supplies that resolved toggle as `swallowOriginalCallback`.

Promoted:
- `DDToAppsYieldDecisionKind`
  - `None`
  - `YieldThenCallOriginal`
  - `SwallowOriginal`
- `DDToAppsYieldDecision`
- `DDResolveToAppsYieldDecision(destinationBundleIdentifiers, yieldInProgress, swallowOriginalCallback)`.

Decision semantics:
- inactive host, yield already in progress, or no matching candidate -> `None`;
- match + swallow off -> `YieldThenCallOriginal`;
- match + swallow on -> `SwallowOriginal`.

The descriptor also carries the matched configured slot index.

## Explicit exclusions

R-085 does not:
- invoke `toApplicationSceneEntities`;
- enumerate `SBDeviceApplicationSceneEntity`;
- resolve private `application.bundleIdentifier` objects;
- mutate the original yield-in-progress byte;
- dismiss DDz2;
- post `com.sensetechlab.appbridge.cpdisconnect`;
- hide DDz1;
- call the private/logging `sub_4D0F4("to-apps yield")`;
- invoke or suppress an actual hooked original callback.

It only reports the original decision to a caller.

## Next

R-086 after compiler green:
- inspect `421CC` private other-settings flag-clear eligibility;
- inspect `41BA0` bounded exception-reason probe plus `403E4/40A38` catch callers;
- promote capability/count decisions only;
- do not invoke `_setFlag:forSetting:` or add exception/log side effects.
