#!/usr/bin/env python3
"""K18 verify USER-SHARED ten-line iPhone TEXT against actual K18 IPA report.

Neither user-shared text nor bundled public key cryptographically attests to
the origin of device execution. Require a separately trusted signer fingerprint.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
KEYS = ("SCHEMA", "CONTEXT", "SCOPE", "ARCH", "REFERENCE_UUID",
        "TRUST_SPKI_SHA256", "SIGNATURE", "REFERENCE_MACHO_TEXT",
        "SELF_INTEGRITY", "COMPLETE")
SCOPE = "K18_USER_SHARED_TEXT_CORRELATED_TO_OFFLINE_REFERENCE_NOT_ATTESTED"
HEX = re.compile(r"^[a-f0-9]{64}$")
UUID = re.compile(r"^[a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}$")


def validate(log: Path, report: Path, approved_fingerprint: str) -> dict:
    if not HEX.fullmatch(approved_fingerprint):
        raise AssertionError("K18 requires independently approved 64-hex public SPKI digest")
    from package import KNOWN_EXPOSED_TEST_KEY
    if approved_fingerprint == KNOWN_EXPOSED_TEST_KEY:
        raise AssertionError("K18 old disclosed TEST signer cannot qualify")
    if not log.is_file() or log.is_symlink() or log.stat().st_size > 4096:
        raise AssertionError("K18 missing or oversize text log")
    raw = log.read_bytes()
    if not raw or not raw.endswith(b"\n") or b"\r" in raw:
        raise AssertionError("K18 expected LF-terminated ten-line ASCII text")
    try:
        lines = raw.decode("ascii").splitlines()
    except UnicodeError as exc:
        raise AssertionError("K18 non-ASCII log") from exc
    if len(lines) != len(KEYS):
        raise AssertionError("K18 device log must have exactly ten lines")
    found = {}
    for key, line in zip(KEYS, lines):
        prefix = "DD_K18_" + key + "="
        if not line.startswith(prefix) or line.count("=") != 1:
            raise AssertionError("K18 missing/duplicate/altered field: " + key)
        found[key] = line[len(prefix):]
    if not report.is_file() or report.is_symlink():
        raise AssertionError("K18 build report required")
    data = json.loads(report.read_text(encoding="utf-8"))
    if (data.get("schema") != 1 or
            data.get("scope") !=
            "K18_READ_ONLY_ROTATED_ED25519_SIGNED_K14_SPECIMEN_IOS_LAB_NOT_SELF_INTEGRITY" or
            data.get("public_spki_sha256") != approved_fingerprint or
            not UUID.fullmatch(str(data.get("reference_uuid", ""))) or
            data.get("runtime_self_integrity") != "NOT_IMPLEMENTED" or
            data.get("embedded_public_key_is_immutable_trust_anchor") is not False or
            data.get("device_execution") != "NOT_TESTED_BY_CI" or
            data.get("iphone_attestation") is not False or
            data.get("crane_production_modified") is not False):
        raise AssertionError("K18 CI report not an isolated approved offline reference")
    expect = {
        "SCHEMA": "1",
        "CONTEXT": "IOS_DEVICE_USER_INITIATED",
        "SCOPE": "BUNDLED_REFERENCE_ONLY",
        "ARCH": "arm64:0x00000000",
        "REFERENCE_UUID": data["reference_uuid"],
        "TRUST_SPKI_SHA256": approved_fingerprint,
        "SIGNATURE": "PASS",
        "REFERENCE_MACHO_TEXT": "PASS",
        "SELF_INTEGRITY": "NOT_IMPLEMENTED",
        "COMPLETE": "PASS",
    }
    if found != expect:
        raise AssertionError("K18 shared text differs from its exact CI artifact")
    return {
        "schema": 1, "scope": SCOPE,
        "reference_uuid": data["reference_uuid"],
        "trusted_fingerprint_correlated_to_independent_value": approved_fingerprint,
        "raw_log_sha256": hashlib.sha256(raw).hexdigest(),
        "strict_ten_lines_matched": True,
        "on_device_execution_cryptographically_attested": False,
        "on_device_self_integrity_verified": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--device-log", type=Path, required=True)
    p.add_argument("--k18-report", type=Path, required=True)
    p.add_argument("--approved-spki-sha256", required=True)
    a = p.parse_args()
    print(json.dumps(validate(a.device_log, a.k18_report,
                              a.approved_spki_sha256), indent=2))


if __name__ == "__main__":
    main()
