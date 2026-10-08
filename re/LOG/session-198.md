# LOG/session-198.md
_Date: 2026-10-08. Objective: decode all remaining static key tables used by migration and promote only the exact pure 85148 key-classification behavior, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD c38ddf4.
- Working tree clean; branch ahead 13.

## Raw constant-object boundaries
`off_154718` NSConstantDictionary:
- count = 1;
- key backing = 0x153B78;
- value backing = 0x153B80;
- exact mapping: `truedash_language` -> `duodash_language`.

`off_154250` NSConstantArray:
- count = 4;
- backing = 0x153B88;
- entries:
  - license_pending_key
  - license_pending_email
  - license_endpoint
  - duodash_reenable_tweaks

`off_154268` NSConstantArray:
- count = 2;
- backing = 0x153BA8;
- entries:
  - license_pending_key
  - license_pending_email

## 85148 classifier semantics
For each source key:
- non-NSString or empty -> dropped;
- if rename map contains key -> destination is mapped key;
- else if denylist contains key -> dropped;
- else if key contains `truedash` with case-insensitive search -> dropped;
- else destination key is the original key.

Rename lookup happens before deny/truedash filtering, so `truedash_language` is preserved via rename despite containing `truedash`.

## Executable promotion
Added:
- DDMigrationRenameMap()
- DDMigrationDeniedPreferenceKeys()
- DDMigrationSourceCleanupKeys()
- DDMigrationDestinationKeyForSourceKey(id)

## Explicit exclusion
The full 85148 two-host CFPreferencesSetMultiple migration/counter loop remains compile-excluded because its decompiled signature/caller argument reconstruction is malformed. No ABI guess was introduced.

## Next
After compiler green, recover 85148 caller register mapping from raw ARM64 if feasible; otherwise switch to another evidence-safe executable subsystem.