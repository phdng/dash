# LOG/session-273.md
_Date: 2026-10-09. Objective: continue exact toggle VALUE promotion with the GPS bundle canonicalizer embedded in 706A0 while excluding CoreLocation manager state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 45d2a2a.
- Working tree clean; branch ahead 88.

## Evidence
In `-[CNABGpsSpeed ensureManager]` (`706A0`), `/var/tmp/duodash_ab_gps_bundle` is normalized before any manager lifecycle work:
- trim with `whitespaceAndNewlineCharacterSet`;
- if the trimmed result has nonzero length, preserve it;
- otherwise use exact fallback `com.sensetechlab.duodash`.

## Executable promotion
Added `DDGPSBundleOverrideValue(value)` to compiled `ToggleValueHelpers.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No file read, CoreLocation framework/class loading, bundle authorization, effective-bundle selector calls, manager recreation, start/stop state, or location-service probing is enabled.
