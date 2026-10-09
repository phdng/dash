# LOG/session-259.md
_Date: 2026-10-09. Objective: continue toggle-matrix VALUE parsing with the exact splash-seconds parser from 358F0 while excluding file/UI/media-time/scheduling state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD ab54e88.
- Working tree clean; branch ahead 74.

## Evidence
`358F0` reads `/var/tmp/duodash_ab_splash_secs`, trims whitespace/newlines, parses `doubleValue` when nonempty, and otherwise uses `0.0`. Immediately after, values greater than `15.0` or less than `0.5` are replaced with exact default `3.0`.

Therefore the pure parser preserves exactly the inclusive interval `[0.5,15.0]`; empty/non-numeric/low/high values resolve to `3.0`.

## Executable promotion
Added `DDSplashSecondsOverrideValue(value)` to compiled `ToggleValueHelpers.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No read of `/var/tmp/duodash_ab_splash_secs`, no splash view/image construction, no `CACurrentMediaTime`, no global deadline update, no weak-reference block state, and no delayed dispatch is enabled.
