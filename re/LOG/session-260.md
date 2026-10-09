# LOG/session-260.md
_Date: 2026-10-09. Objective: reassess hypothesis-marked toggle VALUE candidates and promote only an exact independently pure parser._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 343c128.
- Working tree clean; branch ahead 75.

## Evidence
Direct decompile of whole helper `1A18C` resolves `/var/tmp/duodash_ab_dashsettle` exactly:
- read string in the original helper;
- nil/empty length -> `0.45`;
- otherwise call NSString `doubleValue` directly, with no explicit trimming;
- values greater than `5.0` or less than `0.2` -> `0.45`;
- therefore the accepted interval is exactly `[0.2,5.0]` inclusive.

## Executable promotion
Added `DDDashSettleSecondsOverrideValue(value)` to compiled `ToggleValueHelpers.m`, exported via `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No read of `/var/tmp/duodash_ab_dashsettle` and no behavior from callers `19960`/`1A290` is enabled. This promotes only the supplied-string value decision.
