#!/usr/bin/env python3
"""Fail-closed Kagura K6 selective real VM pilot diagnostics, NOT IPA runtime."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

from oracle import checksums

TARGET = "dd_vm_protected"
GUARD = "dd_vm_guard_protected"
PIPELINE = "function(kagura-vm)"
UUID_CMD = 0x1B


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def body(text: str, function: str) -> str:
    match = re.search(
        rf"^define[^\n]*@{re.escape(function)}\([^\n]*\)[^\n]*\{{\n"
        rf"(.*?)^\}}", text, flags=re.M | re.S)
    if match is None:
        raise AssertionError(f"Missing LLVM function definition: {function}")
    return match.group(1)


def inspect_macho(path: Path) -> str:
    raw = path.read_bytes()
    if len(raw) < 56:
        raise AssertionError("Truncated VM arm64 linked dylib")
    magic, cpu, subtype, kind, count, total, _, _ = struct.unpack_from(
        "<IIIIIIII", raw)
    if (magic, cpu, subtype, kind) != (
        0xFEEDFACF, 0x0100000C, 0, 6):
        raise AssertionError("Expected real arm64 MH_DYLIB, never arm64e")
    if not (1 <= count <= 4096 and 24 <= total <= 1_048_576 and
            32 + total <= len(raw)):
        raise AssertionError("Invalid VM dylib load command bounds")
    offset = 32
    uuids: list[bytes] = []
    for _ in range(count):
        if offset + 8 > 32 + total:
            raise AssertionError("Truncated VM Mach-O command")
        kind_cmd, size = struct.unpack_from("<II", raw, offset)
        if size < 8 or size % 4 != 0 or offset + size > 32 + total:
            raise AssertionError("Malformed VM Mach-O command")
        if kind_cmd == UUID_CMD:
            if size != 24:
                raise AssertionError("Malformed VM LC_UUID")
            uuids.append(raw[offset + 8:offset + 24])
        offset += size
    if offset != 32 + total or len(uuids) != 1:
        raise AssertionError("Expected one complete VM LC_UUID")
    import uuid
    return str(uuid.UUID(bytes=uuids[0]))


def read_native_report(path: Path) -> dict:
    raw = path.read_bytes()
    if not raw or len(raw) > 4096:
        raise AssertionError("Host VM report missing/oversized")
    lines = raw.decode("ascii", errors="strict").splitlines()
    parity, guard = checksums()
    wanted = [
        "DD_VM_SCHEMA=1",
        "DD_VM_CONTEXT=MACOS_HOST",
        "DD_VM_VECTORS_PASS=4096",
        "DD_VM_PARITY_CHECKSUM=" + parity,
        "DD_VM_GUARD_CHECKSUM=" + guard,
        "DD_VM_BENCH_CALLS=1024",
        "DD_VM_BENCH_PAIRS=3",
    ]
    if (not raw.endswith(b"\n") or len(lines) != 14 or
            lines[:7] != wanted or lines[-1] != "DD_VM_COMPLETE=PASS"):
        raise AssertionError("Wrong K6 host result/context/reference checksum")
    pairs = []
    for i in range(3):
        timings = []
        for kind, position in (("PLAIN", 7 + 2 * i),
                               ("PROTECTED", 8 + 2 * i)):
            match = re.fullmatch(
                rf"DD_VM_{kind}_NS_{i}=([0-9]+)", lines[position])
            if match is None or not 1 <= int(match.group(1)) <= 1_000_000_000:
                raise AssertionError("Invalid Kagura VM native timing")
            timings.append(int(match.group(1)))
        pairs.append(timings)
    return {
        "parity_vectors": 4096,
        "baseline_parity_checksum": parity,
        "unprotected_guard_checksum": guard,
        "paired_ns_per_call": pairs,
        "host_timing_observational": True,
        "device_runtime": "NOT_TESTED",
    }


def audit(*, plain_ir: Path, candidate_ir: Path, ios_ir: Path,
          vm_trace: Path, ios_trace: Path, native_log: Path,
          vm_dylib: Path, output: Path) -> dict:
    base = plain_ir.read_text(encoding="utf-8")
    target = candidate_ir.read_text(encoding="utf-8")
    trace = vm_trace.read_text(encoding="utf-8")
    ios_text = ios_ir.read_text(encoding="utf-8")
    ios_log = ios_trace.read_text(encoding="utf-8")
    base_body = body(base, "dd_vm_plain")
    candidate_body = body(target, TARGET)
    guard_base = body(base, "dd_vm_guard_plain")
    guard_candidate = body(target, GUARD)
    if ("@kagura_vm_execute" in base or
            "kagura_vm_execute" not in candidate_body or
            not re.search(r"call\s+i64\s+@kagura_vm_execute\(", candidate_body) or
            "kagura_vm_bc_" not in target or
            "kagura_vm_key_" not in target or
            "kagura_vm_execute" in guard_candidate or
            guard_base != guard_candidate or
            base_body == candidate_body or
            "Running pass: kagura::VMObfuscationPass on dd_vm_protected" not in trace):
        raise AssertionError("Real Kagura VM transformation or allowlist not proven")
    ios_target = body(ios_text, TARGET)
    ios_guard = body(ios_text, GUARD)
    if (not re.search(r"call\s+i64\s+@kagura_vm_execute\(", ios_target) or
            "kagura_vm_bc_" not in ios_text or
            "kagura_vm_key_" not in ios_text or
            "kagura_vm_execute" in ios_guard or
            "Running pass: kagura::VMObfuscationPass on dd_vm_protected" not in ios_log):
        raise AssertionError("iOS arm64 VM actual pass/guard scope absent")
    runtime_data = read_native_report(native_log)
    uuid = inspect_macho(vm_dylib)
    result = {
        "schema": 1,
        "profile": "K6_VM_SELECTIVE_EXPERIMENTAL",
        "upstream_commit": "ac2136ee0408677cf7cdee55307e9b16edd5f4d5",
        "llvm_major": 19,
        "target_symbol": TARGET,
        "guard_symbol": GUARD,
        "pass": PIPELINE,
        "true_vm_trampoline_observed": True,
        "native_guard_body_unchanged": True,
        "vm_bytecode_blob_observed": True,
        "runtime_symbol": "kagura_vm_execute",
        "macos": runtime_data,
        "ios_arm64_build_only": {
            "format": "MH_DYLIB",
            "uuid": uuid,
            "sha256": sha(vm_dylib),
            "device_execution": "NOT_TESTED",
        },
        "inputs_sha256": {
            "baseline_ir": sha(plain_ir),
            "vm_ir": sha(candidate_ir),
            "vm_trace": sha(vm_trace),
            "ios_vm_ir": sha(ios_ir),
            "ios_vm_trace": sha(ios_trace),
            "native_log": sha(native_log),
        },
        "production_crane_modified": False,
        "kagura_lab_k5_ipa_modified": False,
        "arm64e_runtime": "NOT_TESTED",
        "security_attestation": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print("K6_SELECTIVE_VM_HOST_AND_ARM64_BUILD_PASS: 4096 native parity, "
          "real VM trampoline, guard unchanged, iPhone NOT TESTED")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("plain_ir", "candidate_ir", "ios_ir", "vm_trace",
                 "ios_trace", "native_log", "vm_dylib", "output"):
        p.add_argument("--" + name.replace("_", "-"), required=True, type=Path)
    a = p.parse_args()
    audit(**vars(a))


if __name__ == "__main__":
    main()
