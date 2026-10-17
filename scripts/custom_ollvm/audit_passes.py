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
        kagura.get("status") != "K1_NATIVE_7_STAGE_ARTIFACT_VERIFIED" or
        kagura.get("production_merge") is not False or
        kagura.get("vm_state") != "PRODUCTION_DISABLED_K6_K7_ISOLATED_VALIDATION_ONLY" or
        kagura.get("arm64e_pac_runtime") != "DEFERRED_NO_A12_DEVICE" or
        kagura.get("k1_native_ci_status") != "VERIFIED_FROM_USER_CI_ARTIFACT" or
        kagura.get("k2_scope_type") != "TRANSLATION_UNIT_ONLY_NOT_LLVM_FUNCTION_ALLOWLIST" or
        kagura.get("k2_scope_and_benchmark_status") != "MACOS_ARTIFACT_VERIFIED_HOST_ONLY" or
        kagura.get("k2_ios_device_runtime") != "NOT_TESTED"):
        raise AssertionError("Kagura must remain independent/experimental")
    if kagura.get("profile_file") != "scripts/custom_ollvm/kagura_max/profile.json" or (
        kagura.get("workflow") != ".github/workflows/kagura-max-candidate.yml"
    ) or kagura.get("passes") != [
        "kagura-str", "kagura-fla", "kagura-bcf", "kagura-sub", "kagura-co"
    ]:
        raise AssertionError("Experimental Kagura compiler-pipeline drift")
    if (kagura.get("k2_native_runner") !=
        "scripts/custom_ollvm/kagura_max/benchmark_audit.py" or
        not (root / kagura["k2_native_runner"]).is_file()):
        raise AssertionError("K2 benchmark scope must stay experimental")
    if (kagura.get("k3_interleaved_benchmark_runner") !=
        "scripts/custom_ollvm/kagura_max/interleaved_benchmark.py" or
        not (root / kagura["k3_interleaved_benchmark_runner"]).is_file() or
        kagura.get("k3_interleaved_benchmark_status") !=
        "STAGED_NOT_VERIFIED_MACOS_NATIVE" or
        kagura.get("k3_balanced_rounds") != 16 or
        kagura.get("k3_samples_per_variant") != 176):
        raise AssertionError("K3 benchmark cannot claim native or device PASS yet")
    if (kagura.get("ios_arm64_kagura_trollstore_pilot") !=
        "CI_ARTIFACT_HASHES_VERIFIED" or
        kagura.get("ios_arm64_kagura_pilot_workflow") !=
        ".github/workflows/kagura-max-candidate.yml" or
        kagura.get("ios_arm64_kagura_pilot_ipa") !=
        "KaguraLab-TrollStore-arm64.ipa" or
        kagura.get("ios_arm64_kagura_pilot_pipeline") !=
        ["str", "fla", "bcf", "sub", "co", "bbr", "bbs"] or
        kagura.get("ios_arm64_kagura_pilot_on_device") !=
        "USER_REPORTED_PASS_NO_SHARED_DEVICE_LOG" or
        kagura.get("k5_artifact_ipa_sha256") !=
        "7233235c60c9843c8e342c81f63dff326f2bdbfdfc39197db4d07d5c398d9ccd" or
        kagura.get("k5_artifact_review") !=
        "docs/KAGURA_K5_ARTIFACT_REVIEW.md" or
        kagura.get("k5_fast_workflow") !=
        ".github/workflows/kagura-ios-ipa.yml" or
        not (root / "docs/KAGURA_K5_ARTIFACT_REVIEW.md").is_file() or
        kagura.get("k6_selective_vm_status") !=
        "MACOS_CI_ARTIFACT_VERIFIED_HOST_ONLY" or
        kagura.get("k6_vm_workflow") !=
        ".github/workflows/kagura-vm-selective.yml" or
        kagura.get("k6_vm_target") != "dd_vm_protected" or
        kagura.get("k6_vm_device_runtime") != "NOT_TESTED" or
        kagura.get("k6_artifact_review") !=
        "docs/KAGURA_K6_ARTIFACT_REVIEW.md" or
        kagura.get("k6_vm_native_parity_vectors") != 4096 or
        kagura.get("k6_vm_macos_median_paired_overhead_ratio") != 48.0 or
        kagura.get("k7_vm_trollstore_ipa_status") !=
        "CI_ARTIFACT_HASHES_VERIFIED" or
        kagura.get("k7_vm_ipa_workflow") !=
        ".github/workflows/kagura-vm-ios-ipa.yml" or
        kagura.get("k7_vm_ipa_name") !=
        "KaguraVMLab-TrollStore-arm64.ipa" or
        kagura.get("k7_vm_bundle_id") !=
        "com.duodash.research.kaguravmlab" or
        kagura.get("k7_vm_on_device") !=
        "USER_SHARED_TEXT_PARITY_AND_PERF_VALIDATED_NOT_ATTESTED" or
        kagura.get("k7_shared_device_log_status") !=
        "VALIDATED_EXACT_SCHEMA_UUID_CHECKSUM_VS_CI" or
        kagura.get("k7_prior_pasted_log_status") !=
        "REJECTED_MALFORMED_TRANSPORT_TEXT" or
        kagura.get("k7_device_benchmark_status") !=
        "USER_SHARED_THREE_PAIRS_OBSERVATIONAL" or
        kagura.get("k7_device_median_paired_overhead_ratio") != 71.5 or
        kagura.get("k7_device_plain_samples_ns") != [46, 32, 30] or
        kagura.get("k7_device_vm_samples_ns") != [3742, 1918, 2145] or
        kagura.get("k7_device_log_sha256") !=
        "355ecf8be195c9c925ce8d56fe1b78dd63f9e1dc2aa7f543d67d4bfbfefbc763" or
        kagura.get("k7_device_log_review") !=
        "docs/KAGURA_K7_DEVICE_LOG_REVIEW.md" or
        not (root / "docs/KAGURA_K7_DEVICE_LOG_REVIEW.md").is_file() or
        kagura.get("k7_artifact_review") !=
        "docs/KAGURA_K7_ARTIFACT_REVIEW.md" or
        kagura.get("k7_artifact_zip_sha256") !=
        "fdaed5005fd5b3ccefa5bd9db1bcb12cc27a411c586c0afc144ac1d42e5f5a9f" or
        kagura.get("k7_ipa_sha256") !=
        "ab5a6d21bd676e06585e95f61f9295207c55679a89502d8f2198df6dc605f6e5" or
        kagura.get("k7_app_binary_sha256") !=
        "03d5aa93901cb03b5ffe7f8c3e754ee4bd21b13bb353bfb832d75e43bb40904d" or
        kagura.get("k7_app_macho_uuid") !=
        "15a45d46-f0da-37ff-855d-5e6ea078be8e" or
        kagura.get("k7_macos_median_paired_overhead_ratio") != 47.0 or
        not (root / "docs/KAGURA_K7_ARTIFACT_REVIEW.md").is_file() or
        not (root / "docs/KAGURA_K6_ARTIFACT_REVIEW.md").is_file() or
        not (root / "docs/KAGURA_K7_VM_TROLLSTORE.md").is_file() or
        not (root / ".github/workflows/kagura-vm-ios-ipa.yml").is_file() or
        not (root / "scripts/custom_ollvm/kagura_vm/package_ipa.py").is_file() or
        not (root / ".github/workflows/kagura-vm-selective.yml").is_file() or
        not (root / "scripts/custom_ollvm/kagura_vm/vm_canary.c").is_file() or
        not (root / "scripts/custom_ollvm/kagura_max/ios_app_main.m").is_file() or
        not (root / "scripts/custom_ollvm/kagura_max/ios_canary.c").is_file() or
        not (root / "scripts/custom_ollvm/kagura_max/package_ipa.py").is_file()):
        raise AssertionError("Kagura K5 artifact/K6 separate VM scope evidence drift")
    if (kagura.get("k8_five_pass_status") !=
        "MACOS_CI_ARTIFACT_VERIFIED_ISOLATED_FIVE_PASS" or
        kagura.get("k8_artifact_zip_sha256") !=
        "a1bc3b5bf0057e082ff4109c93925e39758f7fd861fb336d3655ffe4c6049dea" or
        kagura.get("k8_artifact_entry_count") != 74 or
        kagura.get("k8_independent_artifact_checks_passed") != 92 or
        kagura.get("k8_native_parity_status") !=
        "FIVE_ISOLATED_4096_VECTORS_PASS" or
        kagura.get("k8_native_c_fixture_checksum") !=
        "25a3318e3d7d6525" or
        kagura.get("k8_native_mvo_fixture_checksum") !=
        "64e61045bbc4a250" or
        kagura.get("k8_source_fixture_sha256") !=
        "39e0b833ab8574bf2e8abb2a66dc440d06424a82d6a0f371297e313bc91992fc" or
        kagura.get("k8_source_runner_sha256") !=
        "4c1929802af256c6a7130e8f010e26f517f887a5b8dcbaad53434c6eb5bc2d6e" or
        kagura.get("k8_source_mvo_ir_sha256") !=
        "abbe02b364571b77fb94fff673111bf381f694211cca148d18a73650a8343e50" or
        kagura.get("k8_artifact_review") !=
        "docs/KAGURA_K8_ARTIFACT_REVIEW.md" or
        kagura.get("k8_five_passes") !=
        ["ibr", "mvo", "genc", "fsplit", "ci"] or
        kagura.get("k8_pass_kinds") != {
            "ibr": "function", "mvo": "function", "genc": "module",
            "fsplit": "module", "ci": "module"
        } or
        kagura.get("k8_native_parity_vectors_per_pass") != 4096 or
        kagura.get("k8_workflow") !=
        ".github/workflows/kagura-k8-pass-coverage.yml" or
        kagura.get("k8_runner") !=
        "scripts/custom_ollvm/kagura_k8/pilot.py" or
        kagura.get("k8_report") != "Kagura-K8-PASS-REPORT.json" or
        kagura.get("k8_ios_arm64") != "BUILD_ONLY_NOT_EXECUTED" or
        kagura.get("k8_combined_five_passes") !=
        "NOT_TESTED_AFTER_ISOLATED_MACOS_NATIVE_VERIFIED" or
        kagura.get("k8_review_doc") !=
        "docs/KAGURA_K8_FIVE_PASS_VALIDATION.md" or
        not (root / kagura["k8_runner"]).is_file() or
        not (root / kagura["k8_workflow"]).is_file() or
        not (root / kagura["k8_review_doc"]).is_file() or
        not (root / "scripts/custom_ollvm/kagura_k8/fixture.c").is_file() or
        not (root / "scripts/custom_ollvm/kagura_k8/runner.c").is_file() or
        not (root / "scripts/custom_ollvm/kagura_k8/mvo.ll").is_file() or
        not (root / "scripts/test_kagura_k8_passes.py").is_file() or
        not (root / kagura["k8_artifact_review"]).is_file()):
        raise AssertionError("K8 isolated CI evidence incorrectly claimed or missing")
    # Pin all source bytes used by the *actual user-provided* CI artifact.
    # These are verified source identities, not a new native execution.
    for source, digest_key in (
        ("scripts/custom_ollvm/kagura_k8/fixture.c", "k8_source_fixture_sha256"),
        ("scripts/custom_ollvm/kagura_k8/runner.c", "k8_source_runner_sha256"),
        ("scripts/custom_ollvm/kagura_k8/mvo.ll", "k8_source_mvo_ir_sha256"),
    ):
        if hashlib.sha256((root / source).read_bytes()).hexdigest() != kagura[digest_key]:
            raise AssertionError("K8 pinned CI source no longer matches verified artifact")
    if (kagura.get("k1_stepwise_runner") !=
        "scripts/custom_ollvm/kagura_max/stage_pipeline.py" or
        kagura.get("k1_extra_passes") != ["kagura-bbr", "kagura-bbs"] or
        not (root / kagura["k1_stepwise_runner"]).is_file()):
        raise AssertionError("K1 separate stepwise runner/CFG pass inventory drift")
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
