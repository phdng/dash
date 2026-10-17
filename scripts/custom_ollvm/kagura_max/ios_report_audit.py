#!/usr/bin/env python3
"""Strict review of user-shared KaguraLab logs; never phone attestation.

Supports the original seven-line schema 1 and the new LC_UUID-tagged schema 2.
Checksums use an independent synthetic reference model; optional CI reports
allow matching a claimed executable UUID to the audited IPA, not verifying
that the user really ran it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from ios_reference import expected_checksums

UUID_RE = r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}"
SHA_RE = r"[0-9a-f]{64}"
PIPELINE = "STR_FLA_BCF_SUB_CO_BBR_BBS"


def _app_uuid(line: str, key: str) -> str:
    match = re.fullmatch(re.escape(key) + r"=(" + UUID_RE + r")", line)
    if not match:
        raise AssertionError("Kagura executable UUID missing/malformed")
    return match.group(1)


def _check_ci_reports(ipa: Path, evidence: Path, claimed_uuid: str) -> dict:
    bundle = json.loads(ipa.read_text(encoding="utf-8"))
    passes = json.loads(evidence.read_text(encoding="utf-8"))
    if not all((
        bundle.get("schema") == 1,
        bundle.get("bundle_identifier") == "com.duodash.research.kaguralab",
        bundle.get("architecture") == "arm64",
        bundle.get("filetype") == "MH_EXECUTE",
        bundle.get("pipeline_expected") ==
            "LLVM19_KAGURA_STR_FLA_BCF_SUB_CO_BBR_BBS",
        bundle.get("macho_uuid") == claimed_uuid,
        re.fullmatch(SHA_RE, bundle.get("binary_sha256", "")),
        re.fullmatch(SHA_RE, bundle.get("ipa_sha256", "")),
        passes.get("schema") == 1,
        passes.get("scope") == "STANDALONE_KAGURA_LAB_APP_ONLY",
        passes.get("passes_observed_count") == 7,
        [x.get("pass") for x in passes.get("passes", [])] ==
            ["str", "fla", "bcf", "sub", "co", "bbr", "bbs"],
        all(x.get("pass_manager_invocation_observed") is True
            for x in passes.get("passes", [])),
        passes.get("app_macho_uuid") == claimed_uuid,
        passes.get("app_sha256") == bundle.get("binary_sha256"),
        passes.get("ipa_sha256") == bundle.get("ipa_sha256"),
        passes.get("actual_device_execution") == "NOT_TESTED_BY_CI",
        passes.get("security_attestation") is False,
    )):
        raise AssertionError("Kagura user UUID/IPA/7-pass CI evidence mismatch")
    return {
        "claimed_executable_uuid": claimed_uuid,
        "matched_ci_ipa_sha256": bundle["ipa_sha256"],
        "matched_ci_binary_sha256": bundle["binary_sha256"],
        "comparison_not_attestation": True,
    }


def validate(log: Path, *, ipa_report: Path | None = None,
             pass_evidence: Path | None = None) -> dict:
    if (ipa_report is None) != (pass_evidence is None):
        raise AssertionError("Provide BOTH IPA and seven-pass CI reports")
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
    if not parity or parity[0] not in ("DD_KAGURA_SCHEMA=1",
                                       "DD_KAGURA_SCHEMA=2"):
        raise AssertionError("Unsupported Kagura report schema")
    schema = int(parity[0][-1])
    if len(parity) != (8 if schema == 2 else 7):
        raise AssertionError("Wrong Kagura parity line count")
    expected_start = [
        f"DD_KAGURA_SCHEMA={schema}",
        "DD_KAGURA_CONTEXT=IOS_DEVICE",
        "DD_KAGURA_ARCH=arm64:0x00000000",
    ]
    if parity[:3] != expected_start:
        raise AssertionError("Invalid Kagura device report context/ABI")
    uuid = _app_uuid(parity[3], "DD_KAGURA_APP_UUID") if schema == 2 else None
    offset = 1 if schema == 2 else 0
    expected_tail = [
        f"DD_KAGURA_PIPELINE={PIPELINE}",
        "DD_KAGURA_VECTORS_PASS=8192",
        "DD_KAGURA_CHECKSUM=" + expected_checksums()["parity_checksum"],
        "DD_KAGURA_COMPLETE=PASS",
    ]
    if len(parity) != 7 + offset or parity[3 + offset:] != expected_tail:
        raise AssertionError("Kagura parity report/checksum mismatch")
    if ipa_report is not None and uuid is None:
        raise AssertionError("Legacy schema 1 has no executable build UUID")

    result = {
        "schema": schema,
        "claimed_architecture": "arm64",
        "claimed_context": "IOS_DEVICE",
        "pipeline": PIPELINE,
        "claimed_parity_vectors": 8192,
        "parity_checksum": expected_checksums()["parity_checksum"],
        "benchmark_expected_checksum": expected_checksums()["benchmark_checksum"],
        "claimed_executable_uuid": uuid,
        "build_uuid_crosschecked_to_ci_reports": False,
        "optional_benchmark": None,
        "user_log_sha256": hashlib.sha256(raw).hexdigest(),
        "device_execution_cryptographically_attested": False,
        "log_provenance": "USER_SHARED_TEXT_NOT_AUTHENTICATED",
        "crane_production_verified": False,
        "arm64e_runtime": "NOT_TESTED",
    }

    if len(sections) == 2:
        lines = sections[1].splitlines()
        if len(lines) != (11 if schema == 2 else 10):
            raise AssertionError("Wrong Kagura benchmark line count")
        expected = [
            f"DD_KAGURA_PERF_SCHEMA={schema}",
            "DD_KAGURA_PERF_CONTEXT=IOS_DEVICE",
            "DD_KAGURA_PERF_ARCH=arm64:0x00000000",
        ]
        if lines[:3] != expected:
            raise AssertionError("Wrong Kagura benchmark schema/device ABI")
        if schema == 2 and _app_uuid(
            lines[3], "DD_KAGURA_PERF_APP_UUID"
        ) != uuid:
            raise AssertionError("Benchmark is from a different app binary")
        value_pos = 5 + offset
        if (len(lines) != 10 + offset or
            lines[3 + offset:5 + offset] != [
                "DD_KAGURA_PERF_PAIRS=5",
                "DD_KAGURA_PERF_CALLS_PER_SAMPLE=4096",
            ] or
            lines[7 + offset] != "DD_KAGURA_PERF_CHECKSUM=" +
                expected_checksums()["benchmark_checksum"] or
            lines[8 + offset] !=
                "DD_KAGURA_PERF_NOTE=OBSERVATIONAL_NOT_SECURITY_ATTESTATION" or
            lines[9 + offset] != "DD_KAGURA_PERF_COMPLETE=PASS"):
            raise AssertionError("Malformed or mismatched Kagura timing report")
        values = []
        for pos, name in ((value_pos, "PLAIN"), (value_pos + 1, "PROTECTED")):
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

    if ipa_report is not None and pass_evidence is not None:
        result["ci_report_comparison"] = _check_ci_reports(
            ipa_report, pass_evidence, uuid
        )
        result["build_uuid_crosschecked_to_ci_reports"] = True
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--log", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--ipa-report", type=Path)
    p.add_argument("--pass-evidence", type=Path)
    a = p.parse_args()
    verified = validate(a.log, ipa_report=a.ipa_report,
                        pass_evidence=a.pass_evidence)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(verified, indent=2, sort_keys=True) + "\n",
                     encoding="utf-8")
    print("KAGURA_IOS_USER_LOG_TEXT_CONSISTENT: independent checksums; "
          "not an attested device result")


if __name__ == "__main__":
    main()
