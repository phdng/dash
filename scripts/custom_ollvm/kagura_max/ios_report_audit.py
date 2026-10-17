#!/usr/bin/env python3
"""Validate user-shared KaguraLab iPhone log text without claiming attestation.

Accepts only the exact 7-line arm64 8192-vector PASS protocol, optionally
followed by a blank line and the exact 10-line observational benchmark log.
This confirms textual consistency, NOT device execution provenance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def validate(log: Path) -> dict:
    raw = log.read_bytes()
    if not raw or len(raw) > 4096:
        raise AssertionError("Kagura device report missing or oversized")
    text = raw.decode("utf-8", errors="strict").replace("\r\n", "\n")
    if not text.endswith("\n"):
        raise AssertionError("Kagura report truncated (missing trailing newline)")
    sections = text[:-1].split("\n\n")
    if len(sections) not in (1, 2):
        raise AssertionError("Wrong number of Kagura iPhone report sections")
    parity = sections[0].splitlines()
    expected_start = [
        "DD_KAGURA_SCHEMA=1",
        "DD_KAGURA_CONTEXT=IOS_DEVICE",
        "DD_KAGURA_ARCH=arm64:0x00000000",
        "DD_KAGURA_PIPELINE=STR_FLA_BCF_SUB_CO_BBR_BBS",
        "DD_KAGURA_VECTORS_PASS=8192",
    ]
    if len(parity) != 7 or parity[:5] != expected_start or (
        re.fullmatch(r"DD_KAGURA_CHECKSUM=[0-9a-f]{16}", parity[5]) is None
    ) or parity[6] != "DD_KAGURA_COMPLETE=PASS":
        raise AssertionError("Invalid or non-PASS Kagura 8192 parity report")
    result = {
        "schema": 1,
        "claimed_architecture": "arm64",
        "claimed_context": "IOS_DEVICE",
        "pipeline": expected_start[3].split("=", 1)[1],
        "claimed_parity_vectors": 8192,
        "parity_checksum": parity[5].split("=", 1)[1],
        "optional_benchmark": None,
        "user_log_sha256": hashlib.sha256(raw).hexdigest(),
        "device_execution_cryptographically_attested": False,
        "log_provenance": "USER_SHARED_TEXT_NOT_AUTHENTICATED",
        "crane_production_verified": False,
        "arm64e_runtime": "NOT_TESTED",
    }
    if len(sections) == 2:
        lines = sections[1].splitlines()
        expected = [
            "DD_KAGURA_PERF_SCHEMA=1",
            "DD_KAGURA_PERF_CONTEXT=IOS_DEVICE",
            "DD_KAGURA_PERF_ARCH=arm64:0x00000000",
            "DD_KAGURA_PERF_PAIRS=5",
            "DD_KAGURA_PERF_CALLS_PER_SAMPLE=4096",
        ]
        if len(lines) != 10 or lines[:5] != expected or (
            lines[8] != "DD_KAGURA_PERF_NOTE=OBSERVATIONAL_NOT_SECURITY_ATTESTATION"
        ) or lines[9] != "DD_KAGURA_PERF_COMPLETE=PASS" or (
            re.fullmatch(r"DD_KAGURA_PERF_CHECKSUM=[0-9a-f]{16}", lines[7]) is None
        ):
            raise AssertionError("Malformed or non-PASS Kagura iOS timing report")
        values = []
        for pos, name in ((5, "PLAIN"), (6, "PROTECTED")):
            match = re.fullmatch(
                rf"DD_KAGURA_PERF_{name}_MEDIAN_NS=([0-9]+)", lines[pos]
            )
            if not match or int(match.group(1)) <= 0 or int(match.group(1)) > 1_000_000_000:
                raise AssertionError("Wrong or implausible iPhone timing data")
            values.append(int(match.group(1)))
        result["optional_benchmark"] = {
            "context": "IOS_DEVICE_CLAIMED",
            "plain_median_ns_per_call": values[0],
            "protected_median_ns_per_call": values[1],
            "ratio_vs_plain": round(values[1] / values[0], 3),
            "observational_only": True,
        }
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--log", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    verified = validate(a.log)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(verified, indent=2, sort_keys=True) + "\n",
                     encoding="utf-8")
    print("KAGURA_IOS_USER_LOG_TEXT_CONSISTENT: 8192 parity, arm64; "
          "user-supplied log, not an attested device result")


if __name__ == "__main__":
    main()
