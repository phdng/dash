# LOG/session-253.md
_Date: 2026-10-09. Objective: inspect F-013 BKS keep-awake flow and promote only an independent pure helper from the stateful gate._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD d952048.
- Working tree clean; branch ahead 68.

## Candidate selection
`4DF94` and `4D158` are stateful: BackBoard callback/original call, keepawake-off marker, Darwin notify sleep state, CarPlay connection, DDz2 active/hosted slots, visibility, navonly marker and delayed work. The helper `4DE48` called by the nav-only branch is independently pure.

## Exact 4DE48 semantics
- retain supplied object and query `length`;
- nil or zero-length -> false;
- exact `com.google.Maps` -> true;
- otherwise return exact comparison to `com.waze.iphone`;
- therefore every other nonempty bundle ID -> false.

## Executable promotion
Added `DDKeepAwakeNavigationBundle(bundleIdentifier)` to compiled `CarPlaySpoofHelpers.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No keepawake marker read, sleeping notify state, CarPlay/DDz1/DDz2 state, hosted-slot enumeration, visibility, BackBoardServices calls, backlight factor reads/writes, screen blanking, delayed dispatch or global mutation is enabled.
