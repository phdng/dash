#!/usr/bin/env python3
"""Cheap cross-platform checks for the opt-in OLLVM configuration."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
policy = json.loads((ROOT / "policy.json").read_text(encoding="utf-8"))
assert policy["policy_map"]["duodash_light"]["enable_sub"] is True
assert policy["policy_map"]["duodash_light"]["sub_times"] == 1
rules = policy["policies"]
assert len(rules) == 1
rule = rules[0]
assert rule["policy"] == "duodash_light"
assert rule["func"] == ".*"
pattern = re.compile(rule["module"])
for selected in (
    "re/RECONSTRUCTION/LicenseHelpers.m",
    "re/RECONSTRUCTION/PrefsResolver.m",
    "scripts/ollvm_probe.c",
):
    assert (ROOT / selected).is_file(), selected
    assert pattern.fullmatch(str(ROOT / selected).replace("\\", "/")), selected
for excluded in (
    "re/RECONSTRUCTION/HostFlowAdapter.m",
    "re/RECONSTRUCTION/ReconstructionRuntime.m",
):
    assert not pattern.fullmatch(str(ROOT / excluded).replace("\\", "/")), excluded

makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
assert "ifeq ($(OLLVM),1)" in makefile
assert "-fpass-plugin=$(OLLVM_PLUGIN)" in makefile

workflow = (ROOT / ".github/workflows/build.yml").read_text(encoding="utf-8")
assert "default: true" in workflow, "OLLVM must be enabled for manual dispatch by default"
assert (
    "OLLVM_ENABLED: ${{ github.event_name != 'workflow_dispatch' || inputs.ollvm == true }}"
    in workflow
), "Push and PR runs must enable OLLVM without workflow_dispatch inputs"
assert "if: ${{ inputs.ollvm == true }}" not in workflow, "Legacy skipped steps remain"
assert "if: ${{ inputs.ollvm != true }}" not in workflow, "Legacy standard-only condition remains"
assert workflow.count("if: ${{ env.OLLVM_ENABLED == 'true' }}") == 5
positions = [
    workflow.index("name: Build tweak (standard)"),
    workflow.index("name: Upload standard artifact"),
    workflow.index("name: Install LLVM 19 and compile pinned OLLVM plugin"),
    workflow.index("name: Verify OLLVM actually transforms iOS arm64 code"),
    workflow.index("name: Build tweak (OLLVM)"),
    workflow.index("name: Upload OLLVM artifact"),
]
assert positions == sorted(positions), "Artifacts must be uploaded in the intended order"
assert "name: DuoDashReconstruction-OLLVM" in workflow
assert "name: DuoDashReconstruction\n" in workflow
print("OLLVM integration policy and workflow dispatch: PASS")
