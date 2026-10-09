# LOG/session-274.md
_Date: 2026-10-09. Objective: continue exact toggle VALUE promotion with the rotate quarter-turn canonicalizer embedded in 2BF84 while excluding transform/layout UI state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD aeac3de.
- Working tree clean; branch ahead 89.

## Evidence
In `-[DDz1 installContent:]` (`2BF84`), `/var/tmp/duodash_ab_rotate` is converted before transform construction:
- nil file result behaves as `0.0`;
- otherwise NSString `doubleValue` is used directly;
- divide by `90.0`, round with C `llround`;
- mask quarter turns with `& 3` and multiply by 90.

The canonical result is therefore exactly one of 0, 90, 180, or 270 degrees. Negative quarter turns wrap through the same low-two-bit mask, e.g. -90 -> 270.

## Executable promotion
Added `DDRotateQuarterTurnDegrees(value)` to compiled `ToggleValueHelpers.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No file read, render-size/window bounds, scale calculation, CGAffineTransform construction, view hierarchy mutation, or layout/UI state is enabled.
