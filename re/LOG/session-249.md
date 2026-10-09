# LOG/session-249.md
_Date: 2026-10-09. Objective: switch from the nearly exhausted Version/device pure scope to init role-detection and promote only the exact role-code label decision from AC7A4._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 5b64518.
- Working tree clean; branch ahead 64.

## Candidate selection
`AC5FC` combines `_NSGetExecutablePath`, suffix classification, a cached global role and a one-time initialized flag. `AC7A4` then mixes role decisions with latch files, notify state, strike/arming persistence and delayed work. The role-code to role-name switch at the top of AC7A4 is independently reproducible.

## Exact AC7A4 role-name mapping
- role 1 / SpringBoard -> `bridge`
- role 2 / Preferences -> `prefsrefresh`
- role 3 / CarPlayApp -> `appbridge_cp`
- role 4 / mediaserverd -> `carplay`
- role 5 / UIApp -> `appbridge_uiapp`
- role 6 / kbd -> `kbdpoc`
- every other value -> no valid role name (nil)

## Executable promotion
Added new compiled `InitRoleHelpers.m` with `DDRoleName(role)`, exported through `DuoDashShared.h`, added to the root Makefile and structural verifier.

## Boundary
No `_NSGetExecutablePath`, AC5FC cached globals, AC738 suffix probing, disabled/state/arm file reads or writes, notify registration/state, strikes, delayed arming, or process-global mutation is activated.
