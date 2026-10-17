#!/usr/bin/env python3
"""Portable K9 fail-closed source and synthetic IR gates (NOT macOS native)."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
K9 = ROOT / "scripts/custom_ollvm/kagura_k9"
spec = importlib.util.spec_from_file_location("k9_composition", K9 / "pilot.py")
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
sys.modules["k9_composition"] = mod
spec.loader.exec_module(mod)


def rejects(fn, name: str) -> None:
    try:
        fn()
    except (ValueError, AssertionError):
        return
    raise AssertionError(f"K9 rejected-negative test instead accepted {name}")


assert mod.STAGES == ("mvo", "genc", "fsplit", "ibr", "ci")
assert mod.SEED == "82712"
assert mod.UPSTREAM_PIN == "ac2136ee0408677cf7cdee55307e9b16edd5f4d5"
assert mod.k8.mvo_expected_checksum() == mod.K8_MVO_DIGEST
base_mvo = (ROOT / "scripts/custom_ollvm/kagura_k8/mvo.ll").read_text()
for triple in ("arm64-apple-ios15.0", "arm64-apple-darwin23.6.0"):
    ir = mod.mvo_module(base_mvo, triple)
    assert 'target triple = "' + triple + '"' in ir
    assert "define i64 @dd_k9_mvo_probe(" in ir
    assert "define i64 @dd_k8_evaluate(" not in ir
    mod.k8.validate_mvo_input_ir(ir)
rejects(lambda: mod.mvo_module(base_mvo + "\ndefine i64 @dd_k8_evaluate(i64 %n, i64 %s) {\nret i64 0\n}\n",
                              "arm64-apple-ios15.0"), "duplicate MVO functions")
rejects(lambda: mod.mvo_module(base_mvo.replace("alloca i64", "alloca ptr"),
                              "arm64-apple-ios15.0"), "MVO without alloca")

C_BASE = ("define i64 @dd_k8_evaluate(i64 %a, i64 %b) {\n"
          "entry:\n"
          "  %x = load volatile i64, ptr @dd_k8_genc_scalar, align 8\n"
          "  ret i64 %a\n}\n"
          "define i64 @dd_k9_mvo_probe(i64 %a, i64 %b) {\n"
          "entry:\n"
          "  %slot = alloca i64, align 8\n"
          "  store volatile i64 %a, ptr %slot, align 8\n"
          "  %value = load volatile i64, ptr %slot, align 8\n"
          "  ret i64 %value\n}\n"
          "@dd_k8_genc_scalar = internal constant i64 21\n")
mod.validate_merged(C_BASE)
rejects(lambda: mod.validate_merged(C_BASE.replace("define i64 @dd_k9_mvo_probe", "define i64 @missing")),
        "merged module with missing MVO ABI")
rejects(lambda: mod.validate_merged(C_BASE.replace("  %slot = alloca i64, align 8\n", "")),
        "merged module with no MVO alloca")
rejects(lambda: mod.validate_merged(C_BASE.replace("@dd_k8_genc_scalar = internal constant i64 21\n", "")),
        "merged module with missing GENC global")

added = {
    "mvo": "  %mixed.mvo = xor i64 %value, 42\n"
           "  %value.mvo = xor i64 %value, 42\n",
    "genc": "  %value.dec = xor i64 %value, 991\n",
    "fsplit": "define internal i64 @__kg_dd_k8_evaluate_bb6(i64 %x) {\nret i64 %x\n}\n",
    "ibr": "@__kagura_fptr_0 = private global ptr @dd_k8_evaluate\n",
    "ci": "@__kagura_thunk_table = internal global [1 x ptr] zeroinitializer\n"
          "declare ptr @kagura_rtld_default_handle()\n",
}
for name in mod.STAGES:
    marker = added[name]
    trace = f"Running pass: kagura::{mod.k8.CANDIDATES[name][1]} on dd_k8_evaluate\n"
    before = C_BASE
    after = C_BASE + marker
    mod.validate_stage(name, before, after, b"original Mach-O", b"modified Mach-O", trace)
    rejects(lambda: mod.validate_stage(name, before, after, b"same", b"same", trace),
            f"{name}: fake object delta")
    rejects(lambda: mod.validate_stage(name, before, before, b"old", b"new", trace),
            f"{name}: fake IR delta")
    rejects(lambda: mod.validate_stage(name, before, after, b"old", b"new", ""),
            f"{name}: fake trace")
    rejects(lambda: mod.validate_stage(name, before,
            after.replace("dd_k9_mvo_probe", "dd_k9_dropped"),
            b"old", b"new", trace), f"{name}: hidden ABI removal")

log = ("DD_K9_SCHEMA=1\nDD_K9_VECTORS_PER_FUNCTION=4096\n"
       f"DD_K9_C_CHECKSUM={mod.K8_C_DIGEST}\n"
       f"DD_K9_MVO_CHECKSUM={mod.K8_MVO_DIGEST}\nDD_K9_COMPLETE=PASS\n")
assert mod.validate_logs(log) == (mod.K8_C_DIGEST, mod.K8_MVO_DIGEST)
rejects(lambda: mod.validate_logs(log.replace("4096", "4095")), "short native vectors")
rejects(lambda: mod.validate_logs(log.replace(mod.K8_C_DIGEST, "0" * 16)), "C wrong digest")
rejects(lambda: mod.validate_logs(log.replace(mod.K8_MVO_DIGEST, "0" * 16)), "MVO wrong digest")
rejects(lambda: mod.validate_logs(log.replace("DD_K9_COMPLETE=PASS", "DD_K9_COMPLETE=FAIL")),
        "incomplete")
rejects(lambda: mod.validate_logs(log + "fake extra output"), "tainted native log")

pins = mod.verify_inputs()
assert len(pins) == 3 and all(len(s) == 64 for s in pins.values())
runner = (K9 / "runner.c").read_text(encoding="utf-8")
assert "i < 4096U" in runner
assert "dd_k9_mvo_probe" in runner and "dd_k8_evaluate" in runner
assert "DD_K9_C_CHECKSUM" in runner and "DD_K9_MVO_CHECKSUM" in runner
wf = (ROOT / ".github/workflows/kagura-k9-composition.yml").read_text()
for required in (
    "workflow_dispatch:", "runs-on: macos-14",
    mod.UPSTREAM_PIN, "scripts/test_kagura_k9_composition.py",
    "scripts/custom_ollvm/kagura_k9/pilot.py",
    "Kagura-K9-COMPOSITION-REPORT.json",
    "DuoDash-Kagura-K9-FIVE-PASS-COMPOSED-LLVM19-EXPERIMENTAL",
    "kagura-k9-build", "libkagura_runtime.a",
    "if: always()", "macos_native_4096_per_function",
):
    assert required in wf, required
for forbidden in (
    "push:", "pull_request:", "codesign", "devicectl",
    "re/RECONSTRUCTION", "THEOS_PACKAGE_SCHEME",
    "MSHook", "ptrauth_strip",
):
    assert forbidden not in wf, forbidden
for prod in ("Makefile", "policy.json", ".github/workflows/build.yml"):
    assert "kagura_k9" not in (ROOT / prod).read_text(encoding="utf-8"), prod
print("KAGURA_K9_PORTABLE_COMPOSITION_PASS: merged module, 5 stages, "
      "two independent 4096-vector oracles, delta/ABI/trace neg tests; "
      "real LLVM19 macOS K9 NOT TESTED")
