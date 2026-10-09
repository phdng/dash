# LOG/session-248.md
_Date: 2026-10-09. Objective: promote the exact pure OS-version formatter used by crash metadata 9EE88 without enabling NSProcessInfo/sysctl/crash packaging state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 7711799.
- Working tree clean; branch ahead 63.

## Exact 9EE88 formatter
After obtaining the operating-system tuple, 9EE88 constructs `os_version` with `+[NSString stringWithFormat:@"%ld.%ld.%ld", major, minor, patch]` unconditionally for the supplied tuple.

## Executable promotion
Added `DDVersionDeviceFormatOSVersion(major, minor, patch)` to compiled `VersionDeviceHelpers.m`, exported via `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No `NSProcessInfo processInfo`, operatingSystemVersion acquisition, A2720/sysctl telemetry, crash context enumeration, file packaging, compression, upload, filesystem, or private API is activated.
