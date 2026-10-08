# LOG/session-194.md
_Date: 2026-10-08. Objective: isolate and promote the exact AppBridge config-repair persistence sequence from 27E20 as an explicit executable action, verify, and commit locally without pushing._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD e51ee0f.
- Working tree clean; branch ahead 9.

## Exact 27E20 repair sequence
- Check `/var/tmp/duodash_ab_noconfigrepair`; when it exists, skip the entire repair read/write path.
- Otherwise `CFPreferencesSynchronize(settings, CurrentUser, AnyHost)` first.
- Enumerate exact `off_154208` ten-key order.
- Read each key with `CFPreferencesCopyValue(settings, CurrentUser, AnyHost)`; omit missing values.
- Normalize via the same 7E908 semantics now exposed as `DDNormalizeAppBridgeConfig`.
- Read `writes`; if count is zero, perform no preference writes and no second synchronize.
- If writes exists, enumerate the same exact ten-key order.
- For each key, if `writes[key]` is non-nil, call `CFPreferencesSetValue(key, value, settings, CurrentUser, AnyHost)`.
- After the write loop, call `CFPreferencesSynchronize` exactly once.

## Executable promotion
Added `DDRepairAppBridgeConfigIfNeeded()`.
The action is explicit/manual and is not invoked from tweak startup or from the R-192 publisher.

## Return-value note
The binary path is embedded in a larger logging function and does not expose this BOOL.
For reconstruction observability:
- knob/no-repair paths return NO;
- repair path returns the final `CFPreferencesSynchronize` result.
This does not change preference side-effect ordering.

## Explicit exclusions
- 27E20 status-file/log-string bookkeeping (`last_repair_at`, `last_fixes`, result/sync strings);
- unrelated dashboard/navbubble migration logic;
- caller/UI behavior around the repair block.

## Next
After compiler green, decide whether a bounded exact integration point can invoke repair + republish together based on proven call timing; otherwise leave both as explicit actions.