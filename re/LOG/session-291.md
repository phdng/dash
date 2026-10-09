# LOG/session-291.md
_Date: 2026-10-09. Objective: continue the respring subsystem with the exact pure latch-reset reenable preference gate embedded in 80574 while excluding CFPreferences ownership and cleanup/notify side effects._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD d93f0e0.
- Working tree clean; branch ahead 106.

## Evidence
Inside `sub_80574`:
- `CFPreferencesCopyValue` may return null; null performs no action;
- non-null value is accepted only when `CFGetTypeID(value) == CFBooleanGetTypeID()`;
- only `CFBooleanGetValue(value) == true` enters the cleanup/respring-request body;
- wrong-type values are released and rejected, with no coercion.

## Executable promotion
Added `DDRespringReenablePreferenceEnabled(value)` to compiled `Respring.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No CFPreferences synchronize/copy calls, ownership release, cleanup-array enumeration, path construction/unlink, crashreport marker removal, status mutation, Darwin notification posting or actual respring execution is enabled.
