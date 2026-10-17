#!/usr/bin/env python3
"""Portable Mach-O LC_UUID/build-vs-user-reported device identity regression."""
from __future__ import annotations

import importlib.util
import json
import random
import struct
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/protection_lab"
sys.path.insert(0, str(LAB))
spec = importlib.util.spec_from_file_location("device_evidence", LAB / "device_evidence.py")
assert spec.loader
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
import device_audit  # noqa: E402
import perf_audit  # noqa: E402

A = "2ffb2cdd-c447-487b-8441-89b47f7306f0"
E = "7ee12c8d-8c2e-4329-a854-2d4e1bf0a73a"


def binary(arch: str, uuid_value: str, *, commands: bytes | None = None,
           declared_ncmds: int = 1, filetype: int = 2) -> bytes:
    subtype = 0 if arch == "arm64" else 0x80000002
    data = commands if commands is not None else struct.pack(
        "<II16s", e.LC_UUID, 24, uuid.UUID(uuid_value).bytes
    )
    return (struct.pack("<IIIIIIII", device_audit.MAGIC,
                        device_audit.ARM64_CPUTYPE, subtype, filetype,
                        declared_ncmds, len(data), 0, 0) + data + b"test-payload")


def identity_lines(arch: str, unique: str, model: str = "iPhone14,2",
                   os: str = "16.6.1") -> list[str]:
    abi = "arm64:0x00000000" if arch == "arm64" else "arm64e:0x80000002"
    return [
        "DD_EVIDENCE_SCHEMA=1",
        "DD_EVIDENCE_CONTEXT=IOS_DEVICE",
        "DD_EVIDENCE_ABI=" + abi,
        "DD_EVIDENCE_MACHO_UUID=" + unique,
        "DD_EVIDENCE_DEVICE_MODEL=" + model,
        "DD_EVIDENCE_IOS_VERSION=" + os,
        "DD_EVIDENCE_NOTE=USER_SHARED_NOT_ATTESTED",
    ]


def performance_lines(arch: str) -> list[str]:
    header = perf_audit.expected_prefix("IOS_DEVICE", arch)
    for item in perf_audit.PAIRS:
        header += [f"DD_PERF_{item}_NATIVE_NS=100000",
                   f"DD_PERF_{item}_PROTECTED_NS=120000"]
    header.append("DD_PERF_NOTE=OBSERVATIONAL_NOT_SECURITY_PROOF")
    return header


def write_text(path: Path, lines: list[str]) -> None:
    path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))


