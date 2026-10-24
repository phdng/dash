#!/usr/bin/env python3
"""K19 synthetic corruption gates. Test-created binaries are NOT macOS CI proof."""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import struct
import sys
import tempfile
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = ROOT / "scripts/custom_ollvm/kagura_k19"
sys.path.insert(0, str(HERE))
import symbol_ranges as k19


def reject(fn, message):
    try:
        fn()
    except (AssertionError, ValueError, KeyError, struct.error):
        return
    raise AssertionError("K19 incorrectly accepted " + message)


def executable(code: bytes, names: tuple[str, ...], *, subtype=0,
               duplicate_alias=False, bad_strx=False, export=True,
               string_prefix=b"\0", unnamed_local=False):
    assert len(code) >= 128 and len(code) % 4 == 0
    segsize = 72 + 80
    cmdsize = segsize + 24 + 24
    textoff = 32 + cmdsize
    vmbase = 0x100000000
    symbols = list(names) + ["_other"]
    addresses = list(range(0, len(symbols) * 32, 32))
    assert addresses[-1] < len(code)
    if duplicate_alias:
        addresses[-1] = addresses[0]
    # Apple ld64 uses linker-dependent padding, often b" \\0".
    assert string_prefix.endswith(b"\0") and len(string_prefix) >= 1
    string_table = bytearray(string_prefix)
    nlists = bytearray()
    for i, name in enumerate(symbols):
        ix = len(string_table)
        string_table.extend(name.encode("ascii") + b"\0")
        local_unnamed = unnamed_local and name == "_other"
        nlists.extend(struct.pack("<IBBHQ",
                                  0xffffffff if bad_strx and i == 0 else
                                  (0 if local_unnamed else ix),
                                  0x0e if local_unnamed else (0x0f if export else 0x0e),
                                  1, 0, vmbase + textoff + addresses[i]))
    symoff = textoff + len(code)
    stroff = symoff + len(nlists)
    header = struct.pack("<8I", 0xfeedfacf, 0x0100000c, subtype,
                         2, 3, cmdsize, 0, 0)
    segment = struct.pack("<II16sQQQQIIII", 0x19, segsize,
                          b"__TEXT" + b"\0" * 10, vmbase, 4096,
                          0, stroff + len(string_table), 7, 5, 1, 0)
    section = struct.pack("<16s16sQQIIIIIIII",
                          b"__text" + b"\0" * 10, b"__TEXT" + b"\0" * 10,
                          vmbase + textoff, len(code), textoff,
                          4, 0, 0, 0x80000400, 0, 0, 0)
    lc_uuid = struct.pack("<II16s", 0x1b, 24,
                          uuid.UUID("7c0cb853-77aa-3ccb-9f20-560e5f40e587").bytes)
    lc_symtab = struct.pack("<6I", 0x2, 24, symoff, len(symbols),
                            stroff, len(string_table))
    data = header + segment + section + lc_uuid + lc_symtab + code + nlists + string_table
    assert len(data) == stroff + len(string_table)
    return bytes(data)


code = b"\x1f\x20\x03\xd5" * 32
changed = b"\xc0\x03\x5f\xd6" * 20 + b"\x1f\x20\x03\xd5" * 12
baseline = executable(code, ("_dd_k8_evaluate",))
protected = executable(changed, ("_dd_k8_evaluate",))
ios = executable(changed, ("_dd_k8_evaluate", "_dd_k14_ios_parity"))
assert k19.inspect(baseline, ("_dd_k8_evaluate",))["observed_symbols"]["_dd_k8_evaluate"]["length"] == 32
# Regression for real ld64 CI failure: string table may begin SPACE NUL,
# not just NUL. Both must decode by n_strx into valid bounded names.
for prefix in (b"\0", b" \0", b" \0\0", b"PAD\0"):
    specimen = executable(code, ("_dd_k8_evaluate",), string_prefix=prefix)
    assert k19.inspect(specimen, ("_dd_k8_evaluate",))["observed_symbols"]["_dd_k8_evaluate"]["length"] == 32
