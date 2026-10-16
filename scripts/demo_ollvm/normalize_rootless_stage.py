#!/usr/bin/env python3
"""Canonicalize exactly the main Crane tweak filename before rootless packaging.

Theos stages project outputs and the rootless /var/jb install prefix in
separate phases. The post-stage rename may miss the original unprefixed
Crane.dylib; do not silently ship a package without " Crane.dylib".
Only operate on an isolated disposable rootless staging directory.
"""
from __future__ import annotations

import sys
from pathlib import Path

RELATIVE = Path("Library/MobileSubstrate/DynamicLibraries")
PLAIN = "Crane.dylib"
CANONICAL = " Crane.dylib"


def normalize(stage_root: Path) -> Path:
    stage = stage_root.resolve(strict=True)
    if not stage.is_dir():
        raise ValueError("Rootless staging root must be a directory")
    prefixed = stage / "var/jb" / RELATIVE
    raw = stage / RELATIVE
    expected = prefixed / CANONICAL
    candidates = (
        expected,
        prefixed / PLAIN,
        raw / CANONICAL,
        raw / PLAIN,
    )
    found = [path for path in candidates if path.is_file() or path.is_symlink()]
    if len(found) != 1:
        names = [str(path.relative_to(stage)) for path in found]
        raise AssertionError(
            "Expected exactly one staged main Crane dylib, "
            f"found {len(found)} at {names!r}; expected {expected}"
        )
    source = found[0]
    if source.is_symlink() or not source.is_file():
        raise AssertionError(f"Refusing symlink/non-file for Crane binary: {source}")
    if source != expected:
        prefixed.mkdir(parents=True, exist_ok=True)
        source.rename(expected)
        print(
            "ROOTLESS_CRANE_NORMALIZED: "
            f"{source.relative_to(stage)} -> {expected.relative_to(stage)}",
            flush=True,
        )
    else:
        print(f"ROOTLESS_CRANE_NORMALIZED: already {expected.relative_to(stage)}", flush=True)

    if not expected.is_file() or expected.stat().st_size == 0:
        raise AssertionError("Rootless canonical leading-space Crane dylib missing/empty")
    for other in candidates[1:]:
        if other.exists() or other.is_symlink():
            raise AssertionError(f"Noncanonical Crane dylib still staged: {other}")
    return expected


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: normalize_rootless_stage.py <THEOS_STAGING_DIR>")
    try:
        normalize(Path(sys.argv[1]))
    except (OSError, ValueError, AssertionError) as exc:
        print(f"ROOTLESS_CRANE_STAGE_ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
