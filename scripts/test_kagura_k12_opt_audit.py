#!/usr/bin/env python3
"""K12 artifact auditor replay: real file SHA, LLVM IR vs bitcode delta.

These files are synthetic fixtures ONLY and do not assert real upstream
macOS/LLVM19 pass verification or any iOS device execution.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import struct
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/custom_ollvm/kagura_k12"
sys.path.insert(0, str(LAB))
import inventory as k12
import audit as k12audit


def rejects(fn, label):
    try:
        fn()
    except (AssertionError, ValueError, TypeError, KeyError):
        return
    raise AssertionError("K12 independent artifact verifier accepted " + label)


def hashbytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def preserve(path: pathlib.Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def wrap_bitcode(payload: bytes, *, offset: int = 20) -> bytes:
    assert payload.startswith(b"BC\xc0\xde") and offset >= 20
    return (struct.pack("<IIIII", 0x0B17C0DE, 0, offset,
                        len(payload), 0x0100000C) +
            b"\0" * (offset - 20) + payload)


# Real LLVM permits BOTH raw BC and a little-endian wrapper.
assert k12audit.bitcode_container(b"BC\xc0\xde" + b"contents") == (
    "RAW_LLVM_BITCODE")
assert k12audit.bitcode_container(wrap_bitcode(
    b"BC\xc0\xde" + b"contents")) == "WRAPPED_LLVM_BITCODE"
assert k12audit.bitcode_container(wrap_bitcode(
    b"BC\xc0\xde" + b"contents", offset=28)) == "WRAPPED_LLVM_BITCODE"
for bad, label in (
    (b"not-bitcode", "random fake content"),
    (b"\xde\xc0\x17\x0b" + b"\x00" * 4, "truncated wrapper"),
    (struct.pack("<IIIII", 0x0B17C0DE, 1, 20, 4, 0) +
     b"BC\xc0\xde", "unknown wrapper version"),
    (struct.pack("<IIIII", 0x0B17C0DE, 0, 19, 4, 0) +
     b"BC\xc0\xde", "wrapper offset into header"),
    (struct.pack("<IIIII", 0x0B17C0DE, 0, 40, 4, 0) +
     b"BC\xc0\xde", "wrapper offset beyond file"),
    (struct.pack("<IIIII", 0x0B17C0DE, 0, 20, 8192, 0) +
     b"BC\xc0\xde", "wrapper payload size overflow"),
    (struct.pack("<IIIII", 0x0B17C0DE, 0, 20, 4, 0) +
     b"NOBC", "wrapper points to fake bitcode"),
):
    rejects(lambda invalid=bad: k12audit.bitcode_container(invalid), label)


covered_rows = []
for fullname in k12.COVERED:
    short = fullname[len("kagura-"):]
    kind = k12.K8_KINDS.get(short, "FN")
    if fullname == "kagura-vm":
        covered_rows.append('KAGURA_INFRA_PASS("kagura-vm", VmRuntimePass())')
    else:
        covered_rows.append(
            f'KAGURA_{kind}_PASS(EnableTest, "{fullname}", "x", T())')
sample = "\n".join(covered_rows + [
    'KAGURA_FN_PASS(EnableFoo, "kagura-test-fn", "test", FnPass())',
    'KAGURA_MOD_PASS(EnableBar, "kagura-test-mod", "test", ModPass())',
    'KAGURA_INFRA_PASS("kagura-test-infra", InfraPass())',
]) + "\n"

with tempfile.TemporaryDirectory(prefix="K12-artifact-fixture-") as tmp:
    root = pathlib.Path(tmp)
    src = root / "pin"
    out = root / "out"
    fixture = ROOT / "scripts/custom_ollvm/kagura_k8/fixture.c"
    preserve(src / "LICENSE", b"synthetic license")
    preserve(src / "include/kagura/PassRegistry.def", sample.encode())
    inv = k12.inventory(src, out)
    assert inv["remaining_registered_unverified_count"] == 3
    original = inv["remaining_registered_unverified"]
    results = []
    baseline = {}
    for target in k12audit.TARGET_LABELS:
        raw_bc = b"BC\xc0\xde" + target.encode()
        base_bc = (wrap_bitcode(raw_bc) if target.startswith("ios")
                   else raw_bc)
        base_ll = ("; ModuleID = '" + target + "-baseline.bc'\n" + (
            'target triple = "arm64-apple-ios15.0.0"\n'
            if target.startswith("ios") else
            'target triple = "arm64-apple-macosx14.0.0"\n'
        ) + "define i64 @dd_k8_evaluate(i64 %v) { ret i64 %v }\n")
        preserve(out / (target + "-baseline.bc"), base_bc)
        preserve(out / (target + "-baseline.ll"), base_ll.encode())
        baseline[target] = (base_bc, base_ll.encode())
    for index, row in enumerate(original, 1):
        stage = out / f"probe-{index:02d}-{row['name']}"
        stage.mkdir()
        if row["kind"] == "INFRA":
            results.append({**row, "screening": "SKIPPED_INFRA_NOT_AUTO_RUN",
                            "native_parity": "NOT_TESTED",
                            "ios_device": "NOT_TESTED", "targets": {}})
            continue
        pipeline = ("function(" + row["name"] + "),verify"
                    if row["kind"] == "FN" else row["name"] + ",verify")
        screens = {}
        for target in k12audit.TARGET_LABELS:
            bc, ir = baseline[target]
            log = b"Running pass: SyntheticExamplePass on function\n"
            preserve(stage / (target + "-opt.log"), log)
            if row["kind"] == "MOD" and target == "macos":
                # Failed opt must not include a stale output file.
                screens[target] = {
                    "screening": k12audit.STATUS_FAILED,
                    "input_sha256": hashbytes(bc),
                    "input_ir_sha256": hashbytes(ir),
                    "normalized_input_ir_sha256": k12.normalized_ir_sha(
                        out / (target + "-baseline.ll")),
                    "output_sha256": None,
                    "output_ir_sha256": None,
                    "normalized_output_ir_sha256": None,
                    "bitcode_byte_delta_only": False,
                    "opt_log_sha256": hashbytes(log),
                    "llvm_dis_log_sha256": None,
                    "error_tail": "synthetic opt error",
                    "native_parity": "NOT_TESTED",
                    "iphone_runtime": "NOT_TESTED",
                }
                continue
            newer_bc = (
                wrap_bitcode(b"BC\xc0\xde" + target.encode() + b"marker",
                             offset=24) if target.startswith("ios")
                else bc + b"marker")
            # KEY NEGATIVE: no changed IR, despite DIFFERENT bitcode bytes.
            newer_ir = ir.replace(
                b"baseline.bc'", b"post-opt.bc'")
            if row["kind"] == "FN" and target == "macos":
                newer_ir = newer_ir.replace(
                    b"ret i64 %v", b"ret i64 %v\n ; fn delta")
            # Every candidate changes the ModuleID path, but only one
            # changes substantive IR. Mac/ios no-op variants must not PASS.
            preserve(stage / (target + "-post-opt.bc"), newer_bc)
            preserve(stage / (target + "-post-opt.ll"), newer_ir)
            preserve(stage / (target + "-llvm-dis.log"), b"")
            screens[target] = {
                "screening": (
                    k12audit.STATUS_DELTA
                    if k12.normalized_ir_sha(stage / (target + "-post-opt.ll"))
                    != k12.normalized_ir_sha(out / (target + "-baseline.ll"))
                    else k12audit.STATUS_NO_DELTA),
                "input_sha256": hashbytes(bc),
                "input_ir_sha256": hashbytes(ir),
                "normalized_input_ir_sha256": k12.normalized_ir_sha(
                    out / (target + "-baseline.ll")),
                "output_sha256": hashbytes(newer_bc),
                "output_ir_sha256": hashbytes(newer_ir),
                "normalized_output_ir_sha256": k12.normalized_ir_sha(
                    stage / (target + "-post-opt.ll")),
                "bitcode_byte_delta_only": True,
                "opt_log_sha256": hashbytes(log),
                "llvm_dis_log_sha256": hashbytes(b""),
                "error_tail": "",
                "native_parity": "NOT_TESTED",
                "iphone_runtime": "NOT_TESTED",
            }
        results.append({**row,
                        "screening": "LLVM19_OPT_ONLY_NOT_PASS_VALIDATION",
                        "opt_pipeline": pipeline, "targets": screens,
                        "native_parity": "NOT_TESTED",
                        "ios_device": "NOT_TESTED"})
    report = {
        "schema": 1,
        "scope": "K12_OPT_DIAGNOSTIC_ONLY_NOT_NATIVE_PASS_VALIDATION",
        "pinned_commit": k12.PIN,
        "source_inventory_sha256": k12.sha(
            out / "Kagura-K12-REMAINING-PASS-INVENTORY.json"),
        "fixture_sha256": k12.sha(fixture),
        "clang19_ir_disassembly_comparison": True,
        "ir_delta_ignores_llvm_dis_moduleid_comment": True,
        "candidate_count": 3,
        "results": results,
        "native_parity_proven": False,
        "ios_device_runtime_proven": False,
        "arm64e_pac_proven": False,
        "crane_production_modified": False,
    }
    report_path = out / "Kagura-K12-REMAINING-OPT-SCREEN.json"

    def save():
        report_path.write_text(json.dumps(report, sort_keys=True),
                               encoding="utf-8")

    def inspect():
        return k12audit.audit(out, fixture)

    save()
    assert inspect() == report
    assert report["results"][0]["targets"]["ios-arm64-build-only"][
        "screening"] == k12audit.STATUS_NO_DELTA
    delta_file = out / "probe-01-kagura-test-fn/macos-post-opt.ll"
    original_bytes = delta_file.read_bytes()
    delta_file.write_bytes(original_bytes + b"; tamper\n")
    rejects(inspect, "tampered transformed LLVM IR SHA")
    delta_file.write_bytes(original_bytes)
    report["results"][0]["targets"]["macos"]["screening"] = (
        k12audit.STATUS_NO_DELTA)
    save()
    rejects(inspect, "false claimed lack of IR delta")
    report["results"][0]["targets"]["macos"]["screening"] = (
        k12audit.STATUS_DELTA)
    report["native_parity_proven"] = True
    save()
    rejects(inspect, "no native parity source artifacts")
    report["native_parity_proven"] = False
    report["results"][1]["targets"]["macos"]["screening"] = (
        k12audit.STATUS_DELTA)
    save()
    rejects(inspect, "failed opt reclassified as PASS")
    report["results"][1]["targets"]["macos"]["screening"] = (
        k12audit.STATUS_FAILED)
    report["results"][2]["screening"] = "INFRA_PASS"
    save()
    rejects(inspect, "infrastructure pass auto verified")
    report["results"][2]["screening"] = "SKIPPED_INFRA_NOT_AUTO_RUN"
    save()
    assert inspect() == report
    wrapped_baseline = out / "ios-arm64-build-only-baseline.bc"
    intact = wrapped_baseline.read_bytes()
    wrapped_baseline.write_bytes(intact[:12] + struct.pack("<I", 10**6) +
                                 intact[16:])
    rejects(inspect, "wrapper payload out of file even with report SHA")
    wrapped_baseline.write_bytes(intact)
    assert inspect() == report

wf = (ROOT / ".github/workflows/kagura-k12-remaining-inventory.yml").read_text(
    encoding="utf-8")
smoke = (LAB / "smoke.py").read_text(encoding="utf-8")
for term in ("scripts/test_kagura_k12_opt_audit.py",
             "scripts/custom_ollvm/kagura_k12/audit.py",
             "llvm-dis", "OPT_EXECUTED_IR_DELTA_UNVERIFIED"):
    assert term in wf + smoke, term
assert "normalized_ir_sha(after_ir) != normalized_ir_sha(input_ir)" in smoke
assert "ir_delta_ignores_llvm_dis_moduleid_comment" in smoke
assert "bitcode_byte_delta_only" in smoke
assert "crane_production_modified" in smoke
assert "native_parity_proven" in smoke

print("KAGURA_K12_OPT_AUDIT_PORTABLE_PASS: raw files + actual textual LLVM IR"
      " hash/delta replay, errors and infrastructure never elevate to native PASS")
