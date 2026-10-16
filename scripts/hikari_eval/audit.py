#!/usr/bin/env python3
"""Fail-closed Hikari evaluation: pass coverage, semantics and binary string audit.

Only a disposable, non-secret test marker is scanned here. Checking absence of
one marker does NOT prove that arbitrary application strings are encrypted.
"""
import argparse
import hashlib
import re
from pathlib import Path

MARKER = b"DUODASH_HIKARI_CANARY_ONLY_7F29D1B3"
PASS_LINES = (
    ">>>> run strenc on dd_hikari_probe_string",
    ">>>> run constenc on dd_hikari_probe_const",
)


def audit_object(plain: bytes, protected: bytes, log: str) -> None:
    for signal in PASS_LINES:
        if signal not in log.splitlines():
            raise AssertionError(f"Hikari did not report expected pass: {signal}")
    if MARKER not in plain:
        raise AssertionError("Baseline object does not contain the test marker")
    if MARKER in protected:
        raise AssertionError("Test marker remains plaintext in the Hikari object")
    if plain == protected:
        raise AssertionError("Protected object is identical to the baseline")


def audit_output(plain: str, protected: str) -> None:
    plain_lines = plain.splitlines()
    protected_lines = protected.splitlines()
    if len(plain_lines) != 513 or len(protected_lines) != 513:
        raise AssertionError(
            f"Expected 513 native vectors in both runs; got "
            f"{len(plain_lines)} and {len(protected_lines)}"
        )
    for index, line in enumerate(plain_lines):
        expected = index - 256
        if not re.fullmatch(r"-?\d+:[0-9a-f]{8}:[0-9a-f]{8}", line):
            raise AssertionError(f"Unexpected native fixture output at {index}")
        if int(line.split(":", 1)[0]) != expected:
            raise AssertionError(f"Native vector input mismatch at {index}")
    if plain_lines != protected_lines:
        mismatch = next(
            i for i, (left, right) in enumerate(zip(plain_lines, protected_lines))
            if left != right
        )
        raise AssertionError(f"Native output mismatch at vector {mismatch}")


def run(kind: str, plain_object: Path, protected_object: Path,
        log_path: Path, report: Path, plain_output: Path | None = None,
        protected_output: Path | None = None,
        protected_executable: Path | None = None) -> None:
    plain_data = plain_object.read_bytes()
    protected_data = protected_object.read_bytes()
    log = log_path.read_text(encoding="utf-8", errors="replace")
    audit_object(plain_data, protected_data, log)
    if kind == "native":
        if plain_output is None or protected_output is None:
            raise ValueError("Native audit requires both output files")
        audit_output(
            plain_output.read_text(encoding="utf-8"),
            protected_output.read_text(encoding="utf-8"),
        )
        if protected_executable is None:
            raise ValueError("Native audit requires protected executable to scan")
        if MARKER in protected_executable.read_bytes():
            raise AssertionError("Test marker remains plaintext in native executable")
    else:
        if (plain_output is not None or protected_output is not None
                or protected_executable is not None):
            raise ValueError("Cross-compiled iOS audit must not claim runtime equivalence")
    sha = lambda content: hashlib.sha256(content).hexdigest()  # noqa: E731
    with report.open("a", encoding="utf-8") as stream:
        stream.write(
            f"| {kind} | {len(plain_data)} | {len(protected_data)} | "
            f"`{sha(plain_data)[:16]}` | `{sha(protected_data)[:16]}` | PASS |\n"
        )
    print(f"Hikari {kind}: string and constant passes confirmed; "
          f"plaintext marker absent in protected object"
          + ("; 513 output vectors identical" if kind == "native" else ""))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("native", "ios"))
    parser.add_argument("plain_object", type=Path)
    parser.add_argument("protected_object", type=Path)
    parser.add_argument("log", type=Path)
    parser.add_argument("report", type=Path)
    parser.add_argument("--plain-output", type=Path)
    parser.add_argument("--protected-output", type=Path)
    parser.add_argument("--protected-executable", type=Path)
    args = parser.parse_args()
    run(args.kind, args.plain_object, args.protected_object, args.log,
        args.report, args.plain_output, args.protected_output,
        args.protected_executable)


if __name__ == "__main__":
    main()
