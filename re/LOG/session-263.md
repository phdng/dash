# LOG/session-263.md
_Date: 2026-10-09. Objective: continue exact toggle VALUE promotion with the simulated-speed parser embedded in 71780 while excluding refresh cache and GPS/navprovider state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 410822d.
- Working tree clean; branch ahead 78.

## Evidence
The `/var/tmp/duodash_ab_simspeed` branch in `71780` is separable from its surrounding 0.5-second refresh/cache logic:
- trim `whitespaceAndNewlineCharacterSet`;
- require trimmed length > 0;
- every UTF-16 code unit must be ASCII `0`..`9`;
- parse via NSString `integerValue`;
- accept values `<= 0xFF` (255), including zero;
- original code stores a separate validity byte and value byte, proving that `0` is valid rather than an invalid sentinel.

## Executable promotion
Added `DDSimulatedSpeedOverrideValue(value,outValue)` to compiled `ToggleValueHelpers.m`. It returns BOOL validity separately and optionally writes the uint8 value, preserving exact zero semantics.

## Boundary
No `CACurrentMediaTime`, 0.5-second refresh cache, file read, byte_1645B8/B9/BA mutation, navprovider plist, GPS provider selection, or logging latch behavior is enabled.
