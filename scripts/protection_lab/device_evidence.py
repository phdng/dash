#!/usr/bin/env python3
"""Compare the iOS app's reported Mach-O LC_UUID with a CI binary manifest.

A UUID match plus user-provided logs is useful consistency evidence, NOT
cryptographic proof of device execution, PAC enforcement, or file identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import uuid
from pathlib import Path

import device_audit
import perf_audit

LC_UUID = 0x1B
MAX_COMMAND_BYTES = 1024 * 1024
MAX_COMMANDS = 4096
IDENTITY_NOTE = "USER_SHARED_NOT_ATTESTED"
MODEL = re.compile(r"(?:iPhone|iPad)[0-9]{1,3},[0-9]{1,3}\Z")
VERSION = re.compile(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\Z")
UUID_LOWER = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z"
)


def macho_uuid(path: Path) -> str:
    data = path.read_bytes()
    if len(data) < 32:
        raise AssertionError("Mach-O truncated before header")
    magic, cpu, sub, kind, ncmds, sizeofcmds, flags, reserved = struct.unpack_from(
        "<IIIIIIII", data
    )
    del cpu, sub, flags, reserved
    if magic != device_audit.MAGIC or kind != device_audit.MH_EXECUTE:
        raise AssertionError("Expected a 64-bit Mach-O executable")
    if not (1 <= ncmds <= MAX_COMMANDS and
            24 <= sizeofcmds <= MAX_COMMAND_BYTES and
            32 + sizeofcmds <= len(data)):
        raise AssertionError("Mach-O load command region out of bounds")
    pos = 32
    end = 32 + sizeofcmds
    matches = []
    for _ in range(ncmds):
        if pos + 8 > end:
            raise AssertionError("Incomplete Mach-O load command")
        cmd, cmdsize = struct.unpack_from("<II", data, pos)
        if cmdsize < 8 or cmdsize % 4 or cmdsize > end - pos:
            raise AssertionError("Invalid Mach-O load command size/alignment")
        if cmd == LC_UUID:
            if cmdsize != 24:
                raise AssertionError("Malformed Mach-O LC_UUID command")
            matches.append(str(uuid.UUID(bytes=data[pos + 8: pos + 24])))
        pos += cmdsize
    if pos != end or len(matches) != 1:
        raise AssertionError("Mach-O must have exactly one LC_UUID")
    return matches[0]


def manifest_for_binaries(arm64: Path, arm64e: Path, output: Path) -> dict:
    slices = {}
    for arch, binary in (("arm64", arm64), ("arm64e", arm64e)):
        details = device_audit.inspect_executable(binary, arch)
        details["macho_uuid"] = macho_uuid(binary)
        slices[arch] = details
    if slices["arm64"]["macho_uuid"] == slices["arm64e"]["macho_uuid"]:
        raise AssertionError("Independent arm64/arm64e binaries share one LC_UUID")
    result = {
        "schema": 1,
        "purpose": "ci_unsigned_lab_app_identity",
        "slices": slices,
        "runtime_on_iphone": "NOT_TESTED_BY_CI",
        "code_signature_and_device_provisioning": "NOT_VERIFIED",
        "uuid_security_attestation": False,
        "prod_crane_modified": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    return result


def parse_evidence(path: Path, arch: str) -> dict:
    expected_abi = device_audit.expected_lines("IOS_DEVICE", arch)[1].split("=", 1)[1]
    lines = path.read_bytes().decode("utf-8", errors="strict").splitlines()
    if len(lines) != 7 or lines[0:3] != [
        "DD_EVIDENCE_SCHEMA=1",
        "DD_EVIDENCE_CONTEXT=IOS_DEVICE",
        "DD_EVIDENCE_ABI=" + expected_abi,
    ] or lines[-1] != "DD_EVIDENCE_NOTE=" + IDENTITY_NOTE:
        raise AssertionError("Malformed or wrong-platform device identity report")
    labels = ("DD_EVIDENCE_MACHO_UUID=", "DD_EVIDENCE_DEVICE_MODEL=",
              "DD_EVIDENCE_IOS_VERSION=")
    values = []
    for item, label in zip(lines[3:6], labels):
        if not item.startswith(label):
            raise AssertionError("Identity report fields missing or out of order")
        values.append(item[len(label):])
    identity_uuid, model, version = values
    if not UUID_LOWER.fullmatch(identity_uuid) or not MODEL.fullmatch(model) or (
        not VERSION.fullmatch(version)
    ):
        raise AssertionError("Invalid LC_UUID, model or OS version format")
    return {"macho_uuid": identity_uuid, "device_model_claimed": model,
            "ios_version_claimed": version, "architecture_claimed": arch,
            "identity_log_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def verify_bundle(*, manifest: Path, arch: str, identity: Path,
                  parity: Path, output: Path, performance: Path | None = None) -> dict:
    original = json.loads(manifest.read_text(encoding="utf-8"))
    if original.get("schema") != 1 or original.get("purpose") != (
        "ci_unsigned_lab_app_identity"
    ) or original.get("uuid_security_attestation") is not False:
        raise AssertionError("Unrecognized CI binary-identity manifest")
    if set(original.get("slices", {})) != {"arm64", "arm64e"}:
        raise AssertionError("Incomplete artifact architecture manifest")
    expected = original["slices"][arch]
    declared = parse_evidence(identity, arch)
    if expected.get("arch") != arch or expected.get("filetype") != "MH_EXECUTE":
        raise AssertionError("CI manifest has wrong architecture/object type")
    if declared["macho_uuid"] != expected.get("macho_uuid"):
        raise AssertionError("On-device claim does not match CI binary LC_UUID")
    parity_result = device_audit.verify_run_log(parity, "IOS_DEVICE", arch)
    perf_result = (perf_audit.verify(performance, "IOS_DEVICE", arch)
                   if performance else None)
    result = {
        "schema": 1,
        "gate": "REPORTED_IDENTITY_UUID_AND_PARITY_TEXT_CONSISTENT",
        "arch_claimed": arch,
        "ci_macho_uuid": expected["macho_uuid"],
        "ci_binary_sha256_before_signing": expected.get("sha256"),
        "identity": declared,
        "parity": parity_result,
        "performance": perf_result,
        "performance_optional": True,
        "actual_device_execution_cryptographically_attested": False,
        "pac_security_assertion": "NONE_RUNTIME_BEHAVIOR_ONLY_IF_REAL_DEVICE",
        "note": ("Binary UUID is not a signature. Logs can be edited or replayed; "
                 "record actual signing, device model, and OS separately."),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="cmd", required=True)
    build = commands.add_parser("build", help="Extract LC_UUID from unsigned iOS binaries")
    build.add_argument("--arm64", type=Path, required=True)
    build.add_argument("--arm64e", type=Path, required=True)
    build.add_argument("--out", type=Path, required=True)
    verify = commands.add_parser("verify", help="Cross-check user-shared iPhone logs")
    verify.add_argument("--manifest", type=Path, required=True)
    verify.add_argument("--arch", choices=("arm64", "arm64e"), required=True)
    verify.add_argument("--identity", type=Path, required=True)
    verify.add_argument("--parity", type=Path, required=True)
    verify.add_argument("--performance", type=Path)
    verify.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.cmd == "build":
        result = manifest_for_binaries(args.arm64, args.arm64e, args.out)
        print("DD_BUILD_UUID_PASS: " + ", ".join(
            f"{arch}={result['slices'][arch]['macho_uuid']}"
            for arch in ("arm64", "arm64e")
        ) + "; device runtime NOT_TESTED")
    else:
        verify_bundle(manifest=args.manifest, arch=args.arch,
                      identity=args.identity, parity=args.parity,
                      performance=args.performance, output=args.out)
        print("DD_EVIDENCE_CONSISTENT: CI LC_UUID + declared ABI + parity "
              "log agree; no device attestation")
if __name__ == "__main__":
    main()
