#!/usr/bin/env python3
"""Fail-closed parser for an opt-in five-round iOS Protection Lab soak report.

A valid report proves text-format consistency only. Device authenticity,
jailbreak integrity and arm64e PAC enforcement remain outside this tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from device_audit import STAGES, VECTORS

ROUNDS = 5
TOTAL_VECTOR_CHECKS = ROUNDS * VECTORS * len(STAGES)
NOTE = "MANUAL_STRESS_NOT_SECURITY_ATTESTATION"


def expected_lines(arch: str) -> list[str]:
    if arch not in ("arm64", "arm64e"):
        raise ValueError("Unsupported ABI for a standalone physical-device soak")
    subtype = "0x00000000" if arch == "arm64" else "0x80000002"
    return [
        "DD_SOAK_SCHEMA=1",
        "DD_SOAK_CONTEXT=IOS_DEVICE",
        f"DD_SOAK_ABI={arch}:{subtype}",
        f"DD_SOAK_ROUNDS={ROUNDS}",
        f"DD_SOAK_VECTORS_PER_SUITE_PER_ROUND={VECTORS}",
        *(f"DD_SOAK_{stage}_ROUNDS_PASS={ROUNDS}" for stage in STAGES),
        f"DD_SOAK_TOTAL_VECTOR_CHECKS={TOTAL_VECTOR_CHECKS}",
        "DD_SOAK_NOTE=" + NOTE,
        "DD_SOAK_COMPLETE=PASS",
    ]


def validate(log: Path, arch: str) -> dict:
    raw = log.read_bytes()
    if len(raw) > 2048:
        raise AssertionError("Unexpectedly large soak report")
    lines = raw.decode("utf-8", errors="strict").splitlines()
    if lines != expected_lines(arch):
        raise AssertionError(
            "Soak report incomplete, wrong architecture, duplicated rounds or invalid result"
        )
    return {
        "schema": 1,
        "claimed_context": "IOS_DEVICE",
        "claimed_architecture": arch,
        "rounds": ROUNDS,
        "vectors_per_suite_per_round": VECTORS,
        "suites": list(STAGES),
        "reported_total_vector_checks": TOTAL_VECTOR_CHECKS,
        "result": "REPORTED_FIVE_ROUND_PASS",
        "log_sha256": hashlib.sha256(raw).hexdigest(),
        "device_execution_attested": False,
        "source": "USER_SHARED_TEXT_NOT_CRYPTOGRAPHICALLY_AUTHENTICATED",
        "security_conclusion": "NONE",
        "production_crane_verified": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("verify", choices=("verify",))
    p.add_argument("--log", type=Path, required=True)
    p.add_argument("--arch", choices=("arm64", "arm64e"), required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    result = validate(args.log, args.arch)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print("DD_SOAK_LOG_ACCEPTED: 5 rounds x 4 suites x 8192 vectors; "
          "user-shared format only, not attestation")


if __name__ == "__main__":
    main()
