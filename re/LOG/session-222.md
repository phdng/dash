# LOG/session-222.md
_Date: 2026-10-08. Objective: promote exact pure legacy TrueDash notification predicate 83FDC without enabling observers, notification posting, payload translation, or relay state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD fc8c2b5.
- Working tree clean; branch ahead 37.

## Exact 83FDC semantics
- Nil input => false.
- CFEqual to `com.sensetechlab.truedash.navUpdate` => true.
- CFEqual to `com.sensetechlab.truedash.speedLimit` => true.
- Otherwise return CFEqual to `com.sensetechlab.truedash.cameraAlert`.
- Therefore every other non-nil notification name returns false.

## Other NavProvider helpers inspected
- `832C0`: comparator over `lastSeen` objects via Objective-C `compare:`; not promoted in this batch because its safety depends on caller-produced object types rather than an independently typed boundary.
- `83354`: dispatch queue initialization is side-effectful global state and remains excluded.

## Executable promotion
Added `DDNavProviderIsLegacyTrueDashNotification(CFStringRef name)` to compiled NavProviderHelpers.m and exported it in DuoDashShared.h.

## Boundary
No observer installation, Darwin/distributed posting, payload translation, relay cache, persistence, queue creation, or global state is activated.

## Next
After compiler green, inspect another pure shared helper only if non-duplicative and side-effect-free; otherwise switch subsystem.