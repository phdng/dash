#!/usr/bin/env python3
"""Compare arm64 CRCredits.o compiled by the SAME LLVM19, with/without OLLVM.

This is a code-generation audit, not a security score. The two objects share
the exact flags, source, SDK and compiler. Only the plugin flag differs.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import re
import struct
import subprocess
from pathlib import Path

ARM64_CPU = 0x0100000C
ARM64_BASE = 0
INSTRUCTION = re.compile(r"^[ \t]+([a-z][a-z0-9.]*)\b")


def verify_arm64_object(path: Path) -> bytes:
    data = path.read_bytes()
    if len(data) < 32:
        raise AssertionError(f"{path}: empty or incomplete object")
    magic, cpu, subtype, kind = struct.unpack_from("<IIII", data)
    if (magic, cpu, subtype & 0x00FFFFFF, kind) != (
        0xFEEDFACF, ARM64_CPU, ARM64_BASE, 1
    ):
        raise AssertionError(
            f"{path}: expected unstripped arm64 MH_OBJECT, "
            f"got header {magic:#x}, {cpu:#x}, {subtype:#x}, {kind}"
        )
    return data


def instructions(assembly: str) -> list[str]:
    result = []
    for line in assembly.splitlines():
        match = INSTRUCTION.match(line)
        if match and not line.strip().endswith(":"):
            result.append(line.strip())
    return result


def conditional_count(insns: list[str]) -> int:
    return sum(
        bool(re.match(r"^(?:b\.(?:eq|ne|lt|le|gt|ge|hi|hs|lo|ls|mi|pl|vs|vc)|cbnz?|tbnz?)\b",
                      instruction))
        for instruction in insns
    )


def disassemble(objdump: str, obj: Path) -> str:
    result = subprocess.run(
        [
            objdump, "--macho", "--disassemble", "--section=__TEXT,__text",
            "--no-leading-addr", "--no-show-raw-insn",
            "--disassembler-color=off", str(obj),
        ],
        capture_output=True, text=True, check=True,
    )
    if not result.stdout.strip():
        raise AssertionError(f"Empty llvm-objdump output for {obj}")
    return result.stdout


def analyze(control: Path, protected: Path, objdump: str, output: Path) -> str:
    control_data = verify_arm64_object(control)
    protected_data = verify_arm64_object(protected)
    if control_data == protected_data:
        raise AssertionError("LLVM19 no-pass and OLLVM objects are byte-identical")
    output.mkdir(parents=True, exist_ok=True)
    before = disassemble(objdump, control)
    after = disassemble(objdump, protected)
    no = instructions(before)
    yes = instructions(after)
    if len(no) < 20 or len(yes) < 20:
        raise AssertionError(
            f"Unable to measure disassembly: no-pass {len(no)} instructions, "
            f"OLLVM {len(yes)}"
        )
    (output / "CRCredits-llvm19-no-pass-arm64.asm").write_text(before, encoding="utf-8")
    (output / "CRCredits-ollvm-strong-arm64.asm").write_text(after, encoding="utf-8")
    if no == yes:
        raise AssertionError("Disassembled arm64 instructions are identical")
    ratio = len(yes) / len(no)
    diff = list(difflib.unified_diff(
        before.splitlines(keepends=True), after.splitlines(keepends=True),
        fromfile="LLVM19 no-pass (arm64)", tofile="LLVM19 + OLLVM strong (arm64)",
    ))
    (output / "CRCredits-arm64.diff").write_text("".join(diff), encoding="utf-8")
    # A noticeable difference is required for this investigation, not
    # falsely presented as evidence of cryptographic resistance.
    if ratio < 1.20:
        raise AssertionError(
            f"Expected clearly visible expansion >=1.20x; got {ratio:.2f}x. "
            "Inspect attached objdump files before accepting the new profile."
        )
    lines = [
        "## Same-compiler arm64 disassembly: no-pass vs OLLVM strong",
        "",
        "Both object files were built from **the same CRCredits.m** using **LLVM19**",
        "and the same architecture, SDK and optimization flags.",
        "**Only the OLLVM plugin flag differs.** These are unstripped build objects,",
        "not the installable .deb or its stripped universal CranePrefs binary.",
        "",
        "| Metric | LLVM19 no-pass | LLVM19 + OLLVM strong |",
        "| --- | ---: | ---: |",
        f"| Instructions in __TEXT,__text | {len(no)} | {len(yes)} |",
        f"| Conditional branches (approx.) | {conditional_count(no)} | {conditional_count(yes)} |",
        f"| Mach-O object bytes | {len(control_data)} | {len(protected_data)} |",
        f"| Object SHA-256 | `{hashlib.sha256(control_data).hexdigest()}` | `{hashlib.sha256(protected_data).hexdigest()}` |",
        "",
        f"Instruction-count ratio: **{ratio:.2f}x** (observability threshold 1.20x).",
        "",
        "Download the two .asm files and CRCredits-arm64.diff for direct inspection",
        "with a disassembler. More branches/instructions are *not* a security",
        "proof; compiler optimizations and basic-block structure affect metrics.",
        "In this package **arm64e** still uses Apple Clang without OLLVM.",
    ]
    report = "\n".join(lines) + "\n"
    (output / "CRCredits-disassembly-report.md").write_text(report, encoding="utf-8")
    print(f"LLVM19 strong evidence PASS: {len(no)} -> {len(yes)} instructions ({ratio:.2f}x); "
          f"branches {conditional_count(no)} -> {conditional_count(yes)}")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--protected", type=Path, required=True)
    parser.add_argument("--objdump", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    analyze(args.control, args.protected, args.objdump, args.out)
