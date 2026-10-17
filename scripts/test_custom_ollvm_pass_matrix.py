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
