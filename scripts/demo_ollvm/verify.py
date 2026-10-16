#!/usr/bin/env python3
"""Check a CranePrefs-only OLLVM demo experiment before shipping CI artifacts.

This validates a limited set of obfuscation/pass + package invariants.
It does not certify iOS behavior, runtime hook compatibility, or security.
"""
import argparse
import hashlib
import re
from pathlib import Path

PASSES = ("split", "bcf", "fla", "sub")
FUNCTIONS = ("CRCreditsOpenTwitter", "CRCreditsLocalizedRows")
PREFS_EXECUTABLE = Path("Library/PreferenceBundles/CranePrefs.bundle/CranePrefs")
REQUIRED_CLASSES = (
    b"CRPCreditsController",
    b"CRPCreditsMiniZipController",
    b"CRPCreditsZipArchiveController",
)


def verify_passes(log: str) -> dict[tuple[str, str], int]:
    matches = []
    for line in log.splitlines():
        match = re.fullmatch(r">>>> run (\w+) on ([\w.$+-]+)", line.strip())
        if match:
            matches.append((match.group(1), match.group(2)))
    allowed = {(name, func) for name in PASSES for func in FUNCTIONS}
    unexpected = set(matches) - allowed
    if unexpected:
        raise AssertionError(f"Unexpected OLLVM transformations: {sorted(unexpected)}")
    counts = {pair: matches.count(pair) for pair in allowed}
    missing = sorted(pair for pair, count in counts.items() if count == 0)
    if missing:
        raise AssertionError(f"Missing OLLVM pass/function coverage: {missing}")
    return counts


def verify_packages(plain: Path, candidate: Path) -> dict[str, str | int]:
    if not plain.is_dir() or not candidate.is_dir():
        raise AssertionError("Both expanded package roots are required")
    plain_files = {str(p.relative_to(plain)) for p in plain.rglob("*") if p.is_file()}
    obf_files = {str(p.relative_to(candidate)) for p in candidate.rglob("*") if p.is_file()}
    if not plain_files or plain_files != obf_files:
        raise AssertionError(
            f"Package paths diverged. Missing: {sorted(plain_files - obf_files)[:10]}; "
            f"new: {sorted(obf_files - plain_files)[:10]}"
        )
    if str(PREFS_EXECUTABLE) not in plain_files:
        raise AssertionError("CranePrefs.bundle executable missing from package")
    baseline = (plain / PREFS_EXECUTABLE).read_bytes()
    protected = (candidate / PREFS_EXECUTABLE).read_bytes()
    if baseline == protected:
        raise AssertionError("CranePrefs Mach-O binary is byte-identical after OLLVM")
    for klass in REQUIRED_CLASSES:
        if klass not in baseline or klass not in protected:
            raise AssertionError(f"Missing Objective-C UI class metadata: {klass!r}")
    return {
        "files": len(plain_files),
        "baseline_bytes": len(baseline),
        "obf_bytes": len(protected),
        "baseline_sha": hashlib.sha256(baseline).hexdigest(),
        "obf_sha": hashlib.sha256(protected).hexdigest(),
    }


def report(plain: Path, candidate: Path, log_path: Path, out: Path) -> None:
    log = log_path.read_text(encoding="utf-8", errors="replace")
    counts = verify_passes(log)
    info = verify_packages(plain, candidate)
    lines = [
        "# Crane demo OLLVM scoped evaluation",
        "",
        "Selected target: CranePrefs / CRCredits.m (2 functions; 4 OLLVM passes).",
        "",
        "| Function | SPLIT | BCF | FLA | SUB |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for function in FUNCTIONS:
        numbers = " | ".join(str(counts[(name, function)]) for name in PASSES)
        lines.append(f"| `{function}` | {numbers} |")
    lines.extend([
        "",
        f"Matching payload paths: **{info['files']}**",
        "",
        "| CranePrefs binary | Bytes | SHA-256 |",
        "| --- | ---: | --- |",
        f"| Baseline | {info['baseline_bytes']} | `{info['baseline_sha']}` |",
        f"| OLLVM | {info['obf_bytes']} | `{info['obf_sha']}` |",
        "",
        "PASS: pass log coverage, binary difference, UI class markers and equal package paths.",
        "",
        "**Limitations:** compilers differ (Apple Clang vs LLVM19 Clang);",
        "binary differences alone are not proof of OLLVM strength.",
        "No iPhone UI or container regression was executed by this workflow.",
        "Do not install on a primary device or alongside another Crane variant.",
    ])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Crane demo OLLVM verification PASS: {info['files']} matched package files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--ollvm", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report(args.baseline, args.ollvm, args.log, args.report)
