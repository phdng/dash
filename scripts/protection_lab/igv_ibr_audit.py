#!/usr/bin/env python3
"""Fail-closed IGV/IBR canary comparator for two Apple Clang Mach-O slices.

Source-level experiment only. Function-pointer dispatch is not an LLVM IBR
pass or evidence of security; host benchmark results are not iOS latency.
"""
from __future__ import annotations

import argparse
import difflib
import json
import math
import re
from pathlib import Path

import audit as macho

HOST_PASS = "IGV_IBR_HOST_PASS: 8192 dual-function parity vectors"
MEASURES = ("igv_plain_us", "igv_protected_us", "ibr_plain_us", "ibr_protected_us")
BENCH = re.compile(
    r"^IGV_IBR_BENCH: " +
    r" ".join(rf"{key}=([0-9]+(?:\.[0-9]+)?)" for key in MEASURES) + r"$"
)


def parse_host_log(log: Path) -> dict[str, object]:
    lines = log.read_text(encoding="utf-8").splitlines()
    if len(lines) != 2 or lines[0] != HOST_PASS:
        raise AssertionError("Host 8192-vector parity proof missing or malformed")
    match = BENCH.fullmatch(lines[1])
    if match is None:
        raise AssertionError("Missing or malformed host benchmark measurements")
    measured = dict(zip(MEASURES, (float(x) for x in match.groups())))
    if any(not math.isfinite(x) or x <= 0 for x in measured.values()):
        raise AssertionError("Host benchmark values must be finite and positive")
    return {
        "tested_vectors": 8192,
        "host_parity": "PASS_MACOS_HOST_ONLY",
        "measurement_unit": "microseconds_per_100000_calls_host_not_ios",
        "measurements": measured,
        "igv_slowdown_host_observation_only": round(
            measured["igv_protected_us"] / measured["igv_plain_us"], 6
        ),
        "ibr_slowdown_host_observation_only": round(
            measured["ibr_protected_us"] / measured["ibr_plain_us"], 6
        ),
        "performance_gate": "NONE_TIMINGS_ARE_NOISY",
    }


def check_pair(plain: Path, protected: Path, plain_asm: Path,
               protected_asm: Path, arch: str, output: Path) -> dict:
    baseline = macho.inspect(plain, arch)
    variant = macho.inspect(protected, arch)
    if plain.read_bytes() == protected.read_bytes():
        raise AssertionError(f"{arch}: plain/protected Mach-O unexpectedly identical")
    before = plain_asm.read_text(encoding="utf-8")
    after = protected_asm.read_text(encoding="utf-8")
    if len(before) < 100 or len(after) < 100:
        raise AssertionError(f"{arch}: empty/incomplete disassembly")
    if before == after:
        raise AssertionError(f"{arch}: expected disassembly difference")
    for symbol in ("_dd_igv_plain", "_dd_ibr_plain"):
        if symbol not in before:
            raise AssertionError(f"{arch}: baseline asm missing {symbol}")
    for symbol in ("_dd_igv_protected", "_dd_ibr_protected"):
        if symbol not in after:
            raise AssertionError(f"{arch}: protected asm missing {symbol}")
    diff = "".join(difflib.unified_diff(
        before.splitlines(keepends=True), after.splitlines(keepends=True),
        fromfile=f"plain-{arch}.asm", tofile=f"protected-{arch}.asm"
    ))
    path = output / f"igv-ibr-{arch}.diff"
    path.write_text(diff, encoding="utf-8")
    if not path.stat().st_size:
        raise AssertionError(f"{arch}: empty asm comparison")
    # This is intentionally informational; symbol names and unrelated
    # relocations alone do not prove the compiler retained the indirection.
    indirect = re.findall(
        r"(?m)^\s*[0-9a-fA-F]+\s+(?:blr|br|braa|brab|blraa|blrab|braaz|brabz)\b",
        after,
    )
    return {
        "plain": baseline,
        "protected": variant,
        "asm_delta_generated": True,
        "indirect_branch_mnemonic_count_whole_asm_heuristic": len(indirect),
        "indirect_branch_verified_in_protected_function": False,
        "source_transformations": [
            "IGV-inspired two-stage typed global pointer load",
            "IBR-inspired bounded state-machine with typed handler pointers",
        ],
        "real_sllvm_compiler_plugin": False,
        "device_pac_runtime": "NOT_TESTED_A12_PLUS_REQUIRED",
        "security_score": None,
    }


def audit(files: dict[str, tuple[Path, Path, Path, Path]],
          host_log: Path, out: Path) -> dict:
    # Avoid writing a partial report if any validation fails.
    timings = parse_host_log(host_log)
    out.mkdir(parents=True, exist_ok=True)
    slices = {arch: check_pair(*files[arch], arch, out)
              for arch in ("arm64", "arm64e")}
    result = {
        "schema": 1,
        "scope": "isolated_source_igv_ibr_pilot_not_crane",
        "host": timings,
        "slices": slices,
        "ios_runtime_test": "NOT_TESTED",
        "arm64e_pac_device_test": "NOT_TESTED_A12_PLUS_REQUIRED",
        "compiler": "Apple Clang",
        "sllvm_plugin_used": False,
        "vmprotect_used": False,
        "disassembly_delta_is_not_security_proof": True,
    }
    (out / "report.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("IGV_IBR_BINARY_PASS: both Mach-O slice pairs, host parity, IDA diffs; A12+ PAC runtime NOT_TESTED")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    for arch in ("arm64", "arm64e"):
        for variant in ("plain", "protected"):
            p.add_argument(f"--{arch}-{variant}", type=Path, required=True)
            p.add_argument(f"--{arch}-{variant}-asm", type=Path, required=True)
    p.add_argument("--host-log", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    files = {
        arch: tuple(getattr(args, arch + "_" + variant + suffix)
                    for variant in ("plain", "protected")
                    for suffix in ("", "_asm"))
        for arch in ("arm64", "arm64e")
    }
    # Reorder to (plain, protected, plain_asm, protected_asm).
    ordered = {k: (v[0], v[2], v[1], v[3]) for k, v in files.items()}
    audit(ordered, args.host_log, args.out)
