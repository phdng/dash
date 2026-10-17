#!/usr/bin/env python3
"""Fail-closed inventory of *actual LLVM compiler passes* in DuoDash.

A source-level "protected" C example is not an LLVM pass. A standalone
Hikari pass is not automatically part of the pinned custom Obfuscator.
This audits source policies and existing CI paths, not native LLVM execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = Path(__file__).with_name("pass_registry.json")
CURRENT = ("split", "bcf", "fla", "sub")
ROOT_KEYS = ("enable_split", "split_n", "enable_bcf", "bcf_prob", "bcf_times",
             "enable_fla", "enable_sub", "sub_times")


def audit(registry: dict, root: Path = ROOT) -> dict:
    if registry.get("schema") != 1 or registry.get("compiler") != "LLVM 19":
        raise AssertionError("Unknown LLVM pass inventory schema/compiler")
    if registry.get("production_pass_families") != list(CURRENT):
        raise AssertionError("Production pass inventory must agree with verifier")
    if registry.get("production_cpu_scope") != "arm64" or (
        "Apple Clang" not in registry.get("arm64e_production_route", "")
    ):
        raise AssertionError("arm64e must not be claimed to run LLVM19 Obfuscator")
    if registry.get("pinned_commit") != "592f215f852e3957da01b2b15024dc63713a462e":
        raise AssertionError("Custom OLLVM plugin SHA changed unexpectedly")

    policy = json.loads((root / registry["production_policy"]).read_text(encoding="utf-8"))
    demo = json.loads((root / registry["demo_policy"]).read_text(encoding="utf-8"))
    for name, document in (("production", policy), ("demo", demo)):
        if set(document) != {"policy_map", "policies"} or not document["policies"]:
            raise AssertionError(f"{name} policy schema invalid")
        for label, profile in document["policy_map"].items():
            if set(profile) != set(ROOT_KEYS):
                raise AssertionError(f"{name}/{label} has unknown/missing OLLVM keys")
            if profile["enable_fla"] is not True:
                raise AssertionError("Known policies must keep current FLA enabled")
        if any(rule["policy"] not in document["policy_map"]
               for rule in document["policies"]):
            raise AssertionError("Unknown pass policy referenced")

    expected_demo = {
        "enable_split": True, "split_n": 4,
        "enable_bcf": True, "bcf_prob": 100, "bcf_times": 2,
        "enable_fla": True, "enable_sub": True, "sub_times": 3,
    }
    if demo["policy_map"].get("credits_ui_strong_eval") != expected_demo:
        raise AssertionError("STRONG demo policy changed unexpectedly")
    strong = policy["policy_map"].get("full_strength_eval")
    if strong != expected_demo:
        raise AssertionError("Production STRONG evaluation flags drifted")
    expected_coverage = {
        "enable_split": True, "split_n": 2,
        "enable_bcf": True, "bcf_prob": 30, "bcf_times": 1,
        "enable_fla": True, "enable_sub": True, "sub_times": 1,
    }
    if policy["policy_map"].get("existing_coverage") != expected_coverage:
        raise AssertionError("Production existing coverage flags drifted")
    if (root / "scripts/verify_ollvm_log.py").read_text(encoding="utf-8").find(
        'PASSES = ("split", "bcf", "fla", "sub")'
    ) < 0:
        raise AssertionError("Production checker does not verify four known passes")
    if (root / "scripts/demo_ollvm/verify.py").read_text(encoding="utf-8").find(
        'PASSES = ("split", "bcf", "fla", "sub")'
    ) < 0:
        raise AssertionError("Demo checker does not verify four known passes")

    selector = (root / "scripts/demo_ollvm/compiler_select.py").read_text(encoding="utf-8")
    if not all(x in selector for x in (
        'if arch == "arm64e":', "return [apple, *arguments]",
        '"-O1"', '"-fpass-plugin={plugin}"'
    )):
        # plugin flag must remain string interpolation, never enabled on arm64e
        if not all(x in selector for x in (
            'if arch == "arm64e":', "return [apple, *arguments]",
            '"-O1"', 'f"-fpass-plugin={plugin}"'
        )):
            raise AssertionError("LLVM19 arm64e bypass/arm64 select contract drift")
    build = (root / ".github/workflows/build.yml").read_text(encoding="utf-8")
    demo_ci = (root / ".github/workflows/demo-ollvm-evaluation.yml").read_text(encoding="utf-8")
    hikari_ci = (root / ".github/workflows/hikari-evaluation.yml").read_text(encoding="utf-8")
    for wf in (build, demo_ci, hikari_ci):
        if registry["pinned_commit"] not in wf:
            raise AssertionError("Unpinned/different LLVM plugin commit")
    if "-fpass-plugin=" not in build or "hikari" in build.lower():
        raise AssertionError("Reconstruction production flow unexpectedly changed to Hikari")
    if "workflow_dispatch:" not in demo_ci or "workflow_dispatch:" not in hikari_ci:
        raise AssertionError("Experimental evaluation must be manual-only")

    expected_hikari = {"strcry", "constenc"}
    declared_hikari = registry.get("separate_llvm_plugin_experiments", [])
    if set(entry["pass"] for entry in declared_hikari) != expected_hikari:
        raise AssertionError("Hikari pass pilot inventory inconsistent")
    hpol = json.loads((root / "scripts/hikari_eval/policy.json").read_text(encoding="utf-8"))
    hkeys = {key for value in hpol["policy_map"].values() for key in value}
    if not {"enable-strcry", "enable-constenc"}.issubset(hkeys):
        raise AssertionError("Hikari policy lacks LLVM pass toggles")
    for entry in declared_hikari:
        if (entry.get("provider") != "Hikari" or entry.get("plugin") != "hikari" or
            entry.get("state") != "experimental_separate_plugin"):
            raise AssertionError("Hikari must not claim to be merged into OLLVM")

    sources = registry.get("source_level_only", [])
    if set(x["technique"] for x in sources) != {
        "CE", "ICALL", "IGV", "IBR", "VM", "ObjC_CE"
    }:
        raise AssertionError("Incomplete standalone Protection Lab inventory")
    for entry in sources:
        expected = ("bytecode_interpreter_not_llvm_pass" if entry["technique"] == "VM"
                    else "source_canary_not_llvm_pass")
        if entry["status"] != expected or not (root / entry["path"]).is_file():
            raise AssertionError("Source canary wrongly promoted to LLVM pass")

    kagura = registry.get("experimental_kagura_pipeline", {})
    if (kagura.get("provider") != "qusamulab/kagura" or
        kagura.get("profile") != "MAX_CANDIDATE" or
        kagura.get("status") != "STAGED_CI_NOT_VERIFIED" or
        kagura.get("production_merge") is not False or
        kagura.get("vm_state") != "DISABLED_PENDING_SEPARATE_OVERHEAD_AND_ABI_TEST" or
        kagura.get("arm64e_pac_runtime") != "DEFERRED_NO_A12_DEVICE"):
        raise AssertionError("Kagura must remain independent/experimental")
    if kagura.get("profile_file") != "scripts/custom_ollvm/kagura_max/profile.json" or (
        kagura.get("workflow") != ".github/workflows/kagura-max-candidate.yml"
    ) or kagura.get("passes") != [
        "kagura-str", "kagura-fla", "kagura-bcf", "kagura-sub", "kagura-co"
    ]:
        raise AssertionError("Experimental Kagura compiler-pipeline drift")
    if not (root / kagura["profile_file"]).is_file() or not (
        root / kagura["workflow"]
    ).is_file():
        raise AssertionError("Kagura experiment requires real sources/CI")
    profile = json.loads((root / kagura["profile_file"]).read_text(encoding="utf-8"))
    if profile.get("stages") != kagura["passes"] or (
        profile.get("llvm_major") != 19
    ):
        raise AssertionError("Kagura staged LLVM19 profile and registry disagree")

    next_passes = registry.get("next_llvm_pass_candidates", [])
    if [item["priority"] for item in next_passes] != list(range(1, 7)):
        raise AssertionError("New compiler pass trial priorities must remain unique")
    if set(item["pass"] for item in next_passes) != {
        "string_ce", "constant_encoding", "indirect_branch",
        "indirect_call", "global_indirection", "virtualization"
    }:
        raise AssertionError("Missing/unknown new compiler-pass candidate")
    if any(item["state"] != "not_implemented_in_custom_obfuscator" or
           not item["prerequisites"] or not item["risk"] for item in next_passes):
        raise AssertionError("Unimplemented features must not masquerade as compiler pass")

    return {
        "schema": 1,
        "existing_actual_llvm_passes": list(CURRENT),
        "production_enabled_count": len(CURRENT),
        "separate_hikari_llvm_passes_not_in_obfuscator": sorted(expected_hikari),
        "source_level_pilots_not_llvm_passes": [x["technique"] for x in sources],
        "separate_kagura_llvm_pipeline": kagura["status"],
        "planned_new_llvm_passes_not_implemented": [x["pass"] for x in next_passes],
        "production_cpu_scope": "arm64",
        "arm64e_production_llvm_passes": [],
        "user_reported_arm64_lab_runtime": "PASS_SEPARATE_APPLICATION_NOT_COMPILER_PROOF",
        "compiler_native_new_pass_build_verified_this_run": False,
        "custom_ollvm_strong_modified": False,
        "registry_sha256": hashlib.sha256(
            json.dumps(registry, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = audit(json.loads(args.registry.read_text(encoding="utf-8")))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
    print("CUSTOM_OLLVM_PASS_AUDIT_PASS: 4 OLLVM actual, 2 separate Hikari, "
          "6 source-level only, 6 candidate LLVM passes NOT integrated")


if __name__ == "__main__":
    main()
