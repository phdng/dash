#!/usr/bin/env python3
"""Portable strict negative tests for isolated Kagura K6 REAL VM pilot.

Synthetic Mach-O/IR and output here verify the parser, NOT real VM or iOS.
"""
from __future__ import annotations

import importlib.util
import json
import struct
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/custom_ollvm/kagura_vm"
sys.path.insert(0, str(LAB))
from oracle import checksums, guard, mix, values  # noqa: E402
import audit  # noqa: E402

assert checksums() == ("9625f13d712f59c3", "09d9d53ddf189ce7")
assert checksums(0) == ("0000000000000000", "0000000000000000")
assert mix(0, 0) != mix(0, 1)
assert guard(0, 0) != guard(1, 0)
assert values(0)[0] == 0

with tempfile.TemporaryDirectory(prefix="Kagura K6 synthetic only ") as work:
    root = Path(work)
    base_ir = root / "plain.ll"
    vm_ir = root / "vm.ll"
    ios_ir = root / "ios-vm.ll"
    native = root / "native.log"
    trace = root / "trace.log"
    ios_trace = root / "ios-trace.log"
    arm64 = root / "ios.dylib"
    report = root / "report.json"

    guard_body = "entry:\n  %v = xor i64 %x, %salt\n  ret i64 %v\n"
    base_ir.write_text(
        "define i64 @dd_vm_plain(i64 %x, i64 %salt) {\n"
        "entry:\n  %v = add i64 %x, %salt\n  ret i64 %v\n}\n"
        "define i64 @dd_vm_guard_plain(i64 %x, i64 %salt) {\n" +
        guard_body + "}\n", encoding="utf-8")
    protected_text = (
        "@kagura_vm_bc_123 = private constant [1 x i8] c\"X\"\n"
        "@kagura_vm_key_123 = private constant i64 999\n"
        "declare i64 @kagura_vm_execute(ptr, i32, ptr, i32, ptr, i32, i64)\n"
        "define i64 @dd_vm_protected(i64 %x, i64 %salt) {\n"
        "entry:\n  %v = call i64 @kagura_vm_execute(ptr null, i32 1, "
        "ptr null, i32 2, ptr null, i32 0, i64 42)\n"
        "  ret i64 %v\n}\n"
        "define i64 @dd_vm_guard_protected(i64 %x, i64 %salt) {\n" +
        guard_body + "}\n"
    )
    vm_ir.write_text(protected_text, encoding="utf-8")
    ios_ir.write_text(protected_text, encoding="utf-8")
    for log in (trace, ios_trace):
        log.write_text("Running pass: kagura::VMObfuscationPass "
                       "on dd_vm_protected\n", encoding="utf-8")
    checksum, guard_sum = checksums()
    lines = [
        "DD_VM_SCHEMA=1",
        "DD_VM_CONTEXT=MACOS_HOST",
        "DD_VM_VECTORS_PASS=4096",
        "DD_VM_PARITY_CHECKSUM=" + checksum,
        "DD_VM_GUARD_CHECKSUM=" + guard_sum,
        "DD_VM_BENCH_CALLS=1024",
        "DD_VM_BENCH_PAIRS=3",
    ]
    for i in range(3):
        lines += [f"DD_VM_PLAIN_NS_{i}={20 + i}",
                  f"DD_VM_PROTECTED_NS_{i}={200 + i}"]
    lines += ["DD_VM_COMPLETE=PASS"]
    native.write_text("\n".join(lines) + "\n", encoding="ascii")
    uuid_bytes = uuid.UUID("179f30eb-1629-3658-86fc-cd7da188a483").bytes
    arm64.write_bytes(
        struct.pack("<IIIIIIII", 0xFEEDFACF, 0x0100000C, 0, 6,
                    1, 24, 0, 0) +
        struct.pack("<II", 0x1B, 24) + uuid_bytes +
        b"test fixture, not an actual Mach-O dylib"
    )
    args = dict(plain_ir=base_ir, candidate_ir=vm_ir, ios_ir=ios_ir,
                vm_trace=trace, ios_trace=ios_trace,
                native_log=native, vm_dylib=arm64, output=report)
    verified = audit.audit(**args)
    assert verified == json.loads(report.read_text(encoding="utf-8"))
    assert verified["true_vm_trampoline_observed"] is True
    assert verified["native_guard_body_unchanged"] is True
    assert verified["macos"]["parity_vectors"] == 4096
    assert verified["ios_arm64_build_only"]["device_execution"] == "NOT_TESTED"
    assert verified["security_attestation"] is False

    def reject(reason: str) -> None:
        try:
            audit.audit(**args)
        except (AssertionError, ValueError, UnicodeDecodeError):
            return
        raise AssertionError("Accepted bad K6 proof: " + reason)

    for file, bad, reason in (
        (vm_ir, protected_text.replace("@kagura_vm_execute(",
                                       "@another_fn("), "not a real VM call"),
        (vm_ir, protected_text.replace("kagura_vm_bc_", "test_bc_"),
         "no VM blob"),
        (vm_ir, protected_text.replace(guard_body,
                                      guard_body.replace("xor", "add")),
         "non-allowlisted guard mutated"),
        (ios_ir, protected_text.replace("kagura_vm_bc_", "test_bc_"),
         "iOS candidate not VM"),
        (trace, "Running pass: FakePass\n", "wrong pass class"),
        (ios_trace, "Running pass: FakePass\n", "iOS pass absent"),
        (native, "\n".join(lines).replace(checksum, "0000000000000000")
         + "\n", "wrong checksum"),
        (native, "\n".join(lines).replace("DD_VM_CONTEXT=MACOS_HOST",
                                         "DD_VM_CONTEXT=IOS_DEVICE")
         + "\n", "fake iPhone context"),
    ):
        old = file.read_text(encoding="utf-8")
        file.write_text(bad, encoding="utf-8")
        reject(reason)
        file.write_text(old, encoding="utf-8")
    old_binary = arm64.read_bytes()
    for subtype in (2, 0x80000002):
        fake = bytearray(old_binary)
        struct.pack_into("<I", fake, 8, subtype)
        arm64.write_bytes(fake)
        reject("arm64 subtype mismatch")
    arm64.write_bytes(old_binary)
    # Invalid LC_UUID count or type must fail.
    invalid = bytearray(old_binary)
    struct.pack_into("<I", invalid, 12, 2)
    arm64.write_bytes(invalid)
    reject("not an MH_DYLIB")
    arm64.write_bytes(old_binary)

