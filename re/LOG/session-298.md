# LOG/session-298.md
_Date: 2026-10-09. Objective: continue DataRouter/nav reconstruction with the exact pure provider-payload validator embedded in 83EB4 while excluding file/cache/timestamp and worker state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD c90d89b.
- Working tree clean; branch ahead 113.

## Evidence
`sub_83EB4(payload, provider)` returns true only when all exact conditions hold:
- payload is an NSDictionary;
- payload[`v`] is an NSNumber;
- `[v intValue] == 2`;
- payload[`provider`] is an NSString;
- provider string equals the supplied target provider.

Everything else returns false, including nil/wrong-type inputs and version values other than 2.

## Executable promotion
Added `DDDataRouterProviderPayloadMatches(payload,provider)` to compiled `DataRouter.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No file/path discovery, provider cache mutation, timestamp extraction (`83250`), newest-provider arbitration, DataRouter submit/publish, relayed notify posting or worker queue state is enabled.
