#!/usr/bin/env python3
"""Audits two real-source DuoDash Objective-C helpers in an isolated CI pilot."""
import argparse
import hashlib
from pathlib import Path

# This is a public input-validation alphabet, not a secret.
ALLOWED_MODEL_ALPHABET = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,_-"
REQUIRED_LOGS = (
    ">>>> run strenc on DDVersionDeviceSanitizeMachineModel",
    ">>>> run constenc on DDVersionDeviceFormatClientVersion",
)


def check_objects(plain: bytes, protected: bytes, log: str) -> None:
    for phrase in REQUIRED_LOGS:
        if phrase not in log.splitlines():
            raise AssertionError(f"Hikari did not report expected pilot pass: {phrase}")
    if ALLOWED_MODEL_ALPHABET not in plain:
        raise AssertionError("Baseline Objective-C object lacks expected allowlist string")
    if ALLOWED_MODEL_ALPHABET in protected:
        raise AssertionError("Objective-C allowlist remains plaintext in Hikari object")
    if plain == protected:
        raise AssertionError("Hikari did not change the Objective-C object")


def check_outputs(plain: str, protected: str) -> None:
    baseline = plain.splitlines()
    candidate = protected.splitlines()
    if len(baseline) != 213 or len(candidate) != 213:
        raise AssertionError(f"Pilot expects 213 vectors; found {len(baseline)} and {len(candidate)}")
    if baseline != candidate:
        for i, (left, right) in enumerate(zip(baseline, candidate)):
            if left != right:
                raise AssertionError(f"Objective-C semantic mismatch at vector {i}")
        raise AssertionError("Objective-C output length mismatch")
    for index, line in enumerate(baseline):
        if not line.startswith(f"{index:03d}:"):
            raise AssertionError(f"Malformed Objective-C pilot vector {index}")


def audit(target: str, plain_object: Path, protected_object: Path, log: Path,
          report: Path, plain_output: Path | None,
          protected_output: Path | None, protected_executable: Path | None) -> None:
    plain_bytes = plain_object.read_bytes()
    protected_bytes = protected_object.read_bytes()
    check_objects(plain_bytes, protected_bytes, log.read_text(encoding="utf-8", errors="replace"))
    if target == "native":
        if not (plain_output and protected_output and protected_executable):
            raise ValueError("Native test needs both outputs and final executable")
        check_outputs(
            plain_output.read_text(encoding="utf-8"),
            protected_output.read_text(encoding="utf-8"),
        )
        if ALLOWED_MODEL_ALPHABET in protected_executable.read_bytes():
            raise AssertionError("Objective-C allowlist remains in protected executable")
    elif any((plain_output, protected_output, protected_executable)):
        raise ValueError("iOS object-only test cannot claim runtime equivalence")

    digest = lambda obj: hashlib.sha256(obj).hexdigest()[:16]  # noqa: E731
    with report.open("a", encoding="utf-8") as stream:
        stream.write(
            f"| Objective-C {target} | {len(plain_bytes)} | {len(protected_bytes)} | "
            f"`{digest(plain_bytes)}` | `{digest(protected_bytes)}` | PASS |\n"
        )
    print(f"Hikari Objective-C {target}: passes and allowlist audit PASS"
          + ("; 213 runtime vectors matched" if target == "native" else ""))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", choices=("native", "ios"))
    parser.add_argument("plain_object", type=Path)
    parser.add_argument("protected_object", type=Path)
    parser.add_argument("log", type=Path)
    parser.add_argument("report", type=Path)
    parser.add_argument("--plain-output", type=Path)
    parser.add_argument("--protected-output", type=Path)
    parser.add_argument("--protected-executable", type=Path)
    args = parser.parse_args()
    audit(args.target, args.plain_object, args.protected_object, args.log,
          args.report, args.plain_output, args.protected_output,
          args.protected_executable)


if __name__ == "__main__":
    main()
