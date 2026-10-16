#!/usr/bin/env python3
"""Theos TARGET_CC adapter: Apple Clang by default, LLVM19 only for CRCredits.m.

Selected file receives OLLVM, while 6 other Crane subprojects, shared
CRCommon.m, daemon code and all other CranePrefs sources stay on Apple Clang.
Do not rely on globally appending -fpass-plugin via CranePrefs_CFLAGS.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def is_selected_compile(arguments: list[str]) -> bool:
    # Forbid accidental selection on link, preprocessing or module commands.
    source_files = [
        item for item in arguments
        if item.endswith((".c", ".m", ".mm", ".cc", ".cpp"))
        and not item.startswith("-")
    ]
    return (
        "-c" in arguments
        and len(source_files) == 1
        and Path(source_files[0]).name == "CRCredits.m"
    )


def command_for(arguments: list[str], env: dict[str, str]) -> list[str]:
    apple = env.get("DEMO_APPLE_CLANG", "")
    if not apple:
        raise RuntimeError("DEMO_APPLE_CLANG must name the Xcode clang")
    if not is_selected_compile(arguments):
        return [apple, *arguments]

    llvm = env.get("DEMO_OLLVM_CLANG", "")
    plugin = env.get("DEMO_OLLVM_PLUGIN", "")
    resources = env.get("DEMO_OLLVM_RESOURCE_DIR", "")
    cache = env.get("DEMO_OLLVM_MODULE_CACHE", "")
    if not all((llvm, plugin, resources, cache)):
        raise RuntimeError("LLVM19, plugin, resource dir and module cache required")
    if not Path(plugin).is_file():
        raise RuntimeError(f"OLLVM plugin is missing: {plugin}")
    if not (Path(resources) / "include" / "stddef.h").is_file():
        raise RuntimeError(f"LLVM19 builtin stddef.h missing: {resources}")
    # Explicit LLVM19 resource dir must be the final flag so Theos/Xcode
    # cannot silently redirect builtin includes to Xcode 15.4 clang headers.
    return [
        llvm, *arguments,
        "-O1",
        f"-fpass-plugin={plugin}",
        f"-fmodules-cache-path={cache}",
        "-resource-dir", resources,
    ]


def main() -> None:
    args = sys.argv[1:]
    try:
        command = command_for(args, dict(os.environ))
    except RuntimeError as exc:
        print(f"DEMO_OLLVM_COMPILER_ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    if is_selected_compile(args):
        print(
            f"DEMO_OLLVM_SELECTED: CRCredits.m -> LLVM19; "
            f"resource_dir={os.environ['DEMO_OLLVM_RESOURCE_DIR']}",
            file=sys.stderr, flush=True,
        )
    os.execv(command[0], command)


if __name__ == "__main__":
    main()
