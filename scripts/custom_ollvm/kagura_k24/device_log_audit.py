#!/usr/bin/env python3
"""K24 strict user-shared log correlation; NEVER device attestation.

Measurement mode checks user's text against post-linked Mach-O report.
Signed mode also requires independent offline Ed25519 envelope validation
using the separate trusted public PEM/fingerprint. Neither mode proves
that the log originated from an unmodified physical device executable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import external_sign
import package as k24


def validate(log: Path, report: Path, mode: str,
             artifact_dir: Path | None = None,
             envelope: Path | None = None,
             trusted_public: Path | None = None,
             fingerprint: str | None = None) -> dict:
    if mode not in ("measurement", "signed"):
        raise AssertionError("K24 unsupported device-log mode")
    if not log.is_file() or log.is_symlink() or not report.is_file() or report.is_symlink():
        raise AssertionError("K24 user log/report missing or symlink")
    raw = log.read_bytes()
    if not 140 <= len(raw) <= 2048 or not raw.endswith(b"\n"):
        raise AssertionError("K24 log incomplete/unbounded")
    text = raw.decode("ascii", errors="strict").replace("\r\n", "\n")
    if "\r" in text:
        raise AssertionError("K24 log contains invalid standalone CR")
    actual = text[:-1].split("\n")
    ref = json.loads(report.read_text(encoding="utf-8"))
    if (ref.get("scope") != k24.SCOPE or ref.get("schema") != 1 or
            ref.get("signing") != "UNSIGNED" or
            ref.get("device_runtime_text_matches_file") != "NOT_TESTED" or
            ref.get("runtime_self_integrity_security_proven") is not False or
            ref.get("device_attestation") is not False or
            ref.get("crane_production_modified") is not False or
            not k24.UUID.fullmatch(str(ref.get("app_executable_uuid", ""))) or
            not k24.HEX64.fullmatch(str(ref.get("self_text_sha256", ""))) or
            type(ref.get("self_text_size")) is not int or
            not (16 <= ref["self_text_size"] <= k24.MAX_FILE)):
        raise AssertionError("K24 report malformed or overstated")
    if mode == "measurement":
        if any(x is not None for x in (artifact_dir, envelope, trusted_public, fingerprint)):
            raise AssertionError("K24 unsigned measurement mode must not accept signed inputs")
        expected = [
            "DD_K24_SCHEMA=1",
            "DD_K24_SCOPE=OWN_RUNNING_MAIN_EXECUTABLE_TEXT_ONLY",
            "DD_K24_MAIN_UUID=" + ref["app_executable_uuid"],
            "DD_K24_RUNTIME_TEXT_BYTES=" + str(ref["self_text_size"]),
            "DD_K24_RUNTIME_TEXT_SHA256=" + ref["self_text_sha256"],
            "DD_K24_EXTERNAL_KEY=" + ("PINNED_AT_BUILD" if
                ref.get("public_key_pinned_into_compiled_app") else "NOT_CONFIGURED"),
            "DD_K24_EXTERNAL_SIGNATURE=NOT_IMPORTED",
            "DD_K24_COMPLETE=MEASUREMENT_ONLY"
        ]
    else:
        if (artifact_dir is None or envelope is None or
            trusted_public is None or fingerprint is None):
            raise AssertionError("K24 signed log needs independent signed artifact proof")
        signed = external_sign.verify(artifact_dir, envelope, trusted_public, fingerprint)
        if (signed["measured_app_uuid"] != ref["app_executable_uuid"] or
                not ref.get("public_key_pinned_into_compiled_app") or
                (artifact_dir / k24.REPORT).read_bytes() != report.read_bytes()):
            raise AssertionError("K24 signed envelope/artifact/report not correlated")
        expected = [
            "DD_K24_SCHEMA=1",
            "DD_K24_SCOPE=OWN_RUNNING_MAIN_EXECUTABLE_TEXT_ONLY",
            "DD_K24_MAIN_UUID=" + ref["app_executable_uuid"],
            "DD_K24_RUNTIME_TEXT_SHA256=" + ref["self_text_sha256"],
            "DD_K24_EXTERNAL_ED25519=PASS",
            "DD_K24_SIGNED_EXPECTED_MATCH=PASS",
            "DD_K24_MUTATED_COPY=REJECTED",
            "DD_K24_TRUNCATED_COPY=REJECTED",
            "DD_K24_FORGED_STATEMENT=REJECTED",
            "DD_K24_SELF_SECURITY=NOT_PROVEN",
            "DD_K24_COMPLETE=PASS_LAB_ONLY"
        ]
    if actual != expected:
        raise AssertionError("K24 user-shared log not correlated to actual IPA/manifest")
    return {
        "schema": 1,
        "scope": "K24_USER_SHARED_TEXT_CORRELATION_ONLY_NOT_DEVICE_ATTESTATION",
        "mode": mode,
        "log_sha256": hashlib.sha256(raw).hexdigest(),
        "claimed_app_uuid": ref["app_executable_uuid"],
        "claimed_memory_code_sha256": ref["self_text_sha256"],
        "user_shared_text_matches_artifact": True,
        "signed_reference_verified_offline": mode == "signed",
        "actual_iPhone_runtime_independently_verified": False,
        "unpatchable_verifier_or_trust_root_proven": False,
        "runtime_security_or_anti_tamper_proven": False,
        "arm64e_pac_proven": False,
        "crane_production_modified": False
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", required=True, choices=("measurement", "signed"))
    p.add_argument("--log", required=True, type=Path)
    p.add_argument("--report", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--artifact-dir", type=Path)
    p.add_argument("--envelope", type=Path)
    p.add_argument("--trusted-public-key", type=Path)
    p.add_argument("--expected-spki-sha256")
    a = p.parse_args()
    if a.out.exists() or a.out.is_symlink():
        raise AssertionError("K24 log review refuses overwrite")
    result = validate(a.log, a.report, a.mode,
                      a.artifact_dir, a.envelope,
                      a.trusted_public_key, a.expected_spki_sha256)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("K24_USER_SHARED_TEXT_CORRELATION_PASS: NOT independent iPhone attestation")


if __name__ == "__main__":
    main()
