# LOG/session-284.md
_Date: 2026-10-09. Objective: continue crash metadata reconstruction with the exact pure 64-bit Mach-O magic gate embedded in A2800 while excluding file/slice/load-command traversal state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD a38d6ec.
- Working tree clean; branch ahead 99.

## Evidence
Inside `sub_A2800`, after selecting a candidate slice offset, load-command parsing proceeds only when the first 32-bit word of that slice equals signed `-17958193`, i.e. exact `0xFEEDFACF` (`MH_MAGIC_64`).

Every other magic is skipped for UUID extraction.

## Executable promotion
Added `DDCrashMachOIs64BitMagic(magic)` to compiled `CrashReporting.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No NSData/file loading, slice-offset arithmetic, remaining-length computation, command-count iteration, load-command bounds checks, UUID formatting, artifact mutation, packaging, network or status state is enabled.
