#!/usr/bin/env python3
"""Portable fail-closed regression for actual vs proposed custom LLVM passes."""
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts/custom_ollvm/audit_passes.py"
REGISTRY = ROOT / "scripts/custom_ollvm/pass_registry.json"
spec = importlib.util.spec_from_file_location("audit_passes", MODULE)
assert spec and spec.loader
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

original = json.loads(REGISTRY.read_text(encoding="utf-8"))
status = audit.audit(original)
assert status["production_enabled_count"] == 4
assert status["existing_actual_llvm_passes"] == ["split", "bcf", "fla", "sub"]
assert status["separate_hikari_llvm_passes_not_in_obfuscator"] == ["constenc", "strcry"]
assert set(status["source_level_pilots_not_llvm_passes"]) == {
    "CE", "ICALL", "IGV", "IBR", "VM", "ObjC_CE"
}
assert len(status["planned_new_llvm_passes_not_implemented"]) == 6
assert status["arm64e_production_llvm_passes"] == []
assert status["compiler_native_new_pass_build_verified_this_run"] is False
assert status["custom_ollvm_strong_modified"] is False
assert status["separate_kagura_llvm_pipeline"] == "K1_NATIVE_7_STAGE_ARTIFACT_VERIFIED"
assert original["experimental_kagura_pipeline"]["k2_scope_and_benchmark_status"] == "MACOS_ARTIFACT_VERIFIED_HOST_ONLY"
assert original["experimental_kagura_pipeline"]["k3_interleaved_benchmark_status"] == "STAGED_NOT_VERIFIED_MACOS_NATIVE"
assert original["experimental_kagura_pipeline"]["k3_samples_per_variant"] == 176
assert original["experimental_kagura_pipeline"]["ios_arm64_kagura_trollstore_pilot"] == "CI_ARTIFACT_HASHES_VERIFIED"
assert original["experimental_kagura_pipeline"]["ios_arm64_kagura_pilot_on_device"] == "USER_REPORTED_PASS_NO_SHARED_DEVICE_LOG"
assert original["experimental_kagura_pipeline"]["k6_selective_vm_status"] == "MACOS_CI_ARTIFACT_VERIFIED_HOST_ONLY"
assert original["experimental_kagura_pipeline"]["k7_vm_trollstore_ipa_status"] == "CI_ARTIFACT_HASHES_VERIFIED"
assert original["experimental_kagura_pipeline"]["k7_vm_on_device"] == "USER_SHARED_TEXT_PARITY_AND_PERF_VALIDATED_NOT_ATTESTED"
assert original["experimental_kagura_pipeline"]["k7_shared_device_log_status"] == "VALIDATED_EXACT_SCHEMA_UUID_CHECKSUM_VS_CI"
assert original["experimental_kagura_pipeline"]["k7_prior_pasted_log_status"] == "REJECTED_MALFORMED_TRANSPORT_TEXT"
assert original["experimental_kagura_pipeline"]["k7_device_benchmark_status"] == "USER_SHARED_THREE_PAIRS_OBSERVATIONAL"
assert original["experimental_kagura_pipeline"]["k7_device_median_paired_overhead_ratio"] == 71.5
assert original["experimental_kagura_pipeline"]["k7_device_plain_samples_ns"] == [46, 32, 30]
assert original["experimental_kagura_pipeline"]["k7_device_vm_samples_ns"] == [3742, 1918, 2145]
assert original["experimental_kagura_pipeline"]["k7_app_macho_uuid"] == "15a45d46-f0da-37ff-855d-5e6ea078be8e"
assert original["experimental_kagura_pipeline"]["k7_macos_median_paired_overhead_ratio"] == 47.0
assert original["experimental_kagura_pipeline"]["k6_vm_device_runtime"] == "NOT_TESTED"
assert original["experimental_kagura_pipeline"]["k8_five_pass_status"] == "MACOS_CI_ARTIFACT_VERIFIED_ISOLATED_FIVE_PASS"
assert original["experimental_kagura_pipeline"]["k8_artifact_zip_sha256"] == "a1bc3b5bf0057e082ff4109c93925e39758f7fd861fb336d3655ffe4c6049dea"
assert original["experimental_kagura_pipeline"]["k8_artifact_entry_count"] == 74
assert original["experimental_kagura_pipeline"]["k8_independent_artifact_checks_passed"] == 92
assert original["experimental_kagura_pipeline"]["k8_native_parity_status"] == "FIVE_ISOLATED_4096_VECTORS_PASS"
assert original["experimental_kagura_pipeline"]["k8_native_c_fixture_checksum"] == "25a3318e3d7d6525"
assert original["experimental_kagura_pipeline"]["k8_native_mvo_fixture_checksum"] == "64e61045bbc4a250"
assert original["experimental_kagura_pipeline"]["k8_five_passes"] == ["ibr", "mvo", "genc", "fsplit", "ci"]
assert original["experimental_kagura_pipeline"]["k8_ios_arm64"] == "BUILD_ONLY_NOT_EXECUTED"
assert original["experimental_kagura_pipeline"]["k8_combined_five_passes"] == "K9_FIVE_COMPOSED_STAGES_MACOS_ARTIFACT_VERIFIED"
assert original["experimental_kagura_pipeline"]["k8_artifact_review"] == "docs/KAGURA_K8_ARTIFACT_REVIEW.md"
assert original["experimental_kagura_pipeline"]["k9_composition_status"] == "MACOS_CI_ARTIFACT_VERIFIED_FIVE_COMPOSED_STAGES"
assert original["experimental_kagura_pipeline"]["k9_artifact_zip_sha256"] == "9925f6ae0f95f2ec52ae53e7416723cd134de2e2e6fafc2ce6a3b58db5f96cf5"
assert original["experimental_kagura_pipeline"]["k9_artifact_entry_count"] == 75
assert original["experimental_kagura_pipeline"]["k9_independent_artifact_checks_passed"] == 179
assert original["experimental_kagura_pipeline"]["k9_artifact_review"] == "docs/KAGURA_K9_ARTIFACT_REVIEW.md"
assert original["experimental_kagura_pipeline"]["k9_llvm_link_warnings"] == "NONFATAL_MVO_DATALAYOUT_AND_HOST_TRIPLE_MISMATCH"
assert original["experimental_kagura_pipeline"]["k9_stage_order"] == ["mvo", "genc", "fsplit", "ibr", "ci"]
assert original["experimental_kagura_pipeline"]["k9_merged_function_names"] == ["dd_k8_evaluate", "dd_k9_mvo_probe"]
assert original["experimental_kagura_pipeline"]["k9_native_vectors_per_function"] == 4096
assert original["experimental_kagura_pipeline"]["k9_c_checksum"] == "25a3318e3d7d6525"
assert original["experimental_kagura_pipeline"]["k9_mvo_checksum"] == "64e61045bbc4a250"
assert original["experimental_kagura_pipeline"]["k9_ios_arm64"] == "OBJECT_BUILD_ONLY_NOT_EXECUTED"
assert original["experimental_kagura_pipeline"]["k9_composition_native"] == "MACOS_NATIVE_FIVE_STAGES_TWO_FUNCTION_4096_PARITY_VERIFIED"
assert original["experimental_kagura_pipeline"]["k9_performance"] == "NOT_EVALUATED"
assert original["experimental_kagura_pipeline"]["k10_strict_link_metadata_status"] == "MACOS_CI_ARTIFACT_VERIFIED_STRICT_LLVM_METADATA"
assert original["experimental_kagura_pipeline"]["k10_artifact_zip_sha256"] == "3567fca73c11aaea0b30e50ca8eb9cda6491ff32cb7832893ffd104725f59383"
assert original["experimental_kagura_pipeline"]["k10_artifact_entry_count"] == 80
assert original["experimental_kagura_pipeline"]["k10_independent_artifact_checks_passed"] == 277
assert original["experimental_kagura_pipeline"]["k10_artifact_review"] == "docs/KAGURA_K10_ARTIFACT_REVIEW.md"
assert original["experimental_kagura_pipeline"]["k10_host_target_triple"] == "arm64-apple-macosx14.0.0"
assert original["experimental_kagura_pipeline"]["k10_ios_target_triple"] == "arm64-apple-ios15.0.0"
assert original["experimental_kagura_pipeline"]["k10_both_target_datalayout"] == "e-m:o-i64:64-i128:128-n32:64-S128-Fn32"
assert original["experimental_kagura_pipeline"]["k10_actual_llvm_link_warning_count"] == 0
assert original["experimental_kagura_pipeline"]["k10_required_link_warning_count"] == 0
assert original["experimental_kagura_pipeline"]["k10_required_metadata_source"] == "CLANG19_COMPILED_C_BITCODE_BOTH_TARGETS"
assert original["experimental_kagura_pipeline"]["k10_pinned_mvo_template_sha256"] == original["experimental_kagura_pipeline"]["k8_source_mvo_ir_sha256"]
assert original["experimental_kagura_pipeline"]["k10_stage_order"] == ["mvo", "genc", "fsplit", "ibr", "ci"]
assert original["experimental_kagura_pipeline"]["k10_host_two_function_vectors"] == 4096
assert original["experimental_kagura_pipeline"]["k10_ios_arm64"] == "OBJECT_BUILD_ONLY_NOT_EXECUTED"
assert original["experimental_kagura_pipeline"]["k10_composition_native"] == "MACOS_NATIVE_FIVE_COMPOSED_STAGES_ZERO_LINK_WARNINGS_VERIFIED"
assert original["experimental_kagura_pipeline"]["k11_ios_ipa_status"] == "STAGED_MANUAL_IOS_IPA_CI_NOT_VERIFIED"
assert original["experimental_kagura_pipeline"]["k11_runtime_locator"] == "scripts/custom_ollvm/kagura_k11/ci_runtime_resolver.py"
assert original["experimental_kagura_pipeline"]["k11_runtime_closure_script"] == "scripts/custom_ollvm/kagura_k11/ci_runtime_closure.py"
assert original["experimental_kagura_pipeline"]["k11_ios_runtime_dependency_closure"] == "RECURSIVE_REAL_PINNED_C_IOS_ARM64_NM_DEFINITIONS_NO_SHIMS"
assert original["experimental_kagura_pipeline"]["k11_last_observed_ci_failure"] == "IOS_LD_UNDEFINED_KAGURA_IMAGE_LIST_CONTAINS_AND_SUSPICIOUS_IMAGE_PATTERNS"
assert original["experimental_kagura_pipeline"]["k11_bundle_id"] == "com.duodash.research.kagurafivelab"
assert original["experimental_kagura_pipeline"]["k11_final_pass_order"] == ["mvo", "genc", "fsplit", "ibr", "ci"]
assert original["experimental_kagura_pipeline"]["k11_vectors_per_function"] == 4096
assert original["experimental_kagura_pipeline"]["k11_expected_c_checksum"] == "25a3318e3d7d6525"
assert original["experimental_kagura_pipeline"]["k11_expected_mvo_checksum"] == "64e61045bbc4a250"
assert original["experimental_kagura_pipeline"]["k11_upstream_ios_ci_runtime"] == "PINNED_C_SOURCE_CROSS_COMPILED_FAIL_CLOSED"
assert original["experimental_kagura_pipeline"]["k11_macho_arch"] == "arm64_SUBTYPE0_MH_EXECUTE_LC_UUID"
assert original["experimental_kagura_pipeline"]["k11_device_runtime"] == "NOT_TESTED"
assert original["experimental_kagura_pipeline"]["k11_arm64e_pac"] == "NOT_TESTED"
assert original["experimental_kagura_pipeline"]["k11_security_attestation"] is False
assert len(status["registry_sha256"]) == 64

