# Session-387 — Decode packed dock geometry from original 83FC

Continued uncommitted Sessions 385–386 on `chore/reconstruction-build-ci`.

## Decompiled source evidence
`Library/MobileSubstrate/DynamicLibraries/DuoDash.dylib_export_for_ai/decompile/83FC.c` is called by 23D94, 269FC, 26E1C and reads notify name `com.sensetechlab.appbridge/dockrect`; its 64-bit state encodes `x` in high 16 bits, `y` in next 16 bits, `width` in next 16 bits, and `height` in low 16 bits, each divided by 10. Valid when min(width,height)>0.

## Changes
- Exported `DDHostDecodeDockRectState(uint64_t state, CGRect * _Nullable outRect)` in DuoDashShared.h and implemented in compiled HostFlowAdapter.m without private notification I/O.
- Smoke cases verify packed coordinates and dimensions, NULL out pointer, zero state, zero width/height, and unchanged output on invalid state.
- Updated structural verifier export list.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), PASS `git diff --check`. macOS Objective-C runtime, Theos arm64 and live CarPlay unverified; no commit/push.
