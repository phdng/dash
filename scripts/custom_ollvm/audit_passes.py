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
        "K9_FIVE_COMPOSED_STAGES_MACOS_ARTIFACT_VERIFIED" or
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
    if (kagura.get("k9_composition_status") !=
        "MACOS_CI_ARTIFACT_VERIFIED_FIVE_COMPOSED_STAGES" or
        kagura.get("k9_artifact_zip_sha256") !=
        "9925f6ae0f95f2ec52ae53e7416723cd134de2e2e6fafc2ce6a3b58db5f96cf5" or
        kagura.get("k9_artifact_entry_count") != 75 or
        kagura.get("k9_independent_artifact_checks_passed") != 179 or
        kagura.get("k9_artifact_review") !=
        "docs/KAGURA_K9_ARTIFACT_REVIEW.md" or
        kagura.get("k9_runner_sha256") !=
        "b10fafa96bbe4e23aea2a5460fce86db8244a8b9a81314f2abe608b17e6afefc" or
        kagura.get("k9_llvm_link_warnings") !=
        "NONFATAL_MVO_DATALAYOUT_AND_HOST_TRIPLE_MISMATCH" or
        kagura.get("k9_workflow") !=
        ".github/workflows/kagura-k9-composition.yml" or
        kagura.get("k9_runner") !=
        "scripts/custom_ollvm/kagura_k9/pilot.py" or
        kagura.get("k9_portable_test") !=
        "scripts/test_kagura_k9_composition.py" or
        kagura.get("k9_doc") !=
        "docs/KAGURA_K9_COMPOSITION.md" or
        kagura.get("k9_stage_order") !=
        ["mvo", "genc", "fsplit", "ibr", "ci"] or
        kagura.get("k9_merged_function_names") !=
        ["dd_k8_evaluate", "dd_k9_mvo_probe"] or
        kagura.get("k9_native_vectors_per_function") != 4096 or
        kagura.get("k9_c_checksum") != "25a3318e3d7d6525" or
        kagura.get("k9_mvo_checksum") != "64e61045bbc4a250" or
        kagura.get("k9_ios_arm64") !=
        "OBJECT_BUILD_ONLY_NOT_EXECUTED" or
        kagura.get("k9_composition_native") !=
        "MACOS_NATIVE_FIVE_STAGES_TWO_FUNCTION_4096_PARITY_VERIFIED" or
        kagura.get("k9_performance") != "NOT_EVALUATED" or
        any(not (root / kagura[path_key]).is_file()
            for path_key in (
                "k9_workflow", "k9_runner", "k9_portable_test", "k9_doc",
                "k9_artifact_review"
            )) or
        not (root / "scripts/custom_ollvm/kagura_k9/runner.c").is_file()):
        raise AssertionError(
            "K9 five-pass composed artifact provenance or scope invalid")
    if hashlib.sha256(
            (root / "scripts/custom_ollvm/kagura_k9/runner.c").read_bytes()
    ).hexdigest() != kagura["k9_runner_sha256"]:
        raise AssertionError("K9 native CI runner no longer matches verified artifact")
    if (kagura.get("k10_strict_link_metadata_status") !=
        "MACOS_CI_ARTIFACT_VERIFIED_STRICT_LLVM_METADATA" or
        kagura.get("k10_artifact_zip_sha256") !=
        "3567fca73c11aaea0b30e50ca8eb9cda6491ff32cb7832893ffd104725f59383" or
        kagura.get("k10_artifact_entry_count") != 80 or
        kagura.get("k10_independent_artifact_checks_passed") != 277 or
        kagura.get("k10_artifact_review") !=
        "docs/KAGURA_K10_ARTIFACT_REVIEW.md" or
        kagura.get("k10_host_target_triple") !=
        "arm64-apple-macosx14.0.0" or
        kagura.get("k10_ios_target_triple") !=
        "arm64-apple-ios15.0.0" or
        kagura.get("k10_both_target_datalayout") !=
        "e-m:o-i64:64-i128:128-n32:64-S128-Fn32" or
        kagura.get("k10_actual_llvm_link_warning_count") != 0 or
        kagura.get("k10_workflow") !=
        ".github/workflows/kagura-k10-link-metadata.yml" or
        kagura.get("k10_runner") !=
        "scripts/custom_ollvm/kagura_k10/pilot.py" or
        kagura.get("k10_test") !=
        "scripts/test_kagura_k10_link_metadata.py" or
        kagura.get("k10_doc") !=
        "docs/KAGURA_K10_LINK_METADATA.md" or
        kagura.get("k10_pinned_mvo_template_sha256") !=
        kagura["k8_source_mvo_ir_sha256"] or
        kagura.get("k10_stage_order") !=
        ["mvo", "genc", "fsplit", "ibr", "ci"] or
        kagura.get("k10_required_link_warning_count") != 0 or
        kagura.get("k10_required_metadata_source") !=
        "CLANG19_COMPILED_C_BITCODE_BOTH_TARGETS" or
        kagura.get("k10_host_two_function_vectors") != 4096 or
        kagura.get("k10_ios_arm64") !=
        "OBJECT_BUILD_ONLY_NOT_EXECUTED" or
        kagura.get("k10_on_device") != "NOT_TESTED" or
        kagura.get("k10_composition_native") !=
        "MACOS_NATIVE_FIVE_COMPOSED_STAGES_ZERO_LINK_WARNINGS_VERIFIED" or
        any(not (root / kagura[field]).is_file() for field in
            ("k10_workflow", "k10_runner", "k10_test", "k10_doc",
             "k10_artifact_review"))):
        raise AssertionError(
            "K10 strict LLVM-link artifact provenance or scope invalid")
    if (kagura.get("k11_ios_ipa_status") !=
        "CI_ARTIFACT_HASHES_VERIFIED_IOS_ARM64_FIVE_PASS_LAB" or
        kagura.get("k11_artifact_zip_sha256") !=
        "e004ea806724659afc9c7fe77efdfe954e8083e1fef10fd75275992405ad45a9" or
        kagura.get("k11_artifact_entry_count") != 119 or
        kagura.get("k11_independent_artifact_checks_passed") != 331 or
        kagura.get("k11_artifact_review") !=
        "docs/KAGURA_K11_ARTIFACT_AND_DEVICE_REVIEW.md" or
        kagura.get("k11_ipa_sha256") !=
        "57fe287ee04503c9bf5b64e8f7ed2589ec0b22a5c80fdcb035855b8781fa31d4" or
        kagura.get("k11_app_binary_sha256") !=
        "a6b01f4df5c1128e2e8f24f13cde786557b354fd9c07b8ed6a8c8a5103899692" or
        kagura.get("k11_app_macho_uuid") !=
        "580390ef-6ba0-357c-a1d7-a0678e3d27ff" or
        kagura.get("k11_final_ios_object_sha256") !=
        "087ad94d637a8e4ac4f58b878517069fa755750088ef4fdcabd7436f4b86c682" or
        kagura.get("k11_runtime_dependency_source") !=
        "runtime/core/imagelist.c" or
        kagura.get("k11_runtime_dependency_object_sha256") !=
        "d026148dac9995954c61160d5864e94176e3eb712f4b027cb26a7c4d2b582530" or
        kagura.get("k11_workflow") !=
        ".github/workflows/kagura-k11-ios-ipa.yml" or
        kagura.get("k11_build") !=
        "scripts/custom_ollvm/kagura_k11/build_ipa.sh" or
        kagura.get("k11_runtime_locator") !=
        "scripts/custom_ollvm/kagura_k11/ci_runtime_resolver.py" or
        kagura.get("k11_packager") !=
        "scripts/custom_ollvm/kagura_k11/package_ipa.py" or
        kagura.get("k11_evidence") !=
        "scripts/custom_ollvm/kagura_k11/ipa_evidence.py" or
        kagura.get("k11_device_audit") !=
        "scripts/custom_ollvm/kagura_k11/device_log_audit.py" or
        kagura.get("k11_portable_test") !=
        "scripts/test_kagura_k11_ios_ipa.py" or
        kagura.get("k11_doc") != "docs/KAGURA_K11_IOS_IPA_LAB.md" or
        kagura.get("k11_bundle_id") !=
        "com.duodash.research.kagurafivelab" or
        kagura.get("k11_ipa_name") !=
        "KaguraFiveLab-TrollStore-arm64.ipa" or
        kagura.get("k11_pinned_upstream_commit") !=
        "ac2136ee0408677cf7cdee55307e9b16edd5f4d5" or
        kagura.get("k11_final_pass_order") !=
        ["mvo", "genc", "fsplit", "ibr", "ci"] or
        kagura.get("k11_expected_c_checksum") !=
        "25a3318e3d7d6525" or
        kagura.get("k11_expected_mvo_checksum") !=
        "64e61045bbc4a250" or
        kagura.get("k11_vectors_per_function") != 4096 or
        kagura.get("k11_upstream_ios_ci_runtime") !=
        "PINNED_C_SOURCE_CROSS_COMPILED_FAIL_CLOSED" or
        kagura.get("k11_ios_runtime_dependency_closure") !=
        "RECURSIVE_REAL_PINNED_C_IOS_ARM64_NM_DEFINITIONS_NO_SHIMS" or
        kagura.get("k11_runtime_closure_script") !=
        "scripts/custom_ollvm/kagura_k11/ci_runtime_closure.py" or
        kagura.get("k11_last_observed_ci_failure") !=
        "IOS_ARM64_NM_J_REJECTED_OBJC_SELECTOR_COLON" or
        kagura.get("k11_macho_arch") !=
        "arm64_SUBTYPE0_MH_EXECUTE_LC_UUID" or
        kagura.get("k11_device_runtime") !=
        "USER_SHARED_TEXT_PARITY_AND_UUID_VALIDATED_NOT_ATTESTED" or
        kagura.get("k11_shared_device_log_status") !=
        "VALIDATED_EXACT_NINE_LINE_UUID_CHECKSUM_VS_CI_IPA" or
        kagura.get("k11_device_log_sha256") !=
        "b61d53c870a7553564a85eb769bcbcb6717b714590fa9ef691738e618b38987b" or
        kagura.get("k11_device_log_review") !=
        "docs/KAGURA_K11_ARTIFACT_AND_DEVICE_REVIEW.md" or
        kagura.get("k11_arm64e_pac") != "NOT_TESTED" or
        kagura.get("k11_security_attestation") is not False or
        any(not (root / kagura[field]).is_file() for field in
            ("k11_workflow", "k11_build", "k11_runtime_locator",
             "k11_runtime_closure_script", "k11_packager", "k11_evidence",
             "k11_device_audit", "k11_portable_test", "k11_doc",
             "k11_artifact_review", "k11_device_log_review")) or
        any(not (root / "scripts/custom_ollvm/kagura_k11" / name).is_file()
            for name in ("ios_probe.c", "ios_app_main.m", "Info.plist"))):
        raise AssertionError(
            "K11 standalone five-pass IPA artifact+user-shared device text"
            " provenance invalid; no cryptographic device attestation,"
            " PAC or Crane production claim")
    if (kagura.get("k12_status") !=
        "PINNED_REGISTRY_AND_OPT_ARTIFACT_REPLAY_VERIFIED_NOT_NATIVE" or
        kagura.get("k12_artifact_review") != "docs/KAGURA_K12_ARTIFACT_REVIEW.md" or
        kagura.get("k12_artifact_zip_sha256") !=
        "6d827807db583c8581d218da2dfc41f7fe784ea607dddd83edd399a04718b0ca" or
        kagura.get("k12_artifact_zip_entry_count") != 147 or
        kagura.get("k12_artifact_file_backed_checks") != 2029 or
        kagura.get("k12_pinned_registry_source_sha256") !=
        "6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa" or
        kagura.get("k12_pinned_registered_pass_count") != 36 or
        kagura.get("k12_remaining_unverified_pass_count") != 23 or
        kagura.get("k12_bitcode_container_in_artifact") !=
        "LLVM_WRAPPED_BITCODE_BOTH_TARGETS" or
        kagura.get("k12_opt_both_targets_ir_delta") != ["kagura-tamper","kagura-anti-debug","kagura-honey","kagura-sv","kagura-cse-break","kagura-dci","kagura-telemetry","kagura-bbcheck"] or
        kagura.get("k12_opt_both_targets_no_ir_delta") != ["kagura-pac","kagura-str-aes","kagura-wstr","kagura-string-split","kagura-objc","kagura-jni","kagura-lt","kagura-pe","kagura-elt"] or
        kagura.get("k12_opt_infra_skipped") != ["kagura-autoselect","kagura-config","kagura-dwarf-control","kagura-symmap","kagura-vtp","kagura-audit"] or
        kagura.get("k12_workflow") !=
        ".github/workflows/kagura-k12-remaining-inventory.yml" or
        kagura.get("k12_inventory") !=
        "scripts/custom_ollvm/kagura_k12/inventory.py" or
        kagura.get("k12_smoke") !=
        "scripts/custom_ollvm/kagura_k12/smoke.py" or
        kagura.get("k12_artifact_auditor") !=
        "scripts/custom_ollvm/kagura_k12/audit.py" or
        kagura.get("k12_artifact_audit_test") !=
        "scripts/test_kagura_k12_opt_audit.py" or
        kagura.get("k12_ir_delta_gate") !=
        "FILE_BACKED_NORMALIZED_LLVM_IR_SHA_IGNORE_MODULEID" or
        kagura.get("k12_bitcode_container_gate") !=
        "RAW_OR_SPEC_VALIDATED_LLVM_WRAPPER_WITH_EMBEDDED_RAW_MAGIC" or
        kagura.get("k12_portable_test") !=
        "scripts/test_kagura_k12_remaining_inventory.py" or
        kagura.get("k12_doc") !=
        "docs/KAGURA_K12_REMAINING_PASS_INVENTORY.md" or
        kagura.get("k12_upstream_commit") !=
        "ac2136ee0408677cf7cdee55307e9b16edd5f4d5" or
        kagura.get("k12_historically_evidenced_distinct_pass_count") != 13 or
        kagura.get("k12_actual_pinned_remaining_names") != ["kagura-pac","kagura-str-aes","kagura-wstr","kagura-string-split","kagura-tamper","kagura-objc","kagura-jni","kagura-anti-debug","kagura-honey","kagura-sv","kagura-cse-break","kagura-lt","kagura-dci","kagura-pe","kagura-telemetry","kagura-bbcheck","kagura-elt","kagura-autoselect","kagura-config","kagura-dwarf-control","kagura-symmap","kagura-vtp","kagura-audit"] or
        kagura.get("k12_new_native_passes_verified") != 0 or
        kagura.get("k12_iphone_runtime") != "NOT_TESTED" or
        kagura.get("k12_arm64e_pac") != "NOT_TESTED" or
        kagura.get("k12_production_merge") is not False or
        any(not (root / kagura[field]).is_file() for field in
            ("k12_workflow", "k12_inventory", "k12_smoke",
             "k12_artifact_auditor", "k12_portable_test",
             "k12_artifact_audit_test", "k12_doc",
             "k12_artifact_review"))):
        raise AssertionError(
            "K12 pinned Kagura remaining pass registry+file-backed"
            " opt artifact provenance invalid; do not elevate into"
            " native/device PASS or Crane production")
    if (kagura.get("k13_status") !=
        "MACOS_NATIVE_AND_IOS_OBJECT_ARTIFACT_VERIFIED_NO_DEVICE" or
        kagura.get("k13_artifact_review") !=
        "docs/KAGURA_K13_ARTIFACT_REVIEW.md" or
        kagura.get("k13_artifact_zip_sha256") !=
        "2f18e54d3cc6f421ab997d96a162fd6b5869a4f5c78e62f739943e2238ce64f3" or
        kagura.get("k13_mac_arm64_baseline_object_sha256") !=
        "d8e1a34f8696d039c6133657eb10969f481c89bf0070dcb9870925a2e4fa09a5" or
        kagura.get("k13_mac_arm64_protected_object_sha256") !=
        "02caa3bc92b5a927463229d0de9854f3422b6ce24d90741175a4ad040464e839" or
        kagura.get("k13_ios_arm64_baseline_object_sha256") !=
        "43b263d0d1eb5b8194dd944e86e1c49ce57061f6ec283dd39f654f67a0c2ec71" or
        kagura.get("k13_ios_arm64_protected_object_sha256") !=
        "a1dea3f6cdb66d4f62d40dcfa7d32608049082700b2c78f7f69854c6b864cc62" or
        kagura.get("k13_native_checksum") !=
        "25a3318e3d7d6525" or
        kagura.get("k13_artifact_entry_count") != 41 or
        kagura.get("k13_independent_artifact_checks_passed") != 422 or
        kagura.get("k13_candidate") != "kagura-cse-break" or
        kagura.get("k13_pass_class") != "kagura::CSEBreakPass" or
        kagura.get("k13_workflow") !=
        ".github/workflows/kagura-k13-cse-break-native.yml" or
        kagura.get("k13_pilot") !=
        "scripts/custom_ollvm/kagura_k13/pilot.py" or
        kagura.get("k13_audit") !=
        "scripts/custom_ollvm/kagura_k13/audit.py" or
        kagura.get("k13_portable_test") !=
        "scripts/test_kagura_k13_native.py" or
        kagura.get("k13_doc") !=
        "docs/KAGURA_K13_CSE_BREAK_NATIVE_LAB.md" or
        kagura.get("k13_pinned_registry_sha256") !=
        "6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa" or
        kagura.get("k13_native_vectors_planned") != 4096 or
        kagura.get("k13_native_result") !=
        "CI_MACOS_4096_PARITY_AND_BINARY_ARTIFACT_VALIDATED" or
        kagura.get("k13_ios_arm64") !=
        "ARM64_SUBTYPE0_MH_OBJECT_ARTIFACT_VALIDATED_NOT_DEVICE" or
        kagura.get("k13_iphone_runtime") != "NOT_TESTED" or
        kagura.get("k13_arm64e_pac") != "NOT_TESTED" or
        kagura.get("k13_production_merge") is not False or
        any(not (root / kagura[field]).is_file() for field in
            ("k13_workflow", "k13_pilot", "k13_audit",
             "k13_portable_test", "k13_doc", "k13_artifact_review"))):
        raise AssertionError(
            "K13 CSEBreak native macOS and iOS arm64 object artifact"
            " provenance invalid; no iPhone/PAC/Crane PASS implied")
    if (kagura.get("k14_status") !=
        "IPA_AND_USER_SHARED_LOG_UUID_CHECKSUM_VERIFIED_NOT_ATTESTED" or
        kagura.get("k14_artifact_review") !=
        "docs/KAGURA_K14_ARTIFACT_AND_DEVICE_REVIEW.md" or
        kagura.get("k14_artifact_zip_sha256") !=
        "0ffbace0a56457a517bded16aa92d1a2e1455982901af5f39644c9140c87da47" or
        kagura.get("k14_ipa_sha256") !=
        "8733e2f93001b6d1195581deea013688825a94aa1d4d29bbfb23814dd5f9716f" or
        kagura.get("k14_app_binary_sha256") !=
        "584e9999d25a2642d818c0857a767173031868868df94d0e7de289176aa0cbd7" or
        kagura.get("k14_app_macho_uuid") !=
        "7c0cb853-77aa-3ccb-9f20-560e5f40e587" or
        kagura.get("k14_protected_ios_object_sha256") !=
        "a1dea3f6cdb66d4f62d40dcfa7d32608049082700b2c78f7f69854c6b864cc62" or
        kagura.get("k14_user_shared_normalized_log_sha256") !=
        "a145013d104fc83b0369a9ff21175ec5f6e4097eb739de8b98601e9aea4360d6" or
        kagura.get("k14_claimed_context") !=
        "IOS_DEVICE_USER_SHARED_TEXT_NOT_INDEPENDENT_ATTESTATION" or
        kagura.get("k14_artifact_entry_count") != 53 or
        kagura.get("k14_independent_artifact_checks_passed") != 103 or
        kagura.get("k14_user_shared_device_log_lines") != 8 or
        kagura.get("k14_iphone_execution_independently_observed") is not False or
        kagura.get("k14_device_execution_cryptographically_attested") is not False or
        kagura.get("k14_workflow") !=
        ".github/workflows/kagura-k14-cse-break-ios-ipa.yml" or
        kagura.get("k14_app_bundle") !=
        "com.duodash.research.kaguracsebreaklab" or
        kagura.get("k14_app_executable") != "KaguraCSEBreakLab" or
        kagura.get("k14_source") !=
        "scripts/custom_ollvm/kagura_k14/ios_probe.c" or
        kagura.get("k14_uikit") !=
        "scripts/custom_ollvm/kagura_k14/ios_app_main.m" or
        kagura.get("k14_info_plist") !=
        "scripts/custom_ollvm/kagura_k14/Info.plist" or
        kagura.get("k14_build") !=
        "scripts/custom_ollvm/kagura_k14/build_ipa.sh" or
        kagura.get("k14_package") !=
        "scripts/custom_ollvm/kagura_k14/package_ipa.py" or
        kagura.get("k14_evidence") !=
        "scripts/custom_ollvm/kagura_k14/ipa_evidence.py" or
        kagura.get("k14_device_audit") !=
        "scripts/custom_ollvm/kagura_k14/device_log_audit.py" or
        kagura.get("k14_portable_test") !=
        "scripts/test_kagura_k14_ios_ipa.py" or
        kagura.get("k14_doc") !=
        "docs/KAGURA_K14_CSE_BREAK_IOS_IPA_LAB.md" or
        kagura.get("k14_pinned_registry_sha256") !=
        "6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa" or
        kagura.get("k14_native_checksum_oracle") !=
        "25a3318e3d7d6525" or
        kagura.get("k14_expected_device_vectors") != 4096 or
        kagura.get("k14_ipa_ci") !=
        "MACOS_UNSIGNED_IPA_OBJECT_UUID_SHA_ARTIFACT_VERIFIED" or
        kagura.get("k14_iphone_runtime") !=
        "USER_SHARED_TEXT_PARITY_UUID_VALIDATED_NOT_ATTESTED" or
        kagura.get("k14_arm64e_pac") != "NOT_TESTED" or
        kagura.get("k14_production_merge") is not False or
        any(not (root / kagura[field]).is_file() for field in
            ("k14_workflow", "k14_source", "k14_uikit", "k14_info_plist",
             "k14_build", "k14_package", "k14_evidence",
             "k14_device_audit", "k14_portable_test", "k14_doc",
             "k14_artifact_review"))):
        raise AssertionError(
            "K14 CSEBreak only IPA real artifact and user-shared eight-line"
            " UUID/checksum correlation; device cryptographic attestation"
            " and Crane/PAC remain UNVERIFIED")
    if (kagura.get("k15_status") !=
        "MACOS_IOS_PROVIDER_ARTIFACT_VERIFIED_WEAK_ALWAYS_PASS_STUB_NOT_NATIVE_OR_SECURITY_PASS" or
        kagura.get("k15_artifact_review") !=
        "docs/KAGURA_K15_ARTIFACT_REVIEW.md" or
        kagura.get("k15_artifact_zip_sha256") !=
        "1f19d3d9eb58a87a9798d11082f3eaf4652e70987100084eb2c292d543bbd336" or
        kagura.get("k15_provider_bb_check_source") !=
        "runtime/core/bb_check.c" or
        kagura.get("k15_provider_bb_check_source_sha256") !=
        "2a87f559f2427c2de5217502c4d62abb1165fba34f5e1702982785dfacb24345" or
        kagura.get("k15_provider_tamper_source") !=
        "runtime/core/tamper_response.c" or
        kagura.get("k15_provider_tamper_source_sha256") !=
        "976cea2786438241b88f84c5c745f59aa669b683037ba81d7c09690339df5377" or
        kagura.get("k15_provider_weak_macho_n_desc") !=
        "0x0080_N_WEAK_DEF_BOTH_TARGETS" or
        kagura.get("k15_provider_uniqueness") !=
        "ONE_GENUINE_PROVIDER_EACH_REQUIRED_SYMBOL_BOTH_TARGETS" or
        kagura.get("k15_provider_kagura_transitive") !=
        "NONE_FOR_TWO_SELECTED_PROVIDERS_BOTH_TARGETS" or
        kagura.get("k15_runtime_bbcheck_behavior") !=
        "WEAK_ALWAYS_RETURNS_ONE_IGNORES_BLOCK_ID_EXPECTED" or
        kagura.get("k15_runtime_tamper_response") !=
        "WEAK_ABORT_DEFAULT_APPLE_NO_EXECUTION_K15" or
        kagura.get("k15_artifact_entry_count") != 231 or
        kagura.get("k15_independent_file_backed_checks") != 2609 or
        kagura.get("k15_runtime_candidate_sources_each_target") != 22 or
        kagura.get("k15_runtime_compiled_candidates_each_target") != 22 or
        kagura.get("k15_security_integrity_proven") is not False or
        kagura.get("k15_candidate") != "kagura-bbcheck" or
        kagura.get("k15_pass_class") !=
        "kagura::BasicBlockChecksumPass" or
        kagura.get("k15_pass_kind") != "FN" or
        kagura.get("k15_pass_enable_flag") != "BBCheck" or
        kagura.get("k15_required_runtime_symbols") !=
        ["_kagura_bb_check", "_kagura_on_tamper_detected"] or
        kagura.get("k15_workflow") !=
        ".github/workflows/kagura-k15-bbcheck-runtime-audit.yml" or
        kagura.get("k15_pilot") !=
        "scripts/custom_ollvm/kagura_k15/pilot.py" or
        kagura.get("k15_audit") !=
        "scripts/custom_ollvm/kagura_k15/audit.py" or
        kagura.get("k15_portable_test") !=
        "scripts/test_kagura_k15_bbcheck.py" or
        kagura.get("k15_doc") !=
        "docs/KAGURA_K15_BBCHECK_RUNTIME_RESEARCH.md" or
        kagura.get("k15_pinned_registry_sha256") !=
        "6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa" or
        kagura.get("k15_macos_native_parity") !=
        "NOT_TESTED_TAMPER_CALLBACK" or
        kagura.get("k15_ios_arm64_object") !=
        "PINNED_BBCHECK_IR_MACHO_ARM64_OBJECT_ARTIFACT_VERIFIED_ONLY" or
        kagura.get("k15_ios_ipa") != "NOT_BUILT" or
        kagura.get("k15_iphone_runtime") != "NOT_TESTED" or
        kagura.get("k15_arm64e_pac") != "NOT_TESTED" or
        kagura.get("k15_production_merge") is not False or
        any(not (root / kagura[f]).is_file() for f in
            ("k15_workflow", "k15_pilot", "k15_audit",
             "k15_portable_test", "k15_doc", "k15_artifact_review"))):
        raise AssertionError("K15 genuine provider artifact is weak"
                             " always-passing BBCheck stub, NOT a security"
                             " integrity, native/device/PAC/Crane PASS")
    if (kagura.get("k16_status") !=
        "REAL_MACOS_OFFLINE_TEXT_ARTIFACT_REPLAY_VERIFIED_NOT_RUNTIME_SECURITY" or
        kagura.get("k16_artifact_review") !=
        "docs/KAGURA_K16_ARTIFACT_REVIEW.md" or
        kagura.get("k16_artifact_zip_sha256") !=
        "521934d99ce952f74b0471cdd259d92e147eee718479a3863b49251b11eb79c4" or
        kagura.get("k16_macos_baseline_text_sha256") !=
        "9682fe57b5dc2e115f25745becc03f9eaa68f56e06f15d72f79a8c2630cef5f9" or
        kagura.get("k16_macos_csebreak_text_sha256") !=
        "2c8fd2006a6d636fb30c088585a9b093108b825c6032915aa1987abd0ee85186" or
        kagura.get("k16_ios_csebreak_text_sha256") !=
        "dd41ee5339eb6fd2732e46f34b9a22ea62233611a4a6269b4088251a6824fd3e" or
        kagura.get("k16_ios_csebreak_macho_uuid") !=
        "7c0cb853-77aa-3ccb-9f20-560e5f40e587" or
        kagura.get("k16_existing_k14_device_log") !=
        "USER_SHARED_K14_UUID_CHECKSUM_CORRELATED_NOT_K16_EXECUTION" or
        kagura.get("k16_artifact_entry_count") != 54 or
        kagura.get("k16_independent_file_backed_checks") != 276 or
        kagura.get("k16_macos_baseline_text_offset") != 15376 or
        kagura.get("k16_macos_baseline_text_size") != 728 or
        kagura.get("k16_macos_csebreak_text_offset") != 15264 or
        kagura.get("k16_macos_csebreak_text_size") != 840 or
        kagura.get("k16_ios_csebreak_text_offset") != 16384 or
        kagura.get("k16_ios_csebreak_text_size") != 6312 or
        kagura.get("k16_mode") !=
        "OFFLINE_UNSIGNED_MACHO_TEXT_SECTION_SHA256_FEASIBILITY" or
        kagura.get("k16_workflow") !=
        ".github/workflows/kagura-k16-offline-macho-text.yml" or
        kagura.get("k16_measure") !=
        "scripts/custom_ollvm/kagura_k16/macho_measure.py" or
        kagura.get("k16_test") !=
        "scripts/test_kagura_k16_offline_text.py" or
        kagura.get("k16_doc") !=
        "docs/KAGURA_K16_OFFLINE_MACHO_TEXT.md" or
        kagura.get("k16_specimens") !=
        ["macos-baseline", "macos-cse-break",
         "KaguraCSEBreakLab.app/KaguraCSEBreakLab"] or
        kagura.get("k16_required_section") != "__TEXT,__text" or
        kagura.get("k16_original_bbcheck") !=
        "BLOCKED_K15_WEAK_ALWAYS_PASS_STUB" or
        kagura.get("k16_macos_ci") !=
        "REAL_MACOS_LINKED_MACHO_TEXT_OFFLINE_EVIDENCE_VERIFIED" or
        kagura.get("k16_reference_authenticated") is not False or
        kagura.get("k16_runtime_verifier_implemented") is not False or
        kagura.get("k16_per_block_integrity") is not False or
        kagura.get("k16_security_integrity_proven") is not False or
        kagura.get("k16_ios_device_runtime") != "NOT_TESTED" or
        kagura.get("k16_arm64e_pac") != "NOT_TESTED" or
        kagura.get("k16_production_merge") is not False or
        any(not (root / kagura[key]).is_file()
            for key in ("k16_workflow", "k16_measure",
                        "k16_test", "k16_doc", "k16_artifact_review"))):
        raise AssertionError("K16 real CI offline SHA/LC_UUID verified for"
                             " linked Mach-O code; manifest unsigned, no BBCheck"
                             " runtime, security/iPhone/PAC/Crane PASS")
    if (kagura.get("k17_status") !=
        "REAL_CI_ED25519_TEST_KEY_SIGNATURE_AND_OFFLINE_MACHO_VERIFIED_NOT_SECURE_TRUST" or
        kagura.get("k17_artifact_review") !=
        "docs/KAGURA_K17_ARTIFACT_REVIEW.md" or
        kagura.get("k17_artifact_zip_sha256") !=
        "9b07e6a8e285102aa80671a6bdd70fe080d9424097632a7e87272f44b77d76db" or
        kagura.get("k17_detached_signature_sha256") !=
        "8e82eef77b726f5412fff4a0e750fc4554915748ef44bbd97aa7be437637c892" or
        kagura.get("k17_raw_k16_manifest_sha256") !=
        "eb322412014ede1f4b5e0aa093e513b067670ac9866b33f1511c62269cfc1cd8" or
        kagura.get("k17_test_public_spki_sha256") !=
        "2e91a1403ffc97eb66c2c1717205eb054ce3c341898b6978b007cb5c56241f40" or
        kagura.get("k17_cryptographic_signature_verification") !=
        "ED25519_SIGNATURE_VALID_WITH_PREVIOUSLY_EXPOSED_TEST_KEY_OFFLINE_ONLY" or
        kagura.get("k17_iphone_app_user_report") !=
        "APP_INSTALLED_AND_FUNCTIONAL_USER_REPORT_ONLY" or
        kagura.get("k17_iphone_app_uuid") !=
        "7c0cb853-77aa-3ccb-9f20-560e5f40e587" or
        kagura.get("k17_artifact_entry_count") != 56 or
        kagura.get("k17_independent_file_backed_checks") != 446 or
        kagura.get("k17_test_private_key_previously_exposed_in_chat") is not True or
        kagura.get("k17_iphone_execution_independently_observed") is not False or
        kagura.get("k17_offline_macho_manifest_replayed") is not True or
        kagura.get("k17_scope") !=
        "EXTERNAL_SPKI_SHA256_ED25519_DETACHED_K16_OFFLINE_MANIFEST_ONLY" or
        kagura.get("k17_workflow") !=
        ".github/workflows/kagura-k17-external-ed25519.yml" or
        kagura.get("k17_signer") !=
        "scripts/custom_ollvm/kagura_k17/signature.py" or
        kagura.get("k17_test") !=
        "scripts/test_kagura_k17_signature.py" or
        kagura.get("k17_doc") !=
        "docs/KAGURA_K17_ED25519_OFFLINE_REFERENCE.md" or
        kagura.get("k17_crypto_dependency") != "cryptography==50.0.2" or
        kagura.get("k17_external_secret") !=
        "K17_ED25519_PRIVATE_KEY_PEM" or
        kagura.get("k17_external_public_key_var") !=
        "K17_ED25519_PUBLIC_KEY_PEM" or
        kagura.get("k17_external_fingerprint_var") !=
        "K17_ED25519_PUBLIC_KEY_SPKI_SHA256" or
        kagura.get("k17_signature_name") !=
        "Kagura-K17-K16-MANIFEST.ed25519" or
        kagura.get("k17_receipt_name") !=
        "Kagura-K17-SIGNATURE-RECEIPT.json" or
        kagura.get("k17_signed_ci_artifact") !=
        "REAL_CI_ED25519_TEST_KEY_DETACHED_SIGNATURE_VERIFIED_OFFLINE_ONLY" or
        any(kagura.get(k) is not False for k in (
            "k17_private_key_in_artifact",
            "k17_trusted_public_key_in_artifact",
            "k17_external_key_verified",
            "k17_manifest_authentication_verified",
            "k17_runtime_verifier_implemented",
            "k17_iphone_device_attested",
            "k17_security_integrity_proven",
            "k17_arm64e_pac_tested",
            "k17_production_merge")) or
        any(not (root / kagura[key]).is_file() for key in
            ("k17_workflow", "k17_signer", "k17_test", "k17_doc",
             "k17_artifact_review"))):
        raise AssertionError("K17 real test-key signature and offline MachO"
                             " file replay verified, but private TEST key was"
                             " exposed: no secure trust/device/security/Crane PASS")
    if (kagura.get("k18_status") !=
        "SKIPPED_BY_USER_NO_MACOS_OR_DEVICE_VERIFICATION" or
        kagura.get("k18_scope") !=
        "SIGNED_BUNDLED_K14_SPECIMEN_ONLY_NOT_RUNNING_APP_INTEGRITY" or
        kagura.get("k18_workflow") !=
        ".github/workflows/kagura-k18-rotated-reference-ipa.yml" or
        kagura.get("k18_swift") !=
        "scripts/custom_ollvm/kagura_k18/K18ReferenceLab.swift" or
        kagura.get("k18_info_plist") !=
        "scripts/custom_ollvm/kagura_k18/Info.plist" or
        kagura.get("k18_packager") !=
        "scripts/custom_ollvm/kagura_k18/package.py" or
        kagura.get("k18_test") != "scripts/test_kagura_k18_reference_lab.py" or
        kagura.get("k18_device_log_audit") !=
        "scripts/custom_ollvm/kagura_k18/device_log_audit.py" or
        kagura.get("k18_doc") !=
        "docs/KAGURA_K18_ROTATED_IOS_REFERENCE_LAB.md" or
        kagura.get("k18_bundle_id") !=
        "com.duodash.research.kagurak18referencelab" or
        kagura.get("k18_required_key_secret") !=
        "K18_ED25519_PRIVATE_KEY_PEM" or
        kagura.get("k18_required_public_key") !=
        "K18_ED25519_PUBLIC_KEY_PEM" or
        kagura.get("k18_required_fingerprint") !=
        "K18_ED25519_PUBLIC_KEY_SPKI_SHA256" or
        kagura.get("k18_forbidden_exposed_k17_test_fingerprint") !=
        "2e91a1403ffc97eb66c2c1717205eb054ce3c341898b6978b007cb5c56241f40" or
        kagura.get("k18_expected_log_schema") != 1 or
        kagura.get("k18_expected_log_lines") != 10 or
        kagura.get("k18_macos_swift_ci") != "NOT_TESTED" or
        any(kagura.get(k) is not False for k in (
            "k18_new_owner_key_provisioned",
            "k18_signed_reference_ci",
            "k18_iphone_executed",
            "k18_independent_device_attestation",
            "k18_embedded_key_immutable",
            "k18_self_integrity_verifier_implemented",
            "k18_security_strength_proven",
            "k18_arm64e_pac_tested",
            "k18_production_merge")) or
        any(not (root / kagura[key]).is_file() for key in
            ("k18_workflow", "k18_swift", "k18_info_plist",
             "k18_packager", "k18_test", "k18_doc", "k18_device_log_audit"))):
        raise AssertionError("K18 new rotated Ed25519 CryptoKit iOS reference"
                             " verifier staged only; no real macOS IPA/device"
                             " evidence, no immutable trust/self-integrity/PAC/Crane")
    if (kagura.get("k19_status") !=
        "REAL_MACOS_OFFLINE_NLIST_ARTIFACT_VERIFIED_NOT_RUNTIME_SECURITY" or
        kagura.get("k19_artifact_sha256") !=
        "8a7625e0c3a5222009e295f515f534bcb1cebdf88ae5f5749c2d7bbc81bcc8bc" or
        kagura.get("k19_artifact_unique_entries") != 55 or
        kagura.get("k19_corroborated_symbol_intervals") != 4 or
        kagura.get("k19_real_ignored_ancillary_per_binary") != 1 or
        kagura.get("k19_scope") !=
        "LC_SYMTAB_N_SECT_NEXT_ADDRESS_BOUNDED_OFFLINE_NO_FUNCTION_BOUNDARY_GUARANTEE" or
        kagura.get("k19_workflow") !=
        ".github/workflows/kagura-k19-symbol-bounded.yml" or
        kagura.get("k19_measure") !=
        "scripts/custom_ollvm/kagura_k19/symbol_ranges.py" or
        kagura.get("k19_test") !=
        "scripts/test_kagura_k19_symbol_ranges.py" or
        kagura.get("k19_doc") !=
        "docs/KAGURA_K19_SYMBOL_BOUNDED_OFFLINE.md" or
        kagura.get("k19_manifest") !=
        "Kagura-K19-SYMBOL-RANGES.json" or
        kagura.get("k19_abi_symbol") != "_dd_k8_evaluate" or
        kagura.get("k19_ios_second_symbol") != "_dd_k14_ios_parity" or
        kagura.get("k19_macos_ci") !=
        "REAL_MACOS_NLIST_AND_K16_OFFLINE_REPLAY_VERIFIED" or
        kagura.get("k19_iphone_runtime") != "NOT_TESTED" or
        any(kagura.get(key) is not False for key in (
            "k19_depends_on_k18",
            "k19_signing_or_secure_trust",
            "k19_exact_function_boundaries_proven",
            "k19_per_basic_block_proven",
            "k19_runtime_integrity_implemented",
            "k19_security_anti_tamper_proven",
            "k19_arm64e_pac_tested",
            "k19_production_merge")) or
        any(not (root / kagura[key]).is_file() for key in
            ("k19_workflow", "k19_measure", "k19_test", "k19_doc"))):
        raise AssertionError("K19 post-link real LC_SYMTAB nlist symbol range"
                             " study is OFFLINE (real macOS artifact reviewed),"
                             " without K18; no function/per-block/device"
                             " security PASS")
    if (kagura.get("k20_status") !=
        "REAL_MACOS_OFFLINE_FUNCTION_STARTS_ARTIFACT_VERIFIED_NOT_RUNTIME_SECURITY" or
        kagura.get("k20_artifact_sha256") !=
        "235e1d4ea16437807d1920e236bb65942ef580bf021734d9093a81e73884b214" or
        kagura.get("k20_artifact_unique_entries") != 56 or
        kagura.get("k20_independent_file_checks") != 190 or
        kagura.get("k20_corroborated_symbol_intervals") != 4 or
        kagura.get("k20_function_starts_per_binary") != [3, 3, 30] or
        kagura.get("k20_artifact_review_doc") !=
        "docs/KAGURA_K20_ARTIFACT_REVIEW.md" or
        kagura.get("k20_scope") !=
        "SAME_MACHO_LC_FUNCTION_STARTS_NLIST_DUAL_SOURCE_OFFLINE_NO_TRUST" or
        kagura.get("k20_workflow") !=
        ".github/workflows/kagura-k20-function-starts.yml" or
        kagura.get("k20_measure") !=
        "scripts/custom_ollvm/kagura_k20/function_starts.py" or
        kagura.get("k20_test") !=
        "scripts/test_kagura_k20_function_starts.py" or
        kagura.get("k20_doc") !=
        "docs/KAGURA_K20_FUNCTION_STARTS_CROSSCHECK.md" or
        kagura.get("k20_manifest") !=
        "Kagura-K20-FUNCTION-START-CROSSCHECK.json" or
        kagura.get("k20_required_command") != "LC_FUNCTION_STARTS" or
        kagura.get("k20_required_symbol_source") != "LC_SYMTAB_N_SECT" or
        kagura.get("k20_macos_ci") !=
        "REAL_MACOS_LC_FUNCTION_STARTS_K19_OFFLINE_REPLAY_VERIFIED" or
        any(kagura.get(k) is not False for k in (
            "k20_k18_dependency", "k20_authenticated_reference",
            "k20_independent_trust_root", "k20_exact_function_size_proven",
            "k20_per_basic_block_integrity_proven",
            "k20_runtime_verifier_implemented", "k20_iphone_device_executed",
            "k20_security_anti_tamper_proven", "k20_arm64e_pac_tested",
            "k20_production_merge")) or
        any(not (root / kagura[k]).is_file() for k in (
            "k20_workflow", "k20_measure", "k20_test", "k20_doc",
            "k20_artifact_review_doc"))):
        raise AssertionError("K20 real macOS artifact corroborates unsigned K19"
                             " in SAME MachO only; no device/security PASS")
    if (kagura.get("k21_status") !=
        "REAL_MACOS_OFFLINE_AARCH64_WORD_ARTIFACT_VERIFIED_NOT_RUNTIME_SECURITY" or
        kagura.get("k21_artifact_sha256") !=
        "1991f38f5af55f310352e0f23d6e2a566eec8dba5d0a35ee6c8c2d91fffe40aa" or
        kagura.get("k21_artifact_unique_entries") != 57 or
        kagura.get("k21_independent_file_checks") != 785 or
        kagura.get("k21_target_word_counts") != [115, 136, 136, 121] or
        kagura.get("k21_function_starts_per_binary") != [3, 3, 30] or
        kagura.get("k21_artifact_review_doc") !=
        "docs/KAGURA_K21_ARTIFACT_REVIEW.md" or
        kagura.get("k21_scope") !=
        "STATIC_AARCH64_WORD_CLASSIFICATION_IN_K20_CORROBORATED_NLIST_INTERVALS_NO_CFG_SECURITY" or
        kagura.get("k21_workflow") !=
        ".github/workflows/kagura-k21-static-opcodes.yml" or
        kagura.get("k21_measure") !=
        "scripts/custom_ollvm/kagura_k21/opcode_inventory.py" or
        kagura.get("k21_test") !=
        "scripts/test_kagura_k21_opcode_inventory.py" or
        kagura.get("k21_doc") !=
        "docs/KAGURA_K21_STATIC_OPCODE_INVENTORY.md" or
        kagura.get("k21_manifest") !=
        "Kagura-K21-STATIC-OPCODE-INVENTORY.json" or
        kagura.get("k21_macos_ci") !=
        "REAL_MACOS_STATIC_AARCH64_WORD_ARTIFACT_REPLAY_VERIFIED" or
        any(kagura.get(k) is not False for k in (
            "k21_k18_dependency", "k21_instruction_semantics_proven",
            "k21_cfg_or_function_extent_proven",
            "k21_runtime_verifier_implemented",
            "k21_security_anti_tamper_proven",
            "k21_iphone_device_executed", "k21_arm64e_pac_tested",
            "k21_production_merge")) or
        any(not (root / kagura[k]).is_file() for k in (
            "k21_workflow", "k21_measure", "k21_test", "k21_doc",
            "k21_artifact_review_doc"))):
        raise AssertionError("K21 real macOS static AArch64 word study"
                             " is OFFLINE only; no device/security PASS")
    if (kagura.get("k22_status") !=
        "REAL_MACOS_TWO_BUILD_OFFLINE_CODE_ARTIFACT_VERIFIED_NOT_RUNTIME_SECURITY" or
        kagura.get("k22_artifact_sha256") !=
        "f7f449e3929f78f42650c46925e37e884c8a4612713abd67bf604c8ce8b01c82" or
        kagura.get("k22_artifact_unique_entries") != 115 or
        kagura.get("k22_independent_file_checks") != 388 or
        kagura.get("k22_matched_target_intervals") != 4 or
        kagura.get("k22_whole_executables_identical") != 3 or
        kagura.get("k22_artifact_review_doc") !=
        "docs/KAGURA_K22_ARTIFACT_REVIEW.md" or
        kagura.get("k22_scope") !=
        "TWO_SEPARATE_K21_SOURCE_REPLAYS_COMPARE_POSTLINK_CODE_INTERVAL_SHA_NO_ATTESTATION" or
        kagura.get("k22_workflow") !=
        ".github/workflows/kagura-k22-reproducibility.yml" or
        kagura.get("k22_measure") !=
        "scripts/custom_ollvm/kagura_k22/reproducibility.py" or
        kagura.get("k22_test") !=
        "scripts/test_kagura_k22_reproducibility.py" or
        kagura.get("k22_doc") !=
        "docs/KAGURA_K22_REPRODUCIBILITY_GATE.md" or
        kagura.get("k22_manifest") !=
        "Kagura-K22-REPRODUCIBILITY.json" or
        kagura.get("k22_macos_ci") !=
        "REAL_MACOS_TWO_SEPARATE_BUILD_SEQUENCES_OFFLINE_ARTIFACT_VERIFIED" or
        any(kagura.get(k) is not False for k in (
            "k22_k18_dependency", "k22_two_independent_ci_runs_attested",
            "k22_runtime_integrity_implemented",
            "k22_iphone_device_executed", "k22_security_anti_tamper_proven",
            "k22_arm64e_pac_tested", "k22_production_merge")) or
        any(not (root / kagura[k]).is_file() for k in (
            "k22_workflow", "k22_measure", "k22_test", "k22_doc",
            "k22_artifact_review_doc"))):
        raise AssertionError("K22 real two-sequence macOS offline artifact"
                             " verified only; no device/security PASS")
    if (kagura.get("k23_status") !=
        "REAL_MACOS_V2_IPA_VERIFIED_USER_REPORTED_THREE_FUNCTIONAL_PASS_NOT_ATTESTED" or
        kagura.get("k23_artifact_sha256") !=
        "eba93a0b5e2f965c4addec02e06262e3ca5db550bf6b23a61496b42b7a844f06" or
        kagura.get("k23_artifact_unique_entries") != 65 or
        kagura.get("k23_unsigned_ipa_sha256") !=
        "337b4144678558ef6067b6c602b3b92b56f5c1f241ed47fefffa925f86819a37" or
        kagura.get("k23_reference_sha256") !=
        "584e9999d25a2642d818c0857a767173031868868df94d0e7de289176aa0cbd7" or
        kagura.get("k23_reference_uuid") !=
        "7c0cb853-77aa-3ccb-9f20-560e5f40e587" or
        kagura.get("k23_artifact_review_doc") !=
        "docs/KAGURA_K23_ARTIFACT_DEVICE_FAILURE_REVIEW.md" or
        kagura.get("k23_v2_artifact_review_doc") !=
        "docs/KAGURA_K23_V2_THREE_RUN_ARTIFACT_REVIEW.md" or
        kagura.get("k23_v2_artifact_sha256") !=
        "7fbea5d7d52dec575011143dea7cacecbdbacc985ce63aedc29e83d2ecd16cf1" or
        kagura.get("k23_v2_artifact_unique_entries") != 65 or
        kagura.get("k23_v2_ipa_sha256") !=
        "c92c030048162f3a1c4182688045af301346aeb78cafca45d4b79fd0fac1452b" or
        kagura.get("k23_v2_app_executable_sha256") !=
        "5e6fee5912451552279464731894f67c05d5a3eb7e1e441851c2017a0d158abe" or
        kagura.get("k23_v2_transport_sha256") !=
        "060497b06ad64f5d38525251a5051535dc8616e4f151d9c79cfccf117386e907" or
        kagura.get("k23_v2_transport_bytes") != 123313 or
        kagura.get("k23_v2_decoded_reference_bytes") != 92456 or
        kagura.get("k23_v2_ipa_member_count") != 3 or
        kagura.get("k23_v2_bundle_version") != "2" or
        kagura.get("k23_scope") !=
        "ISOLATED_IOS_ARM64_K14_BUNDLED_REFERENCE_RUNTIME_SHA256_FAIL_CLOSED_LAB_NO_SELF_INTEGRITY" or
        kagura.get("k23_workflow") !=
        ".github/workflows/kagura-k23-runtime-reference-lab.yml" or
        kagura.get("k23_package") !=
        "scripts/custom_ollvm/kagura_k23/package.py" or
        kagura.get("k23_swift") !=
        "scripts/custom_ollvm/kagura_k23/K23RuntimeLab.swift" or
        kagura.get("k23_device_log_audit") !=
        "scripts/custom_ollvm/kagura_k23/device_log_audit.py" or
        kagura.get("k23_three_stage_qa_tool") !=
        "scripts/custom_ollvm/kagura_k23/device_qa.py" or
        kagura.get("k23_user_shared_log_review_doc") !=
        "docs/KAGURA_K23_USER_SHARED_RUNTIME_LOG_REVIEW.md" or
        kagura.get("k23_qa_runbook_doc") !=
        "docs/KAGURA_K23_IPHONE_QA_RUNBOOK.md" or
        kagura.get("k23_user_shared_log_lines") != 10 or
        kagura.get("k23_three_stage_qa_status") !=
        "USER_REPORTED_3_OF_3_PASS_V2_ARTIFACT_VERIFIED_SOURCE_LOG_FILES_PENDING" or
        kagura.get("k23_three_user_reported_runs_pass") != 3 or
        kagura.get("k23_three_device_logs_independently_provided") is not False or
        kagura.get("k23_cryptographic_device_attestation") is not False or
        kagura.get("k23_info_plist") !=
        "scripts/custom_ollvm/kagura_k23/Info.plist" or
        kagura.get("k23_test") !=
        "scripts/test_kagura_k23_runtime_reference.py" or
        kagura.get("k23_doc") !=
        "docs/KAGURA_K23_RUNTIME_REFERENCE_LAB.md" or
        kagura.get("k23_macos_ci") !=
        "REAL_MACOS_UNSIGNED_IPA_ARTIFACT_BYTE_REPLAY_VERIFIED" or
        kagura.get("k23_iphone_runtime") !=
        "USER_REPORTED_THREE_OF_THREE_BUNDLED_REFERENCE_FUNCTIONAL_PASS_NOT_ATTESTED" or
        any(kagura.get(k) is not False for k in (
            "k23_k18_dependency", "k23_embedded_hash_is_trust_anchor",
            "k23_running_executable_integrity_verified",
            "k23_runtime_self_integrity_implemented",
            "k23_security_anti_tamper_proven", "k23_arm64e_pac_tested",
            "k23_production_merge")) or
        any(not (root / kagura[k]).is_file() for k in (
            "k23_workflow", "k23_package", "k23_swift",
            "k23_device_log_audit", "k23_three_stage_qa_tool",
            "k23_user_shared_log_review_doc", "k23_qa_runbook_doc",
            "k23_info_plist", "k23_test", "k23_doc",
            "k23_artifact_review_doc", "k23_v2_artifact_review_doc"))):
        raise AssertionError("K23 user-shared functional log may PASS but"
                             " device attestation and self-security remain false")
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
