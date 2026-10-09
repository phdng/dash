# LOG/session-289.md
_Date: 2026-10-09. Objective: finish the remaining exact pure top-level minimum-length gate in A2800 while excluding file/path/parser state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD ef0eca1.
- Working tree clean; branch ahead 104.

## Evidence
Immediately after `NSData dataWithContentsOfFile:options:error:`, `sub_A2800` enters Mach-O parsing only when `-[NSData length] >= 0x20`.

Thus the exact pure gate is simply `fileLength >= 32`.

## Executable promotion
Added `DDCrashMachOHasMinimumHeaderBytes(fileLength)` to compiled `CrashReporting.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No NSData/file access, path handling, byte acquisition, magic detection, candidate-array construction, fat/thin traversal, UUID extraction, artifact mutation, packaging, network or status state is enabled.
