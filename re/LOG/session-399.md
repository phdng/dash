# Session-399 — Fix incorrect 269FC covered smoke fixture

Continued dirty Sessions 390–398 on `chore/reconstruction-build-ci`.

## Defect and fix
Session-398 accepted-left-dock assertion passed `CGRectMake(39,39,122,82)` as usable bounds while expecting the candidate expanded left to x=20. `CGRectInset(usable,-1,-1)` only extended the usable area's left side to x=38, therefore the assertion was wrong and would fail native macOS smoke. Corrected this accepted case to usable `CGRectMake(21,39,140,82)`, which expands left to x=20, and added a rejected case at usable x=21.1 that expands only to x=20.1. The failure case also checks unchanged output.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 synthesis modules), PASS `git diff --check`. Native macOS Objective-C test, arm64 Theos CI and hardware remain unverified; no commit or push.
