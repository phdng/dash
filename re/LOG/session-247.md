# LOG/session-247.md
_Date: 2026-10-08. Objective: promote the exact pure client-version formatter embedded in A574C without enabling surrounding device/sysctl/network/global behavior._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 644e78e.
- Working tree clean; branch ahead 62.

## Exact A574C formatter
The client-version loop is independently reproducible once its source string is supplied:
- iterate UTF-16 code units in source order;
- append ASCII digits or letters;
- also append `+`, `-`, `.`;
- skip all other code units;
- before each source code unit, stop if current output length is already >31, so output length is at most 32;
- if output is empty, return `unknown`.

The bitmask branch in the decompile resolves the three extra accepted ASCII punctuation code points 43, 45, 46 (`+`, `-`, `.`).

## Executable promotion
Added `DDVersionDeviceFormatClientVersion(value)` to compiled `VersionDeviceHelpers.m`, exported via `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No sysctl acquisition, OS/device global initialization, device hash, activation request construction, filesystem, network, or private API is activated.
