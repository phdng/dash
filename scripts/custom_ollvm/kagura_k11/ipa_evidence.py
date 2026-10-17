#!/usr/bin/env python3
"""K11 check original five-pass K10 evidence + IPA binary identity."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
K10 = ROOT / "scripts/custom_ollvm/kagura_k10/pilot.py"
spec = importlib.util.spec_from_file_location("k11_k10", K10)
if spec is None or spec.loader is None:
    raise RuntimeError("K11 needs K10 validator")
k10 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(k10)
import package_ipa as package

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inspect(out: Path) -> dict:
    ipa = out / "KaguraFiveLab-TrollStore-arm64.ipa"
    ipa_report = out / "KaguraFiveLab-IPA-report.json"
    app = out / "KaguraFiveLab.app"
    if not (ipa.is_file() and ipa_report.is_file() and app.is_dir()):
        raise AssertionError("K11 missing actual IPA/app/report")
    pack = package.verify_ipa(ipa)
    if pack != json.loads(ipa_report.read_text(encoding="utf-8")):
        raise AssertionError("K11 IPA report mismatches embedded binary")
    app_info = package.check_app(app)
    if (app_info["uuid"] != pack["macho_uuid"] or
            app_info["binary_sha256"] != pack["binary_sha256"]):
        raise AssertionError("K11 app differs from packaged IPA")
    report_path = out / "Kagura-K9-COMPOSITION-REPORT.json"
    k10_report_path = out / "Kagura-K10-METADATA-REPORT.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    k10_summary = k10.verify_report(report, out)
    if k10_summary != json.loads(k10_report_path.read_text(encoding="utf-8")):
        raise AssertionError("K11 original five-pass K10 report was modified")
    ci = out / "05-ci/ios.o"
    if sha(ci) != report["stages"]["ci"]["ios"]["object_sha256"]:
        raise AssertionError("K11 must package exactly final K10 iOS CI object")
    source_log = out / "ios-rtld-source.txt"
    symbols = out / "ipa-app-symbols.txt"
    if not (source_log.is_file() and symbols.is_file()):
        raise AssertionError("K11 missing exact upstream iOS runtime provenance/symbols")
    runtime_source = source_log.read_text(encoding="utf-8").strip()
    if (not re.fullmatch(r"runtime/[a-zA-Z0-9_./-]+\.c", runtime_source) or
            ".." in runtime_source):
        raise AssertionError("K11 runtime source must originate from pinned Kagura C")
    locator = out / "ios-rtld-discovery.json"
    symfile = out / "ios-kagura-rtld-symbols.txt"
    if not (locator.is_file() and symfile.is_file()):
        raise AssertionError("K11 missing actual upstream resolver definition audit")
    discovery = json.loads(locator.read_text(encoding="utf-8"))
    if (discovery.get("schema") != 1 or
            discovery.get("symbol") != "kagura_rtld_default_handle" or
            discovery.get("function_definitions") != [runtime_source] or
            discovery.get("selected_source") != runtime_source or
            not re.fullmatch("[a-f0-9]{64}",
                             discovery.get("selected_source_sha256", ""))):
        raise AssertionError("K11 claimed resolver source is not a unique C definition")
    if not re.search(r"(?m)^\\S+ [Tt] _kagura_rtld_default_handle$",
                     symfile.read_text(encoding="utf-8")):
        raise AssertionError("K11 iOS runtime object did not define Kagura resolver")
    required = ("_dd_k8_evaluate", "_dd_k9_mvo_probe",
                "_kagura_rtld_default_handle", "_dd_k11_ios_parity")
    lines = symbols.read_text(encoding="utf-8").splitlines()
    if any(not any(re.search(r"\b" + re.escape(s) + r"$", line)
                   for line in lines) for s in required):
        raise AssertionError("K11 iOS linked executable missing real CI/resolver symbols")
    object_hashes = {}
    for required_path in ("ios-probe.o", "ios-app-main.o",
                          "ios-kagura-rtld.o"):
        path = out / required_path
        if not path.is_file():
            raise AssertionError("K11 missing genuine iOS object evidence: " + required_path)
        k10.k9.k8.verify_apple_arm64_object(path.read_bytes())
        object_hashes[required_path] = sha(path)
    if not (out / "ipa-macho-arm64.txt").is_file():
        raise AssertionError("K11 missing Apple MachO binary output")
    k10.k9.k8.verify_apple_arm64_object(ci.read_bytes())
    result = {
        "schema": 1,
        "scope": "K11_FIVE_PASS_K10_STRICT_METADATA_TROLLSTORE_LAB_ONLY",
        "k10_status": k10.STATUS,
        "k10_evidence_sha256": sha(k10_report_path),
        "k9_composition_sha256": sha(report_path),
        "k10_final_ci_ios_object_sha256": sha(ci),
        "ios_link_input_object_sha256": object_hashes,
        "ios_upstream_resolver_source_path": runtime_source,
        "ios_upstream_resolver_source_sha256": discovery["selected_source_sha256"],
        "ios_upstream_resolver_definition_verified_by_nm": True,
        "ios_upstream_resolver_discovery_sha256": sha(locator),
        "native_checksums_from_k10": [
            k10.k9.K8_C_DIGEST, k10.k9.K8_MVO_DIGEST],
        "kagura_pinned_commit": k10.k9.UPSTREAM_PIN,
        "ios_runtime_from_exact_kagura_upstream": runtime_source,
        "ipa_sha256": pack["ipa_sha256"],
        "app_binary_sha256": pack["binary_sha256"],
        "app_macho_uuid": pack["macho_uuid"],
        "app_bundle": package.BUNDLE,
        "embedded_binary_sha_matches_app": True,
        "five_pass_ios_object_verified": True,
        "ios_mh_execute_arm64_uuid_verified": True,
        "resolver_symbol_present": True,
        "exported_canary_symbols_present": True,
        "ios_device_execution": "NOT_TESTED_BY_CI",
        "signing": "UNSIGNED",
        "arm64e_pac_runtime": "NOT_TESTED",
        "crane_production_modified": False,
        "security_attestation": False,
    }
    return result

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True, type=Path)
    x = p.parse_args()
    report = inspect(x.out)
    (x.out / "Kagura-K11-IPA-EVIDENCE.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("K11_FIVE_PASS_IPA_EVIDENCE_PASS: K10 real CI objects, iOS resolver, "
          "MachO UUID/SHA; iPhone NOT TESTED")

if __name__ == "__main__":
    main()
