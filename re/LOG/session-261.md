# LOG/session-261.md
_Date: 2026-10-09. Objective: continue exact toggle VALUE promotion with the dash-launch seconds parser from 19A08 while excluding scheduling/callback state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 20654a9.
- Working tree clean; branch ahead 76.

## Evidence
Direct decompile `19A08` resolves `/var/tmp/duodash_ab_dashlaunch_secs`:
- starts with `1500000000` ns = `1.5` seconds;
- nil/empty string leaves the default untouched;
- otherwise calls NSString `doubleValue` directly, with no explicit trim;
- values below `0.5` or above `30.0` keep the default;
- values in `[0.5,30.0]` inclusive become the scheduled delay.

## Executable promotion
Added `DDDashLaunchSecondsOverrideValue(value)` to compiled `ToggleValueHelpers.m`, exported via `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No read of `/var/tmp/duodash_ab_dashlaunch_secs`, no `a2` scheduling gate, no `dispatch_time`/`dispatch_after`, and no callback invocation is enabled.
