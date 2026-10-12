# Session-402 — Fix Objective-C smoke compilation variable collision

## Reported macOS CI failure
`hostflow_preflight_smoke.m:422`: `NSArray<NSString *> *fallback` redeclared after `CGRect fallback` at line 348 in the same lexical scope, yielding four clang errors including invalid Objective-C receiver and NSLog format mismatch.

## Fix
Renamed the earlier dock-geometry variable and all eight related references to `fallbackBounds`. Kept the later NSArray fallback and SpringBoard normalization test unchanged.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `python scripts/test_dock_geometry_vectors.py` (2 tests), PASS `git diff --check`. Search confirms distinct identifiers. Native macOS clang and Theos arm64 CI still await execution. No commit or push.
