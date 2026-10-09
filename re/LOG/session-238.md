# LOG/session-238.md
_Date: 2026-10-08. Objective: promote exact pure license printable-ASCII validator A4744 without enabling key/global state, filesystem, network, or private behavior._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 54d6c35.
- Working tree clean; branch ahead 53.

## Candidate filtering
- `A4688` depends on prefix constants from `off_1461B8`; deferred until the prefix table is promoted with evidence.
- `A47EC` performs key derivation/HMAC and depends on key/global inputs; excluded.
- `A4B08` performs HMAC over prefix+payload and depends on key material; excluded.
- `A4744` is fully pure and self-contained.

## Exact A4744 semantics
- Input must be an NSString instance.
- Empty string returns false.
- Iterate every UTF-16 character.
- Each character must satisfy `(character - 33) < 94`, equivalent to inclusive range 33..126 (`!` through `~`).
- Any character outside that range returns false; otherwise true.

## Executable promotion
Added `DDLicenseIsPrintableASCIIString(value)` to compiled `LicenseHelpers.m`, exported via `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No key derivation, HMAC/sealing, filesystem, network, global mutation, or private API is activated.
