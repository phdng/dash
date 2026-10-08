# LOG/session-200.md
_Date: 2026-10-08. Objective: promote the bounded 4C34 preference-domain orchestration around the now-exact 85148 migrations and source-cleanup phase, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 658654e.
- Working tree clean; branch ahead 15.

## Exact 4C34 orchestration
Once the larger import flow has established `import.running`, the preference-only sequence is:
1. migrate `com.sensetechlab.truedash.settings` -> `com.sensetechlab.duodash.settings` with its own counters[4];
2. migrate `com.sensetechlab.truedash.rescuer` -> `com.sensetechlab.duodash.rescuer` with a separate counters[4];
3. for AnyHost then CurrentHost, snapshot only TrueDash settings;
4. collect present keys from exact cleanup list:
   - license_pending_key
   - license_pending_email
5. only when that host has at least one present cleanup key, call CFPreferencesSetMultiple(NULL, removeKeys, TrueDash settings, CurrentUser, host) and synchronize that host.

Both domain migrations run regardless of the other's BOOL return. Cleanup also runs regardless of either migration return.

## Executable promotion
Added `DDMigrateTrueDashPreferenceDomains(settingsCounters,rescuerCounters)`.
It delegates the two full R-198 migrations in exact order, then performs the exact per-host source cleanup.

## Boundary
The seam does not create/check import.done or import.running and does not enter any license/device-ID/file branch. Those belong to the larger 4C34 orchestration and remain excluded.

## Reconstruction observability
Return value is `settings migrated || rescuer migrated`; original 4C34 stores the two BOOLs separately for later import-record accounting, not for control flow of cleanup.

## Next
After compiler green, inspect `84F74/84FD8/85028/8509C` and only promote import preflight/running-marker handling if all semantics can be isolated exactly without license behavior.