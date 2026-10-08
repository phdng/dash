# LOG/session-199.md
_Date: 2026-10-08. Objective: recover the exact 85148 caller ABI from raw ARM64 and promote the full two-host preference-domain migration loop, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD e71dda4.
- Working tree clean; branch ahead 14.

## Raw ABI recovery
First call at 0x4E18..0x4E2C:
- x0 = `com.sensetechlab.truedash.settings`;
- x1 = `com.sensetechlab.duodash.settings`;
- x2 = `sp + 0x360` counter block.

Second call at 0x4E34..0x4E48:
- x0 = `com.sensetechlab.truedash.rescuer`;
- x1 = `com.sensetechlab.duodash.rescuer`;
- x2 = `sp + 0x2D0` counter block.

Therefore exact ABI is `85148(sourceDomain, destinationDomain, counters[4])`.

## 85664 snapshot semantics
For one domain+host:
- synchronize CurrentUser/host;
- CopyKeyList;
- absent key list => empty dictionary;
- non-empty key list => CopyMultiple;
- any non-dictionary result normalizes to empty dictionary.

## Full 85148 semantics
- Snapshot source AnyHost and CurrentHost first.
- If combined source entry count is zero, return false and leave destination untouched.
- Otherwise migrate each host independently.
- Eligible source key decision uses R-197 classifier precedence.
- Counters:
  - [0] copied identity keys;
  - [1] renamed keys;
  - [2] dropped keys;
  - [3] destination keys removed because absent from desired migrated map.
- Read destination snapshot for same host.
- Remove every destination key not present in desired map.
- CFPreferencesSetMultiple(desired, removeKeys, destination, CurrentUser, host).
- Synchronize destination host.
- Return true.

Important edge: if one source host is empty but the other makes total source count nonzero, the empty host still runs migration and therefore clears all destination keys for that host.

## Executable promotion
Added `DDMigratePreferenceDomain(sourceDomain,destinationDomain,counters)` plus exact private snapshot helper.

## Next
After compiler green, inspect the surrounding 4C34 settings+rescuer orchestration and source-cleanup timing; keep license branches separate.