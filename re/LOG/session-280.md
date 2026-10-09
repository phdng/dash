# LOG/session-280.md
_Date: 2026-10-09. Objective: continue crash metadata reconstruction with the exact pure architecture-name mapper embedded in A2800 while excluding Mach-O parsing and artifact mutation._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 34c6269.
- Working tree clean; branch ahead 95.

## Evidence
Inside `sub_A2800`, after locating a Mach-O UUID command, the artifact dictionary's `arch` field is selected only from the CPU subtype field:
- default exact string is `arm64`;
- mask subtype with `0xFFFFFF`;
- if the masked value equals `2`, select exact `arm64e`.

## Executable promotion
Added `DDCrashArchitectureNameForCPUSubtype(cpuSubtype)` to compiled `CrashReporting.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No NSData file loading, fat-header traversal, Mach-O load-command parsing, UUID formatting, path/name handling, artifact-array mutation, filesystem, packaging, network or status state is enabled.
