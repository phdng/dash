# Session-311 — Supplied host layout override clamp

User confirmed session-310 Theos arm64 CI green. Working tree started clean on `chore/reconstruction-build-ci`.

## Evidence and boundary
`re/EVIDENCE/hosting_engine.md` records `218D8:421-444`: supplied `/var/tmp/duodash_ab_layout` is parsed as an integer and clamped to 1..8 else 2. The absent/empty override uses preference-derived `73E8()` and is explicitly outside the helper scope.

## Implementation
Added `DDHostLayoutProvidedOverrideValue(NSString *value)` to `ToggleValueHelpers.m`, exported with nonnull parameter in `DuoDashShared.h`. It returns 1..8 unchanged and 2 for out-of-range or unparseable supplied values. Caller must distinguish an absent override and use its existing preference fallback. No file reads, host globals, UI or private selectors touched. Updated structural verifier.

## Verification
PASS: `python scripts/verify_reconstruction.py`, `python -m py_compile scripts/verify_reconstruction.py`, `git diff --check` (line-ending warnings only). Theos arm64 CI for session-311 source pending; do not push automatically.
