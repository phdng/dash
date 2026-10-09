# LOG/session-241.md
_Date: 2026-10-08. Objective: promote exact decision-only license verdict text from A774C without enabling blob/refusal/device acquisition or other stateful behavior._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 66ed7ae.
- Working tree clean; branch ahead 56.

## Candidate filtering
- A7474 reads `license.refresh.plist`; excluded.
- A78B8 deletes `license.refused.plist`; excluded.
- A7940 writes refusal state with current time; excluded.
- A7AC4 writes retry state; excluded.
- A774C contains a separable pure decision once verification/refusal/device inputs are supplied.

## Table evidence
`pointers.txt` resolves `off_1468F8` indices 0..10 as: `valid`, `absent`, `malformed`, `unknown_key`, `bad_signature`, `wrong_device`, `expired`, `future_dated`, `unsupported`, `store_failed`, `wrong_product`.

## Exact A774C decision
- If a license nonce is present and equals the refused nonce -> `refused`.
- Else if verification status is nonzero and device hash is absent -> `no_device_id`.
- Else status 0..10 maps through `off_1468F8`.
- Status >10 -> `unknown`.

## Executable promotion
Added `DDLicenseVerdictText(status, licenseNoncePresent, refusalMatches, deviceHashPresent)` to compiled `LicenseHelpers.m`, exported via `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No A4450 verification, nonce extraction, refused-plist read, device-hash acquisition, filesystem, global mutation, network, or private API is activated.
