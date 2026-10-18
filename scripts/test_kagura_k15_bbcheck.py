#!/usr/bin/env python3
"""K15 synthetic negatives: genuine BBCheck class and runtime provider gates.

Portable tests are NEVER evidence of native/macOS/iPhone execution.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import pathlib
import struct
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/custom_ollvm/kagura_k15"
sys.path.insert(0, str(LAB))
import pilot

spec = importlib.util.spec_from_file_location("k15_independent_replay", LAB / "audit.py")
assert spec and spec.loader
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def reject(callback, why):
    try:
        callback()
    except (AssertionError, KeyError, TypeError, ValueError):
        return
    raise AssertionError("K15 false positive accepted: " + why)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def store(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return digest(data)


def registry():
    from inventory import COVERED, K8_KINDS
    rows = []
    for name in COVERED:
        kind = K8_KINDS.get(name[7:], "FN")
        if name == "kagura-vm":
            rows.append('KAGURA_INFRA_PASS("kagura-vm", VmPass())')
        else:
            rows.append(f'KAGURA_{kind}_PASS(EnableX, "{name}", "x", X())')
    rows.append('KAGURA_FN_PASS(BBCheck, "kagura-bbcheck", "guard", '
                'BasicBlockChecksumPass())')
    return "\n".join(rows).encode() + b"\n"


def macho():
    return struct.pack("<IIIIIIII", 0xFEEDFACF, 0x0100000C,
                       0, 1, 0, 0, 0, 0)


def ll(after=False):
    lead = (b"; ModuleID = 'after.bc'\n" if after else
            b"; ModuleID = 'before.bc'\n")
    code = b'define i64 @dd_k8_evaluate(i64 %a) {\n'
    if after:
        code += (b'  %v = call i32 @kagura_bb_check(i32 2, i32 42)\n'
                 b'  call void @kagura_on_tamper_detected()\n')
    return lead + code + b'  ret i64 %a\n}\n'


TRACE = ("Running pass: kagura::BasicBlockChecksumPass on dd_k8_evaluate "
         "(73 instructions)\nRunning pass: VerifierPass on [module]\n"
         "Running pass: BitcodeWriterPass on [module]\n")
assert pilot.PASS_NAME == "kagura-bbcheck"
assert pilot.PASS_CLASS == "kagura::BasicBlockChecksumPass"
assert pilot.PIPELINE == "function(kagura-bbcheck),verify"
assert pilot.REQUIRED == ("_kagura_bb_check", "_kagura_on_tamper_detected")
assert pilot.entry_from_registry(registry().decode())["enable_flag"] == "BBCheck"
reject(lambda: pilot.entry_from_registry(registry().decode().replace(
    "KAGURA_FN_PASS(BBCheck,", "KAGURA_MOD_PASS(BBCheck,")),
    "FN incorrectly changed to MOD")
reject(lambda: pilot.entry_from_registry(registry().decode().replace(
    "KAGURA_FN_PASS(BBCheck,", "KAGURA_FN_PASS(BbCheckAlias,")),
    "wrong pinned runtime flag")
pilot.validate_pass(TRACE, ll().decode(), ll(True).decode())
reject(lambda: pilot.validate_pass(TRACE.replace(
    "BasicBlockChecksumPass", "CSEBreakPass"), ll().decode(),
    ll(True).decode()), "wrong class")
reject(lambda: pilot.validate_pass(TRACE, ll().decode(),
    ll(True).decode().replace("kagura_on_tamper_detected",
                             "kagura_on_tamper_stub")), "tamper guard missing")
reject(lambda: pilot.validate_pass(TRACE, ll(True).decode(),
    ll(True).decode()), "baseline already instrumented")
pilot.macho_arm64_object(macho())
reject(lambda: pilot.macho_arm64_object(
    struct.pack("<IIIIIIII", 0xFEEDFACF, 0x0100000C, 2, 1, 0, 0, 0, 0)),
    "arm64e subtype")

sources = [
    {"source": "runtime/a.c",
     "actual_defined_kagura_symbols": list(pilot.REQUIRED),
     "actual_undefined_kagura_symbols": ["_kagura_helper"]},
    {"source": "runtime/b.c",
     "actual_defined_kagura_symbols": [],
     "actual_undefined_kagura_symbols": []},
]
summary = pilot.summarize_providers(sources)
assert summary["status"] == "UNIQUE_PROVIDERS_WITH_UNRESOLVED_TRANSITIVE_SYMBOLS"
assert summary["transitive_unresolved_kagura_symbols"] == ["_kagura_helper"]
sources[1]["actual_defined_kagura_symbols"] = ["_kagura_bb_check"]
assert "_kagura_bb_check" in pilot.summarize_providers(sources)["duplicate_symbols"]
sources[0]["actual_defined_kagura_symbols"] = ["_kagura_bb_check"]
sources[1]["actual_defined_kagura_symbols"] = []
assert "_kagura_on_tamper_detected" in pilot.summarize_providers(sources)["missing_symbols"]

with tempfile.TemporaryDirectory(prefix="K15-portable-artifact-") as t:
    out = pathlib.Path(t)
    src = registry()
    store(out / "pinned-registry.def", src)
    store(out / "pinned-LICENSE", b"synthetic source license")
    fixture = ROOT / "scripts/custom_ollvm/kagura_k8/fixture.c"
    report = {
        "schema": 1, "scope": audit.SCOPE, "pin": pilot.PIN,
        "registry_sha256": digest(src),
        "license_sha256": digest(b"synthetic source license"),
        "source_fixture_sha256": pilot.sha(fixture),
        "pass": pilot.PASS_NAME, "pass_kind": "FN",
        "pass_flag": "BBCheck", "actual_pass_class": pilot.PASS_CLASS,
        "pipeline": pilot.PIPELINE,
        "required_bbcheck_runtime_symbols": list(pilot.REQUIRED),
        "mentioned_source_count": 1,
        "targets": {},
        **audit.ZERO,
    }
    candidate_source = b'int kagura_bb_check(void);\nvoid kagura_on_tamper_detected(void);\n'
    store(out / "k15-runtime-source-01.c", candidate_source)
    for target in ("macos", "ios"):
        p = target + "-"
        stage = {}
        data = {
            "baseline_bc_sha256": (p + "baseline.bc", b"BC\xc0\xde0"),
            "protected_bc_sha256": (p + "bbcheck.bc", b"BC\xc0\xde1"),
            "baseline_ir_sha256": (p + "baseline.ll", ll()),
            "protected_ir_sha256": (p + "bbcheck.ll", ll(True)),
            "baseline_object_sha256": (p + "baseline.o", macho() + b"baseline"),
            "protected_object_sha256": (p + "bbcheck.o", macho() + b"instrumented"),
            "pass_manager_log_sha256": (p + "pass-manager.log", TRACE.encode()),
            "bbcheck_nm_defined_sha256": (
                p + "bbcheck-defined-nm.log", b"0000000000000000 T _dd_k8_evaluate\n"),
            "bbcheck_nm_undefined_sha256": (
                p + "bbcheck-undefined-nm.log",
                b"_kagura_bb_check\n_kagura_on_tamper_detected\n_strlen\n"),
        }
        for field, (name, blob) in data.items():
            stage[field] = store(out / name, blob)
        stage.update({
            "normalized_baseline_ir_sha256": pilot.normalized_ir_sha(out / data["baseline_ir_sha256"][0]),
            "normalized_protected_ir_sha256": pilot.normalized_ir_sha(out / data["protected_ir_sha256"][0]),
            "pass_ir_object_delta": True,
            "real_pass_class": pilot.PASS_CLASS,
            "native_checksum": "NOT_TESTED",
            "iphone_runtime": "NOT_TESTED",
            "actual_undefined_kagura_symbols": list(pilot.REQUIRED),
        })
        source = {
            "source": "runtime/provider.c",
            "source_sha256": digest(candidate_source),
            "archived_source": "k15-runtime-source-01.c",
            "mentions_required": list(pilot.REQUIRED),
            "compile_log": p + "runtime-candidate-01-compile.log",
            "compile_log_sha256": store(
                out / (p + "runtime-candidate-01-compile.log"), b""),
            "compile_success": True,
            "object": p + "runtime-candidate-01.o",
            "object_sha256": store(out / (p + "runtime-candidate-01.o"), macho()),
            "defined_nm_sha256": store(
                out / (p + "runtime-candidate-01-defined-nm.log"),
                b"0000000000000000 T _kagura_bb_check\n"
                b"0000000000000004 T _kagura_on_tamper_detected\n"),
            "undefined_nm_sha256": store(
                out / (p + "runtime-candidate-01-undefined-nm.log"),
                b"_kagura_helper\n"),
            "actual_defined_kagura_symbols": sorted(pilot.REQUIRED),
            "actual_undefined_kagura_symbols": ["_kagura_helper"],
        }
        stage["providers"] = {
            "candidate_sources": [source],
            **pilot.summarize_providers([source]),
            "native_execution_attempted": False,
            "ios_ipa_link_attempted": False,
        }
        report["targets"][target] = stage

    reportfile = out / "Kagura-K15-REPORT.json"
    def save():
        reportfile.write_text(json.dumps(report, indent=2), encoding="utf-8")
    original = audit.REGISTRY_SHA
    audit.REGISTRY_SHA = digest(src)
    try:
        save()
        assert audit.verify(out) == report
        report["native_4096_parity"] = "PASS"
        save()
        reject(lambda: audit.verify(out), "false native checksum PASS")
        report["native_4096_parity"] = audit.ZERO["native_4096_parity"]
        report["targets"]["ios"]["providers"]["native_execution_attempted"] = True
        save()
        reject(lambda: audit.verify(out), "runtime tamper callback auto-executed")
        report["targets"]["ios"]["providers"]["native_execution_attempted"] = False
        report["targets"]["ios"]["providers"]["required_symbol_providers"][
            "_kagura_bb_check"] = []
        save()
        reject(lambda: audit.verify(out), "forged direct runtime provider")
        report["targets"]["ios"]["providers"]["required_symbol_providers"] = (
            pilot.summarize_providers(
                report["targets"]["ios"]["providers"]["candidate_sources"]
            )["required_symbol_providers"])
        report["targets"]["ios"]["actual_undefined_kagura_symbols"] = []
        save()
        reject(lambda: audit.verify(out), "erased unresolved runtime symbols")
        report["targets"]["ios"]["actual_undefined_kagura_symbols"] = (
            list(pilot.REQUIRED))
        bad_file = out / "ios-bbcheck.ll"
        saved = bad_file.read_bytes()
        bad_file.write_bytes(saved.replace(b"@kagura_bb_check", b"@another_callback"))
        save()
        reject(lambda: audit.verify(out), "tampered real BBCheck IR file")
        bad_file.write_bytes(saved)
        save()
        assert audit.verify(out) == report
    finally:
        audit.REGISTRY_SHA = original

workflow = (ROOT / ".github/workflows/kagura-k15-bbcheck-runtime-audit.yml").read_text(
    encoding="utf-8")
for term in ("workflow_dispatch:", "runs-on: macos-14", pilot.PIN,
             pilot.REGISTRY_SHA, "scripts/test_kagura_k15_bbcheck.py",
             "scripts/custom_ollvm/kagura_k15/pilot.py",
             "scripts/custom_ollvm/kagura_k15/audit.py",
             "DuoDash-Kagura-K15-BBCHECK-RUNTIME-PROVIDER-RESEARCH-EXPERIMENTAL",
             "if: always()"):
    assert term in workflow, term
assert "ios-ipa" not in workflow.lower()
assert "git push" not in workflow
for path in ("Makefile", "policy.json", ".github/workflows/build.yml"):
    assert "kagura_k15" not in (ROOT / path).read_text(encoding="utf-8")
print("KAGURA_K15_PORTABLE_PROVIDER_GATES_PASS: genuine BBCheck FN/guards,"
      " actual nm definitions, transitive deps and tamper callback never run;"
      " native/iPhone NOT_TESTED")
