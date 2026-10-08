# LOG/session-203.md
_Date: 2026-10-08. Objective: continue evidence-safe Migration promotion without entering unproven license status derivation, by promoting exact helper 85748 as a pure issued-at extractor._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD ceaae3e.
- Working tree clean; branch ahead 18.

## Exact 85748 semantics
- Retain payload.
- If validation status is nonzero -> return 0.
- If status is zero, read payload[`iat`].
- Require `iat` to be NSNumber.
- If missing or non-NSNumber -> return 0.
- Otherwise return `[iat longLongValue]` exactly.
- Nil payload naturally behaves as missing `iat` and returns 0.

## Executable promotion
Added `DDMigrationIssuedAtIfValid(validationStatus,payload)` to compiled Migration.m and public reconstruction header.

## Boundary
No license verification, device-ID lookup, blob/key import, resealing, or final licence/blob/key/old_key/undo derivation is enabled.

## Next
After compiler green, continue another bounded helper/subsystem while keeping the unproven license branches excluded.