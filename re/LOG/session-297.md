# LOG/session-297.md
_Date: 2026-10-09. Objective: continue DataRouter/nav reconstruction with the exact pure source-string mapper embedded in 84258 while excluding dictionary extraction and submit/publish state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 9e26d19.
- Working tree clean; branch ahead 112.

## Evidence
`sub_84258` maps the retained source string through exact equality checks in this order:
- `waze` -> 2
- `google_maps` -> 1
- `provider` -> 3
- everything else, including nil -> 0

## Executable promotion
Added `DDDataRouterSourceCode(source)` to compiled `DataRouter.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No NSDictionary key extraction, integerValue conversion/packing, DataRouter camera/speed/nav submission, temp-plist writes, relayed Darwin notification posting, cache state or provider worker state is enabled.
