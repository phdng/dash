# LOG/session-211.md
_Date: 2026-10-08. Objective: promote exact scalar picker writeback/notification boundary from 8B624 without reconstructing UIKit selection state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 5a2a747.
- Working tree clean; branch ahead 26.

## Exact scalar persistence sequence from 8B624
After controller has already toggled its selected set and extracted `selected.anyObject`:
1. use the controller scalarKey directly (the branch is entered only when scalarKey length > 0);
2. retain selected object and test `length`;
3. non-empty selected value => persist that string;
4. nil/empty selected value => persist `NULL` (delete preference);
5. `CFPreferencesSetValue(key,value,settings,CurrentUser,AnyHost)`;
6. synchronize CurrentUser/AnyHost;
7. post Darwin `com.sensetechlab.settings.changed` deliver-immediately;
8. `notify_post("com.sensetechlab.appbridge.listchanged")`.

## Executable promotion
Added `DDPersistPickerScalarPreferenceAnyHost(key, selectedValue)` to compiled PrefsResolver.m and public header.

## Boundary
No excludeBid check, containsObject toggle, setWithObject/set, anyObject choice, row reload, or UIKit controller state is reconstructed.

## Next
After compiler green, continue another bounded pure preference helper or switch subsystem.