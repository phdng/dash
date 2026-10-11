# Session-373 — Guard new private-host entrypoints in structural CI verifier

Continued uncommitted Sessions 361–372 on `chore/reconstruction-build-ci`.

## Change
- Extended `scripts/verify_reconstruction.py` to require exactly one public header declaration and compiled implementation for nine newly promoted host-flow helpers: 3DD4C BID normalizers, 218D8 prepared BID/geometry composition, and 208F4 dimensions preflight.
- Ensured smoke harness retains private-selector invocation, integrated prepared request check, and lookup count assertions, and workflow still references and executes that harness.
- This is structural contract checking, **not** runtime proof; cannot replace the macOS clang executable or arm64 device/CI.

## Verification
PASS `python scripts/verify_reconstruction.py` (30 modules), `python -m py_compile scripts/verify_reconstruction.py`, and `git diff --check`. macOS and arm64 CI not executed. No commit/push.
