# LOG/session-277.md
_Date: 2026-10-09. Objective: switch from exhausted/ambiguous toggle VALUE fallbacks to an exact pure crash-metadata predicate from 9EE88._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD b91da39.
- Working tree clean; branch ahead 92.

## Evidence
Inside `9EE88`, enumerated image filenames are accepted only when both conditions hold:
- `hasSuffix:@".dylib"`;
- either `hasPrefix:@"DuoDash"` or `hasPrefix:@"CarSleeperBT"`.

Only matching names are path-joined and forwarded into later crash-report collection logic.

## Executable promotion
Added `DDCrashShouldIncludeImageName(name)` to compiled `CrashReporting.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No directory enumeration, path traversal, path joining, file hashing/copying, `sub_A2800`, report packaging, network/upload, queue mutation, or global status state is enabled.
