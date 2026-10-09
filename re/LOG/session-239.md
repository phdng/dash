# LOG/session-239.md
_Date: 2026-10-08. Objective: promote exact pure license key-prefix classifier A4688 after resolving its prefix table from static evidence._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 4ea93e2.
- Working tree clean; branch ahead 54.

## Prefix-table evidence
`pointers.txt` resolves `off_1461B8` as four alternating prefix/context strings:
- 1461B8 -> `duodash-key v1 `
- 1461C0 -> `com.sensetechlab.duodash/license.key/v1|`
- 1461C8 -> `truedash-key v1 `
- 1461D0 -> `com.sensetechlab.truedash/license.key/v1|`
`strings.txt` independently confirms the exact trailing spaces on both key prefixes.

## Exact A4688 semantics
- Input must be NSString; otherwise return -1.
- Check prefix index 0 first: `duodash-key v1 ` -> return 0.
- Then prefix index 1: `truedash-key v1 ` -> return 1.
- No match -> return -1.

## Executable promotion
Added `DDLicenseKeyPrefixIndex(value)` to compiled `LicenseHelpers.m`, exported via `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No key derivation/HMAC/sealing, filesystem, network, global mutation, or private API is activated.
