# LOG/session-296.md
_Date: 2026-10-09. Objective: switch from largely exhausted Respring helpers to DataRouter/nav and promote the exact pure TrueDash notification classifier embedded in 83FDC while excluding payload/worker state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 174b141.
- Working tree clean; branch ahead 111.

## Evidence
`sub_83FDC` returns true only for three exact non-null CFString notification names:
- `com.sensetechlab.truedash.navUpdate`
- `com.sensetechlab.truedash.speedLimit`
- `com.sensetechlab.truedash.cameraAlert`

Null returns false, and all other names return false.

## Executable promotion
Added `DDDataRouterIsTrueDashNotification(name)` to compiled `DataRouter.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No plist/cache acquisition, TrueDash/DuoDash payload reads, timestamp arbitration, DataRouter submit/publish, relayed notification posting, dispatch queues, provider ingest, BLE or voice-command worker state is enabled.
