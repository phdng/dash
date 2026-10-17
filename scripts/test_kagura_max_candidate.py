#!/usr/bin/env python3
"""Portable regression for separately built Kagura LLVM19 MAX candidate.

The actual Kagura LLVM plugin is compiled and executed on macOS CI only.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import struct
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "scripts/custom_ollvm/kagura_max"
spec = importlib.util.spec_from_file_location("kagura_max_audit", DIR / "audit.py")
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
config = module.read_profile()
assert config["host_vectors"] == 8192
assert len(config["stages"]) == 5
assert config["selector"]["symbol"] == "dd_kagura_critical"
assert config["profile"] == "MAX_CANDIDATE"
assert config["llvm_major"] == 19
assert config["origin"] == "qusamulab/kagura"
assert len(config["upstream_commit"]) == 40
for update in (
    lambda x: x.update(profile="DEPLOYED_MAX"),
    lambda x: x.update(llvm_major=22),
    lambda x: x.update(upstream_commit="main"),
    lambda x: x["selector"].update(production_allowlist_modified=True),
    lambda x: x["selector"].update(symbol="objc_msgSend"),
    lambda x: x.update(pass_pipeline="kagura-fla"),
    lambda x: x["stages"].append("kagura-vm"),
    lambda x: x.update(host_vectors=0),
    lambda x: x["targets"].update(ios_arm64e="Kagura plugin protected and PAC runtime PASS"),
    lambda x: x["not_enabled"].remove("kagura-pac"),
):
    fake = copy.deepcopy(config)
    update(fake)
    with tempfile.TemporaryDirectory() as folder:
        file = Path(folder) / "profile.json"
        file.write_text(json.dumps(fake), encoding="utf-8")
        try:
            module.read_profile(file)
        except (AssertionError, ValueError, KeyError):
            pass
        else:
            raise AssertionError("Unsafe/unverified Kagura strength claims accepted")


def fake_macho(subtype: int) -> bytes:
    return struct.pack("<IIIIIIII",
                       0xFEEDFACF, 0x0100000C, subtype, 6, 0, 0, 0, 0)


with tempfile.TemporaryDirectory() as folder:
    root = Path(folder)
    native_plain = root / "native-plain.o"
    native_protected = root / "native-candidate.o"
    ir_plain = root / "native-plain.bc"
    ir_protected = root / "native-candidate.bc"
    native_plain.write_bytes(b"MACO:PLAIN:" + module.MARKER)
    native_protected.write_bytes(b"MACO:ENCODED:BYTES")
    ir_plain.write_bytes(b"IR-native-original")
    ir_protected.write_bytes(b"IR-native-transformed")
    result = module.inspect_candidate(native_plain, native_protected,
                                      ir_plain, ir_protected)
    assert result["public_plaintext_absent_candidate"] is True
    assert result["native_byte_difference"] is True
    for path, value in (
        (native_protected, native_plain.read_bytes()),
        (ir_protected, ir_plain.read_bytes()),
        (native_protected, b"MACO:" + module.MARKER),
    ):
        current = path.read_bytes()
        path.write_bytes(value)
        try:
            module.inspect_candidate(native_plain, native_protected,
                                     ir_plain, ir_protected)
        except AssertionError:
            pass
        else:
            raise AssertionError("No transformation/plaintext exposure accepted")
        path.write_bytes(current)

    valid = "\n".join(f"{i:04d}:{i * 27:016x}" for i in range(8192))
    valid += "\nDD_KAGURA_HOST_PASS=8192\n"
    p = root / "plain.log"
    obf = root / "protected.log"
    p.write_text(valid, encoding="utf-8")
    obf.write_text(valid, encoding="utf-8")
    native = module.verify_host(p, obf)
    assert native["macos_host"] == "NATIVE_8192_VALUES_EQUAL"
    assert native["ios_runtime"] == "NOT_TESTED_BY_CI"
    obf.write_text(valid.replace("0000:0000000000000000",
                                 "0000:1111111111111111"), encoding="utf-8")
    try:
        module.verify_host(p, obf)
    except AssertionError:
        pass
    else:
        raise AssertionError("Native nonparity accepted")
    obf.write_bytes(p.read_bytes())

    arm64_plain = root / "ios-plain.dylib"
    arm64_candidate = root / "ios-candidate.dylib"
    arm64e = root / "ios-apple-arm64e.dylib"
    arm64_plain.write_bytes(fake_macho(0) + module.MARKER)
    arm64_candidate.write_bytes(fake_macho(0) + b"ENCODED")
    arm64e.write_bytes(fake_macho(0x80000002) + module.MARKER)
    ios = module.inspect_ios(arm64_plain, arm64_candidate, arm64e)
    assert ios["ios_arm64e"] == "APPLE_CLANG_BUILD_ABI_ONLY_NOT_KAGURA_PROTECTED"
    assert ios["ios_arm64e_apple_clang"]["cpu_subtype_raw"] == "0x80000002"
    assert ios["arm64e_a12plus_pac_runtime"] == "DEFERRED_NO_DEVICE"
    arm64e.write_bytes(fake_macho(1))
    try:
        module.inspect_ios(arm64_plain, arm64_candidate, arm64e)
    except AssertionError:
        pass
    else:
        raise AssertionError("Old PAC ABI accepted")

workflow = (ROOT / ".github/workflows/kagura-max-candidate.yml").read_text(encoding="utf-8")
for required in (
    "workflow_dispatch:", "runs-on: macos-14",
    "python3 scripts/test_kagura_max_candidate.py",
    "https://github.com/qusamulab/kagura.git",
    config["upstream_commit"],
    'test "$(git -C "$src" rev-parse HEAD)" = "$pin"',
    "brew install llvm@19",
    '-DKAGURA_BUILD_TESTS=OFF',
    '--load-pass-plugin="$KAGURA_PLUGIN"',
    "-passes='kagura-str,function(kagura-fla,kagura-bcf,kagura-sub,kagura-co)'",
    'cmp "$out/host-plain.log" "$out/host-candidate.log"',
    "arm64-apple-ios15.0",
    "arm64e-apple-ios15.0",
    "scripts/custom_ollvm/kagura_max/audit.py",
    "DuoDash-Kagura-MAX-CANDIDATE-LLVM19-EXPERIMENTAL",
):
    assert required in workflow, required
for prohibited in (
    "make clean package", "DEVELOPMENT_TEAM=", "codesign -s", "ldid -S",
    "dpkg -i", "devicectl device install", "PAC_STRIP", "mprotect(",
):
    assert prohibited.lower() not in workflow.lower()
assert workflow.count("-passes='kagura-str,function(") == 2
assert workflow.index("host-plain.bc") < workflow.index("host-candidate.bc")
assert "run-on:" not in workflow
assert not (ROOT / "Makefile").read_text(encoding="utf-8").find("KAGURA_PLUGIN") >= 0
assert (DIR / ".gitignore").read_text(encoding="utf-8").strip() == "out/"
assert module.MARKER.decode() in (DIR / "critical.c").read_text(encoding="utf-8")
assert "dd_kagura_critical" in (DIR / "runner.c").read_text(encoding="utf-8")
print("KAGURA_MAX_PROFILE_PORTABLE_PASS: real opt LLVM IR pipeline "
      "staged; native/ABI checks reject malformed fixtures, production untouched")
