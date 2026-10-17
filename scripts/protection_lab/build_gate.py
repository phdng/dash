#!/usr/bin/env python3
"""Machine-readable Protection Lab outcome: arm64 TrollStore IPA structure,
arm64e Apple-Clang link/ABI/UUID BUILD ONLY, device execution deferred.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def generate(build: Path, identity: Path, ipa_report: Path, output: Path) -> dict:
    b = json.loads(build.read_text(encoding="utf-8"))
    ids = json.loads(identity.read_text(encoding="utf-8"))
    ipa = json.loads(ipa_report.read_text(encoding="utf-8"))
    if b.get("schema") != 1 or ids.get("schema") != 1 or ipa.get("schema") != 1:
        raise AssertionError("Unsupported build/audit report schema")
    if b.get("ios_on_device_runtime") != "NOT_TESTED" or (
        ids.get("runtime_on_iphone") != "NOT_TESTED_BY_CI"
    ):
        raise AssertionError("CI must not claim iPhone runtime execution")
    if b.get("automatic_device_installation") is not False or (
        ids.get("uuid_security_attestation") is not False
    ):
        raise AssertionError("Unexpected device install or attestation claims")
    uuids = []
    for arch, subtype in (("arm64", "0x00000000"), ("arm64e", "0x80000002")):
        one = b.get(arch, {})
        two = ids.get("slices", {}).get(arch, {})
        if not isinstance(one, dict) or not isinstance(two, dict):
            raise AssertionError("Missing mandatory architecture report")
        if any(one.get(k) != two.get(k)
               for k in ("sha256", "size_bytes", "filetype", "cpu_subtype_raw")):
            raise AssertionError(f"Conflicting {arch} identity and build reports")
        if one.get("arch") != arch or one.get("filetype") != "MH_EXECUTE" or (
            one.get("cpu_subtype_raw") != subtype
        ):
            raise AssertionError(f"{arch} wrong Mach-O subtype or missing executable")
        uuid = two.get("macho_uuid")
        if not isinstance(uuid, str) or len(uuid) != 36:
            raise AssertionError(f"{arch} missing Mach-O LC_UUID")
        uuids.append(uuid)
    if len(set(uuids)) != 2:
        raise AssertionError("Expected different UUIDs for independently built binaries")
    if ipa.get("architecture_expected") != "arm64" or (
        ipa.get("binary_sha256") != b["arm64"]["sha256"]
    ) or ipa.get("trollstore_installation") != "NOT_TESTED" or (
        ipa.get("code_signing") != "NOT_PERFORMED"
    ):
        raise AssertionError("IPA does not match audited arm64 build or policy")
    result = {
        "schema": 1,
        "goal": "arm64_trollstore_ipa_plus_arm64e_build_only",
        "arm64": {
            "compiler_and_macho_abi": "PASS",
            "trollstore_ipa_structure": "PASS",
            "trollstore_installation": "NOT_TESTED",
            "device_runtime": "NOT_TESTED",
            "macho_sha256": b["arm64"]["sha256"],
            "macho_uuid": uuids[0],
        },
        "arm64e": {
            "compiler_link_macho_abi_uuid": "PASS",
            "abi_versioned_userspace_pac_header": "0x80000002",
            "a12_plus_device_runtime": "DEFERRED_NO_DEVICE",
            "pac_runtime_validation": "NOT_TESTED",
            "macho_sha256": b["arm64e"]["sha256"],
            "macho_uuid": uuids[1],
        },
        "sllvm_compiler_plugin": "NOT_INTEGRATED",
        "crane_production_modified": False,
        "no_security_score": True,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print("PROTECTION_LAB_BUILD_GATES_PASS: arm64 IPA structure; "
          "arm64e Apple-Clang versioned PAC ABI build only; A12+ runtime DEFERRED")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--identity", type=Path, required=True)
    parser.add_argument("--ipa", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    generate(args.build, args.identity, args.ipa, args.out)
