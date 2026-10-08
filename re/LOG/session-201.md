# LOG/session-201.md
_Date: 2026-10-08. Objective: promote the exact 4C34 import preflight/running-marker seam using 84F74/84FD8/85028/8509C without invoking migration or license bodies, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 57945b6.
- Working tree clean; branch ahead 16.

## Exact helpers
84F74: NSFileManager fileExistsAtPath.
84FD8: current NSDate timeIntervalSince1970 * 1000, truncated to integer milliseconds.
85028: append newline to record, atomically write UTF-8, return write success.
8509C: sum CFPreferencesCopyKeyList counts for CurrentUser/AnyHost and CurrentUser/CurrentHost; no synchronize before counting.

## Preflight seam
Added `DDPrepareTrueDashImportIfNeeded()`.

Exact control flow:
- if `/var/mobile/Library/DuoDash/import.done` exists -> return NO;
- mkdir DuoDash root 0755;
- if `import.running` exists:
  - write `at=<ms> result=aborted\n` to import.done;
  - remove import.running only if that write succeeds;
  - return NO;
- otherwise determine eligibility from:
  - TrueDash license.blob exists, OR
  - TrueDash license.key exists, OR
  - TrueDash settings has any key across AnyHost+CurrentHost, OR
  - TrueDash rescuer has any key across AnyHost+CurrentHost;
- if no signal -> return NO with no running marker;
- if eligible -> write exact `at=<ms>\n` to import.running and return that write result.

## Boundary
The seam does not invoke settings/rescuer migration and does not enter license/device-ID logic.

## Next
After compiler green, inspect whether post-migration import.done finalization/accounting can be isolated exactly before broader license handling; otherwise move subsystem.