app_workflow = (ROOT / ".github/workflows/kagura-vm-selective.yml").read_text(
    encoding="utf-8")
script = (LAB / "build.sh").read_text(encoding="utf-8")
fixture = (LAB / "vm_canary.c").read_text(encoding="utf-8")
runner = (LAB / "vm_runner.c").read_text(encoding="utf-8")
for phrase in (
    "workflow_dispatch:", "runs-on: macos-14",
    "ac2136ee0408677cf7cdee55307e9b16edd5f4d5",
    "libkagura_runtime.a", "scripts/test_kagura_vm_selective.py",
    "scripts/custom_ollvm/kagura_vm/build.sh",
    "DuoDash-Kagura-K6-VM-SELECTIVE-LLVM19-EXPERIMENTAL",
    "KaguraVM-arm64-BUILD-ONLY.dylib",
):
    assert phrase in app_workflow, phrase
for phrase in (
    "-kagura-vm", "-kagura-allow=dd_vm_protected",
    "-passes='function(kagura-vm),verify'",
    "vm_interpreter.c", "KaguraVM-arm64-BUILD-ONLY.dylib",
    "xcrun clang", "llvm/bin/opt", "vm-native.log", "--ios-trace",
    "KAGURA-UPSTREAM-LICENSE",
):
    assert phrase in script, phrase
for phrase in ("annotate(\"kagura_vm\")", "DD_VM_ENTRY", "DD_VM_GUARD",
               "noinline"):
    assert phrase in fixture, phrase
for phrase in ("DD_VM_VECTORS = 4096", "DD_VM_CONTEXT=MACOS_HOST",
               "DD_VM_COMPLETE=PASS", "dd_vm_guard_plain",
               "dd_vm_guard_protected"):
    assert phrase in runner, phrase
for text in (app_workflow, script):
    for forbidden in ("make clean package", "codesign -s", "ldid -S",
                      "devicectl device install", "ptrauth_strip",
                      "substitute_crane_tweak", "re/RECONSTRUCTION",
                      "THEOS_PACKAGE_SCHEME"):
        assert forbidden not in text, forbidden
assert "Kagura-K6" not in (ROOT / "Makefile").read_text(encoding="utf-8")
assert "kagura-vm" not in (
    ROOT / ".github/workflows/build.yml").read_text(encoding="utf-8")
print("KAGURA_K6_VM_PORTABLE_PASS: real-pass+allowlist contracts, "
      "synthetic IR/Mach-O negative cases, native parity reference; "
      "actual Kagura VM/macOS CI and iPhone runtime NOT YET TESTED")
