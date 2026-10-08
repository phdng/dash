# LOG/session-205.md
_Date: 2026-10-08. Objective: promote exact 88FD0/890A0 voicecmd cache wrappers around the already-executable 891F0 resolver, without activating Siri hooks or notify registration._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 6205bde.
- Working tree clean; branch ahead 20.

## Exact 88FD0 reload
- CFPreferencesAppSynchronize settings domain first.
- Resolve enabled + selected via 891F0-equivalent helper.
- Lock unfair lock.
- Replace cached enabled and 97-byte selected buffer.
- Store current NSProcessInfo systemUptime.
- Unlock.

## Exact 890A0 cached read
- Sample current systemUptime before taking lock.
- Under lock compute age = sampledNow - cachedTimestamp and read cached enabled.
- If selected output is requested and age < 2.0, copy cached selected while under lock.
- Unlock.
- If age >= 2.0, resolve preferences directly without AppSynchronize.
- Re-lock, replace cached enabled/selected and set timestamp to the earlier sampled uptime, unlock.
- If selected output requested, return refreshed selected.
- Return enabled (cached or refreshed).

## Executable promotion
Added `DDReloadVoiceCommandPreferenceCache()` and `DDVoiceCommandPreferenceCache(NSString **)` plus unfair-lock protected private cache state.

## Boundary
No settings/voicecmd notify observers, fakepress, hook installer, swallow logic, or logger are activated.

## Next
After compiler green, inspect another pure helper only if it does not require hook-global semantics.