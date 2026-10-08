# LOG/session-221.md
_Date: 2026-10-08. Objective: promote exact NavProvider payload/provider validator 83EB4 without duplicating existing preference-reader semantics or enabling notify/persistence side effects._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD a0ba113.
- Working tree clean; branch ahead 36.

## Exact 83EB4 semantics
- Retain payload and caller provider.
- Payload must be NSDictionary; otherwise false.
- Fetch payload key `v`.
- `v` must be NSNumber and `intValue` must equal 2; otherwise false.
- Fetch payload key `provider`.
- Payload provider must be NSString; otherwise false.
- Return `[payloadProvider isEqualToString:callerProvider]` directly.

## Related helpers inspected
- `83184`: selected-provider preference reader is sync + CopyValue CurrentUser/AnyHost + CFString-only + nonempty normalization. This is already represented by the generic executable `DDCopyNonemptyStringPreferenceAnyHost` from R-207, so no redundant wrapper was added.
- `82830`: Darwin post helper is side-effectful and remains excluded from this pure-validator batch.

## Executable promotion
Added `DDNavProviderPayloadMatchesProvider(payload, provider)` to compiled NavProviderHelpers.m and exported it in DuoDashShared.h.

## Boundary
No preference reads are duplicated, and no plist writes, directory scans, notifications, relay caches, or global state are activated.

## Next
After compiler green, inspect another pure shared NavProvider helper only if non-duplicative and side-effect-free; otherwise switch subsystem.