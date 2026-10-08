# LOG/session-206.md
_Date: 2026-10-08. Objective: promote exact SiriProbe file-gate/press-eligibility/swallow decision helpers without installing hooks or notify observers._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 9b6ec31.
- Working tree clean; branch ahead 21.

## Exact 894F0 file gate
- Sample NSProcessInfo.systemUptime.
- If `now - timestamp >= 0.5`, stat path, cache `(stat == 0)`, and store sampled timestamp.
- Otherwise return cached existence byte.
- No lock in original helper; reconstruction keeps independent private gate states for off and swallow paths.

## Exact 89880 press eligibility
- Only button identifier 6 is eligible.
- `duodash_siriprobe_off` present => false.
- Read voicecmd TTL-2s cache into selected buffer.
- selected empty => false.
- selected non-empty => return cached/refreshed enabled.

## Exact 89764 swallow decision
Order is strict:
1. off gate present => false;
2. press eligible => true;
3. swallow gate absent => false;
4. read `/var/tmp/duodash_siriprobe_swallow_id` UTF-8;
5. missing/empty raw content => true wildcard;
6. otherwise trim whitespace/newlines, parse NSString longLongValue, return equality with button identifier.

## Executable promotion
Added `DDSiriProbePressEligible` and `DDSiriProbeShouldSwallow`; hook forwarding remains uninstalled.

## Next
After compiler green, inspect a pure press-notify helper only if its notify state/post behavior can be proven independently.