# LOG/session-192.md
_Date: 2026-10-08. Objective: promote the remaining evidence-safe 7E908 pane/CarPlay assembly into compiled PrefsResolver without linking private ABCfgResult, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 16f965e.
- Working tree clean; branch ahead 7.

## Exact 7E908 assembly
Three pane keys resolve in order: left, right, third.
For each slot:
- missing -> empty string, no write/fix;
- non-NSString -> empty + writes[key]="" + fix `type:index`;
- excluded bundle id -> empty + write + fix `excluded:index`;
- non-empty duplicate of an earlier resolved pane -> empty + write + fix `dup:index`;
- otherwise copy the string, including valid empty string.

Numeric fields are provided by R-190 DDNormalizeAppBridgeNumericConfig and share the same writes/fixes containers.

CarPlay main:
- missing -> empty, no repair;
- empty NSString -> empty, no repair;
- non-string -> empty + write + `cpui_main`;
- non-empty excluded or not present in panes -> empty + write + `cpui_main`;
- otherwise copy the pane bundle id.

CarPlay more:
- first run exact 7E730 ordered/dedup normalization against resolved cpui main;
- then retain only non-excluded bundle ids present in panes;
- if raw value is nil, do not repair;
- if raw exists and is non-array or differs from final array, write final array and append `cpui_more`.

## Compile-safe representation
Added DDNormalizeAppBridgeConfig(source).
Instead of allocating private ABCfgResult, it returns an immutable dictionary with:
- panes
- layout / ratio / fracA / fracB / fracLayout
- cpuiMain / cpuiMore
- writes / fixes.

## Next
After compiler green, integrate this normalized result into a bounded 74C8 republish path using only exact prefs/plist/notify behavior.