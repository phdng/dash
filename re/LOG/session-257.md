# LOG/session-257.md
_Date: 2026-10-09. Objective: continue toggle-matrix VALUE parsing with the exact hold-seconds parser from 163EC while excluding file/scheduling/host state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD f93030b.
- Working tree clean; branch ahead 72.

## Evidence
`163EC` reads `/var/tmp/duodash_ab_holdsec` in two host-action branches. Both copies use the same parser:
- if file string is nil, parsed value is treated as `0.0`;
- otherwise call NSString `doubleValue` directly (no explicit trim stage);
- if parsed value is greater than `3600.0` or less than `10.0`, use `900000000000` ns = `900.0` seconds;
- otherwise use `parsed * 1e9`, so accepted values are exactly `[10,3600]` inclusive.

## Executable promotion
Added `DDHoldSecondsOverrideValue(value)` to compiled `ToggleValueHelpers.m`, exported via `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No read of `/var/tmp/duodash_ab_holdsec`, no delayed host action, no dispatch scheduling, no bundle/slot handling, and no process-global mutation is enabled.
