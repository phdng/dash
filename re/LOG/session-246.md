# LOG/session-246.md
_Date: 2026-10-08. Objective: promote the exact pure hw.machine sanitizer embedded in A574C without enabling sysctl acquisition or surrounding license/network behavior._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD f264e19.
- Working tree clean; branch ahead 61.

## Candidate selection
A2720 is read-only but directly environment-coupled through `sysctlbyname`. A574C contains a cleaner independent sanitizer immediately after its `hw.machine` read, so this session promotes only that decision.

## Exact A574C sanitizer
- Input is the NSString produced from the machine string; reconstruction rejects non-NSString defensively.
- Allowed characters are exactly `abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,_-`.
- Any other character rejects.
- Length greater than 32 rejects.
- No trimming, lowercasing, or other normalization.
- Empty string passes the observed character/range and length checks and is returned unchanged.

## Executable promotion
Added `DDVersionDeviceSanitizeMachineModel(value)` to compiled `VersionDeviceHelpers.m`, exported via `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No `sysctlbyname("hw.machine")`, A2720 environment reads, device-hash/global state, activation request construction, filesystem, network, or private API is activated.
