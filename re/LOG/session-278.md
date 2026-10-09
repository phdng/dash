# LOG/session-278.md
_Date: 2026-10-09. Objective: continue crash metadata reconstruction with the exact pure jailbreak-family mapper embedded in 9EE88 while excluding prefix acquisition/global/report state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD eea2fe7.
- Working tree clean; branch ahead 93.

## Evidence
In the `jb_family` assembly block of `9EE88`:
- `qword_164C68 == NULL` is normalized to `""` for the decision;
- if the first byte is nonzero, exact family text is `"rootless"`;
- otherwise exact family text is `"rootful"`;
- the selected C string is then converted with `+[NSString stringWithUTF8String:]`.

## Executable promotion
Added `DDCrashJailbreakFamilyForPrefixCString(prefix)` to compiled `CrashReporting.m`, exported through `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No `pthread_once`, `sub_9B9C8`, global `qword_164C68` acquisition, `jb_prefix` serialization, metadata dictionary assembly, filesystem, packaging, queue, network or status state is enabled.
