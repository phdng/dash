#!/usr/bin/env python3
"""K14 independently check K13 real native proof and final iOS IPA bytes."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts/custom_ollvm/kagura_k13"))
import audit as k13audit  # noqa: E402
import package_ipa as package  # noqa: E402

EXPORTED = {"_dd_k8_evaluate", "_dd_k14_ios_parity", "_main"}
ORACLE = "25a3318e3d7d6525"
SCOPE = "K14_K13_VERIFIED_SINGLE_CSEBREAK_IOS_ARM64_IPA_LAB_ONLY"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_nm(content: str) -> set[str]:
    defined = set()
    for line in content.splitlines():
        m = re.fullmatch(r"[0-9a-fA-F]+\s+[Tt]\s+(_[A-Za-z0-9_.$]+)", line)
        if m:
            defined.add(m.group(1))
    if not EXPORTED.issubset(defined):
        raise AssertionError("K14 final MachO must define all 3 actual canary/app functions")
    return defined


def inspect(out: Path) -> dict:
    k13 = k13audit.audit(out)
    if (k13.get("pass") != "kagura-cse-break" or
            k13.get("pass_class") != "kagura::CSEBreakPass" or
            k13["targets"]["macos"].get("native_parity") != "PASS" or
            k13["targets"]["macos"].get("baseline_checksum") != ORACLE or
            k13["targets"]["macos"].get("protected_checksum") != ORACLE or
            k13["targets"]["ios"].get("real_ir_and_object_delta") is not True or
            k13["targets"]["ios"].get("iphone_executed") is not False):
        raise AssertionError("K14 K13 pinned real single-pass proof not available")
    app = out / (package.APP + ".app")
    info, binary = package.check_app(app)
    ipa = out / (package.APP + "-TrollStore-arm64.ipa")
    pack = package.verify_ipa(ipa)
    manifest = json.loads((out / "Kagura-K14-IPA-report.json").read_text(
        encoding="utf-8"))
    if pack != manifest or pack["binary_sha256"] != package.sha(binary):
        raise AssertionError("K14 ZIP app/embedded MachO SHA or plist mismatch")
    ios_obj = out / "ios-cse-break.o"
    if sha(ios_obj) != k13["targets"]["ios"]["protected_object_sha256"]:
        raise AssertionError("K14 linked input not actual protected K13 object")
    for name in ("ios-probe.o", "ios-app-main.o"):
        item = out / name
        if not item.is_file() or item.stat().st_size < 32:
            raise AssertionError("K14 missing compiled iPhoneOS ABI object")
        k13audit.ios_macho(item.read_bytes())
    defined_log = out / "ipa-app-defined-symbols.txt"
    if not defined_log.is_file() or not EXPORTED.issubset(
            check_nm(defined_log.read_text(encoding="utf-8"))):
        raise AssertionError("K14 missing final executable symbol provenance")
    # On macOS workflow, verify live actual MachO symbol table again
    # rather than accepting arbitrary report text from build script.
    live_nm = subprocess.run(["xcrun", "nm", "-gU", str(app / package.APP)],
                             capture_output=True, text=True, check=True)
    if not EXPORTED.issubset(check_nm(live_nm.stdout)):
        raise AssertionError("K14 final executable nlist cannot be verified")
    if live_nm.stdout != defined_log.read_text(encoding="utf-8"):
        raise AssertionError("K14 final nm raw log disagrees with executable")
    undefined_nm = subprocess.run(
        ["xcrun", "nm", "-u", "-j", str(app / package.APP)],
        capture_output=True, text=True, check=True)
    if any(line.startswith("_kagura_") for line in undefined_nm.stdout.splitlines()):
        raise AssertionError("K14 final executable has unresolved Kagura runtime")
    link = out / "ipa-link.log"
    if not link.is_file():
        raise AssertionError("K14 missing true iOS link diagnostics")
    object_hashes = {
        "ios-cse-break.o": sha(ios_obj),
        "ios-probe.o": sha(out / "ios-probe.o"),
        "ios-app-main.o": sha(out / "ios-app-main.o"),
    }
    return {
        "schema": 1,
        "scope": SCOPE,
        "pinned_commit": k13["pinned_commit"],
        "pinned_registry_sha256": k13["pinned_registry_sha256"],
        "k13_native_report_sha256": sha(out / "Kagura-K13-REPORT.json"),
        "k13_mac_native_checksum": ORACLE,
        "k13_cse_break_ios_object_sha256": sha(ios_obj),
        "k13_cse_break_ios_object_embedded": True,
        "ios_link_input_object_sha256": object_hashes,
        "pass_class": "kagura::CSEBreakPass",
        "pass_pipeline": "function(kagura-cse-break),verify",
        "ipa_sha256": pack["ipa_sha256"],
        "app_binary_sha256": pack["binary_sha256"],
        "app_macho_uuid": pack["app_macho_uuid"],
        "bundle_identifier": package.BUNDLE,
        "exported_symbols": sorted(EXPORTED),
        "final_app_nlist_verified_with_xcrun": True,
        "ipa_embedded_binary_matches_linked_app": True,
        "signing": "UNSIGNED",
        "ios_device_execution": "NOT_TESTED_BY_CI",
        "arm64e_pac_runtime": "NOT_TESTED",
        "crane_production_modified": False,
        "security_attestation": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    report = inspect(a.out)
    (a.out / "Kagura-K14-IPA-EVIDENCE.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("K14_K13_CSEBREAK_IOS_ARM64_IPA_EVIDENCE_PASS: true object/IPA"
          " UUID/SHA/native oracle; iPhone NOT_TESTED")


if __name__ == "__main__":
    main()
