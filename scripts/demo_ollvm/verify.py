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
PACKAGING_PREFIXES = {"roothide": Path("."), "rootless": Path("var/jb")}
REQUIRED_CLASSES = (
    b"CRPCreditsController",
    b"CRPCreditsMiniZipController",
    b"CRPCreditsZipArchiveController",
)
SELECTED_ROUTE = "DEMO_OLLVM_SELECTED: CRCredits.m (arm64) -> LLVM19;"
BYPASS_ROUTE = "DEMO_OLLVM_BYPASS: CRCredits.m (arm64e) -> Apple Clang;"


def verify_compiler_routes(log: str) -> None:
    routes = [line.strip() for line in log.splitlines()
              if line.strip().startswith(("DEMO_OLLVM_SELECTED:", "DEMO_OLLVM_BYPASS:"))]
    if (len(routes) != 2 or
        sum(line.startswith(SELECTED_ROUTE) for line in routes) != 1 or
        sum(line.startswith(BYPASS_ROUTE) for line in routes) != 1 or
        any(not line.startswith((SELECTED_ROUTE, BYPASS_ROUTE)) for line in routes)):
        raise AssertionError(f"Expected one LLVM19 arm64 / Apple arm64e route: {routes!r}")


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
    incorrect = sorted((pair, count) for pair, count in counts.items() if count != 1)
    if incorrect:
        raise AssertionError(f"Expected each OLLVM pass/function exactly once on arm64: {incorrect}")
    return counts


def verify_packages(plain: Path, candidate: Path, scheme: str = "roothide") -> dict[str, str | int]:
    if scheme not in PACKAGING_PREFIXES:
        raise AssertionError(f"Unsupported scheme {scheme!r}")
    if not plain.is_dir() or not candidate.is_dir():
        raise AssertionError("Both expanded package roots are required")
    executable = PACKAGING_PREFIXES[scheme] / PREFS_EXECUTABLE
    plain_files = {p.relative_to(plain).as_posix() for p in plain.rglob("*") if p.is_file()}
    obf_files = {p.relative_to(candidate).as_posix() for p in candidate.rglob("*") if p.is_file()}
    if not plain_files or plain_files != obf_files:
        raise AssertionError(
            f"Package paths diverged. Missing: {sorted(plain_files - obf_files)[:10]}; "
            f"new: {sorted(obf_files - plain_files)[:10]}"
        )
    if executable.as_posix() not in plain_files:
        raise AssertionError(f"CranePrefs.bundle executable missing from {scheme} package")
    baseline = (plain / executable).read_bytes()
    protected = (candidate / executable).read_bytes()
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


def report(plain: Path, candidate: Path, log_path: Path, out: Path,
           scheme: str = "roothide") -> None:
    log = log_path.read_text(encoding="utf-8", errors="replace")
    verify_compiler_routes(log)
    counts = verify_passes(log)
    info = verify_packages(plain, candidate, scheme)
    lines = [
        "# Crane demo OLLVM scoped evaluation",
        "",
        f"Theos package scheme: **{scheme}**.",
        f"Expected Debian Architecture: **{'iphoneos-arm64' if scheme == 'rootless' else 'iphoneos-arm64e'}**.",
        "",
        "Profile: STRONG / experimental — SPLIT4, BCF 100% × 2, FLA, SUB × 3.",
        "Selected target: CranePrefs / CRCredits.m (2 functions; 4 OLLVM pass families).",
        "Architecture scope: **arm64 only** receives LLVM19 + OLLVM.",
        "The **arm64e** slice is compiled by Apple Clang without OLLVM to preserve its ABI.",
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
        "PASS: one LLVM19 arm64 compile + one Apple arm64e compile, eight OLLVM pass events,",
        "binary difference, UI class markers and equal package paths.",
        "",
        "**Limitations:** compilers differ (Apple Clang vs LLVM19 Clang);",
        "binary differences alone are not proof of OLLVM strength.",
        "For direct evidence, inspect same-LLVM19 CRCredits disassembly",
        "without plugin vs with STRONG plugin, plus installed arm64 CranePrefs",
        "slices, all included in this experiment's binary-audit artifacts.",
        "**Device validation:** not executed by this workflow. Installation or",
        "Settings/Credits runtime PASS must be reported separately from this audit.",
        "Test plan: docs/CRANE_ROOTHIDE_DEVICE_TEST.md (D01-D09).",
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
    parser.add_argument("--scheme", choices=PACKAGING_PREFIXES, default="roothide")
    args = parser.parse_args()
    report(args.baseline, args.ollvm, args.log, args.report, args.scheme)
