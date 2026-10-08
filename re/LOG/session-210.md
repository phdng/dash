# LOG/session-210.md
_Date: 2026-10-08. Objective: promote the exact picker array writeback/notification boundary from 8B624 without reconstructing UIKit selection mutation._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 12e234f.
- Working tree clean; branch ahead 25.

## Exact array persistence sequence from 8B624
After the controller has already mutated its NSMutableSet and materialized `selected.allObjects`:
1. resolve key: non-empty arrayKey as-is, otherwise `bridgedApps`;
2. `CFPreferencesSetValue(key, allObjects, settings, CurrentUser, AnyHost)`;
3. `CFPreferencesSynchronize(settings, CurrentUser, AnyHost)`;
4. post Darwin `com.sensetechlab.settings.changed` with deliver-immediately;
5. `notify_post("com.sensetechlab.appbridge.listchanged")`.

The binary does not sanitize or reorder the array in this persistence block; any ordering is inherited from `NSMutableSet allObjects` in the controller layer.

## Executable promotion
Added `DDPersistPickerArrayPreferenceAnyHost(key, values)` to compiled PrefsResolver.m and public reconstruction header.

## Boundary
The helper accepts an already-materialized NSArray. It does not reconstruct contains/remove/add/anyObject/allObjects behavior, maxSel eviction, row reload, or UIKit controller state.

## Next
After compiler green, inspect scalar picker writeback boundary separately; keep selection mutation excluded.