# LOG/session-272.md
_Date: 2026-10-09. Objective: continue exact toggle VALUE promotion with the canvas portrait classifier embedded in 3B2D8 while excluding screen/layout orchestration._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD d83da76.
- Working tree clean; branch ahead 87.

## Evidence
In `3B2D8`, `/var/tmp/duodash_ab_canvas` is handled by a local pure decision:
- trim with `whitespaceAndNewlineCharacterSet`;
- compare the trimmed result with exact string `portrait` using `isEqualToString:`;
- only exact lowercase `portrait` selects the portrait branch; nil/empty/other values are false.

## Executable promotion
Added `DDCanvasPortraitOverrideEnabled(value)` to compiled `ToggleValueHelpers.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No file read, no `UIScreen` bounds lookup, no width/height selection, no render-scale multiplication, and no surrounding generation/layout globals are enabled.