negative_mutations = (
    lambda x: x.update(production_pass_families=["split", "bcf", "fla", "sub", "ce"]),
    lambda x: x.update(production_cpu_scope="arm64e"),
    lambda x: x.update(pinned_commit="UNPINNED"),
    lambda x: x["separate_llvm_plugin_experiments"][0].update(provider="Obfuscator"),
    lambda x: x["separate_llvm_plugin_experiments"][0].update(
        state="merged_into_production_ollvm"
    ),
    lambda x: x["next_llvm_pass_candidates"][0].update(
        state="implemented_in_custom_obfuscator"
    ),
    lambda x: x["next_llvm_pass_candidates"][0].update(prerequisites=[]),
    lambda x: x["source_level_only"][0].update(
        status="integrated_real_llvm_pass"
    ),
    lambda x: x["source_level_only"][0].update(path="not-existing-llvm-pass.cpp"),
    lambda x: x["next_llvm_pass_candidates"][1].update(priority=1),
    lambda x: x["next_llvm_pass_candidates"][1].update(**{"pass": "string_ce"}),
    lambda x: x["experimental_kagura_pipeline"].update(status="MERGED_PRODUCTION"),
    lambda x: x["experimental_kagura_pipeline"].update(production_merge=True),
    lambda x: x["experimental_kagura_pipeline"].update(vm_state="VM_PAC_PASS"),
    lambda x: x["experimental_kagura_pipeline"]["passes"].append("kagura-vm"),
    lambda x: x["experimental_kagura_pipeline"].update(k1_native_ci_status="PASS_WITHOUT_RUN"),
    lambda x: x["experimental_kagura_pipeline"]["k1_extra_passes"].append("kagura-vm"),
    lambda x: x["experimental_kagura_pipeline"].update(k2_scope_type="STRICT_FUNCTION_WHITELIST_VERIFIED"),
    lambda x: x["experimental_kagura_pipeline"].update(k2_scope_and_benchmark_status="IOS_DEVICE_PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k3_interleaved_benchmark_status="MACOS_NATIVE_PASS_WITHOUT_ARTIFACT"),
    lambda x: x["experimental_kagura_pipeline"].update(k3_balanced_rounds=2),
    lambda x: x["experimental_kagura_pipeline"].update(k3_samples_per_variant=11),
    lambda x: x["experimental_kagura_pipeline"].update(ios_arm64_kagura_trollstore_pilot="ON_DEVICE_PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k6_selective_vm_status="PASS_WITHOUT_MACOS_CI"),
    lambda x: x["experimental_kagura_pipeline"].update(k6_vm_device_runtime="IOS_PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k6_vm_target="dd_vm_guard_protected"),
    lambda x: x["experimental_kagura_pipeline"].update(k7_vm_trollstore_ipa_status="IOS_DEVICE_PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k8_five_pass_status="IOS_PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k8_five_pass_status="STAGED_MACOS_CI_NOT_VERIFIED"),
    lambda x: x["experimental_kagura_pipeline"].update(k8_artifact_zip_sha256="0" * 64),
    lambda x: x["experimental_kagura_pipeline"].update(k8_artifact_entry_count=73),
    lambda x: x["experimental_kagura_pipeline"].update(k8_independent_artifact_checks_passed=0),
    lambda x: x["experimental_kagura_pipeline"].update(k8_native_parity_status="PASS_WITHOUT_LOG"),
    lambda x: x["experimental_kagura_pipeline"].update(k8_native_c_fixture_checksum="0" * 16),
    lambda x: x["experimental_kagura_pipeline"].update(k8_native_mvo_fixture_checksum="0" * 16),
    lambda x: x["experimental_kagura_pipeline"].update(k8_source_fixture_sha256="0" * 64),
    lambda x: x["experimental_kagura_pipeline"].update(k8_source_runner_sha256="0" * 64),
    lambda x: x["experimental_kagura_pipeline"].update(k8_source_mvo_ir_sha256="0" * 64),
    lambda x: x["experimental_kagura_pipeline"].update(k8_artifact_review="docs/no-such-K8-artifact.md"),
    lambda x: x["experimental_kagura_pipeline"].update(k8_ios_arm64="DEVICE_RUNTIME_VERIFIED"),
    lambda x: x["experimental_kagura_pipeline"].update(k8_combined_five_passes="COMBINED_PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k9_composition_status="FULL_PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k9_artifact_zip_sha256="0" * 64),
    lambda x: x["experimental_kagura_pipeline"].update(k9_artifact_entry_count=74),
    lambda x: x["experimental_kagura_pipeline"].update(k9_independent_artifact_checks_passed=0),
    lambda x: x["experimental_kagura_pipeline"].update(k9_artifact_review="docs/no-k9-review.md"),
    lambda x: x["experimental_kagura_pipeline"].update(k9_runner_sha256="0" * 64),
    lambda x: x["experimental_kagura_pipeline"].update(k9_llvm_link_warnings="NONE"),
    lambda x: x["experimental_kagura_pipeline"].update(k9_composition_native="MACOS_PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k9_stage_order=["ci", "ibr", "mvo", "genc", "fsplit"]),
    lambda x: x["experimental_kagura_pipeline"]["k9_stage_order"].append("vm"),
    lambda x: x["experimental_kagura_pipeline"].update(k9_merged_function_names=["dd_k8_evaluate"]),
    lambda x: x["experimental_kagura_pipeline"].update(k9_native_vectors_per_function=128),
    lambda x: x["experimental_kagura_pipeline"].update(k9_c_checksum="0" * 16),
    lambda x: x["experimental_kagura_pipeline"].update(k9_mvo_checksum="0" * 16),
    lambda x: x["experimental_kagura_pipeline"].update(k9_ios_arm64="RUN_ON_IPHONE"),
    lambda x: x["experimental_kagura_pipeline"].update(k9_performance="OPTIMIZED"),
    lambda x: x["experimental_kagura_pipeline"].update(k10_strict_link_metadata_status="MACOS_PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k10_strict_link_metadata_status="STAGED_MANUAL_STRICT_LLVM_LINK_CI_NOT_VERIFIED"),
    lambda x: x["experimental_kagura_pipeline"].update(k10_artifact_zip_sha256="0" * 64),
    lambda x: x["experimental_kagura_pipeline"].update(k10_artifact_entry_count=79),
    lambda x: x["experimental_kagura_pipeline"].update(k10_independent_artifact_checks_passed=0),
    lambda x: x["experimental_kagura_pipeline"].update(k10_artifact_review="docs/no-such-k10.md"),
    lambda x: x["experimental_kagura_pipeline"].update(k10_host_target_triple="arm64-apple-darwin23.6.0"),
    lambda x: x["experimental_kagura_pipeline"].update(k10_ios_target_triple="arm64-apple-macosx14.0.0"),
    lambda x: x["experimental_kagura_pipeline"].update(k10_both_target_datalayout=""),
    lambda x: x["experimental_kagura_pipeline"].update(k10_actual_llvm_link_warning_count=1),
    lambda x: x["experimental_kagura_pipeline"].update(k10_composition_native="IOS_PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k10_required_link_warning_count=1),
    lambda x: x["experimental_kagura_pipeline"].update(k10_required_metadata_source="HOST_TRIPLE_GUESSED"),
    lambda x: x["experimental_kagura_pipeline"].update(k10_pinned_mvo_template_sha256="0" * 64),
    lambda x: x["experimental_kagura_pipeline"].update(k10_stage_order=["ci", "mvo"]),
    lambda x: x["experimental_kagura_pipeline"].update(k10_host_two_function_vectors=128),
    lambda x: x["experimental_kagura_pipeline"].update(k10_ios_arm64="DEVICE_PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k10_on_device="PASS_NO_LOG"),
    lambda x: x["experimental_kagura_pipeline"].update(k11_ios_ipa_status="IOS_DEVICE_PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k11_runtime_locator="scripts/custom_ollvm/kagura_k9/pilot.py"),
    lambda x: x["experimental_kagura_pipeline"].update(k11_runtime_closure_script="scripts/custom_ollvm/kagura_k9/pilot.py"),
    lambda x: x["experimental_kagura_pipeline"].update(k11_ios_runtime_dependency_closure="FAKE_LD_STUB"),
    lambda x: x["experimental_kagura_pipeline"].update(k11_last_observed_ci_failure="NONE"),
    lambda x: x["experimental_kagura_pipeline"].update(k11_final_pass_order=["ci", "ibr"]),
    lambda x: x["experimental_kagura_pipeline"].update(k11_vectors_per_function=256),
    lambda x: x["experimental_kagura_pipeline"].update(k11_bundle_id="com.duodash.research.kaguralab"),
    lambda x: x["experimental_kagura_pipeline"].update(k11_expected_c_checksum="0" * 16),
    lambda x: x["experimental_kagura_pipeline"].update(k11_expected_mvo_checksum="0" * 16),
    lambda x: x["experimental_kagura_pipeline"].update(k11_upstream_ios_ci_runtime="SHIM_FAKE_RESOLVER"),
    lambda x: x["experimental_kagura_pipeline"].update(k11_macho_arch="arm64e"),
    lambda x: x["experimental_kagura_pipeline"].update(k11_device_runtime="DEVICE_VERIFIED_NO_LOG"),
    lambda x: x["experimental_kagura_pipeline"].update(k11_arm64e_pac="PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k11_security_attestation=True),
    lambda x: x["experimental_kagura_pipeline"].update(k11_workflow=".github/workflows/build.yml"),
    lambda x: x["experimental_kagura_pipeline"].update(k11_doc="docs/KAGURA_K10_LINK_METADATA.md"),
    lambda x: x["experimental_kagura_pipeline"].update(k10_workflow=".github/workflows/build.yml"),
    lambda x: x["experimental_kagura_pipeline"].update(k10_runner="scripts/custom_ollvm/kagura_k9/pilot.py"),
    lambda x: x["experimental_kagura_pipeline"].update(k10_doc="docs/KAGURA_K9_COMPOSITION.md"),
    lambda x: x["experimental_kagura_pipeline"].update(k9_workflow=".github/workflows/build.yml"),
    lambda x: x["experimental_kagura_pipeline"].update(k9_runner="scripts/test_custom_ollvm_pass_matrix.py"),
    lambda x: x["experimental_kagura_pipeline"].update(k9_doc="docs/KAGURA_K8_ARTIFACT_REVIEW.md"),
    lambda x: x["experimental_kagura_pipeline"]["k8_five_passes"].append("vm"),
    lambda x: x["experimental_kagura_pipeline"]["k8_pass_kinds"].update(ci="function"),
    lambda x: x["experimental_kagura_pipeline"].update(k7_vm_on_device="PASS_WITHOUT_LOG"),
    lambda x: x["experimental_kagura_pipeline"].update(k7_shared_device_log_status="IOS_PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k7_device_benchmark_status="VERIFIED_FROM_FRAGMENT"),
    lambda x: x["experimental_kagura_pipeline"].update(k7_device_median_paired_overhead_ratio=1.0),
    lambda x: x["experimental_kagura_pipeline"].update(k7_device_log_sha256="0" * 64),
    lambda x: x["experimental_kagura_pipeline"].update(k7_vm_bundle_id="com.duodash.research.kaguralab"),
    lambda x: x["experimental_kagura_pipeline"].update(k7_app_macho_uuid="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
    lambda x: x["experimental_kagura_pipeline"].update(k7_ipa_sha256="0" * 64),
    lambda x: x["experimental_kagura_pipeline"].update(k7_macos_median_paired_overhead_ratio=1.0),
    lambda x: x["experimental_kagura_pipeline"].update(ios_arm64_kagura_pilot_on_device="PASS_WITHOUT_LOG"),
    lambda x: x["experimental_kagura_pipeline"]["ios_arm64_kagura_pilot_pipeline"].append("vm"),
)
for idx, change in enumerate(negative_mutations):
    data = copy.deepcopy(original)
    change(data)
    try:
        audit.audit(data)
    except (AssertionError, KeyError, ValueError):
        pass
    else:
        raise AssertionError(f"False compiler-pass coverage accepted #{idx}")

# Do not let a valid-looking registry hide unrecognized toggles in policy.json.
with tempfile.TemporaryDirectory() as folder:
    temp = Path(folder)
    for path in (
        "policy.json", "scripts/demo_ollvm/policy.json",
        "scripts/verify_ollvm_log.py", "scripts/demo_ollvm/verify.py",
        "scripts/demo_ollvm/compiler_select.py",
        ".github/workflows/build.yml", ".github/workflows/demo-ollvm-evaluation.yml",
        ".github/workflows/hikari-evaluation.yml",
        "scripts/hikari_eval/policy.json",
    ):
        dest = temp / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((ROOT / path).read_bytes())
    for entry in original["source_level_only"]:
        dest = temp / entry["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((ROOT / entry["path"]).read_bytes())
    fake_policy = json.loads((temp / "policy.json").read_text(encoding="utf-8"))
    fake_policy["policy_map"]["full_strength_eval"]["enable_ce"] = True
    (temp / "policy.json").write_text(json.dumps(fake_policy), encoding="utf-8")
    try:
        audit.audit(original, temp)
    except AssertionError as exc:
        assert "unknown/missing OLLVM keys" in str(exc)
    else:
        raise AssertionError("Phantom CE compiler pass was silently accepted")

demo_ci = (ROOT / ".github/workflows/demo-ollvm-evaluation.yml").read_text(encoding="utf-8")
hikari_ci = (ROOT / ".github/workflows/hikari-evaluation.yml").read_text(encoding="utf-8")
assert "python3 scripts/test_custom_ollvm_pass_matrix.py" in demo_ci
assert "python3 ../test_custom_ollvm_pass_matrix.py" in hikari_ci
assert "workflow_dispatch:" in demo_ci and "workflow_dispatch:" in hikari_ci
assert "scripts/custom_ollvm/pass_registry.json" not in (
    ROOT / "Makefile"
).read_text(encoding="utf-8"), "Production OLLVM Makefile must remain independent"
print("CUSTOM_OLLVM_PASS_MATRIX_PASS: 4 verified OLLVM vs separate Hikari/6 source "
      "canaries; 12 forbidden new-pass/ABI/policy mutations rejected")
