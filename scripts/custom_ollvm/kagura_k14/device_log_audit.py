#!/usr/bin/env python3
"""K14 exact eight-line user-shared iPhone text check; NOT device attestation."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

UUID = r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}"
ORACLE = "25a3318e3d7d6525"


def validate(log: Path, ipa_report: Path | None = None,
             evidence: Path | None = None) -> dict:
    if (ipa_report is None) != (evidence is None):
        raise AssertionError("K14 requires both IPA CI manifests")
    raw = log.read_bytes()
    if len(raw) > 2048 or len(raw) < 100 or not raw.endswith(b"\n"):
        raise AssertionError("K14 8-line text log truncated/too large")
    text = raw.decode("ascii", errors="strict").replace("\r\n", "\n")
    if "\r" in text:
        raise AssertionError("K14 malformed carriage return")
    lines = text[:-1].split("\n")
    if len(lines) != 8:
        raise AssertionError("K14 needs exact full eight lines")
    match = re.fullmatch("DD_K14_IOS_APP_UUID=(" + UUID + ")", lines[3])
    if not match:
        raise AssertionError("K14 missing genuine-format UUID")
    claimed = match.group(1)
    expected = [
        "DD_K14_IOS_SCHEMA=1",
        "DD_K14_IOS_CONTEXT=IOS_DEVICE",
        "DD_K14_IOS_ARCH=arm64:0x00000000",
        "DD_K14_IOS_APP_UUID=" + claimed,
        "DD_K14_IOS_PASS=CSE_BREAK",
        "DD_K14_IOS_VECTORS=4096",
        "DD_K14_IOS_CHECKSUM=" + ORACLE,
        "DD_K14_IOS_COMPLETE=PASS",
    ]
    if lines != expected:
        raise AssertionError("K14 context/oracle/pass/vector mismatch")
    result = {
        "schema": 1,
        "user_shared_text_consistent": True,
        "claimed_device_context": "IOS_DEVICE",
        "claimed_macho_uuid": claimed,
        "log_sha256": hashlib.sha256(raw).hexdigest(),
        "ci_build_correlation": None,
        "device_execution_cryptographically_attested": False,
        "iphone_execution_independently_observed": False,
        "arm64e_pac_runtime": "NOT_TESTED",
        "crane_production_modified": False,
    }
    if ipa_report is not None:
        import package_ipa as pkg
        p = json.loads(ipa_report.read_text(encoding="utf-8"))
        e = json.loads(evidence.read_text(encoding="utf-8"))
        if (p.get("schema") != 1 or p.get("scope") != pkg.SCOPE or
                p.get("bundle_identifier") != pkg.BUNDLE or
                p.get("app_macho_uuid") != claimed or
                e.get("schema") != 1 or
                e.get("scope") !=
                "K14_K13_VERIFIED_SINGLE_CSEBREAK_IOS_ARM64_IPA_LAB_ONLY" or
                e.get("app_macho_uuid") != claimed or
                e.get("ipa_sha256") != p.get("ipa_sha256") or
                e.get("app_binary_sha256") != p.get("binary_sha256") or
                e.get("k13_cse_break_ios_object_embedded") is not True or
                e.get("ios_device_execution") != "NOT_TESTED_BY_CI" or
                e.get("security_attestation") is not False):
            raise AssertionError("K14 shared log cannot correlate to CI IPA")
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
    result = validate(x.log, x.ipa_report, x.evidence)
    x.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                     encoding="utf-8")
    print("K14_USER_SHARED_LOG_SCHEMA_PASS: not device attestation")


if __name__ == "__main__":
    main()
