# LOG/session-190.md
_Date: 2026-10-08. Objective: close the verified 7E730/7EEDC dependencies in executable PrefsResolver without duplicating ReconstructionRuntime logic, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 0f48fc2.
- Working tree clean; branch ahead 5.

## Evidence
7E730:
- non-NSArray input -> empty array;
- iterate in source order;
- keep only NSString elements with length > 0;
- when main bundle identifier has length, exclude elements equal to main;
- remove duplicates by containsObject on the accumulating result;
- retained output preserves first occurrence order.

7E63C/7EEDC:
- already reconstructed exactly in ReconstructionRuntime from session-072;
- status model 0 missing / 1 integer CFNumber / 2 NSString coercion / 3 invalid;
- inclusive bounds and fallback semantics live in DDValidateIntegerValue;
- DDNormalizeIntegerSetting performs exact 7EEDC repair behavior: statuses 2/3 write canonical NSNumber and append fix name; statuses 0/1 do not repair.

## Executable promotion
Added to PrefsResolver:
- DDNormalizeCarPlayUIAdditional(candidate, mainBundleIdentifier), exact 7E730 behavior;
- DDNormalizeAppBridgeIntegerSetting(...), a thin executable seam delegating to DDNormalizeIntegerSetting.

PrefsResolver now imports ReconstructionRuntime.h, making the phase-in architecture explicit: compiled synthesis module consumes verified Runtime contracts instead of duplicating them.

## Remaining 7E908 blockers
- exact numeric parameters for appbridge_layout call (73E8-equivalent bounds/default);
- exact numeric parameters for appbridge_split_ratio call (80D0-equivalent bounds/default);
- final ABCfgResult integration shape is understood, but full resolver should not be enabled until those numeric parameters are proven.

## Next
After compiler green, recover 73E8/80D0 numeric call-site parameters from raw ARM64 or equivalent evidence; do not guess.