assert k19.inspect(executable(code, ("_dd_k8_evaluate",), unnamed_local=True),
                   ("_dd_k8_evaluate",))["observed_symbols"]["_dd_k8_evaluate"]["length"] == 32
first_nlist = 32 + (72 + 80 + 24 + 24) + len(code)
# Darwin n_strx is an offset, not necessarily a NUL-delimited *start*:
# a linker can reuse the suffix of an earlier string. Accept valid suffix
# lookup, but never accept malformed/out-of-bounds or the wrong target.
suffix_table = b"prefix_dd_k8_evaluate\0"
suffix_binary = bytearray(executable(code, ("_dd_k8_evaluate",),
                                     string_prefix=suffix_table))
struct.pack_into("<I", suffix_binary, first_nlist, len(b"prefix"))
assert k19.inspect(bytes(suffix_binary), ("_dd_k8_evaluate",))[
    "observed_symbols"]["_dd_k8_evaluate"]["length"] == 32
invalid_start = bytearray(baseline)
struct.pack_into("<I", invalid_start, first_nlist, 2)
reject(lambda: k19.inspect(bytes(invalid_start), ("_dd_k8_evaluate",)),
       "symbol pointer that decodes to a different name")
external_zero = bytearray(baseline)
struct.pack_into("<I", external_zero, first_nlist, 0)
reject(lambda: k19.inspect(bytes(external_zero), ("_dd_k8_evaluate",)),
       "external N_SECT strx zero")
assert len(k19.inspect(ios, ("_dd_k8_evaluate", "_dd_k14_ios_parity"))["observed_symbols"]) == 2
assert k19.inspect(ios, ("_dd_k8_evaluate", "_dd_k14_ios_parity"))["observed_symbols"]["_dd_k14_ios_parity"]["length"] == 32
assert k19.inspect(baseline, ("_dd_k8_evaluate",))["observed_symbols"]["_dd_k8_evaluate"]["sha256"] != k19.inspect(protected, ("_dd_k8_evaluate",))["observed_symbols"]["_dd_k8_evaluate"]["sha256"]
reject(lambda: k19.inspect(executable(code, ("_dd_k8_evaluate",), subtype=2), ("_dd_k8_evaluate",)), "arm64e")
reject(lambda: k19.inspect(executable(code, ("_dd_k8_evaluate",), duplicate_alias=True), ("_dd_k8_evaluate",)), "alias")
reject(lambda: k19.inspect(executable(code, ("_dd_k8_evaluate",), bad_strx=True), ("_dd_k8_evaluate",)), "bad symbol strx")
reject(lambda: k19.inspect(executable(code, ("_dd_k8_evaluate",), export=False), ("_dd_k8_evaluate",)), "non-exported source")
reject(lambda: k19.inspect(baseline, ("_fake",)), "fake source symbol")
reject(lambda: k19.inspect(baseline[:-12], ("_dd_k8_evaluate",)), "truncated string table")
no_symtab = bytearray(baseline)
# Third load command is LC_SYMTAB; corrupt its type.
struct.pack_into("<I", no_symtab, 32 + 152 + 24, 0x9)
reject(lambda: k19.inspect(bytes(no_symtab), ("_dd_k8_evaluate",)), "missing LC_SYMTAB")

