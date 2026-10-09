# LOG/session-275.md
_Date: 2026-10-09. Objective: continue exact toggle VALUE promotion with whole pure helper 3620C for content-inset parsing while excluding preferences/window/layout state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD f35d31a.
- Working tree clean; branch ahead 90.

## Evidence
Whole helper `3620C`, called by `29BC4`, parses the content-inset supplied string independently:
- original input length must be nonzero;
- trim using `whitespaceAndNewlineCharacterSet`;
- split by comma and require exactly four components;
- parse left/top/right/bottom with NSString `doubleValue`;
- reject any negative component;
- require strict `left + right < width - 40.0` and `top + bottom < height - 40.0`;
- write outputs only on success.

## Executable promotion
Added `DDContentInsetOverrideValue(value,width,height,outLeft,outTop,outRight,outBottom)` to compiled `ToggleValueHelpers.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No `/var/tmp/duodash_ab_content_inset` read, CFPreferences fallback, uniqueId lookup, safe-area/window bounds acquisition, or caller layout state is enabled.