with tempfile.TemporaryDirectory() as folder:
    root = Path(folder)
    arm64, arm64e = root / "app-arm64", root / "app-arm64e"
    arm64.write_bytes(binary("arm64", A))
    arm64e.write_bytes(binary("arm64e", E))
    assert e.macho_uuid(arm64) == A
    assert e.macho_uuid(arm64e) == E
    manifest = root / "manifest.json"
    result = e.manifest_for_binaries(arm64, arm64e, manifest)
    assert json.loads(manifest.read_text(encoding="utf-8")) == result
    assert result["uuid_security_attestation"] is False
    assert result["runtime_on_iphone"] == "NOT_TESTED_BY_CI"

    # Invalid or incompatible Mach-O LC_UUID / load commands must fail closed.
    correct = arm64e.read_bytes()
    malformed = [
        binary("arm64e", E, commands=b""),
        binary("arm64e", E, commands=struct.pack("<II", e.LC_UUID, 8)),
        binary("arm64e", E, commands=struct.pack("<II16s", e.LC_UUID, 28,
                                                  uuid.UUID(E).bytes)),
        binary("arm64e", E, commands=struct.pack("<II16s", e.LC_UUID, 0,
                                                  uuid.UUID(E).bytes)),
        binary("arm64e", E, commands=struct.pack("<II16s", e.LC_UUID, 24,
                                                  uuid.UUID(E).bytes),
               declared_ncmds=2),
        binary("arm64e", E, commands=struct.pack("<II16s", e.LC_UUID, 24,
                                                  uuid.UUID(E).bytes) * 2,
               declared_ncmds=2),
        binary("arm64e", E, commands=struct.pack("<II16s", 42, 24,
                                                  uuid.UUID(E).bytes)),
        binary("arm64e", E, filetype=6),
        b"not macho",
    ]
    for i, data in enumerate(malformed):
        arm64e.write_bytes(data)
        try:
            e.macho_uuid(arm64e)
        except (AssertionError, ValueError):
            pass
        else:
            raise AssertionError(f"Malformed LC_UUID/load command {i} accepted")
    arm64e.write_bytes(correct)

    report = root / "identity.log"
    parity = root / "functional.log"
    perf = root / "performance.log"
    write_text(report, identity_lines("arm64e", E))
    write_text(parity, device_audit.expected_lines("IOS_DEVICE", "arm64e"))
    write_text(perf, performance_lines("arm64e"))
    consolidated = e.verify_bundle(manifest=manifest, arch="arm64e",
                                   identity=report, parity=parity,
                                   performance=perf, output=root / "out.json")
    assert consolidated["gate"] == "REPORTED_IDENTITY_UUID_AND_PARITY_TEXT_CONSISTENT"
    assert consolidated["actual_device_execution_cryptographically_attested"] is False
    assert consolidated["identity"]["macho_uuid"] == E
    assert consolidated["performance"]["measurements"]["IBR"][
        "observed_ratio_not_an_acceptance_gate"
    ] == 1.2
    assert consolidated == json.loads((root / "out.json").read_text(encoding="utf-8"))
    minimal = e.verify_bundle(manifest=manifest, arch="arm64e",
                              identity=report, parity=parity,
                              output=root / "minimal.json")
    assert minimal["performance"] is None and minimal["performance_optional"]

    def fail():
        try:
            e.verify_bundle(manifest=manifest, arch="arm64e",
                            identity=report, parity=parity,
                            performance=perf, output=root / "reject.json")
        except (AssertionError, ValueError, KeyError):
            return
        raise AssertionError("Spoofed/partial report was accepted")

    for index in range(7):
        lines = identity_lines("arm64e", E)
        del lines[index]
        write_text(report, lines)
        fail()
    for altered in [
        identity_lines("arm64e", A),
        identity_lines("arm64", E),
        identity_lines("arm64e", E.upper()),
        identity_lines("arm64e", E, "iPhone;UDID=abc"),
        identity_lines("arm64e", E, "iPhone14,2", "NaN"),
        identity_lines("arm64e", E, "iPhone14,2", "1.2"),
        identity_lines("arm64e", E) + ["EXTRA=1"],
        identity_lines("arm64e", E)[:-1] + ["DD_EVIDENCE_NOTE=SECURE_ATTESTATION"],
    ]:
        write_text(report, altered)
        fail()
    write_text(report, identity_lines("arm64e", E))

    write_text(parity, ["DD_RUNTIME_COMPLETE=PASS"])
    fail()
    write_text(parity, device_audit.expected_lines("IOS_DEVICE", "arm64e"))
    write_text(perf, performance_lines("arm64"))
    fail()
    write_text(perf, performance_lines("arm64e"))
    corrupted = json.loads(manifest.read_text(encoding="utf-8"))
    corrupted["slices"]["arm64e"]["macho_uuid"] = A
    manifest.write_text(json.dumps(corrupted), encoding="utf-8")
    fail()

    # Realistic random deterministic UUID fixtures exercise parsing consistency.
    rng = random.Random(94631)
    for _ in range(100):
        value = uuid.UUID(int=rng.getrandbits(128), version=4)
        arm64e.write_bytes(binary("arm64e", str(value)))
        assert e.macho_uuid(arm64e) == str(value)

app = (LAB / "ios_app_main.m").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/protection-ios-app.yml").read_text(
    encoding="utf-8"
)
for x in (
    "DDLoadedMachOUUID", "_dyld_get_image_header(0)",
    "struct uuid_command", "LC_UUID", "command.cmdsize",
    "DD_EVIDENCE_MACHO_UUID=", "DD_EVIDENCE_CONTEXT=IOS_DEVICE",
    "DD_EVIDENCE_NOTE=USER_SHARED_NOT_ATTESTED",
    "DD_EVIDENCE_DEVICE_MODEL=", "DD_EVIDENCE_IOS_VERSION=",
    "DDRunEvidence(DDRuntimeABI())", "self.evidenceReport = identity",
    "Share binary identity / OS model", "presentShareWithText:self.evidenceReport",
):
    assert x in app, x
assert "serialNumber" not in app and "identifierForVendor" not in app
assert "DD_RUNTIME_COMPLETE=PASS" in app and "DD_PERF_SCHEMA=1" not in app
for x in (
    "python3 scripts/test_device_evidence.py",
    '"$lab/device_evidence.py" build',
    "build-identity.json", "--arm64e", "UUID is not device cryptographic attestation",
):
    assert x in workflow, x
for denied in ("codesign -s", "ldid -S", "devicectl device install",
               "make clean package", "TARGET_CC="):
    assert denied.lower() not in workflow.lower()

print("Device evidence: LC_UUID Mach-O parser, 100 randomized UUIDs, "
      "7-line build/device/ABI/parity and optional timing negative gates PASS")
