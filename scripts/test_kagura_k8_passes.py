#!/usr/bin/env python3
"""Portable K8 negative and source-scope checks. NO Kagura macOS native PASS."""
from __future__ import annotations

import importlib.util
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "scripts/custom_ollvm/kagura_k8"
spec = importlib.util.spec_from_file_location("k8_pilot", BASE / "pilot.py")
assert spec and spec.loader
k8 = importlib.util.module_from_spec(spec)
sys.modules["k8_pilot"] = k8
spec.loader.exec_module(k8)


def rejects(fn, label: str) -> None:
    try:
        fn()
    except (AssertionError, ValueError):
        return
    raise AssertionError("Accepted fake K8 pass proof: " + label)


assert set(k8.CANDIDATES) == {"ibr", "mvo", "genc", "fsplit", "ci"}
assert k8.SEED == "82712"
registry = "\n".join(
    f'KAGURA_{kind}_PASS({name.upper()}, "kagura-{name}", "fixture", Pass())'
    for name, (kind, _cls, _pipeline) in k8.CANDIDATES.items()
) + '\nKAGURA_FN_PASS(VM, "kagura-vm", "fixture", Pass())\n'
k8.validate_registry(registry)
rejects(lambda: k8.validate_registry(registry.replace('"kagura-ci"', '"no-ci"')),
        "CI absent")
rejects(lambda: k8.validate_registry(registry.replace(
    'KAGURA_FN_PASS(IBR,', 'KAGURA_MOD_PASS(IBR,')), "IBR wrong pass type")
rejects(lambda: k8.validate_registry(registry + registry.split("\n")[0] + "\n"),
        "duplicate pass")

base = ("define i64 @dd_k8_evaluate(i64 %n, i64 %salt) {\n"
        "entry:\n  %tmp = load i64, ptr @dd_k8_table\n"
        "  store volatile i64 %n, ptr %local\n  ret i64 %n\n}\n"
        "define internal i64 @dd_k8_internal(i64 %n, i64 %salt) {\n"
        "entry:\n  ret i64 %n\n}\n"
        "@dd_k8_table = internal constant [8 x i64] zeroinitializer\n")
for name, (_, cls, _) in k8.CANDIDATES.items():
    signature = {
        "ibr": "@__kagura_fptr_123 = private global ptr @dd_k8_internal\n",
        "mvo": "  %n.mvo = xor i64 %n, 123\n",
        "genc": "  %x.dec = xor i64 %n, 123\n",
        "fsplit": "define internal void @dd_k8_outlined(ptr %p) {\nret void\n}\n",
        "ci": "@__kagura_thunk_table = internal global [1 x ptr] zeroinitializer\n"
              "declare ptr @kagura_rtld_default_handle()\n",
    }[name]
    after = base + signature
    trace = f"Running pass: kagura::{cls} on dd_k8_evaluate\n"
    k8.validate_delta(name, base, after, b"baseline object",
                      b"modified object", trace)
    rejects(lambda: k8.validate_delta(name, base, after,
                                      b"same", b"same", trace), "identical object " + name)
    rejects(lambda: k8.validate_delta(name, base, after,
                                      b"plain", b"other", ""), "not invoked " + name)
    rejects(lambda: k8.validate_delta(name, base, base,
                                      b"plain", b"other", trace), "IR unchanged " + name)
    rejects(lambda: k8.validate_delta(name, base, base + " ; no eligible input",
                                      b"plain", b"other", trace),
            "pass called without required transform " + name)

# The C fixture must retain every pass trigger after O1 or fail on macOS.
fixture = (BASE / "fixture.c").read_text(encoding="utf-8")
assert "static const uint64_t dd_k8_table[8]" in fixture
assert "volatile uint64_t box" in fixture
assert "strlen(token)" in fixture
assert "DD_NOINLINE static uint64_t dd_k8_internal" in fixture
assert fixture.count("if (n &") >= 5
assert "dd_k8_evaluate" in fixture
runner = (BASE / "runner.c").read_text(encoding="utf-8")
assert "i < 4096U" in runner and "DD_K8_CHECKSUM=%016" in runner
assert k8.validate_native_output(
    "DD_K8_SCHEMA=1\nDD_K8_VECTORS=4096\n"
    "DD_K8_CHECKSUM=0123456789abcdef\nDD_K8_COMPLETE=PASS\n"
) == "0123456789abcdef"
for corruption in ("DD_K8_VECTORS=4095", "DD_K8_CHECKSUM=1",
                   "DD_K8_COMPLETE=FAIL", "DD_K8_SCHEMA=2"):
    valid = ("DD_K8_SCHEMA=1\nDD_K8_VECTORS=4096\n"
             "DD_K8_CHECKSUM=0123456789abcdef\nDD_K8_COMPLETE=PASS\n")
    rejects(lambda: k8.validate_native_output(
        re.sub(r"DD_K8_(?:SCHEMA|VECTORS|CHECKSUM|COMPLETE)=[^\n]+",
               corruption, valid, count=1)), "invalid log " + corruption)
mach = struct.pack("<IIIIIIII", 0xFEEDFACF, 0x0100000C, 0, 1, 0, 0, 0, 0)
k8.verify_apple_arm64_object(mach)
rejects(lambda: k8.verify_apple_arm64_object(
    struct.pack("<IIIIIIII", 0xFEEDFACF, 0x0100000C, 0x80000002, 1, 0, 0, 0, 0)),
    "arm64e disguised as arm64")
rejects(lambda: k8.verify_apple_arm64_object(
    struct.pack("<IIIIIIII", 0xFEEDFACF, 0x0100000C, 0, 6, 0, 0, 0, 0)),
    "MH_DYLIB disguised as object")
wf = (ROOT / ".github/workflows/kagura-k8-pass-coverage.yml").read_text()
for mandatory in ("workflow_dispatch:", "runs-on: macos-14",
                  "ac2136ee0408677cf7cdee55307e9b16edd5f4d5",
                  "scripts/test_kagura_k8_passes.py",
                  "scripts/custom_ollvm/kagura_k8/pilot.py",
                  "Kagura-K8-PASS-REPORT.json",
                  "kagura-k8-build", "libkagura_runtime.a",
                  "if: always()", "native_4096_vector_parity"):
    assert mandatory in wf, mandatory
for forbidden in ("pull_request:", "push:", "re/RECONSTRUCTION",
                  "THEOS_PACKAGE_SCHEME", "code_sign", "codesign",
                  "devicectl device install", "MSHook", "ptrauth_strip"):
    assert forbidden not in wf, forbidden
assert "kagura_k8" not in (ROOT / "Makefile").read_text()
assert "kagura_k8" not in (ROOT / ".github/workflows/build.yml").read_text()
assert "kagura_k8" not in (ROOT / "policy.json").read_text()
print("KAGURA_K8_PORTABLE_PASS: 5 real upstream pass types, eligible triggers,"
      " strict IR/object/native/arm64 negatives; actual macOS K8 NOT TESTED")
