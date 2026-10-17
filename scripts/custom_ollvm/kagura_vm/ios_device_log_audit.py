#!/usr/bin/env python3
"""Audit user-shared KaguraVM K7 text; no cryptographic device attestation."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
from pathlib import Path

from oracle import checksums

UUID_RE = r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}"


def validate(log: Path, *, ipa_report: Path | None = None,
             evidence: Path | None = None) -> dict:
    if (ipa_report is None) != (evidence is None):
        raise AssertionError("Both CI reports required for build matching")
    raw = log.read_bytes()
    if not 1 <= len(raw) <= 4096 or not raw.endswith(b"\n"):
        raise AssertionError("Truncated or oversized K7 log")
    original_text = raw.decode("ascii", errors="strict")
    text = original_text.replace("\r\n", "\n")
    if "\r" in text:
        raise AssertionError("Invalid lone carriage return in K7 log")
    sections = text[:-1].split("\n\n")
    if len(sections) not in (1, 2):
        raise AssertionError("Unexpected K7 log sections")
    parity, guard = checksums()
    lines = sections[0].split("\n")
    if len(lines) != 9:
        raise AssertionError("K7 parity lines count mismatch")
    match = re.fullmatch("DD_VM_IOS_APP_UUID=(" + UUID_RE + ")", lines[3])
    if match is None:
        raise AssertionError("Missing/malformed K7 executable UUID")
    u = match.group(1)
    expected = [
        "DD_VM_IOS_SCHEMA=1", "DD_VM_IOS_CONTEXT=IOS_DEVICE",
        "DD_VM_IOS_ARCH=arm64:0x00000000", "DD_VM_IOS_APP_UUID=" + u,
        "DD_VM_IOS_PIPELINE=KAGURA_VM_SELECTIVE",
        "DD_VM_IOS_VECTORS_PASS=4096",
        "DD_VM_IOS_PARITY_CHECKSUM=" + parity,
        "DD_VM_IOS_GUARD_CHECKSUM=" + guard,
        "DD_VM_IOS_COMPLETE=PASS",
    ]
    if lines != expected:
        raise AssertionError("K7 parity context/checksums do not match reference")
    result = {
        "schema": 1, "user_shared_text_consistent": True,
        "claimed_executable_uuid": u,
        "expected_parity_checksum": parity,
        "expected_guard_checksum": guard,
        "optional_benchmark": None,
        "ci_build_correlation": None,
        "log_sha256": hashlib.sha256(raw).hexdigest(),
        "cryptographic_device_attestation": False,
        "actual_device_execution_verified_by_ci": False,
        "arm64e_runtime": "NOT_TESTED",
        "crane_production_modified": False,
    }
    if len(sections) == 2:
        perf = sections[1].split("\n")
        if len(perf) != 14:
            raise AssertionError("Wrong K7 benchmark line count")
        expected_head = [
            "DD_VM_IOS_PERF_SCHEMA=1",
            "DD_VM_IOS_PERF_CONTEXT=IOS_DEVICE",
            "DD_VM_IOS_PERF_ARCH=arm64:0x00000000",
            "DD_VM_IOS_PERF_APP_UUID=" + u,
            "DD_VM_IOS_PERF_PAIRS=3",
            "DD_VM_IOS_PERF_CALLS_PER_SAMPLE=1024",
        ]
        if perf[:6] != expected_head or perf[12:] != [
            "DD_VM_IOS_PERF_NOTE=OBSERVATIONAL_NOT_SECURITY_ATTESTATION",
            "DD_VM_IOS_PERF_COMPLETE=PASS",
        ]:
            raise AssertionError("Malformed K7 benchmark context/note")
        pairs = []
        for i in range(3):
            pair = []
            for kind, idx in (("PLAIN", 6 + 2 * i),
                              ("PROTECTED", 7 + 2 * i)):
                m = re.fullmatch(
                    rf"DD_VM_IOS_PERF_{kind}_NS_{i}=([0-9]+)", perf[idx])
                if m is None or not 1 <= int(m.group(1)) <= 1_000_000_000:
                    raise AssertionError("Invalid K7 iPhone performance sample")
                pair.append(int(m.group(1)))
            pairs.append(pair)
        paired_ratios = [protected / plain for plain, protected in pairs]
        result["optional_benchmark"] = {
            "pairs_ns_per_call": pairs,
            "paired_overhead_ratios": [round(x, 6) for x in paired_ratios],
            "median_paired_overhead_ratio": round(
                statistics.median(paired_ratios), 6),
            "plain_median_ns_per_call": statistics.median(x[0] for x in pairs),
            "protected_median_ns_per_call": statistics.median(x[1] for x in pairs),
            "observational_only": True,
            "not_security_attestation": True,
            "not_stable_performance_characterization": True,
        }

    if ipa_report is not None:
        from package_ipa import BUNDLE
        ipar = json.loads(ipa_report.read_text(encoding="utf-8"))
        ev = json.loads(evidence.read_text(encoding="utf-8"))
        if not (ipar.get("bundle_identifier") == BUNDLE and
                ipar.get("scope") == "STANDALONE_K7_VM_IPA" and
                ipar.get("architecture") == "arm64" and
                ipar.get("macho_uuid") == u and
                ev.get("scope") == "STANDALONE_K7_VM_TROLLSTORE_IPA" and
                ev.get("app_macho_uuid") == u and
                ev.get("app_binary_sha256") == ipar.get("binary_sha256") and
                ev.get("ipa_sha256") == ipar.get("ipa_sha256") and
                ev.get("virtualization_ir_confirmed") is True and
                ev.get("guard_ir_equal_to_baseline") is True and
                ev.get("actual_ios_device_execution") == "NOT_TESTED_BY_CI" and
                ev.get("security_attestation") is False):
            raise AssertionError("K7 log UUID mismatches CI IPA/VM evidence")
        result["ci_build_correlation"] = {
            "claimed_uuid_matches_ipa_evidence": True,
            "ipa_sha256": ipar["ipa_sha256"],
            "binary_sha256": ipar["binary_sha256"],
            "not_device_attestation": True,
        }
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--log", type=Path, required=True)
    p.add_argument("--ipa-report", type=Path)
    p.add_argument("--evidence", type=Path)
    p.add_argument("--out", type=Path, required=True)
    x = p.parse_args()
    result = validate(x.log, ipa_report=x.ipa_report, evidence=x.evidence)
    x.out.parent.mkdir(parents=True, exist_ok=True)
    x.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                     encoding="utf-8")
    print("K7_IPHONE_LOG_TEXT_CONSISTENT: build correlation is NOT device attestation")


if __name__ == "__main__":
    main()
