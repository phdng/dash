#!/usr/bin/env python3
"""Portable K1 per-pass evidence gates, not native Kagura compiler execution."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/custom_ollvm/kagura_max"
sys.path.insert(0, str(LAB))
file = LAB / "stage_pipeline.py"
spec = importlib.util.spec_from_file_location("kagura_k1", file)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

assert module.MAIN_SYMBOL == "dd_kagura_critical"
assert module.RANDOM_SEED.isdecimal()
assert [x[0] for x in module.PASS_STAGES] == [
    "str", "fla", "bcf", "sub", "co", "bbr", "bbs"
]
assert [x[1] for x in module.PASS_STAGES] == [
    "kagura-str", "function(kagura-fla)", "function(kagura-bcf)",
    "function(kagura-sub)", "function(kagura-co)",
    "function(kagura-bbr)", "function(kagura-bbs)"
]

before = (
    "source_filename = \"fixture.c\"\n"
    "define i64 @dd_kagura_critical(i64 %x, i64 %y) {\n"
    "entry:\n"
    "  %sum = add i64 %x, %y\n"
    "  ret i64 %sum\n"
    "}\n"
)
after = (
    "source_filename = \"fixture.c\"\n"
    "define i64 @dd_kagura_critical(i64 %x, i64 %y) {\n"
    "entry:\n"
    "  %p = xor i64 %x, 23\n"
    "  br label %merge\n"
    "merge:\n"
    "  %sum = add i64 %p, %y\n"
    "  ret i64 %sum\n"
    "}\n"
)
assert "ret i64 %sum" in module.function_body(before)
delta = module.analyze_delta(before, after, b"plain-bytes", b"protected", "fla")
assert delta["critical_function_ir_changed"] is True
assert delta["object_bytes_changed"] is True
assert delta["classification"] == "IR_AND_OBJECT_DELTA"
assert delta["critical_function_basic_blocks_after"] == 2
assert delta["critical_function_basic_blocks_before"] == 1
assert delta["no_obfuscation_strength_score"] is True
noop = module.analyze_delta(before, before, b"same", b"same", "bbr")
assert noop["classification"] == "NO_OBSERVED_IR_DELTA"
assert not noop["critical_function_ir_changed"]
ir_only = module.analyze_delta(before, after, b"same", b"same", "sub")
assert ir_only["classification"] == "IR_ONLY_DELTA"
obj_only = module.analyze_delta(before, before, b"before", b"after", "co")
assert obj_only["classification"] == "OBJECT_ONLY_DELTA_NOT_ATTRIBUTABLE"
try:
    module.function_body(before.replace("dd_kagura_critical", "objc_msgSend"))
except AssertionError:
    pass
else:
    raise AssertionError("Unexpected function accepted")

workflow = (ROOT / ".github/workflows/kagura-max-candidate.yml").read_text(
    encoding="utf-8"
)
for guard in (
    "workflow_dispatch:",
    "python3 scripts/test_kagura_k1_stages.py",
    "scripts/custom_ollvm/kagura_max/stage_pipeline.py",
    '--llvm "$KAGURA_LLVM"',
    '--plugin "$KAGURA_PLUGIN"',
    '--plain-bc "$KAGURA_OUT/host-plain.bc"',
    '--baseline-log "$KAGURA_OUT/host-plain.log"',
    '--runner-obj "$KAGURA_OUT/runner.o"',
    '--out "$KAGURA_OUT/stages"',
    'cat "$KAGURA_OUT/stages/kagura-k1-stage-report.json"',
    "DuoDash-Kagura-MAX-CANDIDATE-LLVM19-EXPERIMENTAL",
):
    assert guard in workflow, guard
assert workflow.index("Native LLVM19 IR passes") < workflow.index(
    "K1 inspect each real Kagura pass"
) < workflow.index("Cross-compile iOS arm64")
for forbidden in (
    "make clean package", "codesign -s", "ldid -S",
    "DEVELOPMENT_TEAM=", "PAC_STRIP", "devicectl device install",
):
    assert forbidden.lower() not in workflow.lower()

source = file.read_text(encoding="utf-8")
for required in (
    "-debug-pass-manager",
    "Running pass:",
    "-kagura-seed=",
    "native_8192_parity",
    "NO_OBSERVED_IR_DELTA",
    "IR_ONLY_DELTA",
    "OBJECT_ONLY_DELTA_NOT_ATTRIBUTABLE",
    "static_analysis_impossibility_claim",
    "production_crane_unchanged",
    "arm64_ios_device_runtime",
    "KAGURA_K1_STAGE_AUDIT_PASS",
):
    assert required in source, required
assert "VM" not in str(module.PASS_STAGES)
assert "arm64e" not in str(module.PASS_STAGES)

print("KAGURA_K1_STAGED_PORTABLE_PASS: 7 actual opt pass routes, "
      "IR/object contribution classification, fail-closed scope")
