#!/usr/bin/env python3
"""Portable IGV/IBR source-pilot model, Mach-O and CI negative regression tests."""
from __future__ import annotations

import importlib.util
import json
import random
import struct
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/protection_lab"
sys.path.insert(0, str(LAB))


def load(name: str):
    path = LAB / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec.loader is not None
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


audit = load("igv_ibr_audit")
macho = load("audit")
MASK = (1 << 64) - 1
KEYS = (0x9e3779b97f4a7c15, 0xd1b54a32d192ed03,
        0xa0761d6478bd642f, 0xe7037ed1a0b428db)


def igv_plain(a: int, b: int, index: int) -> int:
    key = KEYS[index & 3]
    return ((a ^ key) + b * ((key >> 1) | 1)) & MASK


def igv_protected(a: int, b: int, index: int) -> int:
    globals_ = (KEYS[2], KEYS[3], KEYS[0], KEYS[1])
    refs = (2, 3, 0, 1)
    key = globals_[refs[index & 3]]
    return ((a ^ key) + b * ((key >> 1) | 1)) & MASK


def steps(x: int, b: int):
    return (
        ((x ^ ((b + KEYS[0]) & MASK)) +
         (((b << 7) | (b >> 57)) & MASK)) & MASK,
        (((x + (b ^ KEYS[1])) & MASK) ^ (x >> 11)) & MASK,
        (x * KEYS[2] + (b >> 3)) & MASK,
        (((x << 9) | (x >> 55)) ^ ((b + KEYS[3]) & MASK)) & MASK,
    )


def ibr_plain(a: int, b: int, mode: int) -> int:
    x = a
    for n in range(7):
        selector = ((x ^ (b >> ((n & 3) * 8))) + mode + n) & 3
        x = steps(x, b)[selector]
    return x


def ibr_protected(a: int, b: int, mode: int) -> int:
    handlers = (
        lambda x, b: ((x ^ ((b + KEYS[0]) & MASK)) +
                      (((b << 7) | (b >> 57)) & MASK)) & MASK,
        lambda x, b: (((x + (b ^ KEYS[1])) & MASK) ^ (x >> 11)) & MASK,
        lambda x, b: (x * KEYS[2] + (b >> 3)) & MASK,
        lambda x, b: (((x << 9) | (x >> 55)) ^
                      ((b + KEYS[3]) & MASK)) & MASK,
    )
    x = a
    for n in range(7):
        selector = ((x ^ (b >> ((n & 3) * 8))) + mode + n) & 3
        x = handlers[selector](x, b)
    return x


vectors = [(0, 0, 0), (MASK, MASK, 0xffffffff),
           (MASK, 0, 2), (0, MASK, 3)]
rng = random.Random(762318)
vectors.extend((rng.getrandbits(64), rng.getrandbits(64),
                rng.getrandbits(32)) for _ in range(10000))
for a, b, mode in vectors:
    assert igv_plain(a, b, mode) == igv_protected(a, b, mode)
    assert ibr_plain(a, b, mode) == ibr_protected(a, b, mode)
    assert igv_plain(a, b, mode) == igv_plain(a, b, mode & 3)

protected_src = (LAB / "igv_ibr_protected.c").read_text(encoding="utf-8")
plain_src = (LAB / "igv_ibr_plain.c").read_text(encoding="utf-8")
for expected in ("volatile dd_test_global_refs[4]",
                 "const volatile uint64_t *pointer",
                 "dd_ibr_handler handler = dd_ibr_handlers[choice]",
                 "x = handler(x, b)"):
    assert expected in protected_src, expected
assert "switch (choice)" in plain_src and "switch (index & 3U)" in plain_src
for forbidden in ("uintptr_t", "ptrauth_strip", "__builtin_ptrauth",
                  "mprotect(", "mmap(", "syscall("):
    assert forbidden not in protected_src

