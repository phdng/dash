# Session-317 — Pure in-place switch mode-flag guard

Workspace branch `chore/reconstruction-build-ci` started clean, ahead of origin by 3 commits. No new Theos arm64 CI result supplied.

## Evidence
`re/EVIDENCE/hosting_engine.md` §3, `208F4:170-206` records three early mode checks: `word_162ED8 == 0x0100`, `byte_162EDA == 2`, and `(word_163C18 & 0x101) == 0`. All other eligibility and private controller checks are excluded.

## Change
- Compiled `HostFlowAdapter.m`: pure `DDHostSwitchModeFlagsAllow(hostMode,hostPhase,stateFlags)` predicate with exactly those three checks.
- Export declaration in `DuoDashShared.h`, structural regression guard in `scripts/verify_reconstruction.py`, update `re/STATE.md`.
- This predicate is NOT sufficient to allow an in-place switch; no acquisition, private selector or state mutation is performed.

## Verification
PASS: reconstruction verifier, Python py_compile, git diff --check (LF/CRLF warning only). Exact arm64 CI still pending; no commit or push.
