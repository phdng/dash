#!/usr/bin/env python3
"""Prepare an isolated demo/Crane Theos tree; never alter uploaded demo sources.

LLVM19 OLLVM is scoped only to two functions within CRCredits.m. The
compiler_select.py adapter applies OLLVM flags only to CRCredits.m compile
invocations; hooks, daemons, CRCommon.m, and other UI source files stay on
Apple Clang. No production or sandbox Makefile is modified.
"""
import argparse
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICY = HERE / "policy.json"
BUNDLE_INCLUDE = "include $(THEOS_MAKE_PATH)/bundle.mk"


def prepare(source: Path, destination: Path, variant: str, plugin: Path | None) -> None:
    if variant not in ("baseline", "ollvm"):
        raise ValueError("Unknown build variant")
    if not (source / "Makefile").is_file() or not (
        source / "sources/prefs/CRCredits.m"
    ).is_file():
        raise ValueError("demo/reconstruction/Makefile and CRCredits.m are required")
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing sandbox: {destination}")
    shutil.copytree(
        source, destination,
        ignore=shutil.ignore_patterns(".theos", "packages", "obj", "build.log", "*.deb"),
    )

    if variant == "baseline":
        return
    if plugin is None or not plugin.is_file() or not plugin.is_absolute():
        raise ValueError("OLLVM variant requires a compiled absolute plugin path")
    if any(c.isspace() for c in str(plugin)):
        raise ValueError("Plugin path must not contain whitespace")

    configuration = json.loads(POLICY.read_text(encoding="utf-8"))
    if set(configuration) != {"policy_map", "policies"}:
        raise ValueError("Unexpected OLLVM policy shape")
    # The OLLVM pass reads policy.json from process current working directory.
    # Theos subprojects can compile in either the root or their own directories.
    content = POLICY.read_text(encoding="utf-8")
    for directory in (destination, destination / "sources/prefs"):
        (directory / "policy.json").write_text(content, encoding="utf-8")

    # All source Makefiles remain byte-for-byte original. Only the CI-supplied
    # compiler dispatcher chooses LLVM19 for one translation unit.
    makefile = destination / "sources/prefs/Makefile"
    original = makefile.read_text(encoding="utf-8")
    if original.count(BUNDLE_INCLUDE) != 1:
        raise ValueError("Unexpected CranePrefs makefile layout")
    if makefile.read_bytes() != (source / "sources/prefs/Makefile").read_bytes():
        raise AssertionError("Sandbox unexpectedly modified CranePrefs Makefile")

    assert (destination / "sources/maindylib/Makefile").read_bytes() == (
        source / "sources/maindylib/Makefile"
    ).read_bytes()
    assert (destination / "sources/cranesb/Makefile").read_bytes() == (
        source / "sources/cranesb/Makefile"
    ).read_bytes()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--dest", type=Path, required=True)
    parser.add_argument("--variant", choices=("baseline", "ollvm"), required=True)
    parser.add_argument("--plugin", type=Path)
    args = parser.parse_args()
    prepare(args.source.resolve(), args.dest.resolve(), args.variant,
            args.plugin.resolve() if args.plugin is not None else None)
    print(f"Demo {args.variant} sandbox prepared (source untouched): {args.dest}")
