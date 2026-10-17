#!/usr/bin/env python3
"""K10 strict Clang target-metadata gates; local only, NOT native CI."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "scripts/custom_ollvm/kagura_k10"
spec = importlib.util.spec_from_file_location("k10_pilot", BASE / "pilot.py")
assert spec and spec.loader
k10 = importlib.util.module_from_spec(spec)
sys.modules["k10_pilot"] = k10
spec.loader.exec_module(k10)
k9 = k10.k9


def rejects(fn, label: str) -> None:
    try:
        fn()
    except (AssertionError, ValueError):
        return
    raise AssertionError("K10 false target-metadata evidence accepted: " + label)


assert k10.STAGES == ("mvo", "genc", "fsplit", "ibr", "ci")
assert k10.STATUS == "MACOS_FIVE_COMPOSED_STAGES_STRICT_METADATA_NATIVE_PASS_IOS_BUILD_ONLY"
assert k9.verify_inputs()["source_mvo_sha256"] == (
    "abbe02b364571b77fb94fff673111bf381f694211cca148d18a73650a8343e50")
mvo_src = (ROOT / "scripts/custom_ollvm/kagura_k8/mvo.ll").read_text(encoding="utf-8")
original = mvo_src.encode("utf-8")
assert original.count(b"@@TRIPLE@@") == 1 and b"target datalayout" not in original

layout = "e-m:o-i64:64-i128:128-n32:64-S128-Fn32"
for ios, triple in (
    (False, "arm64-apple-macosx14.0.0"),
    (False, "x86_64-apple-macosx13.3.0"),
    (True, "arm64-apple-ios15.0.0"),
):
    c = (f'; LLVM19 Clang canary C module\n'
         f'target datalayout = "{layout}"\n'
         f'target triple = "{triple}"\n'
         f'define i64 @dd_k8_evaluate(i64 %a, i64 %b) {{\n'
         f'  ret i64 %a\n}}\n')
    header = k9.get_target_metadata(c, ios=ios)
    assert header == (layout, triple)
    mvo = k9.align_mvo_to_c_module(mvo_src, c, ios=ios)
    assert k9.get_target_metadata(mvo, ios=ios) == header
    assert "define i64 @dd_k9_mvo_probe(" in mvo
    assert "define i64 @dd_k8_evaluate(" not in mvo
    k9.k8.validate_mvo_input_ir(mvo)
    assert k9.validate_llvm_link_metadata(
        c, mvo, c, "", ios=ios) == {
        "triple": triple,
        "datalayout": layout,
        "llvm_link_warning_count": 0,
    }
    for label, bad in (
        ("Clang IR missing datalayout",
         c.replace(f'target datalayout = "{layout}"\n', "")),
        ("Clang IR duplicate triple",
         c + f'target triple = "{triple}"\n'),
        ("Clang IR duplicated datalayout",
         c + f'target datalayout = "{layout}"\n'),
        ("Clang IR other CPU/platform",
         c.replace(triple, "arm64-unknown-linux-gnu")),
        ("Clang IR invalid layout",
         c.replace(layout, "nonsense-no-macho")),
    ):
        rejects(lambda bad=bad: k9.get_target_metadata(bad, ios=ios), label)
    rejects(lambda: k9.validate_llvm_link_metadata(
        c, mvo.replace(layout, layout + "-BAD"), c, "", ios=ios),
        "MVO target layout differs from C")
    rejects(lambda: k9.validate_llvm_link_metadata(
        c, mvo.replace(triple, "arm64-apple-ios19.0"), c, "", ios=ios),
        "MVO target triple differs from C")
    rejects(lambda: k9.validate_llvm_link_metadata(
        c, mvo, c.replace(layout, layout + "-BAD"), "", ios=ios),
        "llvm-link output has changed datalayout")
    rejects(lambda: k9.validate_llvm_link_metadata(
        c, mvo, c, "llvm-link: warning: datalayout mismatch\n", ios=ios),
        "real llvm-link warning suppressed")
    rejects(lambda: k9.validate_llvm_link_metadata(
        c, mvo, c, "llvm-link: error: triple mismatch\n", ios=ios),
        "real llvm-link error suppressed")
    rejects(lambda: k9.align_mvo_to_c_module(
        mvo_src.replace('target triple = "@@TRIPLE@@"',
                        'target datalayout = "injected"\n'
                        'target triple = "@@TRIPLE@@"'),
        c, ios=ios), "MVO K8 template injected datalayout")
    assert (ROOT / "scripts/custom_ollvm/kagura_k8/mvo.ll").read_bytes() == original

for target, invalid in (
    ("iOS C metadata sent to macOS", 'target datalayout = "' + layout +
     '"\ntarget triple = "arm64-apple-ios15.0.0"\n'),
    ("macOS C metadata sent to iOS", 'target datalayout = "' + layout +
     '"\ntarget triple = "arm64-apple-macosx14.0.0"\n'),
):
    rejects(lambda invalid=invalid, target=target: k9.get_target_metadata(
        invalid, ios=target.startswith("macOS")), target)

workflow = (ROOT / ".github/workflows/kagura-k10-link-metadata.yml").read_text(
    encoding="utf-8")
for required in (
    "workflow_dispatch:", "runs-on: macos-14",
    k9.UPSTREAM_PIN, "scripts/test_kagura_k10_link_metadata.py",
    "scripts/custom_ollvm/kagura_k10/pilot.py",
    "Kagura-K10-METADATA-REPORT.json",
    "DuoDash-Kagura-K10-STRICT-LLVM-LINK-METADATA-LLVM19-EXPERIMENTAL",
    "if: always()", "--verify-report", "kagura-k9-build",
    "libkagura_runtime.a",
):
    assert required in workflow, required
for forbidden in ("push:", "pull_request:", "codesign", "devicectl",
                  "re/RECONSTRUCTION", "THEOS_PACKAGE_SCHEME",
                  "MSHook", "ptrauth_strip"):
    assert forbidden not in workflow, forbidden
code = (ROOT / "scripts/custom_ollvm/kagura_k9/pilot.py").read_text()
for required in (
    "strict_link_metadata: bool = False",
    "align_mvo_to_c_module(template, c_text, ios=ios)",
    "get_target_metadata(c_ir, ios=ios)",
    "validate_llvm_link_metadata(",
    "llvm_link_warning_count",
    'folder / "target-metadata.json"',
    'run_command([dis, str(c_bc), "-o", str(c_ir)])',
):
    assert required in code, required
wrapper = (BASE / "pilot.py").read_text()
assert "strict_link_metadata=True" in wrapper
assert "validate_composition_report(report)" in wrapper or (
    "k9.validate_composition_report(report)" in wrapper)
assert "Kagura-K9-COMPOSITION-REPORT.json" in wrapper
assert "Kagura-K10-METADATA-REPORT.json" in wrapper
assert "verify_report(report, a.out)" in wrapper
assert "llvm_link_warning_count" in wrapper
assert k9.sh(ROOT / "scripts/custom_ollvm/kagura_k8/mvo.ll") == (
    "abbe02b364571b77fb94fff673111bf381f694211cca148d18a73650a8343e50")
for prod in ("Makefile", "policy.json", ".github/workflows/build.yml"):
    assert "kagura_k10" not in (ROOT / prod).read_text(), prod
# Synthetic *file-backed* end-to-end K10 audit. It is NOT a native
# LLVM run. It proves the second verifier does not trust JSON PASS flags:
# actual per-stage previous/current files, macOS+iOS metadata, objects,
# link logs and native bytes must agree.
import struct
import tempfile

with tempfile.TemporaryDirectory() as temporary:
    out = Path(temporary)
    sample = {
        "schema": 1,
        "scope": "K9_PINNED_KAGURA_FIVE_PASS_ONE_MODULE_COMPOSITION",
        "status": "MACOS_NATIVE_ALL_FIVE_COMPOSED_STAGES_PASS_IOS_BUILD_ONLY",
        "pinned_commit": k9.UPSTREAM_PIN,
        "stage_order": list(k10.STAGES),
        "native_vectors_per_function": 4096,
        "native_digest_c": k9.K8_C_DIGEST,
        "native_digest_mvo": k9.K8_MVO_DIGEST,
        "mvo_independent_oracle": k9.K8_MVO_DIGEST,
        "ios_arm64": "OBJECT_BUILD_ONLY_NOT_EXECUTED",
        "iphone_runtime_executed": False,
        "arm64e_pac_runtime_executed": False,
        "crane_production_modified": False,
        "performance_evaluated": False,
        "stages": {},
        "link_metadata": {},
    }
    baseline_log = (
        "DD_K9_SCHEMA=1\nDD_K9_VECTORS_PER_FUNCTION=4096\n"
        f"DD_K9_C_CHECKSUM={k9.K8_C_DIGEST}\n"
        f"DD_K9_MVO_CHECKSUM={k9.K8_MVO_DIGEST}\n"
        "DD_K9_COMPLETE=PASS\n"
    ).encode("ascii")
    (out / "plain-native.log").write_bytes(baseline_log)
    current_ir = {}
    previous_objects = {}
    for target, triple in (
        ("macos", "arm64-apple-macosx14.0.0"),
        ("ios", "arm64-apple-ios15.0.0"),
    ):
        base = out / target
        base.mkdir()
        c = (
            f'target datalayout = "{layout}"\n'
            f'target triple = "{triple}"\n'
            '@dd_k8_genc_scalar = internal constant i64 1\n'
            'define i64 @dd_k8_evaluate(i64 %n, i64 %s) {\n'
            'entry:\n'
            '  %g = load volatile i64, ptr @dd_k8_genc_scalar, align 8\n'
            '  ret i64 %n\n}\n'
        )
        mvo = k9.align_mvo_to_c_module(mvo_src, c, ios=target == "ios")
        merged = c + "define i64 @dd_k9_mvo_probe(" + mvo.split(
            "define i64 @dd_k9_mvo_probe(", 1)[1]
        for filename, payload in (
            ("c.ll", c),
            ("mvo-source.ll", mvo),
            ("merged.ll", merged),
            ("llvm-link.log", ""),
        ):
            (base / filename).write_text(payload, encoding="utf-8")
        raw = (struct.pack("<IIIIIIII", 0xFEEDFACF, 0x0100000C, 0, 1,
                           0, 0, 0, 0) if target == "ios" else b"host-obj")
        (base / "merged.o").write_bytes(raw + b"0")
        current_ir[target] = merged
        previous_objects[target] = raw + b"0"
        sidecar = {
            **k9.validate_llvm_link_metadata(
                c, mvo, merged, "", ios=target == "ios"),
            "c_ir_sha256": k9.sh(base / "c.ll"),
            "mvo_ir_sha256": k9.sh(base / "mvo-source.ll"),
            "merged_ir_sha256": k9.sh(base / "merged.ll"),
        }
        sample["link_metadata"][target] = sidecar
        (base / "target-metadata.json").write_text(
            json.dumps(sidecar), encoding="utf-8")
    for idx, name in enumerate(k10.STAGES, 1):
        stage = out / f"{idx:02d}-{name}"
        stage.mkdir()
        (stage / "native.log").write_bytes(baseline_log)
        entry = {
            "pass": name, "index": idx,
            "macos_native_4096_per_function": "PASS",
            "native_log_sha256": k9.sh(stage / "native.log"),
        }
        ext = {
            "mvo": "  %mixed.mvo = xor i64 %value, 42\n"
                   "  %value.mvo = xor i64 %value, 42\n",
            "genc": "  %x.dec = xor i64 %n, 56\n",
            "fsplit": "define internal void @__kg_fake_bb4() {\nret void\n}\n",
            "ibr": "@__kagura_fptr_123 = private global ptr @dd_k8_evaluate\n",
            "ci": "@__kagura_thunk_table = internal global [1 x ptr] zeroinitializer\n"
                  "declare ptr @kagura_rtld_default_handle()\n",
        }[name]
        for target in ("macos", "ios"):
            ir = stage / f"{target}.ll"
            obj = stage / f"{target}.o"
            opt = stage / f"{target}-opt.log"
            opt.write_text(
                f"Running pass: kagura::{k9.k8.CANDIDATES[name][1]} on dd_k8_evaluate\n",
                encoding="utf-8")
            current_ir[target] += ext
            ir.write_text(current_ir[target], encoding="utf-8")
            obj.write_bytes(previous_objects[target] + bytes([idx]))
            previous_objects[target] = obj.read_bytes()
            entry[target] = {
                "class": k9.k8.CANDIDATES[name][1],
                "kind": k9.k8.CANDIDATES[name][0],
                "ir_and_object_changed": True,
                "previous_object_sha256": k9.sh(
                    out / target / "merged.o"
                    if idx == 1 else
                    out / f"{idx-1:02d}-{k10.STAGES[idx-2]}" / f"{target}.o"),
                "object_sha256": k9.sh(obj),
                "ir_sha256": k9.sh(ir),
                "opt_log_sha256": k9.sh(opt),
            }
        sample["stages"][name] = entry
    (out / "Kagura-K9-COMPOSITION-REPORT.json").write_text(
        json.dumps(sample, sort_keys=True), encoding="utf-8")
    success = k10.verify_report(json.loads(
        (out / "Kagura-K9-COMPOSITION-REPORT.json").read_text()), out)
    assert success["llvm_link_metadata_aligned"] is True
    assert success["llvm_link_warning_count"] == 0
    # A warning in the actual raw link log MUST override JSON "0".
    (out / "ios/llvm-link.log").write_text(
        "llvm-link: warning: different data layouts!\n")
    rejects(lambda: k10.verify_report(sample, out),
            "actual iOS link warning despite clean JSON")
    (out / "ios/llvm-link.log").write_text("")
    # Tamper stage output, not report: post-CI verification must fail.
    (out / "04-ibr/macos.ll").write_text(current_ir["macos"] + "tampered\n")
    rejects(lambda: k10.verify_report(sample, out),
            "altered raw stage IR despite valid summary hashes")

print("KAGURA_K10_PORTABLE_METADATA_GATES_PASS: Clang target IR triple+datalayout "
      "aligned, negative warns/mismatch/ABI, source pin intact; macOS LLVM19 K10 "
      "NOT TESTED")
