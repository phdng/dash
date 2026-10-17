#!/usr/bin/env python3
"""Truthful manual acceptance receipt for the standalone arm64 TrollStore Lab.

The user may confirm runtime PASS and correct device recognition without
uploading an individual device identifier. Raw parity/identity logs, when
later supplied, enable *content consistency* checks; never attestation.
arm64e remains build-only until real A12+ hardware exists.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

import device_audit
import device_evidence


def generate(*, output: Path, user_confirmed: bool,
             parity: Path | None = None, identity: Path | None = None,
             manifest: Path | None = None, performance: Path | None = None) -> dict:
    if not user_confirmed:
        raise AssertionError("Receipt requires explicit user-reported device PASS")
    provided = (parity is not None, identity is not None, manifest is not None)
    if any(provided) and not all(provided):
        raise ValueError("Parity, identity and CI manifest must be supplied together")
    if performance is not None and not all(provided):
        raise ValueError("Benchmark alone cannot elevate functional test evidence")

    result = {
        "schema": 1,
        "scope": "STANDALONE_PROTECTION_LAB_ONLY",
        "architecture": "arm64",
        "delivery": "TROLLSTORE_USER_REPORTED_INSTALLED_AND_LAUNCHED",
        "suite_names": list(device_audit.STAGES),
        "expected_vectors_per_suite": device_audit.VECTORS,
        "suite_status": "USER_REPORTED_PASS",
        "device_recognition_status": "USER_REPORTED_CORRECT",
        "unique_device_identifier_recorded": False,
        "raw_device_identifier_required": False,
        "evidence_validation": "NOT_PERFORMED_NO_LOGS",
        "cryptographic_device_attestation": False,
        "product_crane_protection_verified": False,
        "arm64e": {
            "acceptance_target": "BUILD_LINK_MACHO_ABI_AND_UUID_ONLY",
            "a12_plus_runtime": "DEFERRED_NO_DEVICE",
            "pac_runtime": "NOT_TESTED",
        },
    }

    if all(provided):
        # Existing validators reject host-only logs, wrong architecture,
        # missing/duplicated stages, mismatched LC_UUID and malformed timing.
        # No synthetic passing log is ever constructed by this script.
        with tempfile.TemporaryDirectory(prefix="duodash-validation-") as folder:
            checked = device_evidence.verify_bundle(
                manifest=manifest, arch="arm64", identity=identity,
                parity=parity, performance=performance,
                output=Path(folder) / "validation.json",
            )
        result["evidence_validation"] = "SHARED_LOG_TEXT_AND_CI_UUID_CONSISTENT"
        result["parity_log_sha256"] = checked["parity"]["log_sha256"]
        result["identity_log_sha256"] = checked["identity"]["identity_log_sha256"]
        result["ci_macho_uuid"] = checked["ci_macho_uuid"]
        if checked["performance"] is not None:
            result["performance_log_sha256"] = checked["performance"]["log_sha256"]
        # Use only hashes and a non-personal Mach-O identifier in receipt.

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    status = result["evidence_validation"]
    print("DD_ARM64_DEVICE_ACCEPTANCE: USER_REPORTED_PASS; " + status +
          "; arm64e A12+ runtime DEFERRED_NO_DEVICE")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--user-confirmed-pass", action="store_true", required=True)
    p.add_argument("--parity", type=Path)
    p.add_argument("--identity", type=Path)
    p.add_argument("--manifest", type=Path)
    p.add_argument("--performance", type=Path)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    generate(output=args.out, user_confirmed=args.user_confirmed_pass,
             parity=args.parity, identity=args.identity,
             manifest=args.manifest, performance=args.performance)


if __name__ == "__main__":
    main()
