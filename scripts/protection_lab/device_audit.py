#!/usr/bin/env python3
"""Strict Mach-O executable auditor and manually supplied iOS runtime log gate.

Build success is never device runtime proof. Device logs are user-supplied,
not cryptographically authenticated, and must match a specific requested ABI.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit import (ARCHES, ARM64_CPUTYPE, ARM64E_KERNEL_ABI,
                   ARM64E_PTRAUTH_VERSIONED, MAGIC)

MH_EXECUTE = 2
VECTORS = 8192
STAGES = ("VM", "CE_ICALL", "IGV_IBR", "OBJC_CE")


def inspect_executable(binary: Path, arch: str) -> dict:
    if arch not in ARCHES:
        raise ValueError(f"unsupported architecture: {arch}")
    data = binary.read_bytes()
    if len(data) < 32:
        raise AssertionError("Incomplete Mach-O executable")
    magic, cpu, raw_subtype, kind = struct.unpack_from("<IIII", data)
    subtype = raw_subtype & 0x00FFFFFF
    if magic != MAGIC or cpu != ARM64_CPUTYPE or kind != MH_EXECUTE or subtype != ARCHES[arch]:
        raise AssertionError(
            f"{binary}: expected {arch} MH_EXECUTE, "
            f"got magic={magic:#x} cpu={cpu:#x} subtype={raw_subtype:#x} kind={kind}"
        )
    if arch == "arm64e" and (
        not (raw_subtype & ARM64E_PTRAUTH_VERSIONED) or
        (raw_subtype & ARM64E_KERNEL_ABI)
    ):
        raise AssertionError("arm64e executable must use versioned userspace PAC ABI")
    return {
        "arch": arch,
        "cpu_subtype_raw": f"0x{raw_subtype:08x}",
        "filetype": "MH_EXECUTE",
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
        "target": "iphoneos",
        "code_signing_and_installation": "NOT_VERIFIED",
        "ios_device_execution": "NOT_TESTED",
        "arm64e_pac_runtime": "NOT_TESTED",
    }


def expected_lines(context: str, arch: str | None = None) -> list[str]:
    if context == "MACOS_HOST":
        abi = "NOT_APPLICABLE"
    elif context == "IOS_DEVICE" and arch in ARCHES:
        abi = f"{arch}:0x{(0x80000000 if arch == 'arm64e' else 0) | ARCHES[arch]:08x}"
    else:
        raise ValueError("Unknown context or iOS architecture")
    return [
        "DD_RUNTIME_CONTEXT=" + context,
        "DD_RUNTIME_ABI=" + abi,
        *(f"DD_RUNTIME_{stage}_PASS={VECTORS}" for stage in STAGES),
        "DD_RUNTIME_COMPLETE=PASS",
    ]


def verify_run_log(path: Path, context: str, arch: str | None = None) -> dict:
    raw = path.read_bytes()
    # Permit CRLF from device collection, but not extra / stale / duplicated lines.
    lines = raw.decode("utf-8", errors="strict").splitlines()
    if lines != expected_lines(context, arch):
        raise AssertionError(
            f"{path}: missing/incorrect runtime parity, ABI, context or COMPLETE=PASS"
        )
    return {
        "context_from_log": context,
        "reported_architecture": arch if context == "IOS_DEVICE" else None,
        "vector_count_per_stage": VECTORS,
        "validated_stages": list(STAGES),
        "log_sha256": hashlib.sha256(raw).hexdigest(),
        "attestation": "USER_SUPPLIED_TEXT_NOT_CRYPTOGRAPHICALLY_AUTHENTICATED",
    }


def build_report(arm64: Path, arm64e: Path, out: Path) -> dict:
    report = {
        "schema": 1,
        "purpose": "manual_on_device_runtime_validation_canary",
        "arm64": inspect_executable(arm64, "arm64"),
        "arm64e": inspect_executable(arm64e, "arm64e"),
        "host_parity": "SEPARATE_WORKFLOW_STEP",
        "ios_on_device_runtime": "NOT_TESTED",
        "iOS_pac_runtime": "NOT_TESTED_A12_PLUS_REQUIRED",
        "device_provisioning": "NOT_CONFIGURED",
        "automatic_device_installation": False,
        "crane_binary_modified": False,
        "commercial_sllvm_or_vmprotect_used": False,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("DD_DEVICE_MACHO_AUDIT_PASS: two MH_EXECUTE slices; device runtime NOT_TESTED")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="Audit cross-compiled iOS executables only")
    build.add_argument("--arm64", type=Path, required=True)
    build.add_argument("--arm64e", type=Path, required=True)
    build.add_argument("--out", type=Path, required=True)
    host = sub.add_parser("verify-host", help="Verify macOS CI host parity log")
    host.add_argument("--log", type=Path, required=True)
    host.add_argument("--out", type=Path, required=True)
    logs = sub.add_parser("verify-log", help="Check an ACTUAL user-collected runtime log")
    logs.add_argument("--log", type=Path, required=True)
    logs.add_argument("--arch", choices=("arm64", "arm64e"), required=True)
    logs.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    if args.command == "build":
        build_report(args.arm64, args.arm64e, args.out)
    else:
        if args.command == "verify-host":
            result = verify_run_log(args.log, "MACOS_HOST")
        else:
            result = verify_run_log(args.log, "IOS_DEVICE", args.arch)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
        if args.command == "verify-host":
            print("DD_HOST_PARITY_VERIFIED: 4 suites x 8192, macOS only")
        else:
            print(f"DD_DEVICE_RUNTIME_LOG_ACCEPTED: claimed {args.arch} execution; "
                  "log provenance not independently verified")
