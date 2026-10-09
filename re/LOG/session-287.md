# LOG/session-287.md
_Date: 2026-10-09. Objective: continue crash metadata reconstruction with the exact pure fat-Mach-O header-size validation embedded in A2800 while excluding file/table traversal state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 00d0a91.
- Working tree clean; branch ahead 102.

## Evidence
Inside `sub_A2800`, after fat-magic detection and endian normalization of `nfat_arch`, the fat table is accepted only when all exact conditions hold:
- file length is at least 8 bytes;
- architecture count is at most 16;
- file length covers the 8-byte fat header plus 20 bytes per architecture entry.

Thus the pure predicate is `fileLength >= 8 && architectureCount <= 16 && fileLength >= 8 + 20*architectureCount`.

## Executable promotion
Added `DDCrashMachOFatHeaderFits(fileLength,architectureCount)` to compiled `CrashReporting.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No NSData/file loading, fat-magic detection, endian normalization, table iteration, slice-offset extraction/validation, load-command traversal, artifact mutation, packaging, network or status state is enabled.
