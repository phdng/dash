# LOG/session-191.md
_Date: 2026-10-08. Objective: recover the previously-elided 73E8/80D0 and direct 7E908 numeric call parameters from raw ARM64, promote the complete numeric block into executable PrefsResolver, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 1effbaa.
- Working tree clean; branch ahead 6.

## Raw ARM64 recovery
73E8 immediately before 7E63C:
- w1 = 1
- w2 = 8
- w3 = 2
- x4 = 0
=> appbridge_layout cached read uses range 1..8, fallback 2.

80D0 immediately before 7E63C:
- w1 = 1
- w2 = 0x63 (99)
- w3 = 0x32 (50)
- x4 = 0
=> appbridge_split_ratio cached read uses range 1..99, fallback 50.

Direct 7E908 -> 7EEDC call setup:
- appbridge_layout: min 1, max 8, fallback 2, fixName `layout`.
- appbridge_split_ratio: min 1, max 99, fallback 50, fixName `ratio`.
- appbridge_split_frac_a: min 0, max 99, fallback 0, fixName `frac_a`.
- appbridge_split_frac_b: min 0, max 99, fallback 0, fixName `frac_b`.
- appbridge_split_frac_layout: min 0, max 8, fallback 0, fixName `frac_tag`.

## Executable promotion
Added DDNormalizeAppBridgeNumericConfig(source,writes,fixes).
It delegates all five fields through the already-verified ReconstructionRuntime DDNormalizeIntegerSetting contract, preserving exact 7E63C/7EEDC status/write/fix semantics.

## Consequence
73E8 and 80D0 are no longer unresolved.
The remaining full-7E908 work is pane normalization, cpui main/more validation, writes/fixes assembly, and representing ABCfgResult without introducing private class dependencies.

## Next
After compiler green, promote the remaining pane/CarPlay assembly of 7E908 into a compile-safe public result representation, preserving exact repair behavior.