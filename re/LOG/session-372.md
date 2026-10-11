# Session-372 — Assert private application lookup call counts in macOS smoke

Continued uncommitted Sessions 361–371 on `chore/reconstruction-build-ci`.

## Change
Extended test-only SBApplicationController mock in `scripts/hostflow_preflight_smoke.m` with `DDMockApplicationLookupCount`. For the four-slot normalization scenario, assert exactly two application lookups: unknown non-CarPlay BID and existing non-CarPlay BID; skip CarPlay UI and duplicate normalized entries. With nil shared controller, assert no application lookups during normalization or prepared-host checks. This directly protects private conditional invocation semantics from decoded `3DD4C.c`.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules) and `git diff --check`. macOS Objective-C smoke executable not run locally; arm64 Theos CI and jailbreak CarPlay remain unverified. No commit or push.
