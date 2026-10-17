#!/usr/bin/env python3
"""Privacy-aware acceptance receipt regression, no real UDID or iPhone log needed."""
from __future__ import annotations

import json
import struct
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/protection_lab"
sys.path.insert(0, str(LAB))

import device_acceptance as acc
import device_audit as audit
import device_evidence as evidence
import perf_audit as perf

UUID_ARM64 = "11111111-1111-4111-8111-111111111111"
UUID_ARM64E = "22222222-2222-4222-8222-222222222222"


def binary(subtype: int, value: str) -> bytes:
    lc = struct.pack("<II16s", evidence.LC_UUID, 24, uuid.UUID(value).bytes)
    return struct.pack(
        "<IIIIIIII", audit.MAGIC, audit.ARM64_CPUTYPE,
        subtype, audit.MH_EXECUTE, 1, len(lc), 0, 0
    ) + lc


def identity_lines(value: str) -> list[str]:
    return [
        "DD_EVIDENCE_SCHEMA=1",
        "DD_EVIDENCE_CONTEXT=IOS_DEVICE",
        "DD_EVIDENCE_ABI=arm64:0x00000000",
        "DD_EVIDENCE_MACHO_UUID=" + value,
        "DD_EVIDENCE_DEVICE_MODEL=iPhone10,4",
        "DD_EVIDENCE_IOS_VERSION=16.6.1",
        "DD_EVIDENCE_NOTE=USER_SHARED_NOT_ATTESTED",
    ]


def perf_lines() -> list[str]:
    lines = perf.expected_prefix("IOS_DEVICE", "arm64")
    for pair in perf.PAIRS:
        lines.extend([f"DD_PERF_{pair}_NATIVE_NS=23000",
                      f"DD_PERF_{pair}_PROTECTED_NS=31000"])
    return lines + ["DD_PERF_NOTE=OBSERVATIONAL_NOT_SECURITY_PROOF"]


def put(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    receipt = root / "device-acceptance.json"
    # Current user verbal confirmation, no synthesized PASS device logs.
    result = acc.generate(output=receipt, user_confirmed=True)
    assert result == json.loads(receipt.read_text(encoding="utf-8"))
    assert result["suite_status"] == "USER_REPORTED_PASS"
    assert result["device_recognition_status"] == "USER_REPORTED_CORRECT"
    assert result["evidence_validation"] == "NOT_PERFORMED_NO_LOGS"
    assert result["unique_device_identifier_recorded"] is False
    assert result["raw_device_identifier_required"] is False
    assert result["cryptographic_device_attestation"] is False
    assert result["arm64e"]["a12_plus_runtime"] == "DEFERRED_NO_DEVICE"
    assert not any(x in receipt.read_text(encoding="utf-8").lower()
                   for x in ("udid=", "serial=", "deviceid=", "device_id="))

    def should_fail(*, parity=None, identity=None, manifest=None, performance=None,
                    reported=True):
        try:
            acc.generate(output=root / "invalid.json", user_confirmed=reported,
                         parity=parity, identity=identity, manifest=manifest,
                         performance=performance)
        except (AssertionError, ValueError, KeyError):
            return
        raise AssertionError("Invalid or partial device evidence accepted")

    should_fail(reported=False)
    p = root / "parity.txt"
    i = root / "identity.txt"
    perf_path = root / "perf.txt"
    m = root / "manifest.json"
    should_fail(parity=p)
    should_fail(performance=perf_path)

    arm64 = root / "arm64"
    arm64e = root / "arm64e"
    arm64.write_bytes(binary(0, UUID_ARM64))
    arm64e.write_bytes(binary(0x80000002, UUID_ARM64E))
    evidence.manifest_for_binaries(arm64, arm64e, m)
    put(p, audit.expected_lines("IOS_DEVICE", "arm64"))
    put(i, identity_lines(UUID_ARM64))
    put(perf_path, perf_lines())
    matched = acc.generate(output=receipt, user_confirmed=True,
                           parity=p, identity=i, manifest=m,
                           performance=perf_path)
    assert matched["evidence_validation"] == "SHARED_LOG_TEXT_AND_CI_UUID_CONSISTENT"
    assert matched["ci_macho_uuid"] == UUID_ARM64
    assert len(matched["parity_log_sha256"]) == 64
    assert len(matched["performance_log_sha256"]) == 64
    assert matched["unique_device_identifier_recorded"] is False
    assert matched["cryptographic_device_attestation"] is False
    assert "UDID" not in json.dumps(matched).upper()

    no_perf = acc.generate(output=receipt, user_confirmed=True,
                           parity=p, identity=i, manifest=m)
    assert no_perf["evidence_validation"] == "SHARED_LOG_TEXT_AND_CI_UUID_CONSISTENT"
    assert "performance_log_sha256" not in no_perf

    put(p, audit.expected_lines("MACOS_HOST"))
    should_fail(parity=p, identity=i, manifest=m)
    put(p, audit.expected_lines("IOS_DEVICE", "arm64"))
    put(i, identity_lines(UUID_ARM64E))
    should_fail(parity=p, identity=i, manifest=m)
    put(i, identity_lines(UUID_ARM64))
    put(perf_path, perf.expected_prefix("MACOS_HOST", None))
    should_fail(parity=p, identity=i, manifest=m, performance=perf_path)

app = (LAB / "ios_app_main.m").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/protection-ios-app.yml").read_text(encoding="utf-8")
assert "DDValidationPassed(result)" in app
assert "UDID" not in app or "no serial, UDID" in app
assert "python3 scripts/test_device_acceptance.py" in workflow
assert "for arch in arm64 arm64e; do" in workflow
assert "build_gate.py" in workflow
assert "package_trollstore_ipa.py" in workflow
assert "devicectl device install" not in workflow
print("Device acceptance: reported PASS vs shared-log validation, negative "
      "host/ABI/UUID/perf cases, no unique device ID, arm64e deferred PASS")
