# LOG/session-232.md
_Date: 2026-10-08. Objective: promote exact pure crash-report string comparator A3214 without enabling regex/global initialization or report I/O/archive/upload state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD a360377.
- Working tree clean; branch ahead 47.

## Candidate filtering
- `A2C20/A2FC8` write tar/gzip streams and remain excluded.
- `A32B8` initializes global regex arrays and remains excluded.
- `A3214` is an independent pure NSString comparator.

## Exact A3214 semantics
- Retain right then left in the binary, compare string lengths.
- If lengths are equal, return `[left compare:right]` directly.
- If left is longer, return -1 / NSOrderedAscending so the longer string sorts first.
- If left is shorter, return 1 / NSOrderedDescending.

## Executable promotion
Added `DDCrashStringLengthDescendingComparator(NSString *left, NSString *right)` to already-compiled CrashReporting.m and exported it in DuoDashShared.h.

## Boundary
No regex initialization, global mutation, report collection, filesystem/archive writes, upload/network, queue state, or private API is activated.

## Next
After compiler green, inspect another pure crash-report helper only if independent from regex/global/filesystem/archive/upload state; otherwise switch subsystem.