#!/usr/bin/env python3
"""K11 exact nine-line user-shared log vs IPA UUID; NOT attestation."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

UUID = r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}"
C = "25a3318e3d7d6525"
MVO = "64e61045bbc4a250"

def validate(log: Path, ipa_report: Path | None = None,
             evidence: Path | None = None) -> dict:
    if (ipa_report is None) != (evidence is None):
        raise AssertionError("K11 requires both CI manifests together")
    raw = log.read_bytes()
    if not 1 <= len(raw) <= 2048 or not raw.endswith(b"\n"):
        raise AssertionError("K11 text log truncated/oversized")
    text = raw.decode("ascii", errors="strict").replace("\r\n", "\n")
    if "\r" in text:
        raise AssertionError("K11 lone carriage return")
    lines = text[:-1].split("\n")
    if len(lines) != 9:
        raise AssertionError("K11 complete exact nine lines are required")
    match = re.fullmatch("DD_K11_IOS_APP_UUID=(" + UUID + ")", lines[3])
    if match is None:
        raise AssertionError("K11 invalid binary UUID")
    u = match.group(1)
    expected = [
        "DD_K11_IOS_SCHEMA=1",
        "DD_K11_IOS_CONTEXT=IOS_DEVICE",
        "DD_K11_IOS_ARCH=arm64:0x00000000",
        "DD_K11_IOS_APP_UUID=" + u,
        "DD_K11_IOS_PIPELINE=MVO_GENC_FSPLIT_IBR_CI",
        "DD_K11_IOS_VECTORS_PER_FUNCTION=4096",
        "DD_K11_IOS_C_CHECKSUM=" + C,
        "DD_K11_IOS_MVO_CHECKSUM=" + MVO,
        "DD_K11_IOS_COMPLETE=PASS",
    ]
    if lines != expected:
        raise AssertionError("K11 device context/checksums/5-pass order mismatch")
    result = {
        "schema": 1,
        "user_shared_text_consistent": True,
        "claimed_device_context": "IOS_DEVICE",
        "macho_uuid_claimed": u,
        "log_sha256": hashlib.sha256(raw).hexdigest(),
        "ci_build_correlation": None,
        "device_execution_cryptographically_attested": False,
        "arm64e_pac_runtime": "NOT_TESTED",
        "crane_production_modified": False,
    }
    if ipa_report is not None:
        import package_ipa as package
        p = json.loads(ipa_report.read_text(encoding="utf-8"))
        e = json.loads(evidence.read_text(encoding="utf-8"))
        if (p.get("schema") != 1 or p.get("scope") !=
                "STANDALONE_K11_FIVE_PASS_LAB_IPA" or
                p.get("bundle_identifier") != package.BUNDLE or
                p.get("macho_uuid") != u or
                e.get("scope") != "K11_FIVE_PASS_K10_STRICT_METADATA_TROLLSTORE_LAB_ONLY" or
                e.get("app_macho_uuid") != u or
                e.get("ipa_sha256") != p.get("ipa_sha256") or
                e.get("app_binary_sha256") != p.get("binary_sha256") or
                e.get("five_pass_ios_object_verified") is not True or
                e.get("resolver_symbol_present") is not True or
                e.get("ios_device_execution") != "NOT_TESTED_BY_CI" or
                e.get("security_attestation") is not False):
            raise AssertionError("K11 shared log UUID not correlated with CI artifact")
        result["ci_build_correlation"] = {
            "claimed_uuid_matches_ipa": True,
            "ipa_sha256": p["ipa_sha256"],
            "binary_sha256": p["binary_sha256"],
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
    report = validate(x.log, x.ipa_report, x.evidence)
    x.out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n",
                     encoding="utf-8")
    print("K11_USER_SHARED_LOG_CONSISTENT: UUID/text correlation NOT device attestation")

if __name__ == "__main__":
    main()
