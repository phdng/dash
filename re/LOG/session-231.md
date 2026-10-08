# LOG/session-231.md
_Date: 2026-10-08. Objective: promote exact pure crash-report SHA-256 formatter A2560 without enabling report collection, filesystem/archive writes, upload, queue mutation, or global state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 7b4e067.
- Working tree clean; branch ahead 46.

## Candidate filtering
- 9Exxx main crash-report orchestration is large and side-effectful.
- `A2370` writes archive artifacts/metadata and remains excluded.
- `A2684` creates/persists install IDs and remains excluded.
- `A2720` performs sysctl reads and is not selected here.
- `A2560` is a standalone pure digest formatter shared by crash-report artifact paths.

## Exact A2560 semantics
- Hash `NSData.bytes` over `NSData.length` using `CC_SHA256`.
- Render each of the 32 digest bytes with lowercase `%02x` into a 64-character string.
- If prefixLength is nonzero and full-string length is greater than prefixLength, return `substringToIndex:prefixLength`.
- Otherwise return the full hex string.

## Executable promotion
Added `DDCrashSHA256Hex(NSData *data, NSUInteger prefixLength)` to already-compiled CrashReporting.m, imported CommonCrypto/CommonDigest.h, and exported the helper in DuoDashShared.h.

## Boundary
No filesystem reads/writes, archive/tar/gzip output, report enumeration, queue mutation, network upload, notifications, or global state are activated.

## Next
After compiler green, inspect another pure crash-report formatter/filter only if independent from filesystem/archive/upload state; otherwise switch subsystem.