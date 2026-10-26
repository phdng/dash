#!/usr/bin/env python3
"""K23 manual three-stage iPhone log QA correlated with the exact v2 IPA.

Three user-labeled logs are NOT proof of independent runs or device
attestation. This script never changes app files, signs IPA, or installs apps.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import re
import stat
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import device_log_audit as log_audit
import package as pkg

STAGES = ("fresh_install", "relaunch", "reinstall")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def verify_ipa(ipa: Path, report: Path, swift: Path) -> dict:
    if not ipa.is_file() or ipa.is_symlink() or not report.is_file() or report.is_symlink():
        raise AssertionError("K23 QA requires actual IPA and accompanying report")
    claims = json.loads(report.read_text(encoding="utf-8"))
    if (type(claims) is not dict or claims.get("scope") != pkg.SCOPE or
            claims.get("schema") != 1 or claims.get("signing") != "UNSIGNED" or
            claims.get("reference_transport_format") !=
            "BASE64_V1_INERT_RESOURCE_NOT_TRUST_ANCHOR" or
            claims.get("reference_transport_member") != pkg.REFERENCE or
            claims.get("compiled_digests_not_immutable_trust_anchor") is not True or
            claims.get("bundled_reference_checked_at_packaging") is not True or
            claims.get("iphone_runtime") != "NOT_TESTED_BY_CI" or
            claims.get("running_app_self_integrity") is not False or
            claims.get("security_anti_tamper_proven") is not False or
            claims.get("arm64e_pac_tested") is not False or
            claims.get("crane_production_modified") is not False):
        raise AssertionError("K23 QA refuses malformed or security-upgraded report")
    if (not ipa.name == pkg.IPA or not ipa.stat().st_size <= 64 * 1024 * 1024 or
            digest(ipa.read_bytes()) != claims.get("ipa_sha256")):
        raise AssertionError("K23 QA IPA name/size/SHA mismatch")
    with zipfile.ZipFile(ipa) as z:
        entries = z.infolist()
        names = {pkg.PREFIX + x for x in pkg.EXPECTED_MEMBERS}
        if (len(entries) != len(names) or {x.filename for x in entries} != names or
                z.testzip() is not None):
            raise AssertionError("K23 QA IPA members/CRC mismatch")
        for m in entries:
            typ = stat.S_IFMT(m.external_attr >> 16)
            if (typ != stat.S_IFREG or m.file_size > pkg.MAX_FILE or
                    m.flag_bits & 1 or
                    (m.filename == pkg.PREFIX + pkg.APP and
                     not (m.external_attr >> 16) & stat.S_IXUSR)):
                raise AssertionError("K23 QA unsafe IPA ZIP member")
        info = z.read(pkg.PREFIX + "Info.plist")
        pkg.info_check(info)
        if plistlib.loads(info).get("CFBundleVersion") != "2":
            raise AssertionError("K23 QA requires IPA v2, not a stale prior install")
        exe = z.read(pkg.PREFIX + pkg.APP)
        packed = z.read(pkg.PREFIX + pkg.REFERENCE)
    if digest(exe) != claims.get("app_executable_sha256"):
        raise AssertionError("K23 QA app binary SHA mismatch")
    if digest(packed) != claims.get("reference_transport_sha256"):
        raise AssertionError("K23 QA encoded reference SHA mismatch")
    raw = pkg.decode_reference(packed)
    if digest(raw) != claims.get("reference_binary_sha256"):
        raise AssertionError("K23 QA decoded reference SHA mismatch")
    if not isinstance(claims.get("reference_uuid"), str):
        raise AssertionError("K23 QA missing reference UUID")
    # Confirm generated Swift matches the raw hashes and lengths used by
    # the device verifier, NOT merely the same untrusted report.
    if not swift.is_file() or swift.is_symlink():
        raise AssertionError("K23 QA requires generated K23Expected.swift")
    source = swift.read_text(encoding="utf-8")
    for property_name, val in (
        ("fullSHA256", claims["reference_binary_sha256"]),
        ("transportSHA256", claims["reference_transport_sha256"]),
        ("uuid", claims["reference_uuid"]),
    ):
        if f'static let {property_name} = "{val}"' not in source:
            raise AssertionError("K23 QA compiled expected field mismatch " + property_name)
    for name, expected in (
        ("fileSize", len(raw)), ("transportSize", len(packed))
    ):
        if f"static let {name} = {expected}" not in source:
            raise AssertionError("K23 QA generated size mismatch " + name)
    target_hashes = claims.get("reference_target_region_sha256")
    if not isinstance(target_hashes, dict) or set(target_hashes) != {
        "_dd_k8_evaluate", "_dd_k14_ios_parity"
    }:
        raise AssertionError("K23 QA needs the exact two measured target intervals")
    for name, sha in target_hashes.items():
        if not re.fullmatch("[a-f0-9]{64}", sha) or sha not in source:
            raise AssertionError("K23 QA missing compiled target " + name)
    return {
        "ipa_sha256": claims["ipa_sha256"],
        "reference_sha256": claims["reference_binary_sha256"],
        "reference_transport_sha256": claims["reference_transport_sha256"],
        "reference_uuid": claims["reference_uuid"],
        "reference_target_intervals": 2,
        "unsigned": True,
    }


def review(artifact: Path, stages: dict[str, Path]) -> dict:
    if set(stages) != set(STAGES):
        raise AssertionError("K23 QA requires all three labeled test stages")
    sources = [stages[s].resolve() for s in STAGES]
    if len(set(sources)) != 3:
        raise AssertionError("K23 QA log inputs must be separate file paths")
    bundle = artifact.resolve()
    if not bundle.is_dir() or artifact.is_symlink():
        raise AssertionError("K23 QA artifact folder missing")
    report_path = bundle / pkg.REPORT
    code = verify_ipa(bundle / pkg.IPA, report_path, bundle / "K23Expected.swift")
    entries = {}
    for stage in STAGES:
        p = stages[stage]
        if not p.is_file() or p.is_symlink():
            raise AssertionError("K23 QA missing regular log for " + stage)
        obj = log_audit.validate(p, report_path)
        if (obj["claimed_reference_uuid"] != code["reference_uuid"] or
                obj["user_shared_ten_lines_matched"] is not True):
            raise AssertionError("K23 QA device text differs from IPA reference")
        entries[stage] = {
            "log_sha256": obj["log_sha256"],
            "text_schema": "EXACT_TEN_LINES_PASS",
        }
    return {
        "schema": 1,
        "scope": "USER_SHARED_K23_V2_THREE_STAGE_TEXT_CORRELATION_NOT_ATTESTATION",
        "artifact": code,
        "stages": entries,
        "three_distinct_file_paths_supplied": True,
        "three_independent_device_runs_attested": False,
        "user_claimed_steps_not_independently_observed": True,
        "device_execution_cryptographically_attested": False,
        "runtime_self_integrity_implemented": False,
        "arm64e_pac_or_security_proven": False,
        "crane_production_modified": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--artifact-dir", required=True, type=Path)
    p.add_argument("--fresh-install", required=True, type=Path)
    p.add_argument("--relaunch", required=True, type=Path)
    p.add_argument("--reinstall", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    if a.out.exists() or a.out.is_symlink():
        raise AssertionError("K23 QA refuses overwrite of prior device review")
    result = review(a.artifact_dir, {
        "fresh_install": a.fresh_install,
        "relaunch": a.relaunch,
        "reinstall": a.reinstall,
    })
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("K23_V2_THREE_STAGE_USER_SHARED_LOG_CORRELATION_PASS:"
          " not device attestation or self-integrity")


if __name__ == "__main__":
    main()
