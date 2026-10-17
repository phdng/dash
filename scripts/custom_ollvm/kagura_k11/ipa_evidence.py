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
import ci_runtime_closure as runtime_closure

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
    if not re.search(r"(?m)^\S+ [Tt] _kagura_rtld_default_handle$",
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
    closure_file = out / "ios-runtime-closure.json"
    if not closure_file.is_file():
        raise AssertionError("K11 missing real upstream iOS Kagura dependency closure")
    closure = json.loads(closure_file.read_text(encoding="utf-8"))
    nm_report_file = out / "ios-runtime-initial-nm.json"
    if not nm_report_file.is_file():
        raise AssertionError("K11 missing unmodified raw Apple nm symbol output")
    raw_nm = json.loads(nm_report_file.read_text(encoding="utf-8"))
    expected_originals = ("05-ci/ios.o", "ios-kagura-rtld.o",
                          "ios-probe.o", "ios-app-main.o")
    if set(raw_nm) != set(expected_originals):
        raise AssertionError("K11 raw nm evidence missing original iOS objects")
    for path in expected_originals:
        entry = raw_nm[path]
        if (entry.get("nm_command") != "xcrun nm -u -j" or
                entry.get("parsed_kagura_symbols") != sorted(
                    s for s in runtime_closure.parse_undefined_names(
                        entry.get("raw_stdout", ""))
                    if s.startswith("_kagura_"))):
            raise AssertionError("K11 raw Apple nm stdout/parser evidence mismatch")
    required_runtime = {"_kagura_image_list_contains",
                        "_kagura_suspicious_image_patterns"}
    providers = closure.get("providers_by_undefined_symbol")
    sources = closure.get("selected_provider_sources")
    if (closure.get("schema") != 1 or
            closure.get("scope") !=
            "PINNED_IOS_ARM64_RUNTIME_C_SYMBOL_CLOSURE_NOT_SHIMS" or
            closure.get("resolver_source") != runtime_source or
            closure.get("initial_nm_format") !=
            "APPLE_NM_UNDEFINED_JUST_SYMBOL_NAMES" or
            closure.get("initial_nm_raw_report_sha256") != sha(nm_report_file) or
            not required_runtime.issubset(
                set(raw_nm["ios-kagura-rtld.o"]["parsed_kagura_symbols"])) or
            closure.get("macos_library_linked_to_ios") is not False or
            closure.get("stubs_inserted") is not False or
            closure.get("final_unresolved_kagura_symbols") != [] or
            not isinstance(providers, dict) or
            not required_runtime.issubset(providers) or
            not isinstance(sources, list) or not sources or
            len(sources) > 12):
        raise AssertionError("K11 iOS pinned runtime symbol closure invalid")
    closure_by_name = {}
    source_paths = set()
    actual_defined_per_source = {}
    for entry in sources:
        name, rel = entry.get("object"), entry.get("source")
        if (not isinstance(name, str) or
                not re.fullmatch(r"ios-kagura-dependency-\d{2}\.o", name) or
                name in closure_by_name or
                not isinstance(rel, str) or
                not re.fullmatch(r"runtime/[A-Za-z0-9_./-]+\.c", rel) or
                ".." in rel or rel == runtime_source or
                rel in source_paths or
                not re.fullmatch(r"[0-9a-f]{64}",
                                 entry.get("source_sha256", "")) or
                not re.fullmatch(r"[0-9a-f]{64}",
                                 entry.get("object_sha256", ""))):
            raise AssertionError("K11 invalid pinned runtime dependency source/object")
        obj = out / name
        if not obj.is_file() or sha(obj) != entry["object_sha256"]:
            raise AssertionError("K11 pinned runtime dependency object SHA mismatch")
        k10.k9.k8.verify_apple_arm64_object(obj.read_bytes())
        # Re-read the real iOS Mach-O symbol table; do not trust a status
        # flag or definitions copied into the JSON by the same build step.
        actual_defined = runtime_closure.defined_of(obj)
        declared = set(entry.get("defines", []))
        if not declared or not declared.issubset(actual_defined):
            raise AssertionError("K11 dependency object does not really define its claimed Kagura symbols")
        actual_defined_per_source[rel] = actual_defined
        closure_by_name[name] = entry
        source_paths.add(rel)
    if any(source not in source_paths for source in providers.values()):
        raise AssertionError("K11 unresolved provider not tied to real compiled source")
    if any(symbol not in actual_defined_per_source[source]
           for symbol, source in providers.items()):
        raise AssertionError("K11 provider symbol is not defined by claimed iOS object")
    inputs = [ci, out / "ios-probe.o", out / "ios-app-main.o",
              out / "ios-kagura-rtld.o"] + [
                  out / name for name in closure_by_name]
    if runtime_closure.required_symbols(inputs):
        raise AssertionError("K11 real iOS objects still have unresolved Kagura runtime symbols")
    listed_objects = (out / "ios-runtime-extra-objects.txt").read_text(
        encoding="utf-8").splitlines()
    if set(Path(s).name for s in listed_objects) != set(closure_by_name) or (
            len(listed_objects) != len(closure_by_name)):
        raise AssertionError("K11 linker dependency inputs differ from evidence")
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
        "ios_runtime_closure_sha256": sha(closure_file),
        "ios_runtime_initial_nm_raw_report_sha256": sha(nm_report_file),
        "ios_runtime_nm_source_format": closure["initial_nm_format"],
        "ios_runtime_resolved_symbols": dict(sorted(providers.items())),
        "ios_runtime_dependency_objects_sha256": {
            key: value["object_sha256"]
            for key, value in sorted(closure_by_name.items())},
        "ios_runtime_extra_objects": len(closure_by_name),
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
