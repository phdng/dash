# LOG/session-245.md
_Date: 2026-10-08. Objective: leave the stateful remainder of perf and promote the first evidence-safe Version/device helper._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 7e91c7b.
- Working tree clean; branch ahead 60.

## Perf close-out
`A7FE78` reads `perf_tweak_enabled` but the decompiled value does not affect its control flow. The meaningful remainder is `notify_register_check`/token reuse, state=60, cancel-on-failure, and notify post through global `dword_163210`, so no independent pure/read-only slice was promoted.

## Version/device candidate
`A4008` has a fallback branch that compares the already-resolved installed OS tuple against a required tuple. This logic is independent once the two tuples are supplied.

## Exact decision slice
- installed major > required major -> true.
- installed major < required major -> false.
- majors equal: compare minor the same way.
- major/minor equal: return installed patch >= required patch.

## Executable promotion
Added compiled `VersionDeviceHelpers.m` with `DDVersionTupleAtLeast(...)`, exported via `DuoDashShared.h`, added to the root Makefile and structural verifier.

## Boundary
No `_availability_version_check`, weak-link resolution, global initialization, `SystemVersion.plist` parsing, sysctl telemetry, device hash, or private API is activated.
