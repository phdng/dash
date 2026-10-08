# LOG/session-179.md
_Date: 2026-10-08. Objective: continue executable promotion by compiling an evidence-safe Foundation/CoreFoundation slice of existing CrashReporting.m, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 748b941.
- Working tree clean and aligned with origin after user push.
- Prior executable modules: RecoveryRouting, HostFlowAdapter, DDzPicker admission.

## Evidence re-check
Read exact decompile 0x9DE28:
- CFPreferencesSynchronize(com.sensetechlab.duodash.settings, CurrentUser, AnyHost);
- CFPreferencesCopyValue(dynamic key, same domain, CurrentUser, AnyHost);
- return value only when it is NSString; otherwise nil.

Read 0x9E014 early flow:
- /var/tmp/duodash_cr_off must be absent;
- /var/mobile/Library/DuoDash/crashreport_collecting must be absent;
- only then collection proceeds;
- /var/tmp/duodash_cr_dryrun independently suppresses upload;
- crashreport_endpoint is read via 9DE28 before upload decision;
- crashreport_token is read via 9DE28 for optional Bearer Authorization.

## Executable promotion
Existing re/RECONSTRUCTION/CrashReporting.m is now compiled.

Added public compile-safe surface:
- DDCrashReportingAdapterStart()
- DDCrashReportingAdapterReady()
- DDCrashReportingMayCollect()
- DDCrashReportingDryRunEnabled()
- DDCrashReportingEndpoint()
- DDCrashReportingToken()

The endpoint/token helper mirrors 9DE28:
- synchronize exact settings domain with CurrentUser/AnyHost;
- CopyValue on CurrentUser/AnyHost;
- bridge ownership safely under ARC;
- return NSString only.

Collection admission mirrors 9E014 early access() gates using NSFileManager fileExistsAtPath:.

## Build integration
Makefile includes CrashReporting.m.
Tweak.x bootstraps DDCrashReportingAdapterStart().
DuoDashShared.h exports the stable guard/config APIs.
Verifier requires source/build/bootstrap/path/prefs contracts.

## Explicit exclusions
Still not executed:
- crash report UUID/latch file creation;
- collector 9EE88;
- outgoing queue pruning;
- status writer 9DEEC;
- multipart packaging;
- endpoint URL normalization/network request;
- token header application;
- upload task/semaphore/timers;
- cleanup/unlink lifecycle;
- Darwin notify trigger / re-entrancy spinlock.

## Next
After compiler green, continue executable promotion in existing synthesis modules, preferring independent Foundation/CoreFoundation-safe behavior before networking/private UI/global mutation.
