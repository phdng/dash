# LOG/session-207.md
_Date: 2026-10-08. Objective: promote exact SiriProbe 89338 press-notify emission without installing the button hook._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 9c6c849.
- Working tree clean; branch ahead 22.

## Exact 89338 semantics
- Read selected through 890A0-equivalent TTL cache.
- Ignore the returned enabled BOOL; only selected content gates this helper.
- Revalidate selected with the same 1..96 ASCII reverse-DNS rule.
- Require `strlen(selected)+33 <= 129`.
- Build `com.sensetechlab.voicecmd.press.<selected>` into a 129-byte buffer.
- Sample NSProcessInfo.systemUptime.
- `notify_register_check(name,&token)` success only:
  - `notify_set_state(token,(uint64_t)(uptime*1000.0))`;
  - `notify_cancel(token)`.
- Always call and return `notify_post(name)` after name validation, regardless of register-check result.

## Executable promotion
Added explicit `DDPostVoiceCommandPress()` plus a private exact C-string identifier validator.

## Boundary
No Siri button hook or observer registration is installed. Press eligibility remains a separate caller decision.

## Next
After compiler green, continue only hook-independent helpers or switch subsystem until hook ABI/lifecycle is independently proven.