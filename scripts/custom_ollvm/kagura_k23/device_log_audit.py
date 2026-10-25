#!/usr/bin/env python3
"""K23 strict 10-line user-shared log schema check, NOT device attestation."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

EXPECTED_SCOPE = "BUNDLED_REFERENCE_ONLY"


def validate(log: Path, report: Path) -> dict:
    raw = log.read_bytes()
    if len(raw) > 2048 or not raw.endswith(b"\n") or len(raw) < 150:
        raise AssertionError("K23 user log incomplete/unbounded")
    text = raw.decode("ascii", errors="strict").replace("\r\n", "\n")
    if "\r" in text:
        raise AssertionError("K23 invalid CR")
    lines = text[:-1].split("\n")
    if len(lines) != 10:
        raise AssertionError("K23 requires 10 exact device log lines")
    ref = json.loads(report.read_text(encoding="utf-8"))
    if (ref.get("schema") != 1 or
        ref.get("scope") !=
        "K23_ISOLATED_BUNDLED_K14_CODE_REFERENCE_SHA256_RUNTIME_FUNCTIONALITY_NO_SELF_SECURITY" or
        ref.get("iphone_runtime") != "NOT_TESTED_BY_CI" or
        ref.get("signing") != "UNSIGNED" or
        ref.get("running_app_self_integrity") is not False or
        ref.get("security_anti_tamper_proven") is not False or
        ref.get("crane_production_modified") is not False):
        raise AssertionError("K23 IPA report no longer reflects study scope")
    uid = ref.get("reference_uuid")
    if not isinstance(uid, str) or not re.fullmatch(
            r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}", uid):
        raise AssertionError("K23 reference UUID malformed")
    expected = [
        "DD_K23_SCHEMA=1",
        "DD_K23_CONTEXT=IOS_DEVICE_USER_INITIATED",
        "DD_K23_SCOPE=" + EXPECTED_SCOPE,
        "DD_K23_REFERENCE_UUID=" + uid,
        "DD_K23_REFERENCE_SHA256=PASS",
        "DD_K23_CODE_INTERVALS=2",
        "DD_K23_MUTATED_CODE=REJECTED",
        "DD_K23_TRUNCATED_REFERENCE=REJECTED",
        "DD_K23_SELF_INTEGRITY=NOT_IMPLEMENTED",
        "DD_K23_COMPLETE=PASS",
    ]
    if lines != expected:
        raise AssertionError("K23 fake/malformed/out-of-scope user log")
    return {
        "schema": 1, "scope": "K23_USER_SHARED_TEXT_CORRELATION_ONLY",
        "user_shared_ten_lines_matched": True,
        "claimed_reference_uuid": uid,
        "log_sha256": hashlib.sha256(raw).hexdigest(),
        "claimed_ios_device_context_not_attested": True,
        "device_execution_independently_observed": False,
        "runtime_self_integrity_proven": False,
        "anti_tamper_or_arm64e_pac_proven": False,
        "crane_production_modified": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--log", type=Path, required=True)
    p.add_argument("--ipa-report", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    if a.out.exists() or a.out.is_symlink():
        raise AssertionError("K23 refuses to overwrite device log review")
    payload = validate(a.log, a.ipa_report)
    a.out.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n",
                     encoding="utf-8")
    print("K23_USER_SHARED_DEVICE_TEXT_CHECK_PASS: NOT execution attestation")


if __name__ == "__main__":
    main()
