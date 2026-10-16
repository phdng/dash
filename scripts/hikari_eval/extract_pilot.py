#!/usr/bin/env python3
"""Extract two exact, isolated Objective-C helper bodies from DuoDash source.

The generated translation unit is for experiment-only compilation. This
deliberately does not rewrite any production source, symbol, hook or Makefile.
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "re/RECONSTRUCTION/VersionDeviceHelpers.m"
FUNCTIONS = (
    "DDVersionDeviceSanitizeMachineModel",
    "DDVersionDeviceFormatClientVersion",
)


def extract_function(source: str, name: str) -> str:
    declaration = re.compile(
        rf"(?m)^NSString \*{re.escape(name)}\(NSString \*value\)\s*\{{"
    )
    matches = list(declaration.finditer(source))
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one definition for {name}")
    start = matches[0].start()
    open_brace = source.find("{", matches[0].start(), matches[0].end())
    if open_brace < 0:
        raise ValueError(f"Missing opening brace for {name}")

    # Fail closed on an unbalanced / unexpected function boundary.
    depth = 0
    in_string = False
    escaped = False
    for index in range(open_brace, len(source)):
        ch = source[index]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1] + "\n"
    raise ValueError(f"Unterminated definition for {name}")


def render(source: str) -> str:
    blocks = [extract_function(source, name) for name in FUNCTIONS]
    assert all(name in block for name, block in zip(FUNCTIONS, blocks))
    return (
        "/* Generated from re/RECONSTRUCTION/VersionDeviceHelpers.m. */\n"
        "#import <Foundation/Foundation.h>\n\n"
        + "\n".join(blocks)
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = SOURCE.read_text(encoding="utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(source), encoding="utf-8")
    print("Extracted 2 real DuoDash Objective-C helper functions for Hikari evaluation")


if __name__ == "__main__":
    main()