with tempfile.TemporaryDirectory(prefix="K19-portable-only-") as tmp:
    out = pathlib.Path(tmp)
    for name, data in (
        ("macos-baseline", baseline),
        ("macos-cse-break", protected),
        ("KaguraCSEBreakLab.app/KaguraCSEBreakLab", ios),
    ):
        f = out / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(data)
    k13 = {
        "scope": "K13_SINGLE_ISOLATED_PINNED_CSE_BREAK_NATIVE_MACOS_AND_IOS_OBJECT_ONLY",
        "pass": "kagura-cse-break", "pass_class": "kagura::CSEBreakPass",
        "targets": {"macos": {"native_parity": "PASS", "native_vectors": 4096,
                              "baseline_checksum": "25a3318e3d7d6525",
                              "protected_checksum": "25a3318e3d7d6525"}},
        "security_strength_claim": False,
    }
    k14exe = k19.k16.inspect_macho(ios)
    k14 = {"scope": "STANDALONE_K14_SINGLE_CSE_BREAK_IOS_ARM64_UNSIGNED_LAB",
           "signing": "UNSIGNED", "app_macho_uuid": k14exe["uuid"],
           "ipa_sha256": "a" * 64, "binary_sha256": k14exe["binary_sha256"]}
    k14ev = {"k13_cse_break_ios_object_embedded": True,
             "ipa_sha256": k14["ipa_sha256"],
             "app_binary_sha256": k14["binary_sha256"],
             "ios_device_execution": "NOT_TESTED_BY_CI", "security_attestation": False}
    def save():
        for filename, obj in (
            ("Kagura-K13-REPORT.json", k13),
            ("Kagura-K14-IPA-report.json", k14),
            ("Kagura-K14-IPA-EVIDENCE.json", k14ev),
        ):
            (out / filename).write_text(json.dumps(obj, sort_keys=True), encoding="utf-8")
    save()
    k19.k16.measure(out)
    measure = k19.record(out)
    assert measure["k18_dependency"] == "NONE_SKIPPED_BY_USER_NOT_TESTED"
    assert measure["runtime_verifier_implemented"] is False
    assert measure["addresses_are_boundaries_not_precise_function_lengths"] is True
    assert k19.verify(out) == measure
    record_path = out / k19.NAME
    original = record_path.read_bytes()
    fake = copy.deepcopy(measure)
    fake["security_anti_tamper_proven"] = True
    record_path.write_text(json.dumps(fake), encoding="utf-8")
    reject(lambda: k19.verify(out), "forged security result")
    record_path.write_bytes(original)
    path = out / "macos-cse-break"
    path.write_bytes(protected[:-1] + bytes([protected[-1] ^ 1]))
    reject(lambda: k19.verify(out), "modified file after manifest captured")
    path.write_bytes(protected)
    # Tamper with a code byte AFTER computing authentic K16 whole text reference.
    at = 32 + (72+80) + 24 + 24
    path.write_bytes(protected[:at] + bytes([protected[at] ^ 1]) + protected[at + 1:])
    reject(lambda: k19.verify(out), "modified symbol code after manifest captured")
    path.write_bytes(protected)
    k13["targets"]["macos"]["native_parity"] = "NOT_TESTED"
    save()
    reject(lambda: k19.verify(out), "unverified K13 native source")
    k13["targets"]["macos"]["native_parity"] = "PASS"
    save()
    assert k19.verify(out) == measure

workflow = (ROOT / ".github/workflows/kagura-k19-symbol-bounded.yml").read_text(
    encoding="utf-8")
for required in (
    "workflow_dispatch:", "runs-on: macos-14",
    "scripts/test_kagura_k19_symbol_ranges.py",
    "scripts/custom_ollvm/kagura_k13/pilot.py",
    "scripts/custom_ollvm/kagura_k13/audit.py",
    "scripts/custom_ollvm/kagura_k14/build_ipa.sh",
    "scripts/custom_ollvm/kagura_k16/macho_measure.py",
    "scripts/custom_ollvm/kagura_k19/symbol_ranges.py",
    "DuoDash-Kagura-K19-SYMBOL-BOUNDED-MACHO-OFFLINE-EXPERIMENTAL",
    "if: always()", "K18 SKIPPED/NOT TESTED",
):
    assert required in workflow, required
for banned in ("kagura_k18/", "K18_ED25519_PRIVATE_KEY_PEM",
               "kagura-bbcheck", "devicectl", "codesign -s", "git push"):
    assert banned not in workflow, banned
print("K19_PORTABLE_SYMTAB_ADDRESS_BOUND_PASS: 3 thin arm64 Mach-O symbol canaries,"
      " raw nlist and text SHA gates, corruption and false security rejected;"
      " real macOS CI NOT_TESTED; K18 SKIPPED")
