# LOG/session-181.md
_Date: 2026-10-08. Objective: continue executable promotion by adding the exact local crash-report outgoing-queue retention policy to the already-compiled CrashReporting.m, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 0e31068.
- Working tree clean and aligned with origin after user push.
- CrashReporting.m already compiled with guard/config and upload-preflight APIs.

## Evidence re-check
9E014 queue handling:
- enumerate /var/mobile/Library/DuoDash/reports/outgoing;
- only prune when directory count is at least 4;
- each entry stores full path under key p and modification date under key d;
- missing modification date falls back to NSDate.distantPast;
- sortUsingComparator uses global block stru_1465C8;
- after sort, remove entries at indices 3 and above; removal errors are ignored.

Comparator block mapping:
- stru_1465C8 -> sub_A1CAC;
- A1CAC returns [a3[@"d"] compare:a2[@"d"]];
- therefore sort order is descending modification date, newest first.

## Executable promotion
Added DDCrashReportingPruneOutgoingQueue().

Behavior:
- returns 0 when adapter unavailable;
- returns 0 when outgoing count < 4;
- builds exact p/d dictionaries for all entries;
- uses NSDate.distantPast when modification date is absent;
- sorts newest first using exact reversed-date comparator semantics;
- retains indices 0..2;
- attempts to remove indices 3+ and ignores removal errors;
- returns the count of successful removals for reconstruction observability.

## Activation boundary
This API is compiled and callable but intentionally not invoked during tweak startup. It is a real local-file mutation surface matching the original retention policy, while avoiding accidental pruning outside the reconstructed crash-report flow.

## Explicit exclusions
- collector 9EE88;
- crashreport_collecting file lifecycle;
- status writer 9DEEC;
- multipart body creation;
- request/upload task/network;
- semaphore/timer behavior;
- notify-trigger/re-entrancy spinlock.

## Next
After compiler green, continue executable promotion in existing synthesis modules with another bounded Foundation/CoreFoundation behavior or non-network crash-report helper.