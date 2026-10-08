# LOG/session-216.md
_Date: 2026-10-08. Objective: promote the exact numeric parse/range sub-semantics embedded in Keyinput helper 4A0F8 without enabling its global/file-cache state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD c7b04ad.
- Working tree clean; branch ahead 31.

## Exact parser semantics extracted from 4A0F8
- Empty NSString => 800.0.
- UTF8String nil => 800.0.
- Parse with `strtod(utf8,&end)`.
- `end == utf8` (no numeric prefix consumed) => 800.0.
- Parsed numeric zero => -1.0 sentinel.
- Nonzero value <120 or >4096 => 800.0.
- Nonzero value in [120,4096] => return value unchanged.
- The binary does not require `*end == '\0'`; therefore a valid numeric prefix followed by trailing junk is accepted.

## Executable promotion
Added `DDKeyinputParseWidthOverride(NSString *rawValue)` to compiled KeyinputGate.m and exported it in DuoDashShared.h.

## Boundary
Did not promote 4A0F8 global enable byte, `/var/tmp`/legacy file search, or 1-second cache. Did not promote 49D94 because its fallback uses 4A044/global screen-width state.

## Next
After compiler green, inspect another pure numeric/file helper only if independent from relay globals/private selectors; otherwise switch subsystem.