good_bench = (
    audit.HOST_PASS + "\n" +
    "IGV_IBR_BENCH: igv_plain_us=101.250 igv_protected_us=202.500 "
    "ibr_plain_us=400.250 ibr_protected_us=802.000\n"
)
with tempfile.TemporaryDirectory() as folder:
    tmp = Path(folder)
    log = tmp / "host.txt"
    log.write_text(good_bench, encoding="utf-8")
    perf = audit.parse_host_log(log)
    assert perf["tested_vectors"] == 8192
    assert perf["igv_slowdown_host_observation_only"] == 2
    assert perf["performance_gate"] == "NONE_TIMINGS_ARE_NOISY"

    for malformed in (
        "", audit.HOST_PASS + "\n", "FAKE_HOST_PASS\n" + good_bench,
        good_bench.replace("101.250", "0.000"),
        good_bench.replace("202.500", "-2.000"),
        good_bench.replace("802.000", "NaN"),
        good_bench + "extra\n",
    ):
        log.write_text(malformed, encoding="utf-8")
        try:
            audit.parse_host_log(log)
        except AssertionError:
            pass
        else:
            raise AssertionError("Invalid host benchmark or parity evidence accepted")
    log.write_text(good_bench, encoding="utf-8")

    def binary(subtype: int, suffix: bytes) -> bytes:
        return struct.pack("<IIIIIIII", macho.MAGIC,
                           macho.ARM64_CPUTYPE, subtype,
                           macho.MH_DYLIB, 0, 0, 0, 0) + suffix

    files = {}
    for arch, subtype in (("arm64", 0), ("arm64e", 0x80000002)):
        plain, protected = tmp / f"{arch}-plain.dylib", tmp / f"{arch}-protected.dylib"
        plain_asm = tmp / f"{arch}-plain.asm"
        protected_asm = tmp / f"{arch}-protected.asm"
        plain.write_bytes(binary(subtype, b"plain" + arch.encode("ascii")))
        protected.write_bytes(binary(subtype, b"protected" + arch.encode("ascii")))
        plain_asm.write_text(
            "_dd_igv_plain:\n    add x0, x0, x1\n_dd_ibr_plain:\n    eor x0, x0, x1\n"
            + "    ret\n" * 12, encoding="utf-8"
        )
        protected_asm.write_text(
            "_dd_igv_protected:\n    ldr x0, [x1]\n_dd_ibr_protected:\n"
            "    blr x11\n" + "    ret\n" * 12, encoding="utf-8"
        )
        files[arch] = (plain, protected, plain_asm, protected_asm)
    report = audit.audit(files, log, tmp / "proof")
    saved = json.loads((tmp / "proof/report.json").read_text(encoding="utf-8"))
    assert saved == report
    assert report["slices"]["arm64e"]["protected"]["versioned_pac_abi"] is True
    assert report["slices"]["arm64e"]["device_pac_runtime"].startswith("NOT_TESTED")
    assert report["slices"]["arm64"]["asm_delta_generated"]
    assert (tmp / "proof/igv-ibr-arm64.diff").is_file()
    assert (tmp / "proof/igv-ibr-arm64e.diff").is_file()

    def must_reject():
        try:
            audit.audit(files, log, tmp / "negative")
        except (AssertionError, ValueError):
            return
        raise AssertionError("Invalid Mach-O/asm test evidence accepted")

    one = files["arm64e"][1]
    one.write_bytes(binary(1, b"unversioned_old_ABI"))
    must_reject()
    one.write_bytes(binary(0x80000002, b"protectedarm64e"))
    one = files["arm64"][1]
    one.write_bytes(files["arm64"][0].read_bytes())
    must_reject()
    one.write_bytes(binary(0, b"protectedarm64"))
    asm = files["arm64"][3]
    asm.write_text("missing symbols", encoding="utf-8")
    must_reject()
    asm.write_text(
        "_dd_igv_protected:\n    ldr x0, [x1]\n_dd_ibr_protected:\n"
        "    blr x11\n" + "    ret\n" * 12, encoding="utf-8"
    )
    log.write_text("spoofed host\n", encoding="utf-8")
    must_reject()

workflow = (ROOT / ".github/workflows/protection-igv-ibr-pilot.yml").read_text(
    encoding="utf-8"
)
assert "workflow_dispatch:" in workflow and "runs-on: macos-14" in workflow
assert "xcrun --sdk iphoneos --find clang" in workflow
assert "for arch in arm64 arm64e; do" in workflow
assert "for variant in plain protected; do" in workflow
assert "igv_ibr_runner.c" in workflow and "igv_ibr_audit.py" in workflow
assert "--arm64e-protected-asm" in workflow
assert "IGV_IBR_HOST_PASS: 8192 dual-function parity vectors" in workflow
assert "IGV_IBR_BENCH:" in workflow
assert "otool -tvV" in workflow and "report.json" in workflow
assert "actions/upload-artifact@v4" in workflow
assert "make clean package" not in workflow and "TARGET_CC=" not in workflow
assert "fpass-plugin" not in workflow and "llvm@19" not in workflow
assert "NOT TESTED" in workflow and "test_sllvm_pilot.py" in workflow
assert "protection-sllvm-pilot.yml" not in workflow
print(f"IGV/IBR pilot: {len(vectors)} portable parity vectors, "
      "Mach-O/host negative guards, isolated CI PASS")
