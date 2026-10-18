#!/usr/bin/env python3
"""K15 portable, independently replayed file-backed BBCheck discovery report.

Only source/IR/object/provider inventories can PASS. Runtime tamper callback
MUST NOT run and neither native parity nor IPA/device are proven.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from pilot import (
    ROOT, PIN, PASS_NAME, PASS_CLASS, PIPELINE, REGISTRY_SHA, REQUIRED,
    sha, normalized_ir_sha, entry_from_registry, validate_pass,
    macho_arm64_object, parse_nm, parse_undefined_names, summarize_providers,
)

SCOPE = "K15_BBCHECK_PINNED_LLVM19_DEPENDENCY_DISCOVERY_NO_NATIVE_EXECUTION"
ZERO = {"native_4096_parity": "NOT_TESTED_GUARD_HAS_TAMPER_CALLBACK",
        "ios_ipa_built": False, "ios_device_executed": False,
        "arm64e_pac_tested": False, "crane_production_modified": False,
        "security_strength_claim": False}


def require_hash(out: Path, name: str, expected: str) -> Path:
    p = out / name
    if (not p.is_file() or p.is_symlink() or not isinstance(expected, str) or
            not re.fullmatch(r"[a-f0-9]{64}", expected) or
            sha(p) != expected):
        raise AssertionError("K15 raw file missing or SHA mismatch: " + name)
    return p


def verify(out: Path) -> dict:
    report_path = out / "Kagura-K15-REPORT.json"
    if not report_path.is_file():
        raise AssertionError("K15 actual discovery report missing")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    pin = out / "pinned-registry.def"
    src = require_hash(out, "pinned-registry.def", REGISTRY_SHA)
    entry = entry_from_registry(src.read_text(encoding="utf-8"))
    require_hash(out, "pinned-LICENSE", report.get("license_sha256"))
    fixture = ROOT / "scripts/custom_ollvm/kagura_k8/fixture.c"
    if (not fixture.is_file() or
            report.get("source_fixture_sha256") != sha(fixture) or
            report.get("schema") != 1 or
            report.get("scope") != SCOPE or report.get("pin") != PIN or
            report.get("registry_sha256") != REGISTRY_SHA or
            report.get("pass") != PASS_NAME or
            report.get("pass_kind") != entry["kind"] or
            report.get("pass_flag") != entry["enable_flag"] or
            report.get("actual_pass_class") != PASS_CLASS or
            report.get("pipeline") != PIPELINE or
            report.get("required_bbcheck_runtime_symbols") != list(REQUIRED) or
            set(report.get("targets", {})) != {"macos", "ios"} or
            any(report.get(k) != v for k, v in ZERO.items())):
        raise AssertionError("K15 pass or scope report inflated/malformed")
    source_items = {}
    for target in ("macos", "ios"):
        info = report["targets"][target]
        stage = {
            "baseline_bc_sha256": f"{target}-baseline.bc",
            "protected_bc_sha256": f"{target}-bbcheck.bc",
            "baseline_ir_sha256": f"{target}-baseline.ll",
            "protected_ir_sha256": f"{target}-bbcheck.ll",
            "baseline_object_sha256": f"{target}-baseline.o",
            "protected_object_sha256": f"{target}-bbcheck.o",
            "pass_manager_log_sha256": f"{target}-pass-manager.log",
            "bbcheck_nm_defined_sha256": f"{target}-bbcheck-defined-nm.log",
            "bbcheck_nm_undefined_sha256": f"{target}-bbcheck-undefined-nm.log",
        }
        paths = {key: require_hash(out, name, info.get(key))
                 for key, name in stage.items()}
        before = paths["baseline_ir_sha256"]
        after = paths["protected_ir_sha256"]
        if (info.get("normalized_baseline_ir_sha256") != normalized_ir_sha(before) or
                info.get("normalized_protected_ir_sha256") != normalized_ir_sha(after) or
                normalized_ir_sha(before) == normalized_ir_sha(after) or
                sha(paths["baseline_object_sha256"]) ==
                sha(paths["protected_object_sha256"]) or
                info.get("pass_ir_object_delta") is not True or
                info.get("real_pass_class") != PASS_CLASS or
                info.get("native_checksum") != "NOT_TESTED" or
                info.get("iphone_runtime") != "NOT_TESTED"):
            raise AssertionError("K15 no actual IR/object delta or inflated status")
        validate_pass(paths["pass_manager_log_sha256"].read_text(encoding="utf-8"),
                      before.read_text(encoding="utf-8"),
                      after.read_text(encoding="utf-8"))
        if target == "ios":
            macho_arm64_object(paths["baseline_object_sha256"].read_bytes())
            macho_arm64_object(paths["protected_object_sha256"].read_bytes())
        defined = parse_nm(
            paths["bbcheck_nm_defined_sha256"].read_text(encoding="utf-8"), defined=True)
        undefined = parse_undefined_names(
            paths["bbcheck_nm_undefined_sha256"].read_text(encoding="utf-8"))
        if ("_dd_k8_evaluate" not in defined or
                not set(REQUIRED).issubset(undefined) or
                info.get("actual_undefined_kagura_symbols") !=
                sorted(x for x in undefined if x.startswith("_kagura_"))):
            raise AssertionError("K15 BBCheck Mach-O import/ABI evidence mismatch")

        pinfo = info.get("providers")
        if (not isinstance(pinfo, dict) or
                pinfo.get("native_execution_attempted") is not False or
                pinfo.get("ios_ipa_link_attempted") is not False or
                not isinstance(pinfo.get("candidate_sources"), list)):
            raise AssertionError("K15 provider status implies runtime execution")
        rows = pinfo["candidate_sources"]
        if len(rows) != report.get("mentioned_source_count"):
            raise AssertionError("K15 candidate count differs between targets")
        source_list = []
        for index, row in enumerate(rows, 1):
            if (not isinstance(row, dict) or
                    not isinstance(row.get("source"), str) or
                    not row["source"].startswith("runtime/") or
                    ".." in Path(row["source"]).parts or
                    row.get("archived_source") != f"k15-runtime-source-{index:02d}.c" or
                    not isinstance(row.get("mentions_required"), list) or
                    not row["mentions_required"] or
                    not set(row["mentions_required"]).issubset(set(REQUIRED))):
                raise AssertionError("K15 pinned C source provenance corrupted")
            src_file = require_hash(out, row["archived_source"],
                                    row.get("source_sha256"))
            source_text = src_file.read_text(encoding="utf-8")
            mentioned = [name for name in REQUIRED if re.search(
                r"\b" + re.escape(name.lstrip("_")) + r"\b", source_text)]
            if row["mentions_required"] != mentioned:
                raise AssertionError("K15 archived source did not actually mention symbol")
            source_list.append((row["source"], row["source_sha256"]))
            compile_log = f"{target}-runtime-candidate-{index:02d}-compile.log"
            require_hash(out, compile_log, row.get("compile_log_sha256"))
            if row.get("compile_log") != compile_log:
                raise AssertionError("K15 candidate compile log changed")
            if row.get("compile_success") is True:
                obj_name = f"{target}-runtime-candidate-{index:02d}.o"
                obj = require_hash(out, obj_name, row.get("object_sha256"))
                if row.get("object") != obj_name:
                    raise AssertionError("K15 provider candidate object name changed")
                if target == "ios":
                    macho_arm64_object(obj.read_bytes())
                def_nm = require_hash(
                    out, f"{target}-runtime-candidate-{index:02d}-defined-nm.log",
                    row.get("defined_nm_sha256"))
                und_nm = require_hash(
                    out, f"{target}-runtime-candidate-{index:02d}-undefined-nm.log",
                    row.get("undefined_nm_sha256"))
                actual_def = sorted(s for s in parse_nm(
                    def_nm.read_text(encoding="utf-8"), defined=True)
                    if s.startswith("_kagura_"))
                actual_und = sorted(s for s in parse_undefined_names(
                    und_nm.read_text(encoding="utf-8")) if s.startswith("_kagura_"))
                if (row.get("actual_defined_kagura_symbols") != actual_def or
                        row.get("actual_undefined_kagura_symbols") != actual_und):
                    raise AssertionError("K15 provider nm actual symbols do not match source report")
            elif row.get("compile_success") is False:
                if (row.get("object") is not None or
                        row.get("object_sha256") is not None or
                        row.get("defined_nm_sha256") is not None or
                        row.get("undefined_nm_sha256") is not None or
                        row.get("actual_defined_kagura_symbols") != [] or
                        row.get("actual_undefined_kagura_symbols") != []):
                    raise AssertionError("K15 failed provider compilation recorded false symbols")
            else:
                raise AssertionError("K15 invalid compile status")
        if target == "macos":
            source_items = source_list
        elif source_items != source_list:
            raise AssertionError("K15 macOS and iOS sources differ")
        if any(pinfo.get(k) != v for k, v in
               summarize_providers(rows).items()):
            raise AssertionError("K15 provider classification altered from nm evidence")
    print("K15_BBCHECK_FILE_BACKED_DISCOVERY_AUDIT_PASS:"
          " genuine BBCheck IR/object imported both guards;"
          " pinned runtime providers classified; NO native/device/PAC/Crane")
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True, type=Path)
    verify(p.parse_args().out)


if __name__ == "__main__":
    main()
