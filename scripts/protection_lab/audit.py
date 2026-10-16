#!/usr/bin/env python3
"""Fail-closed Mach-O ABI audit for Apple-Clang-only iOS canary slices.

This is compile/link/ABI evidence, never an on-device runtime/PAC pass.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

ARM64_CPUTYPE = 0x0100000C
ARCHES = {"arm64": 0, "arm64e": 2}
MH_DYLIB = 6
MAGIC = 0xFEEDFACF
ARM64E_PTRAUTH_VERSIONED = 0x80000000
ARM64E_KERNEL_ABI = 0x40000000


def inspect(path: Path, expected: str) -> dict:
    if expected not in ARCHES:
        raise ValueError("Unknown architecture")
    raw = path.read_bytes()
    if len(raw) < 32:
        raise AssertionError(f"{path}: not a complete Mach-O header")
    magic, cputype, subtype, filetype = struct.unpack_from("<IIII", raw)
    # ARM64E_ABI_V2 (2) is distinct from unsupported arm64e.old (1).
    sub = subtype & 0x00FFFFFF
    if magic != MAGIC or cputype != ARM64_CPUTYPE or sub != ARCHES[expected] or filetype != MH_DYLIB:
        raise AssertionError(
            f"{path}: expected native {expected} Mach-O dylib subtype={ARCHES[expected]}, "
            f"got magic={magic:#x} cpu={cputype:#x} subtype={sub} type={filetype}; "
            "never relabel arm64e.old or alter Mach-O headers."
        )
    if expected == "arm64e" and (
        not (subtype & ARM64E_PTRAUTH_VERSIONED) or (subtype & ARM64E_KERNEL_ABI)
    ):
        raise AssertionError(
            f"{path}: arm64e must use versioned user-space PAC ABI (subtype={subtype:#x})"
        )
    return {
        "architecture": expected,
        "cpu_subtype": sub,
        "cpu_subtype_raw": f"0x{subtype:08x}",
        "versioned_pac_abi": bool(subtype & ARM64E_PTRAUTH_VERSIONED) if expected == "arm64e" else None,
        "filetype": "MH_DYLIB",
        "size_bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "compiler": "Apple Clang (workflow xcrun)",
        "obfuscation": "none (ABI canary only)",
        "device_runtime": "NOT_TESTED",
        "pac_runtime": "NOT_TESTED",
    }


def report(arm64: Path, arm64e: Path, sources: list[Path], destination: Path,
           host_log: Path | None = None) -> dict:
    if host_log is not None:
        expected = "PROTECTION_LAB_HOST_PASS: 8192 native/VM/indirect vectors"
        if host_log.read_text(encoding="utf-8").strip() != expected:
            raise AssertionError("Host VM parity attestation missing/invalid")
    result = {
        "schema": 1,
        "scope": "isolated_protection_lab_not_installed_by_crane",
        "slices": {
            "arm64": inspect(arm64, "arm64"),
            "arm64e": inspect(arm64e, "arm64e"),
        },
        "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        "vm_backend": "experimental_static_bytecode_interpreter",
        "vmp_commercial_integration": False,
        "sllvm_compiler_integration": False,
        "host_vectors": 8192 if host_log is not None else 0,
        "host_runtime": "PASS_HOST_MACOS_ONLY" if host_log is not None else "NOT_TESTED",
        "ios_device_runtime": "NOT_TESTED",
        "arm64e_pac_device_validation": "NOT_TESTED_A12_PLUS_REQUIRED",
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PROTECTION_LAB_ABI_PASS: native Apple arm64 and arm64e v2 subtype; runtime untested")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--arm64", type=Path, required=True)
    p.add_argument("--arm64e", type=Path, required=True)
    p.add_argument("--source", type=Path, action="append", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--host-log", type=Path, help="Host runner PASS line; NEVER iOS device proof")
    args = p.parse_args()
    report(args.arm64, args.arm64e, args.source, args.out, args.host_log)
