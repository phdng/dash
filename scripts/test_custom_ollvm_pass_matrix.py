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
assert original["experimental_kagura_pipeline"]["k11_ios_ipa_status"] == "CI_ARTIFACT_HASHES_VERIFIED_IOS_ARM64_FIVE_PASS_LAB"
assert original["experimental_kagura_pipeline"]["k11_artifact_zip_sha256"] == "e004ea806724659afc9c7fe77efdfe954e8083e1fef10fd75275992405ad45a9"
assert original["experimental_kagura_pipeline"]["k11_artifact_entry_count"] == 119
assert original["experimental_kagura_pipeline"]["k11_independent_artifact_checks_passed"] == 331
assert original["experimental_kagura_pipeline"]["k11_artifact_review"] == "docs/KAGURA_K11_ARTIFACT_AND_DEVICE_REVIEW.md"
assert original["experimental_kagura_pipeline"]["k11_ipa_sha256"] == "57fe287ee04503c9bf5b64e8f7ed2589ec0b22a5c80fdcb035855b8781fa31d4"
assert original["experimental_kagura_pipeline"]["k11_app_binary_sha256"] == "a6b01f4df5c1128e2e8f24f13cde786557b354fd9c07b8ed6a8c8a5103899692"
assert original["experimental_kagura_pipeline"]["k11_app_macho_uuid"] == "580390ef-6ba0-357c-a1d7-a0678e3d27ff"
assert original["experimental_kagura_pipeline"]["k11_final_ios_object_sha256"] == "087ad94d637a8e4ac4f58b878517069fa755750088ef4fdcabd7436f4b86c682"
assert original["experimental_kagura_pipeline"]["k11_runtime_dependency_source"] == "runtime/core/imagelist.c"
assert original["experimental_kagura_pipeline"]["k11_runtime_dependency_object_sha256"] == "d026148dac9995954c61160d5864e94176e3eb712f4b027cb26a7c4d2b582530"
assert original["experimental_kagura_pipeline"]["k11_runtime_locator"] == "scripts/custom_ollvm/kagura_k11/ci_runtime_resolver.py"
assert original["experimental_kagura_pipeline"]["k11_runtime_closure_script"] == "scripts/custom_ollvm/kagura_k11/ci_runtime_closure.py"
assert original["experimental_kagura_pipeline"]["k11_ios_runtime_dependency_closure"] == "RECURSIVE_REAL_PINNED_C_IOS_ARM64_NM_DEFINITIONS_NO_SHIMS"
assert original["experimental_kagura_pipeline"]["k11_last_observed_ci_failure"] == "IOS_ARM64_NM_J_REJECTED_OBJC_SELECTOR_COLON"
assert original["experimental_kagura_pipeline"]["k11_bundle_id"] == "com.duodash.research.kagurafivelab"
assert original["experimental_kagura_pipeline"]["k11_final_pass_order"] == ["mvo", "genc", "fsplit", "ibr", "ci"]
assert original["experimental_kagura_pipeline"]["k11_vectors_per_function"] == 4096
assert original["experimental_kagura_pipeline"]["k11_expected_c_checksum"] == "25a3318e3d7d6525"
assert original["experimental_kagura_pipeline"]["k11_expected_mvo_checksum"] == "64e61045bbc4a250"
assert original["experimental_kagura_pipeline"]["k11_upstream_ios_ci_runtime"] == "PINNED_C_SOURCE_CROSS_COMPILED_FAIL_CLOSED"
assert original["experimental_kagura_pipeline"]["k11_macho_arch"] == "arm64_SUBTYPE0_MH_EXECUTE_LC_UUID"
assert original["experimental_kagura_pipeline"]["k11_device_runtime"] == "USER_SHARED_TEXT_PARITY_AND_UUID_VALIDATED_NOT_ATTESTED"
assert original["experimental_kagura_pipeline"]["k11_shared_device_log_status"] == "VALIDATED_EXACT_NINE_LINE_UUID_CHECKSUM_VS_CI_IPA"
assert original["experimental_kagura_pipeline"]["k11_device_log_sha256"] == "b61d53c870a7553564a85eb769bcbcb6717b714590fa9ef691738e618b38987b"
assert original["experimental_kagura_pipeline"]["k11_device_log_review"] == "docs/KAGURA_K11_ARTIFACT_AND_DEVICE_REVIEW.md"
assert original["experimental_kagura_pipeline"]["k11_arm64e_pac"] == "NOT_TESTED"
assert original["experimental_kagura_pipeline"]["k11_security_attestation"] is False
assert original["experimental_kagura_pipeline"]["k12_status"] == "PINNED_REGISTRY_AND_OPT_ARTIFACT_REPLAY_VERIFIED_NOT_NATIVE"
assert original["experimental_kagura_pipeline"]["k12_artifact_review"] == "docs/KAGURA_K12_ARTIFACT_REVIEW.md"
assert original["experimental_kagura_pipeline"]["k12_artifact_zip_sha256"] == "6d827807db583c8581d218da2dfc41f7fe784ea607dddd83edd399a04718b0ca"
assert original["experimental_kagura_pipeline"]["k12_artifact_zip_entry_count"] == 147
assert original["experimental_kagura_pipeline"]["k12_artifact_file_backed_checks"] == 2029
assert original["experimental_kagura_pipeline"]["k12_pinned_registry_source_sha256"] == "6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa"
assert original["experimental_kagura_pipeline"]["k12_pinned_registered_pass_count"] == 36
assert original["experimental_kagura_pipeline"]["k12_remaining_unverified_pass_count"] == 23
assert original["experimental_kagura_pipeline"]["k12_bitcode_container_in_artifact"] == "LLVM_WRAPPED_BITCODE_BOTH_TARGETS"
assert original["experimental_kagura_pipeline"]["k12_opt_both_targets_ir_delta"] == ["kagura-tamper","kagura-anti-debug","kagura-honey","kagura-sv","kagura-cse-break","kagura-dci","kagura-telemetry","kagura-bbcheck"]
assert original["experimental_kagura_pipeline"]["k12_opt_both_targets_no_ir_delta"] == ["kagura-pac","kagura-str-aes","kagura-wstr","kagura-string-split","kagura-objc","kagura-jni","kagura-lt","kagura-pe","kagura-elt"]
assert original["experimental_kagura_pipeline"]["k12_opt_infra_skipped"] == ["kagura-autoselect","kagura-config","kagura-dwarf-control","kagura-symmap","kagura-vtp","kagura-audit"]
assert original["experimental_kagura_pipeline"]["k12_workflow"] == ".github/workflows/kagura-k12-remaining-inventory.yml"
assert original["experimental_kagura_pipeline"]["k12_inventory"] == "scripts/custom_ollvm/kagura_k12/inventory.py"
assert original["experimental_kagura_pipeline"]["k12_smoke"] == "scripts/custom_ollvm/kagura_k12/smoke.py"
assert original["experimental_kagura_pipeline"]["k12_artifact_auditor"] == "scripts/custom_ollvm/kagura_k12/audit.py"
assert original["experimental_kagura_pipeline"]["k12_artifact_audit_test"] == "scripts/test_kagura_k12_opt_audit.py"
assert original["experimental_kagura_pipeline"]["k12_ir_delta_gate"] == "FILE_BACKED_NORMALIZED_LLVM_IR_SHA_IGNORE_MODULEID"
assert original["experimental_kagura_pipeline"]["k12_bitcode_container_gate"] == "RAW_OR_SPEC_VALIDATED_LLVM_WRAPPER_WITH_EMBEDDED_RAW_MAGIC"
assert original["experimental_kagura_pipeline"]["k12_portable_test"] == "scripts/test_kagura_k12_remaining_inventory.py"
assert original["experimental_kagura_pipeline"]["k12_doc"] == "docs/KAGURA_K12_REMAINING_PASS_INVENTORY.md"
assert original["experimental_kagura_pipeline"]["k12_upstream_commit"] == "ac2136ee0408677cf7cdee55307e9b16edd5f4d5"
assert original["experimental_kagura_pipeline"]["k12_historically_evidenced_distinct_pass_count"] == 13
assert original["experimental_kagura_pipeline"]["k12_actual_pinned_remaining_names"] == ["kagura-pac","kagura-str-aes","kagura-wstr","kagura-string-split","kagura-tamper","kagura-objc","kagura-jni","kagura-anti-debug","kagura-honey","kagura-sv","kagura-cse-break","kagura-lt","kagura-dci","kagura-pe","kagura-telemetry","kagura-bbcheck","kagura-elt","kagura-autoselect","kagura-config","kagura-dwarf-control","kagura-symmap","kagura-vtp","kagura-audit"]
assert original["experimental_kagura_pipeline"]["k12_new_native_passes_verified"] == 0
assert original["experimental_kagura_pipeline"]["k12_iphone_runtime"] == "NOT_TESTED"
assert original["experimental_kagura_pipeline"]["k12_arm64e_pac"] == "NOT_TESTED"
assert original["experimental_kagura_pipeline"]["k12_production_merge"] is False
assert original["experimental_kagura_pipeline"]["k13_status"] == "MACOS_NATIVE_AND_IOS_OBJECT_ARTIFACT_VERIFIED_NO_DEVICE"
assert original["experimental_kagura_pipeline"]["k13_artifact_review"] == "docs/KAGURA_K13_ARTIFACT_REVIEW.md"
assert original["experimental_kagura_pipeline"]["k13_artifact_zip_sha256"] == "2f18e54d3cc6f421ab997d96a162fd6b5869a4f5c78e62f739943e2238ce64f3"
assert original["experimental_kagura_pipeline"]["k13_mac_arm64_baseline_object_sha256"] == "d8e1a34f8696d039c6133657eb10969f481c89bf0070dcb9870925a2e4fa09a5"
assert original["experimental_kagura_pipeline"]["k13_mac_arm64_protected_object_sha256"] == "02caa3bc92b5a927463229d0de9854f3422b6ce24d90741175a4ad040464e839"
assert original["experimental_kagura_pipeline"]["k13_ios_arm64_baseline_object_sha256"] == "43b263d0d1eb5b8194dd944e86e1c49ce57061f6ec283dd39f654f67a0c2ec71"
assert original["experimental_kagura_pipeline"]["k13_ios_arm64_protected_object_sha256"] == "a1dea3f6cdb66d4f62d40dcfa7d32608049082700b2c78f7f69854c6b864cc62"
assert original["experimental_kagura_pipeline"]["k13_native_checksum"] == "25a3318e3d7d6525"
assert original["experimental_kagura_pipeline"]["k13_artifact_entry_count"] == 41
assert original["experimental_kagura_pipeline"]["k13_independent_artifact_checks_passed"] == 422
assert original["experimental_kagura_pipeline"]["k13_candidate"] == "kagura-cse-break"
assert original["experimental_kagura_pipeline"]["k13_pass_class"] == "kagura::CSEBreakPass"
assert original["experimental_kagura_pipeline"]["k13_workflow"] == ".github/workflows/kagura-k13-cse-break-native.yml"
assert original["experimental_kagura_pipeline"]["k13_pilot"] == "scripts/custom_ollvm/kagura_k13/pilot.py"
assert original["experimental_kagura_pipeline"]["k13_audit"] == "scripts/custom_ollvm/kagura_k13/audit.py"
assert original["experimental_kagura_pipeline"]["k13_portable_test"] == "scripts/test_kagura_k13_native.py"
assert original["experimental_kagura_pipeline"]["k13_doc"] == "docs/KAGURA_K13_CSE_BREAK_NATIVE_LAB.md"
assert original["experimental_kagura_pipeline"]["k13_pinned_registry_sha256"] == "6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa"
assert original["experimental_kagura_pipeline"]["k13_native_vectors_planned"] == 4096
assert original["experimental_kagura_pipeline"]["k13_native_result"] == "CI_MACOS_4096_PARITY_AND_BINARY_ARTIFACT_VALIDATED"
assert original["experimental_kagura_pipeline"]["k13_ios_arm64"] == "ARM64_SUBTYPE0_MH_OBJECT_ARTIFACT_VALIDATED_NOT_DEVICE"
assert original["experimental_kagura_pipeline"]["k13_iphone_runtime"] == "NOT_TESTED"
assert original["experimental_kagura_pipeline"]["k13_arm64e_pac"] == "NOT_TESTED"
assert original["experimental_kagura_pipeline"]["k13_production_merge"] is False
assert original["experimental_kagura_pipeline"]["k14_status"] == "IPA_AND_USER_SHARED_LOG_UUID_CHECKSUM_VERIFIED_NOT_ATTESTED"
assert original["experimental_kagura_pipeline"]["k14_artifact_review"] == "docs/KAGURA_K14_ARTIFACT_AND_DEVICE_REVIEW.md"
assert original["experimental_kagura_pipeline"]["k14_artifact_zip_sha256"] == "0ffbace0a56457a517bded16aa92d1a2e1455982901af5f39644c9140c87da47"
assert original["experimental_kagura_pipeline"]["k14_ipa_sha256"] == "8733e2f93001b6d1195581deea013688825a94aa1d4d29bbfb23814dd5f9716f"
assert original["experimental_kagura_pipeline"]["k14_app_binary_sha256"] == "584e9999d25a2642d818c0857a767173031868868df94d0e7de289176aa0cbd7"
assert original["experimental_kagura_pipeline"]["k14_app_macho_uuid"] == "7c0cb853-77aa-3ccb-9f20-560e5f40e587"
assert original["experimental_kagura_pipeline"]["k14_protected_ios_object_sha256"] == "a1dea3f6cdb66d4f62d40dcfa7d32608049082700b2c78f7f69854c6b864cc62"
assert original["experimental_kagura_pipeline"]["k14_user_shared_normalized_log_sha256"] == "a145013d104fc83b0369a9ff21175ec5f6e4097eb739de8b98601e9aea4360d6"
assert original["experimental_kagura_pipeline"]["k14_claimed_context"] == "IOS_DEVICE_USER_SHARED_TEXT_NOT_INDEPENDENT_ATTESTATION"
assert original["experimental_kagura_pipeline"]["k14_artifact_entry_count"] == 53
assert original["experimental_kagura_pipeline"]["k14_independent_artifact_checks_passed"] == 103
assert original["experimental_kagura_pipeline"]["k14_user_shared_device_log_lines"] == 8
assert original["experimental_kagura_pipeline"]["k14_iphone_execution_independently_observed"] is False
assert original["experimental_kagura_pipeline"]["k14_device_execution_cryptographically_attested"] is False
assert original["experimental_kagura_pipeline"]["k14_workflow"] == ".github/workflows/kagura-k14-cse-break-ios-ipa.yml"
assert original["experimental_kagura_pipeline"]["k14_app_bundle"] == "com.duodash.research.kaguracsebreaklab"
assert original["experimental_kagura_pipeline"]["k14_app_executable"] == "KaguraCSEBreakLab"
assert original["experimental_kagura_pipeline"]["k14_source"] == "scripts/custom_ollvm/kagura_k14/ios_probe.c"
assert original["experimental_kagura_pipeline"]["k14_uikit"] == "scripts/custom_ollvm/kagura_k14/ios_app_main.m"
assert original["experimental_kagura_pipeline"]["k14_info_plist"] == "scripts/custom_ollvm/kagura_k14/Info.plist"
assert original["experimental_kagura_pipeline"]["k14_build"] == "scripts/custom_ollvm/kagura_k14/build_ipa.sh"
assert original["experimental_kagura_pipeline"]["k14_package"] == "scripts/custom_ollvm/kagura_k14/package_ipa.py"
assert original["experimental_kagura_pipeline"]["k14_evidence"] == "scripts/custom_ollvm/kagura_k14/ipa_evidence.py"
assert original["experimental_kagura_pipeline"]["k14_device_audit"] == "scripts/custom_ollvm/kagura_k14/device_log_audit.py"
assert original["experimental_kagura_pipeline"]["k14_portable_test"] == "scripts/test_kagura_k14_ios_ipa.py"
assert original["experimental_kagura_pipeline"]["k14_doc"] == "docs/KAGURA_K14_CSE_BREAK_IOS_IPA_LAB.md"
assert original["experimental_kagura_pipeline"]["k14_pinned_registry_sha256"] == "6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa"
assert original["experimental_kagura_pipeline"]["k14_native_checksum_oracle"] == "25a3318e3d7d6525"
assert original["experimental_kagura_pipeline"]["k14_ipa_ci"] == "MACOS_UNSIGNED_IPA_OBJECT_UUID_SHA_ARTIFACT_VERIFIED"
assert original["experimental_kagura_pipeline"]["k14_iphone_runtime"] == "USER_SHARED_TEXT_PARITY_UUID_VALIDATED_NOT_ATTESTED"
assert original["experimental_kagura_pipeline"]["k14_arm64e_pac"] == "NOT_TESTED"
assert original["experimental_kagura_pipeline"]["k14_expected_device_vectors"] == 4096
assert original["experimental_kagura_pipeline"]["k14_production_merge"] is False
assert original["experimental_kagura_pipeline"]["k15_status"] == "MACOS_IOS_PROVIDER_ARTIFACT_VERIFIED_WEAK_ALWAYS_PASS_STUB_NOT_NATIVE_OR_SECURITY_PASS"
assert original["experimental_kagura_pipeline"]["k15_artifact_review"] == "docs/KAGURA_K15_ARTIFACT_REVIEW.md"
assert original["experimental_kagura_pipeline"]["k15_artifact_zip_sha256"] == "1f19d3d9eb58a87a9798d11082f3eaf4652e70987100084eb2c292d543bbd336"
assert original["experimental_kagura_pipeline"]["k15_provider_bb_check_source"] == "runtime/core/bb_check.c"
assert original["experimental_kagura_pipeline"]["k15_provider_bb_check_source_sha256"] == "2a87f559f2427c2de5217502c4d62abb1165fba34f5e1702982785dfacb24345"
assert original["experimental_kagura_pipeline"]["k15_provider_tamper_source"] == "runtime/core/tamper_response.c"
assert original["experimental_kagura_pipeline"]["k15_provider_tamper_source_sha256"] == "976cea2786438241b88f84c5c745f59aa669b683037ba81d7c09690339df5377"
assert original["experimental_kagura_pipeline"]["k15_provider_weak_macho_n_desc"] == "0x0080_N_WEAK_DEF_BOTH_TARGETS"
assert original["experimental_kagura_pipeline"]["k15_provider_uniqueness"] == "ONE_GENUINE_PROVIDER_EACH_REQUIRED_SYMBOL_BOTH_TARGETS"
assert original["experimental_kagura_pipeline"]["k15_provider_kagura_transitive"] == "NONE_FOR_TWO_SELECTED_PROVIDERS_BOTH_TARGETS"
assert original["experimental_kagura_pipeline"]["k15_runtime_bbcheck_behavior"] == "WEAK_ALWAYS_RETURNS_ONE_IGNORES_BLOCK_ID_EXPECTED"
assert original["experimental_kagura_pipeline"]["k15_runtime_tamper_response"] == "WEAK_ABORT_DEFAULT_APPLE_NO_EXECUTION_K15"
assert original["experimental_kagura_pipeline"]["k15_artifact_entry_count"] == 231
assert original["experimental_kagura_pipeline"]["k15_independent_file_backed_checks"] == 2609
assert original["experimental_kagura_pipeline"]["k15_runtime_candidate_sources_each_target"] == 22
assert original["experimental_kagura_pipeline"]["k15_runtime_compiled_candidates_each_target"] == 22
assert original["experimental_kagura_pipeline"]["k15_security_integrity_proven"] is False
assert original["experimental_kagura_pipeline"]["k15_candidate"] == "kagura-bbcheck"
assert original["experimental_kagura_pipeline"]["k15_pass_class"] == "kagura::BasicBlockChecksumPass"
assert original["experimental_kagura_pipeline"]["k15_pass_kind"] == "FN"
assert original["experimental_kagura_pipeline"]["k15_pass_enable_flag"] == "BBCheck"
assert original["experimental_kagura_pipeline"]["k15_workflow"] == ".github/workflows/kagura-k15-bbcheck-runtime-audit.yml"
assert original["experimental_kagura_pipeline"]["k15_pilot"] == "scripts/custom_ollvm/kagura_k15/pilot.py"
assert original["experimental_kagura_pipeline"]["k15_audit"] == "scripts/custom_ollvm/kagura_k15/audit.py"
assert original["experimental_kagura_pipeline"]["k15_portable_test"] == "scripts/test_kagura_k15_bbcheck.py"
assert original["experimental_kagura_pipeline"]["k15_doc"] == "docs/KAGURA_K15_BBCHECK_RUNTIME_RESEARCH.md"
assert original["experimental_kagura_pipeline"]["k15_pinned_registry_sha256"] == "6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa"
assert original["experimental_kagura_pipeline"]["k15_macos_native_parity"] == "NOT_TESTED_TAMPER_CALLBACK"
assert original["experimental_kagura_pipeline"]["k15_ios_arm64_object"] == "PINNED_BBCHECK_IR_MACHO_ARM64_OBJECT_ARTIFACT_VERIFIED_ONLY"
assert original["experimental_kagura_pipeline"]["k15_ios_ipa"] == "NOT_BUILT"
assert original["experimental_kagura_pipeline"]["k15_iphone_runtime"] == "NOT_TESTED"
assert original["experimental_kagura_pipeline"]["k15_arm64e_pac"] == "NOT_TESTED"
assert original["experimental_kagura_pipeline"]["k15_required_runtime_symbols"] == ["_kagura_bb_check", "_kagura_on_tamper_detected"]
assert original["experimental_kagura_pipeline"]["k15_production_merge"] is False
assert original["experimental_kagura_pipeline"]["k16_status"] == "STAGED_MANUAL_OFFLINE_POST_LINK_MACHO_TEXT_NOT_MACOS_VERIFIED"
assert original["experimental_kagura_pipeline"]["k16_mode"] == "OFFLINE_UNSIGNED_MACHO_TEXT_SECTION_SHA256_FEASIBILITY"
assert original["experimental_kagura_pipeline"]["k16_workflow"] == ".github/workflows/kagura-k16-offline-macho-text.yml"
assert original["experimental_kagura_pipeline"]["k16_measure"] == "scripts/custom_ollvm/kagura_k16/macho_measure.py"
assert original["experimental_kagura_pipeline"]["k16_test"] == "scripts/test_kagura_k16_offline_text.py"
assert original["experimental_kagura_pipeline"]["k16_doc"] == "docs/KAGURA_K16_OFFLINE_MACHO_TEXT.md"
assert original["experimental_kagura_pipeline"]["k16_required_section"] == "__TEXT,__text"
assert original["experimental_kagura_pipeline"]["k16_original_bbcheck"] == "BLOCKED_K15_WEAK_ALWAYS_PASS_STUB"
assert original["experimental_kagura_pipeline"]["k16_macos_ci"] == "NOT_TESTED"
assert original["experimental_kagura_pipeline"]["k16_ios_device_runtime"] == "NOT_TESTED"
assert original["experimental_kagura_pipeline"]["k16_arm64e_pac"] == "NOT_TESTED"
assert original["experimental_kagura_pipeline"]["k16_specimens"] == ["macos-baseline", "macos-cse-break", "KaguraCSEBreakLab.app/KaguraCSEBreakLab"]
assert original["experimental_kagura_pipeline"]["k16_reference_authenticated"] is False
assert original["experimental_kagura_pipeline"]["k16_runtime_verifier_implemented"] is False
assert original["experimental_kagura_pipeline"]["k16_per_block_integrity"] is False
assert original["experimental_kagura_pipeline"]["k16_security_integrity_proven"] is False
assert original["experimental_kagura_pipeline"]["k16_production_merge"] is False
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
    lambda x: x["experimental_kagura_pipeline"].update(k11_artifact_zip_sha256="0" * 64),
    lambda x: x["experimental_kagura_pipeline"].update(k11_artifact_entry_count=118),
    lambda x: x["experimental_kagura_pipeline"].update(k11_independent_artifact_checks_passed=0),
    lambda x: x["experimental_kagura_pipeline"].update(k11_ipa_sha256="0" * 64),
    lambda x: x["experimental_kagura_pipeline"].update(k11_app_binary_sha256="0" * 64),
    lambda x: x["experimental_kagura_pipeline"].update(k11_app_macho_uuid="00000000-0000-0000-0000-000000000000"),
    lambda x: x["experimental_kagura_pipeline"].update(k11_final_ios_object_sha256="0" * 64),
    lambda x: x["experimental_kagura_pipeline"].update(k11_runtime_dependency_source="FAKE_SOURCE"),
    lambda x: x["experimental_kagura_pipeline"].update(k11_runtime_dependency_object_sha256="0" * 64),
    lambda x: x["experimental_kagura_pipeline"].update(k11_artifact_review="docs/KAGURA_K10_LINK_METADATA.md"),
    lambda x: x["experimental_kagura_pipeline"].update(k11_device_log_sha256="0" * 64),
    lambda x: x["experimental_kagura_pipeline"].update(k11_shared_device_log_status="CRYPTOGRAPHIC_ATTESTED"),
    lambda x: x["experimental_kagura_pipeline"].update(k11_device_log_review="docs/KAGURA_K10_LINK_METADATA.md"),
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
    lambda x: x["experimental_kagura_pipeline"].update(k12_status="NEW_PASSES_NATIVE_PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_status="NATIVE_PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_status="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_status="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k16_status="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k16_mode="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k16_workflow="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k16_measure="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k16_test="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k16_doc="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k16_required_section="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k16_original_bbcheck="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k16_macos_ci="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k16_ios_device_runtime="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k16_arm64e_pac="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k16_specimens=["macos-baseline"]),
    lambda x: x["experimental_kagura_pipeline"].update(k16_reference_authenticated=True),
    lambda x: x["experimental_kagura_pipeline"].update(k16_runtime_verifier_implemented=True),
    lambda x: x["experimental_kagura_pipeline"].update(k16_per_block_integrity=True),
    lambda x: x["experimental_kagura_pipeline"].update(k16_security_integrity_proven=True),
    lambda x: x["experimental_kagura_pipeline"].update(k16_production_merge=True),
    lambda x: x["experimental_kagura_pipeline"].update(k15_artifact_review="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_artifact_zip_sha256="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_provider_bb_check_source="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_provider_bb_check_source_sha256="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_provider_tamper_source="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_provider_tamper_source_sha256="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_provider_weak_macho_n_desc="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_provider_uniqueness="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_provider_kagura_transitive="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_runtime_bbcheck_behavior="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_runtime_tamper_response="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_artifact_entry_count=0),
    lambda x: x["experimental_kagura_pipeline"].update(k15_independent_file_backed_checks=0),
    lambda x: x["experimental_kagura_pipeline"].update(k15_runtime_compiled_candidates_each_target=0),
    lambda x: x["experimental_kagura_pipeline"].update(k15_runtime_candidate_sources_each_target=0),
    lambda x: x["experimental_kagura_pipeline"].update(k15_security_integrity_proven=True),
    lambda x: x["experimental_kagura_pipeline"].update(k15_candidate="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_pass_class="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_pass_kind="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_pass_enable_flag="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_workflow="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_pilot="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_audit="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_portable_test="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_doc="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_pinned_registry_sha256="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_macos_native_parity="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_ios_arm64_object="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_ios_ipa="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_iphone_runtime="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_arm64e_pac="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k15_required_runtime_symbols=["_kagura_bb_check"]),
    lambda x: x["experimental_kagura_pipeline"].update(k15_production_merge=True),
    lambda x: x["experimental_kagura_pipeline"].update(k14_artifact_review="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_artifact_zip_sha256="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_ipa_sha256="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_app_binary_sha256="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_app_macho_uuid="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_protected_ios_object_sha256="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_user_shared_normalized_log_sha256="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_claimed_context="FORGED"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_artifact_entry_count=0),
    lambda x: x["experimental_kagura_pipeline"].update(k14_independent_artifact_checks_passed=0),
    lambda x: x["experimental_kagura_pipeline"].update(k14_user_shared_device_log_lines=7),
    lambda x: x["experimental_kagura_pipeline"].update(k14_iphone_execution_independently_observed=True),
    lambda x: x["experimental_kagura_pipeline"].update(k14_device_execution_cryptographically_attested=True),
    lambda x: x["experimental_kagura_pipeline"].update(k14_workflow="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_app_bundle="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_app_executable="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_source="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_uikit="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_info_plist="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_build="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_package="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_evidence="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_device_audit="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_portable_test="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_doc="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_pinned_registry_sha256="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_native_checksum_oracle="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_ipa_ci="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_iphone_runtime="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_arm64e_pac="FALSE_POSITIVE"),
    lambda x: x["experimental_kagura_pipeline"].update(k14_expected_device_vectors=4095),
    lambda x: x["experimental_kagura_pipeline"].update(k14_production_merge=True),
    lambda x: x["experimental_kagura_pipeline"].update(k13_artifact_review="FAKE"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_artifact_zip_sha256="FAKE"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_mac_arm64_baseline_object_sha256="FAKE"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_mac_arm64_protected_object_sha256="FAKE"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_ios_arm64_baseline_object_sha256="FAKE"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_ios_arm64_protected_object_sha256="FAKE"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_artifact_entry_count=0),
    lambda x: x["experimental_kagura_pipeline"].update(k13_independent_artifact_checks_passed=0),
    lambda x: x["experimental_kagura_pipeline"].update(k13_native_checksum="0"*16),
    lambda x: x["experimental_kagura_pipeline"].update(k13_candidate="kagura-pac"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_pass_class="kagura::OtherPass"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_workflow=".github/workflows/build.yml"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_pilot="scripts/custom_ollvm/kagura_k8/pilot.py"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_audit="scripts/custom_ollvm/kagura_k8/pilot.py"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_portable_test="scripts/test_kagura_k8_passes.py"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_doc="docs/KAGURA_K12_ARTIFACT_REVIEW.md"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_pinned_registry_sha256="0"*64),
    lambda x: x["experimental_kagura_pipeline"].update(k13_native_vectors_planned=0),
    lambda x: x["experimental_kagura_pipeline"].update(k13_native_result="PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_ios_arm64="IPHONE_TESTED"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_iphone_runtime="PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_arm64e_pac="PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k13_production_merge=True),
    lambda x: x["experimental_kagura_pipeline"].update(k12_artifact_zip_sha256="0" * 64),
    lambda x: x["experimental_kagura_pipeline"].update(k12_artifact_zip_entry_count=0),
    lambda x: x["experimental_kagura_pipeline"].update(k12_artifact_file_backed_checks=0),
    lambda x: x["experimental_kagura_pipeline"].update(k12_remaining_unverified_pass_count=0),
    lambda x: x["experimental_kagura_pipeline"].update(k12_opt_both_targets_ir_delta=["kagura-pac"]),
    lambda x: x["experimental_kagura_pipeline"].update(k12_opt_infra_skipped=[]),
    lambda x: x["experimental_kagura_pipeline"].update(k12_bitcode_container_in_artifact="RAW_ONLY"),
    lambda x: x["experimental_kagura_pipeline"].update(k12_artifact_review="docs/KAGURA_K11_IOS_IPA_LAB.md"),
    lambda x: x["experimental_kagura_pipeline"].update(k12_workflow=".github/workflows/build.yml"),
    lambda x: x["experimental_kagura_pipeline"].update(k12_inventory="scripts/custom_ollvm/kagura_k8/pilot.py"),
    lambda x: x["experimental_kagura_pipeline"].update(k12_smoke="scripts/custom_ollvm/kagura_k9/pilot.py"),
    lambda x: x["experimental_kagura_pipeline"].update(k12_artifact_auditor="scripts/custom_ollvm/kagura_k8/pilot.py"),
    lambda x: x["experimental_kagura_pipeline"].update(k12_artifact_audit_test="scripts/test_kagura_k8_passes.py"),
    lambda x: x["experimental_kagura_pipeline"].update(k12_ir_delta_gate="BITCODE_ONLY_DELTA_FALSE_PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k12_bitcode_container_gate="RAW_ONLY_REJECTS_IOS_WRAPPER"),
    lambda x: x["experimental_kagura_pipeline"].update(k12_portable_test="scripts/test_kagura_k11_ios_ipa.py"),
    lambda x: x["experimental_kagura_pipeline"].update(k12_doc="docs/KAGURA_K11_IOS_IPA_LAB.md"),
    lambda x: x["experimental_kagura_pipeline"].update(k12_upstream_commit="UNPINNED"),
    lambda x: x["experimental_kagura_pipeline"].update(k12_historically_evidenced_distinct_pass_count=99),
    lambda x: x["experimental_kagura_pipeline"].update(k12_actual_pinned_remaining_names=["kagura-all-pass"]),
    lambda x: x["experimental_kagura_pipeline"].update(k12_new_native_passes_verified=7),
    lambda x: x["experimental_kagura_pipeline"].update(k12_iphone_runtime="VERIFIED"),
    lambda x: x["experimental_kagura_pipeline"].update(k12_arm64e_pac="PASS"),
    lambda x: x["experimental_kagura_pipeline"].update(k12_production_merge=True),
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
