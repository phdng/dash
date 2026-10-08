# LOG/session-187.md
_Date: 2026-10-08. Objective: promote the exact Foundation/CoreFoundation clearpanes front-phase from sub_74C8 into existing PrefsResolver.m, compile that synthesis module safely, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD a39bd01.
- Working tree clean; branch ahead 2.

## Evidence
74C8 front phase confirms:
- read attributes for /var/tmp/duodash_ab_clearpanes and its fileModificationDate;
- read /var/tmp/duodash_ab_clearpanes.done as UTF-8;
- threshold is done.doubleValue + 0.5 when done has length, otherwise 0.5;
- fire only when trigger mtime timeIntervalSince1970 is strictly greater than threshold;
- write trigger mtime to done file with exact `%.3f`, atomically YES, UTF-8;
- clear exactly nine prefs with CFPreferencesSetValue(..., NULL, settings, CurrentUser, AnyHost):
  appbridge_split_left, appbridge_split_right, appbridge_split_third, appbridge_layout,
  appbridge_split_frac_a, appbridge_split_frac_b, appbridge_split_frac_layout,
  appbridge_split_carplay_ui, appbridge_split_carplay_ui_more;
- synchronize CurrentUser/AnyHost;
- remove the trigger file;
- write/sync/remove return values do not gate later steps.

## Executable promotion
- PrefsResolver.m is now in the Makefile.
- DDClearPanesIfNeeded returns BOOL for reconstruction observability without changing side-effect order.
- Public DDClearAppBridgePanesIfRequested() invokes the exact safe phase.
- Missing/no-mtime/stale request returns NO; applied request returns YES.

## Compile boundary
The subsequent DDRepublishAppBridge body still references unresolved 7EA4/8058/7E568/7E908/85CDC contracts, so it is explicitly compile-excluded with #if 0.
This allows the existing synthesis module itself to join the target without fabricating later phases.

## Next
After compiler green, promote another PrefsResolver phase only when all helper contracts needed by that phase are exact; otherwise continue another bounded Foundation/CoreFoundation synthesis module.