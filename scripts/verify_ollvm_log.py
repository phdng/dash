#!/usr/bin/env python3
"""Require every enabled OLLVM pass to run on every evaluation function.

A build is not considered obfuscated merely because -fpass-plugin was accepted.
This checker intentionally validates the known log contract of the pinned
lich4/ollvm-pass source. A log format change must be reviewed, not ignored.
"""
import argparse
from pathlib import Path

PASSES = ("split", "bcf", "fla", "sub")
TARGETS = {
    "probe": (
        "dd_ollvm_probe",
        "dd_ollvm_probe_branch",
        "dd_ollvm_probe_check",
    ),
    "tweak": (
        "DDLicenseIsPrintableASCIIString",
        "DDLicenseKeyPrefixIndex",
        "DDAppBridgeBaseClassification",
        "DDVersionTupleAtLeast",
        "DDVersionDeviceSanitizeMachineModel",
        "DDFontFloorOverrideValue",
    ),
}


def verify(log: str, kind: str) -> None:
    lines = set(log.splitlines())
    absent = [
        f">>>> run {name} on {function}"
        for function in TARGETS[kind]
        for name in PASSES
        if f">>>> run {name} on {function}" not in lines
    ]
    if absent:
        raise AssertionError(
            f"{kind} OLLVM coverage missing {len(absent)} pass/function events:\n"
            + "\n".join(absent)
        )
    print(f"OLLVM {kind}: {len(TARGETS[kind])} functions x {len(PASSES)} passes verified")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=sorted(TARGETS))
    parser.add_argument("log", type=Path)
    args = parser.parse_args()
    verify(args.log.read_text(encoding="utf-8", errors="replace"), args.kind)


if __name__ == "__main__":
    main()
