# LOG/session-189.md
_Date: 2026-10-08. Objective: decode exact constant-array boundaries behind 7E568/74C8 and promote only bounded PrefsResolver primitives, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD c6b46e1.
- Working tree clean; branch ahead 4.

## Constant-array decoding
Raw __objc_arrayobj headers prove:
- object at 0x1541F0: NSConstantArray count=5, data=0x153A48;
- object at 0x154208: NSConstantArray count=10, data=0x153A70.

Therefore the old source comments are corrected semantically:
- 7E568 exclusion set source `off_1541F0` is the five bundle IDs at 153A48..153A68;
- 74C8 bulk config source `off_154208` is the ten AppBridge keys at 153A70..153AB8.

## Exact 7E568 exclusion set
- com.apple.springboard
- com.apple.CarPlayApp
- com.apple.InCallService
- com.sensetechlab.duodash
- com.sensetechlab.duodashkey

7E568 returns false for non-NSString or empty string, otherwise set membership.

## Exact off_154208 config keys
- appbridge_split_left
- appbridge_split_right
- appbridge_split_third
- appbridge_layout
- appbridge_split_ratio
- appbridge_split_frac_a
- appbridge_split_frac_b
- appbridge_split_frac_layout
- appbridge_split_carplay_ui
- appbridge_split_carplay_ui_more

74C8 copies only non-null CFPreferencesCopyAppValue results into the temporary dictionary.

## Executable promotion
Added:
- DDAppBridgeIdentifierIsExcluded(id)
- DDCopyAppBridgeConfigPreferences()

The snapshot preserves sparsity: missing preferences are omitted rather than defaulted.

## Explicit exclusions
- 7E908 ABCfgResult normalization;
- 7EEDC integer normalization;
- 7E730 CarPlay UI-more normalization;
- repair writes/fixes and republish plist/post path.

## Next
After compiler green, decode 7EEDC, 7E730, and ABCfgResult fully before enabling any 7E908 behavior.