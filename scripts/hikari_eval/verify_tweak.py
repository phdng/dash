#!/usr/bin/env python3
"""Fail closed before exposing an experimental DuoDash Hikari dylib.

Only the two Objective-C helpers selected for this opt-in test may report a
Hikari pass. The final binary is still NOT device-verified or release-ready.
"""
import argparse
import hashlib
import re
from pathlib import Path

WHITELIST = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,_-"
EXPECTED = {
    "strenc": "DDVersionDeviceSanitizeMachineModel",
    "constenc": "DDVersionDeviceFormatClientVersion",
}


def inspect(baseline: bytes, candidate: bytes, log: str, symbols: str) -> None:
    if WHITELIST not in baseline:
        raise AssertionError("Normal tweak dylib is missing baseline model alphabet")
    if WHITELIST in candidate:
        raise AssertionError("Hikari tweak dylib still has plaintext model alphabet")
    if baseline == candidate:
        raise AssertionError("Baseline and Hikari dylibs are byte-identical")
    seen = []
    for line in log.splitlines():
        match = re.fullmatch(r">>>> run ([A-Za-z0-9_]+) on (.+)", line.strip())
        if match:
            seen.append((match.group(1), match.group(2)))
    expected = set(EXPECTED.items())
    if set(seen) != expected or len(seen) != len(expected):
        raise AssertionError(
            "Unexpected Hikari coverage. Required exactly two selected "
            f"pass/function events; observed {seen!r}"
        )
    for name in EXPECTED.values():
        if not re.search(r"(?m)^.*\b_" + re.escape(name) + r"\b.*$", symbols):
            raise AssertionError(f"Required exported function not found: {name}")


def record(baseline_path: Path, candidate_path: Path, log_path: Path,
           symbols_path: Path, report_path: Path) -> None:
    baseline = baseline_path.read_bytes()
    candidate = candidate_path.read_bytes()
    inspect(
        baseline, candidate,
        log_path.read_text(encoding="utf-8", errors="replace"),
        symbols_path.read_text(encoding="utf-8", errors="replace"),
    )
    def digest(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    with report_path.open("a", encoding="utf-8") as report:
        report.write("\n## Experimental DuoDash tweak dylib (NOT FOR PRODUCTION)\n\n")
        report.write("| Variant | Bytes | SHA-256 |\n| --- | ---: | --- |\n")
        report.write(f"| Baseline | {len(baseline)} | `{digest(baseline)}` |\n")
        report.write(f"| Hikari only | {len(candidate)} | `{digest(candidate)}` |\n")
        report.write(
            "\nPASS: exactly two Hikari pass/function events; model alphabet "
            "is absent in the experimental dylib; required function symbols "
            "are retained. This does not certify iPhone runtime behavior.\n"
        )
    print("Hikari tweak pilot: precisely 2 pass events, plaintext and symbols PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("log", type=Path)
    parser.add_argument("symbols", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    record(args.baseline, args.candidate, args.log, args.symbols, args.report)
