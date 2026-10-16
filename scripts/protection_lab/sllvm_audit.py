#!/usr/bin/env python3
"""Compare exact CE canary exposure in real Apple-Clang Mach-O dylib pairs.

Subtypes and PAC ABI are validated using the existing strict lab auditor.
Binary marker absence is an *observability* test, not proof of security.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import audit as macho_audit
import sllvm_generator as ce


def check_pair(plain: Path, protected: Path, arch: str) -> dict:
    control = macho_audit.inspect(plain, arch)
    candidate = macho_audit.inspect(protected, arch)
    before, after = plain.read_bytes(), protected.read_bytes()
    marker = ce.MARKER
    encoded = ce.encode(marker)
    if before == after:
        raise AssertionError(f"{arch}: binary did not change")
    if before.count(marker) < 1:
        raise AssertionError(f"{arch}: control Mach-O missing literal marker")
    if marker in after:
        raise AssertionError(f"{arch}: plaintext marker leaked into protected Mach-O")
    if encoded not in after:
        raise AssertionError(f"{arch}: encoded CE test-only bytes absent from Mach-O")
    return {
        "architecture": arch,
        "plain": control,
        "protected": candidate,
        "plain_marker_occurrences": before.count(marker),
        "protected_marker_occurrences": after.count(marker),
        "encoded_data_present": True,
        "transformations": ["source-level CE-inspired", "typed ICALL-inspired"],
        "sllvm_commercial_plugin_loaded": False,
        "vmprotect_commercial_plugin_loaded": False,
        "runtime_iOS_device": "NOT_TESTED",
        "security_score": None,
    }


def build_report(files: dict[str, tuple[Path, Path]],
                 host_log: Path, header: Path, out: Path) -> dict:
    expected = "SLLVM_PILOT_HOST_PASS: 8192 CE/ICALL parity vectors"
    if host_log.read_text(encoding="utf-8").strip() != expected:
        raise AssertionError("Missing/incorrect actual native host parity result")
    header_bytes = header.read_bytes()
    expected_initializer = ", ".join(f"0x{b:02x}" for b in ce.encode())
    if ce.MARKER in header_bytes or expected_initializer.encode("ascii") not in header_bytes:
        raise AssertionError("CE header missing expected encoded initializer or leaks plaintext")
    report = {
        "schema": 1,
        "scope": "isolated_duodash_protection_lab_only",
        "host_vectors_verified": 8192,
        "slices": {arch: check_pair(*files[arch], arch) for arch in ("arm64", "arm64e")},
        "encoded_header_sha256": hashlib.sha256(header_bytes).hexdigest(),
        "ios_device_pac_runtime": "NOT_TESTED_A12_PLUS_REQUIRED",
        "claim": "binary visibility and host parity only; not SLLVM compiler nor VMProtect",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("SLLVM_PILOT_BINARY_PASS: arm64/arm64e CE absence + encoded data presence; PAC runtime untested")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    for arch in ("arm64", "arm64e"):
        for variant in ("plain", "protected"):
            p.add_argument(f"--{arch}-{variant}", type=Path, required=True)
    p.add_argument("--host-log", type=Path, required=True)
    p.add_argument("--header", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    build_report({
        arch: (getattr(args, arch + "_plain"), getattr(args, arch + "_protected"))
        for arch in ("arm64", "arm64e")
    }, args.host_log, args.header, args.out)
