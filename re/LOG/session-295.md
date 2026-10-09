# LOG/session-295.md
_Date: 2026-10-09. Objective: continue respring reconstruction with the exact pure alternate planned-marker base-path routing gate embedded in 9C8A8 while excluding path acquisition/construction and file state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 7101336.
- Working tree clean; branch ahead 110.

## Evidence
Inside `sub_9C8A8`:
- base path comes from `sub_9C698()`;
- null base path returns nil;
- canonical `/var/mobile/Library/DuoDash` also returns nil;
- only another non-null base path selects `sub_9C914(@"respring_planned")`.

## Executable promotion
Added `DDRespringUsesAlternatePlannedMarkerBasePath(basePath)` to compiled `Respring.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No `sub_9C698` acquisition, `sub_9C914` construction, retain/autorelease, file probing, marker freshness, notify/global/dispatch or respring execution side effects are enabled.
