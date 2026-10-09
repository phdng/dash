# LOG/session-258.md
_Date: 2026-10-09. Objective: continue toggle-matrix VALUE parsing with the exact disconnect-close seconds parser from 7B9EC while excluding file/generation/scheduling state._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD d117a44.
- Working tree clean; branch ahead 73.

## Evidence
`7B9EC` arms disconnect-close with an initial delay of `12000000000` ns = `12.0` seconds, then optionally reads `/var/tmp/duodash_ab_discoclose_secs`.

Exact parser behavior:
- default remains `12.0` seconds;
- only if input length is nonzero does it trim `whitespaceAndNewlineCharacterSet`;
- trimmed-empty keeps `12.0`;
- otherwise parse with NSString `doubleValue`;
- parsed values in `[0.0,120.0]` inclusive override the default, so zero is valid;
- negative or >120 values keep `12.0`.

## Executable promotion
Added `DDDisconnectCloseSecondsOverrideValue(value)` to compiled `ToggleValueHelpers.m`, exported via `DuoDashShared.h`, and covered by structural verification/docs.

## Boundary
No read of `/var/tmp/duodash_ab_discoclose_secs`, no `qword_164700` generation increment, no `byte_164708` arm-state write, and no `dispatch_time`/`dispatch_after` scheduling is enabled.
