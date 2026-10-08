# LOG/session-196.md
_Date: 2026-10-08. Objective: promote the exact 4C34 defaults-bootstrap phase into executable Migration.m while compile-excluding unresolved migration phases, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD f0e0ec3.
- Working tree clean; branch ahead 11.

## Exact defaults bootstrap
- Guard: if /var/mobile/Library/DuoDash/defaults.done exists, do nothing.
- Capture import.done existence.
- AirPlay existing marker is true if either airplay_backup.plist or airplay_absent exists.
- Synchronize and count settings keys under CurrentUser/AnyHost and CurrentUser/CurrentHost; sum both counts.
- `existing = airplay marker || summed key count > 0 || import.done exists`.

## Existing-install behavior
Inspect exactly:
- pane_unload_close_enabled
- appbridge_autostart
- disconnect_close_enabled

Each present CurrentUser/AnyHost value is recorded as kept.
Each missing key is recorded as pinned and written as kCFBooleanFalse under CurrentUser/AnyHost.
Then CurrentUser/AnyHost is synchronized even when the pinned set is empty.

## Fresh-install behavior
No safety key is seeded.

## Record
mkdir /var/mobile/Library/DuoDash mode 0755.
Existing record: `at=<ms> v=1 result=existing why=<import,airplay,keys:N> pinned=<...|none> kept=<...|none> sync=<ok|failed>`.
Fresh record: `at=<ms> v=1 result=new`.
Append newline and atomically write UTF-8 to defaults.done.

## Executable boundary
- Migration.m is now included in Makefile.
- Added DDRunDefaultsBootstrapIfNeeded().
- Import guards, TrueDash preference migration, license migration, navapps/files migration remain inside #if 0 because their static tables/contracts are not all exact yet.
- Function remains explicit/manual; not startup-wired.

## Next
After compiler green, inspect another Migration helper only if its static data dependencies can be decoded completely; otherwise move to a different bounded synthesis module.