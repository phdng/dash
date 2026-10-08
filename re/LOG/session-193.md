# LOG/session-193.md
_Date: 2026-10-08. Objective: integrate the now-executable 7E908 normalization into a bounded publish-facing reconstruction of 74C8, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD daa38b7.
- Working tree clean; branch ahead 8.

## Closed raw-evidence gap
Raw ARM64 around 0x78E4..0x78EC:
- CFPreferencesCopyValue returns into x0;
- result is copied to x20 for later release;
- there is no x0 rewrite before `bl 0x85cdc`;
- therefore 85CDC receives the direct autostart CopyValue result exactly.

## Executable bounded publisher
Added DDRepublishAppBridgeResolvedSnapshot().

Order and behavior:
- run clearpanes one-shot;
- CFPreferencesAppSynchronize(settings domain);
- refresh/read reconstructed font-floor then keypane resolver ordering;
- read appbridge_enabled and publish 1 only when value is true and key is valid/existing;
- read bridgedApps; non-array becomes empty; non-string elements pass through; only excluded NSString bundle IDs are removed;
- read appbridge_autostart with CFPreferencesCopyValue(CurrentUser, AnyHost) and exact nil-default-true/CFBoolean-only semantics;
- copy the exact ten AppBridge config prefs and normalize through DDNormalizeAppBridgeConfig;
- build the exact 14 core resolved keys;
- add navprovider_selected as CFString else empty;
- add navprovider_autostart as value&&valid/existing;
- atomically write DD_APPBRIDGE_CACHE;
- post exact DD_N_APPBRIDGE_RESOLVED unconditionally after the write attempt.

## Repair-write boundary
DDNormalizeAppBridgeConfig exposes writes/fixes, but this publisher intentionally does not persist them.
Original 74C8 only asks for fixes.count and never writes cfg.writes; repair persistence is observed in a different path such as 27E20.

## Reconstruction observability
The original function is void. DDRepublishAppBridgeResolvedSnapshot returns the plist write BOOL so tests/callers can observe write success without changing the original publish/notify side-effect ordering.

## Next
After compiler green, inspect the 27E20 repair-write path and only promote it if the exact preference-write/synchronize/gating sequence is fully evidenced.