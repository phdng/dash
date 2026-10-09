# LOG/session-234.md
_Date: 2026-10-08. Objective: promote exact pure crash-report identifier sanitizer A372C without enabling global/report I/O/archive/upload state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 24bc71c.
- Working tree clean; branch ahead 49.

## Candidate filtering
- `A30AC` writes CFPreferences and remains outside this pure slice.
- `A397C` is full license verification and remains outside crash helper scope.
- `A4208` is another pure candidate but belongs license/base64url decode semantics; deferred.
- `A1D40/A2370` perform file/archive/report mutation and remain excluded.
- `A372C` is an independent pure NSString sanitizer used by crash-report identity initialization.

## Exact A372C semantics
- Trim whitespace and newline characters.
- Lowercase the result.
- Require length in inclusive range 16..64.
- Allowed character set is exactly `0123456789abcdef-`.
- Reject when any character belongs to the inverted allowed set; otherwise return the normalized string.

## Executable promotion
Added `DDCrashNormalizeIdentifier(NSString *value)` to already-compiled CrashReporting.m and exported it in DuoDashShared.h.

## Boundary
No global mutation, report collection, filesystem/archive writes, upload/network, queue mutation, or private API is activated.

## Next
After compiler green, inspect another pure crash-report helper only if independent from global/filesystem/archive/upload state; otherwise switch subsystem.
