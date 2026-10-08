# LOG/session-226.md
_Date: 2026-10-08. Objective: promote exact pure CFDictionary numeric accessor 87C40 without enabling IOKit power traversal or CarSleeper control behavior._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 292a5b6.
- Working tree clean; branch ahead 41.

## Candidate filtering
- `87B10` battery-percentage helper requires IOPowerSources/IOKit and is not promoted.
- `87F60` and `87FD4` depend on dynamic/private system APIs and remain excluded.
- `87C40` is a pure CoreFoundation dictionary decoder with no external state.

## Exact 87C40 semantics
- Fetch `CFDictionaryGetValue(dictionary,key)`.
- Missing value => `-1`.
- Non-CFNumber value => `-1`.
- For CFNumber, zero-initialize a C long, call `CFNumberGetValue(..., kCFNumberLongType, &value)`, and return the resulting long.
- No extra normalization or fallback is added.

## Executable promotion
Added `DDLongValueForCFDictionaryKey(CFDictionaryRef,const void *)` to already-compiled PrefsResolver.m and exported it in DuoDashShared.h.

## Boundary
No IOKit linkage, power-source enumeration, battery policy, CarSleeper transition state, private APIs, or notifications are activated.

## Next
After compiler green, inspect another pure decoder/helper only if independent from IOKit/system-control/private APIs; otherwise switch subsystem.