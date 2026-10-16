#!/usr/bin/env python3
"""Theos TARGET_CC adapter: apply LLVM19+OLLVM only to CRCredits.m / arm64.

The Apple arm64e ABI used by Xcode is not link-compatible with LLVM19's
arm64e.old objects. Compile CRCredits.m / arm64e with Apple Clang, like every
other file. Never change Mach-O CPU subtypes or force-link incompatible ABIs.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path


def is_credits_compile(arguments: list[str]) -> bool:
    sources = [
        item for item in arguments
        if item.endswith((".c", ".m", ".mm", ".cc", ".cpp"))
        and not item.startswith("-")
    ]
    return (
        "-c" in arguments
        and len(sources) == 1
        and Path(sources[0]).name == "CRCredits.m"
    )


def compile_architecture(arguments: list[str]) -> str:
    """Identify the single requested architecture (Theos may use -arch or -target).

    Ambiguous or missing architectures must fail closed for the selected file.
    """
    arches = []
    for index, value in enumerate(arguments):
        if value in ("-arch", "-target", "--target"):
            if index + 1 >= len(arguments):
                raise RuntimeError(f"Compiler flag {value} has no value")
            candidate = arguments[index + 1]
        elif value.startswith(("-arch=", "-target=", "--target=")):
            candidate = value.split("=", 1)[1]
        else:
            continue
        match = re.match(r"^(arm64e|arm64)(?:-|$)", candidate)
        if not match:
            raise RuntimeError(f"Unsupported demo architecture: {candidate}")
        arches.append(match.group(1))
    if len(set(arches)) != 1 or not arches:
        raise RuntimeError(f"Missing or ambiguous architecture for CRCredits.m: {arches}")
    return arches[0]


def is_selected_compile(arguments: list[str]) -> bool:
    return is_credits_compile(arguments) and compile_architecture(arguments) == "arm64"


def command_for(arguments: list[str], env: dict[str, str]) -> list[str]:
    apple = env.get("DEMO_APPLE_CLANG", "")
    if not apple:
        raise RuntimeError("DEMO_APPLE_CLANG must name the Xcode clang")
    if not is_credits_compile(arguments):
        return [apple, *arguments]

    arch = compile_architecture(arguments)
    if arch == "arm64e":
        # Apple Clang emits the correct arm64e ABI; Homebrew LLVM19 emits
        # arm64e.old, rejected by Apple's linker. This slice is NOT obfuscated.
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
        arch = compile_architecture(args) if is_credits_compile(args) else None
    except RuntimeError as exc:
        print(f"DEMO_OLLVM_COMPILER_ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    if arch == "arm64":
        print(
            "DEMO_OLLVM_SELECTED: CRCredits.m (arm64) -> LLVM19; "
            f"resource_dir={os.environ['DEMO_OLLVM_RESOURCE_DIR']}",
            file=sys.stderr, flush=True,
        )
    elif arch == "arm64e":
        print(
            "DEMO_OLLVM_BYPASS: CRCredits.m (arm64e) -> Apple Clang; "
            "reason=LLVM19-arm64e.old",
            file=sys.stderr, flush=True,
        )
    os.execv(command[0], command)


if __name__ == "__main__":
    main()
