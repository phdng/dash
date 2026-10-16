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
print("OLLVM integration policy: PASS")
