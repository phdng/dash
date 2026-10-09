# LOG/session-237.md
_Date: 2026-10-08. Objective: promote exact decision-only license status mapping from A54A4 without enabling blob/refusal acquisition, full verification, key/global state, filesystem, or network behavior._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 5e6b711.
- Working tree clean; branch ahead 52.

## Candidate filtering
- `A385C` is a duplicate SHA-256 lowercase-hex semantic already covered by executable `DDCrashSHA256Hex(data, 0)`, so no duplicate implementation was added.
- `A4BC0`, `A50CC`, and `A5114` depend on file I/O, key/global state, crypto sealing, or random state and remain excluded.
- `A54A4` contains a clean decision-only mapping once its `A4450` verify status and `A7400` refusal-match inputs are supplied externally.

## Exact A54A4 decision mapping
- verification status 6 -> `Expired — connect to the internet`.
- verification status 1 -> `Not activated`.
- any other nonzero status -> `Licence invalid`.
- status 0 + refusal match -> `Licence invalid`.
- status 0 + no refusal match -> `Active`.

## Executable promotion
Added `DDLicenseStatusTextForVerification(status, refusalMatches)` to compiled `LicenseHelpers.m`, exported via `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No `A4450` blob verification, `A7400` refusal-state acquisition, full `A397C`, key iteration, filesystem, network, verdict/global mutation, or private API is activated.
