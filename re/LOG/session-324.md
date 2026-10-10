# Session-324 — Two-pane BID nil coalescing

Continued on `chore/reconstruction-build-ci` preserving uncommitted sessions 320–323.

## Evidence
`re/EVIDENCE/hosting_engine.md` §2, `217EC:26-37`: `hostSplitL:right:skipEvict:` coalesces nil left/right bundle IDs to empty strings before building the two-element slot list. Only this pure conversion is promoted.

## Implementation
- `HostFlowAdapter.m`: `DDHostSplitBidOrEmpty(NSString * _Nullable bid)` returns `bid ?: @""`.
- `DuoDashShared.h`: explicit nullable input/non-null output declaration.
- `scripts/verify_reconstruction.py`: structural guard.
- `re/STATE.md`: session update.

No private selectors, `hostSlots` call, slot mutation, or scheduling.

## Verification
PASS reconstruction verifier, Python py_compile, git diff --check (LF/CRLF warnings only). Theos arm64 CI pending; no commit/push.
