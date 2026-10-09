# LOG/session-302.md
_Date: 2026-10-09. Objective: repair the next Theos CI failure, `-Wnullability-completeness-on-arrays` in `DuoDashShared.h`._

## Reported failure
After the session-301 `NS_ASSUME_NONNULL_BEGIN/END` repair, Clang correctly advanced to six sized C-array parameters that still require explicit element-pointer nullability under `-Werror,-Wnullability-completeness-on-arrays`.

Affected public contracts:
- `DDMigratePreferenceDomain(..., NSUInteger counters[4])`
- `DDMigrateTrueDashPreferenceDomains(NSUInteger settingsCounters[4], NSUInteger rescuerCounters[4])`
- `DDFinalizeTrueDashImportRecord(const NSUInteger settingsCounters[4], ..., const NSUInteger rescuerCounters[4], ...)`
- `DDCrashMachOUUIDHex(const uint8_t uuidBytes[16])`

## Contract decision
All six array parameters are `_Nonnull`. This is not a warning-suppression guess: `Migration.m` directly indexes all counter arrays and `CrashReporting.m` reads all 16 UUID bytes with no null guard. Nullable would contradict the executable contract.

Declaration and definition signatures are updated together to avoid drift.

## Regression guard
`scripts/verify_reconstruction.py` now rejects any sized-array parameter in `DuoDashShared.h` that reaches `,` or `)` immediately after the closing bracket without an explicit nullability qualifier.

## Verification
- Workspace search confirms zero remaining unannotated sized-array parameters in `DuoDashShared.h`.
- PASS: `python scripts/verify_reconstruction.py`.
- PASS: `python -m py_compile scripts/verify_reconstruction.py`.
- PASS: `git diff --check` (LF/CRLF warnings only).
- CatDesk standard verifier remains `NOT_CONFIGURED` for this Theos-only repository.
- Exact Theos/arm64 compiler confirmation remains CI-only because the Windows workspace lacks Xcode/iOS SDK.

## Next
Run CI from this repair commit. If Clang advances to another concrete diagnostic, repair that next issue only. Do not push automatically.
