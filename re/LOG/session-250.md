# LOG/session-250.md
_Date: 2026-10-09. Objective: continue init role-detection without guessing AC5FC suffix constants by promoting only exact pure helper AC738._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 74929ac.
- Working tree clean; branch ahead 65.

## Evidence boundary
AC5FC calls AC738 five times and maps successful probes to roles 1,2,3,4,6, with fallback role 5. The decompile does not preserve the five second arguments, so reconstructing the full executable-path classifier would require guessing suffix constants and is intentionally not done.

## Exact AC738 semantics
- if value is null or suffix is null -> false;
- compute `strlen(value)` and `strlen(suffix)`;
- if value is shorter than suffix -> false;
- otherwise compare `value + valueLength - suffixLength` with suffix using `strcmp`;
- return true only when `strcmp == 0`.
- An empty suffix matches any non-null value, matching the original C-string logic.

## Executable promotion
Added `DDRoleCStringHasSuffix(value, suffix)` to compiled `InitRoleHelpers.m`, exported via `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No `_NSGetExecutablePath`, unresolved role suffix constants, AC5FC cache globals, AC7A4 disabled/state/arm files, notify state, strike accounting, delayed arming, or process-global mutation is activated.
