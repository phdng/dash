# Session-388 — 26654 CarPlay dock edge-strip classification

Continued uncommitted Sessions 385–387 on branch `chore/reconstruction-build-ci`.

## Original evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/26654.c` intersects the dock rectangle with a usable area. Returns labels `not-an-edge-strip`, `strip-outside-area`, `left`, `right`, `top`, `bottom` and `degenerate`, based on 2pt coverage/edge tolerance, with residual width/height below 40pt classified `degenerate`. This branch classification is separate from the CGRect return-value ABI recovery.

## Implementation
- Exported `DDHostDockEdgeLabel(CGRect usableBounds, CGRect dockBounds)` in DuoDashShared.h, with a pure-data implementation in HostFlowAdapter.m.
- Added smoke coverage for four edges, outside, middle/non-edge, degenerate and empty dock.
- Updated `scripts/verify_reconstruction.py` to recognize `NSString *` return-type definitions for the new helper, alongside existing BOOL, NSArray and struct signatures.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules); PASS `python -m py_compile scripts/verify_reconstruction.py`; PASS `git diff --check`. macOS Objective-C executable, Theos arm64 and live CarPlay remain unverified. No commit/push.
