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
        "  %direct = load volatile i64, ptr @dd_k8_genc_scalar, align 8\n"
        "  store volatile i64 %n, ptr %local\n  ret i64 %n\n}\n"
        "define internal i64 @dd_k8_internal(i64 %n, i64 %salt) {\n"
        "entry:\n  ret i64 %n\n}\n"
        "@dd_k8_table = internal constant [8 x i64] zeroinitializer\n"
        "@dd_k8_genc_scalar = internal constant i64 123\n")
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

# GENC upstream only recognizes a direct load of a private constant
# scalar, not a runtime-index GEP through an array at -O1.
k8.validate_genc_input_ir(base)
rejects(lambda: k8.validate_genc_input_ir(base.replace(
    "@dd_k8_genc_scalar = internal constant i64 123\n", "")),
    "GENC missing constant global")
rejects(lambda: k8.validate_genc_input_ir(base.replace(
    "  %direct = load volatile i64, ptr @dd_k8_genc_scalar, align 8\n",
    "  %ptr = getelementptr i64, ptr @dd_k8_genc_scalar, i32 0\n"
    "  %direct = load volatile i64, ptr %ptr, align 8\n")),
    "GENC only GEP indirect global use not accepted")
rejects(lambda: k8.validate_genc_input_ir(base.replace(
    "internal constant i64 123", "internal global i64 123")),
    "GENC mutable global not eligible")

# MVO regression: -O1 can remove/promote the integer alloca. The K8
# pilot MUST use a separate O0/no-optnone input and compare it against
# the matching O0 baseline, not O1 (that would be fake IR/object delta).
mvo_eligible = (
    "define i64 @dd_k8_evaluate(i64 %n, i64 %salt) {\n"
    "entry:\n"
    "  %box = alloca i64, align 8\n"
    "  store volatile i64 %n, ptr %box, align 8\n"
    "  %loaded = load volatile i64, ptr %box, align 8\n"
    "  ret i64 %loaded\n}\n"
)
k8.validate_mvo_input_ir(mvo_eligible)
rejects(lambda: k8.validate_mvo_input_ir(mvo_eligible.replace(
    "  %box = alloca i64, align 8\n", "")), "MVO missing alloca")
rejects(lambda: k8.validate_mvo_input_ir(mvo_eligible.replace(
    "store volatile", "store")), "MVO missing volatile store")
rejects(lambda: k8.validate_mvo_input_ir(mvo_eligible.replace(
    "load volatile", "load")), "MVO missing volatile load")
rejects(lambda: k8.validate_mvo_input_ir(mvo_eligible +
        "attributes #0 = { noinline optnone }\n"), "MVO optnone rejected")
rejects(lambda: k8.validate_mvo_input_ir(mvo_eligible.replace(
    "  %loaded = load volatile i64, ptr %box, align 8\n",
    "  call void @llvm.lifetime.start.p0(i64 8, ptr %box)\n"
    "  %loaded = load volatile i64, ptr %box, align 8\n")),
    "MVO escaped address used by lifetime intrinsic rejected")
# An unrelated lifetime call must NOT block a separate eligible alloca.
k8.validate_mvo_input_ir(mvo_eligible.replace(
    "  ret i64 %loaded\n",
    "  %other = alloca i64, align 8\n"
    "  call void @llvm.lifetime.start.p0(i64 8, ptr %other)\n"
    "  ret i64 %loaded\n"))
pilot_source = (BASE / "pilot.py").read_text(encoding="utf-8")
for contract in (
    '"-O0", "-Xclang", "-disable-O0-optnone"',
    'mvo_host_bc if name == "mvo" else plain_bc',
    'mvo_host_obj if name == "mvo" else plain_obj',
    'mvo_ios_bc if name == "mvo" else ios_plain_bc',
    'mvo_ios_obj if name == "mvo" else ios_plain_obj',
    'mvo_host_log.read_bytes() != plain_log.read_bytes()',
    'validate_mvo_input_ir(mvo_text)',
    'validate_mvo_input_ir(mvo_ios_ir.read_text',
    'host_before_obj.read_bytes()',
    'ios_before_obj.read_bytes()',
    'candidate_obj.read_bytes()',
):
    assert contract in pilot_source, contract

# The C fixture must retain every pass trigger after O1 or fail on macOS.
fixture = (BASE / "fixture.c").read_text(encoding="utf-8")
assert "static const uint64_t dd_k8_table[8]" in fixture
assert "static const uint64_t dd_k8_genc_scalar" in fixture
assert "*(const volatile uint64_t *)&dd_k8_genc_scalar" in fixture
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
