#!/usr/bin/env python3
"""K20 portable Mach-O LC_FUNCTION_STARTS ULEB128 crosscheck negative gates."""
from __future__ import annotations

import copy
import json
import pathlib
import struct
import sys
import tempfile
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = ROOT / "scripts/custom_ollvm/kagura_k20"
sys.path.insert(0, str(HERE))
import function_starts as k20


def rejects(fn, label):
    try:
        fn()
    except (AssertionError, ValueError, KeyError, struct.error):
        return
    raise AssertionError("K20 wrongfully accepted " + label)


def uleb(n: int) -> bytes:
    assert n >= 0
    out = bytearray()
    while n > 0x7f:
        out.append((n & 0x7f) | 0x80)
        n >>= 7
    out.append(n)
    return bytes(out)


def specimen(code: bytes, symbols: tuple[str, ...], *,
             points: tuple[int, ...] | None = None) -> bytes:
    assert len(code) >= 128 and len(code) % 4 == 0
    segment_size = 72 + 80
    cmds_size = segment_size + 24 + 24 + 16
    offset = 32 + cmds_size
    vm = 0x100000000
    targets = (*symbols, "_other")
    addresses = tuple(k * 32 for k in range(len(targets)))
    assert addresses[-1] < len(code)
    strings = bytearray(b" \0")
    names = bytearray()
    for i, name in enumerate(targets):
        ix = len(strings)
        strings.extend(name.encode("ascii") + b"\0")
        names.extend(struct.pack("<IBBHQ", ix, 0x0f, 1, 0, vm + offset + addresses[i]))
    symoff = offset + len(code)
    stroff = symoff + len(names)
    starts = tuple(offset + x for x in addresses) if points is None else points
    cumulative = 0
    stream = bytearray()
    for x in starts:
        assert x >= cumulative
        stream.extend(uleb(x - cumulative))
        cumulative = x
    stream.extend(b"\0")
    fs_off = stroff + len(strings)
    header = struct.pack("<8I", 0xfeedfacf, 0x0100000c, 0, 2, 4,
                         cmds_size, 0, 0)
    segment = struct.pack("<II16sQQQQIIII", 0x19, segment_size,
                          b"__TEXT" + b"\0" * 10, vm, 4096, 0,
                          fs_off + len(stream), 7, 5, 1, 0)
    section = struct.pack("<16s16sQQIIIIIIII",
                          b"__text" + b"\0" * 10, b"__TEXT" + b"\0" * 10,
                          vm + offset, len(code), offset, 4,
                          0, 0, 0x80000400, 0, 0, 0)
    lc_uuid = struct.pack("<II16s", 0x1b, 24,
                          uuid.UUID("7c0cb853-77aa-3ccb-9f20-560e5f40e587").bytes)
    lc_sym = struct.pack("<6I", 0x2, 24, symoff, len(targets),
                         stroff, len(strings))
    lc_starts = struct.pack("<4I", 0x26, 16, fs_off, len(stream))
    binary = bytes(header + segment + section + lc_uuid + lc_sym +
                   lc_starts + code + names + strings + stream)
    assert len(binary) == fs_off + len(stream)
    return binary


code = b"\x1f\x20\x03\xd5" * 32
changed = b"\xc0\x03\x5f\xd6" * 20 + b"\x1f\x20\x03\xd5" * 12
baseline = specimen(code, ("_dd_k8_evaluate",))
protected = specimen(changed, ("_dd_k8_evaluate",))
ios = specimen(changed, ("_dd_k8_evaluate", "_dd_k14_ios_parity"))
assert len(k20.inspect_macho(
    baseline, k20.k19.inspect(baseline, ("_dd_k8_evaluate",))
)["symbol_intervals_corroborated"]) == 1
assert len(k20.inspect_macho(
    ios, k20.k19.inspect(ios, ("_dd_k8_evaluate", "_dd_k14_ios_parity"))
)["symbol_intervals_corroborated"]) == 2
assert k20.inspect_macho(ios, k20.k19.inspect(
    ios, ("_dd_k8_evaluate", "_dd_k14_ios_parity")
))["lc_function_starts_count"] == 3

assert k20.decode_uleb(b"\x80\x01", 0) == (128, 2)
assert k20.decode_uleb(b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01", 0)[0] == (1 << 64) - 1
for raw in (b"", b"\x80", b"\x80\x00", b"\x81\x00",
            b"\xff" * 10, b"\xff" * 9 + b"\x02", b"\x80" * 11):
    rejects(lambda raw=raw: k20.decode_uleb(raw, 0), "malformed ULEB128 " + str(raw))

lc_at = 32 + (72 + 80) + 24 + 24
def mutate_int(original: bytes, field_offset: int, value: int) -> bytes:
    copied = bytearray(original)
    struct.pack_into("<I", copied, field_offset, value)
    return bytes(copied)

def inspect(raw: bytes, symbols: tuple[str, ...] = ("_dd_k8_evaluate",)) -> dict:
    return k20.inspect_macho(raw, k20.k19.inspect(raw, symbols))

rejects(lambda: inspect(mutate_int(baseline, lc_at, 0)), "missing LC_FUNCTION_STARTS")
rejects(lambda: inspect(mutate_int(baseline, lc_at + 8, 0)), "function starts at offset0")
rejects(lambda: inspect(mutate_int(baseline, lc_at + 12, 0)), "empty LC_FUNCTION_STARTS")
rejects(lambda: inspect(mutate_int(baseline, lc_at + 12, 0xffffffff)), "giant LC_FUNCTION_STARTS")
rejects(lambda: inspect(mutate_int(baseline, lc_at + 4, 24)), "wrong LC_FUNCTION_STARTS size")

offset = 32 + (72 + 80 + 24 + 24 + 16)
rejects(lambda: inspect(specimen(code, ("_dd_k8_evaluate",),
                                 points=(offset,))),
        "next symbol boundary missing from function starts")
rejects(lambda: inspect(specimen(code, ("_dd_k8_evaluate",),
                                 points=(offset + 4, offset + 32))),
        "start symbol boundary missing from function starts")
rejects(lambda: inspect(specimen(code, ("_dd_k8_evaluate",),
                                 points=(offset + 1, offset + 32))),
        "unaligned function starts")

lc_offset = 32 + (72 + 80) + 24 + 24
fs_off = struct.unpack_from("<I", baseline, lc_offset + 8)[0]
p = bytearray(baseline)
p[fs_off] = 0
rejects(lambda: inspect(bytes(p)), "early terminator plus nonzero padding")
p = bytearray(baseline)
p[-1] = 0x81
rejects(lambda: inspect(bytes(p)), "no terminating zero")

with tempfile.TemporaryDirectory(prefix="K20-synthetic-only-") as tmp:
    out = pathlib.Path(tmp)
    for name, data in (
        ("macos-baseline", baseline),
        ("macos-cse-break", protected),
        ("KaguraCSEBreakLab.app/KaguraCSEBreakLab", ios),
    ):
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    k13 = {
        "scope": "K13_SINGLE_ISOLATED_PINNED_CSE_BREAK_NATIVE_MACOS_AND_IOS_OBJECT_ONLY",
        "pass": "kagura-cse-break", "pass_class": "kagura::CSEBreakPass",
        "targets": {"macos": {"native_parity": "PASS", "native_vectors": 4096,
                              "baseline_checksum": "25a3318e3d7d6525",
                              "protected_checksum": "25a3318e3d7d6525"}},
        "security_strength_claim": False,
    }
    i = k20.k19.k16.inspect_macho(ios)
    k14 = {"scope": "STANDALONE_K14_SINGLE_CSE_BREAK_IOS_ARM64_UNSIGNED_LAB",
           "signing": "UNSIGNED", "app_macho_uuid": i["uuid"],
           "ipa_sha256": "a" * 64, "binary_sha256": i["binary_sha256"]}
    ev = {"k13_cse_break_ios_object_embedded": True,
          "ipa_sha256": k14["ipa_sha256"], "app_binary_sha256": i["binary_sha256"],
          "ios_device_execution": "NOT_TESTED_BY_CI", "security_attestation": False}
    def write_json(n, d):
        (out / n).write_text(json.dumps(d, sort_keys=True) + "\n", encoding="utf-8")
    write_json("Kagura-K13-REPORT.json", k13)
    write_json("Kagura-K14-IPA-report.json", k14)
    write_json("Kagura-K14-IPA-EVIDENCE.json", ev)
    k20.k19.k16.measure(out)
    k20.k19.record(out)
    valid = k20.record(out)
    assert valid["k18_dependency"] == "NONE_SKIPPED_BY_USER_NOT_TESTED"
    assert valid["reference_authenticated"] is False
    assert valid["two_data_sources_in_same_binary_not_independent_trust"] is True
    assert valid["exact_function_size_proven"] is False
    assert valid["runtime_self_verifier"] is False
    assert k20.verify(out) == valid
    ref = out / k20.NAME
    untouched = ref.read_bytes()
    fake = copy.deepcopy(valid)
    fake["runtime_self_verifier"] = True
    ref.write_text(json.dumps(fake), encoding="utf-8")
    rejects(lambda: k20.verify(out), "promoted runtime-security claim")
    ref.write_bytes(untouched)
    fake = copy.deepcopy(valid)
    fake["specimens"]["ios_csebreak_lab"]["symbol_intervals_corroborated"][
        "_dd_k14_ios_parity"]["sha256"] = "0" * 64
    ref.write_text(json.dumps(fake), encoding="utf-8")
    rejects(lambda: k20.verify(out), "forged iOS function interval hash")
    ref.write_bytes(untouched)
    path = out / "macos-cse-break"
    changed_raw = path.read_bytes()
    path.write_bytes(changed_raw[:-1] + bytes([changed_raw[-1] ^ 1]))
    rejects(lambda: k20.verify(out), "changed original MachO/LC_FUNCTION_STARTS")
    path.write_bytes(changed_raw)
    assert k20.verify(out) == valid

wf = (ROOT / ".github/workflows/kagura-k20-function-starts.yml").read_text(
    encoding="utf-8")
for expected in ("workflow_dispatch:", "runs-on: macos-14",
                 "scripts/test_kagura_k20_function_starts.py",
                 "scripts/test_kagura_k19_symbol_ranges.py",
                 "scripts/custom_ollvm/kagura_k19/symbol_ranges.py",
                 "scripts/custom_ollvm/kagura_k20/function_starts.py",
                 "DuoDash-Kagura-K20-FUNCTION-STARTS-DUAL-SOURCE-OFFLINE-EXPERIMENTAL",
                 "K18 SKIPPED/NOT TESTED", "if: always()"):
    assert expected in wf, expected
for forbidden in ("kagura_k18/", "K18_ED25519_PRIVATE_KEY_PEM",
                  "kagura-bbcheck", "devicectl", "codesign -s",
                  "git push"):
    assert forbidden not in wf, forbidden
print("K20_PORTABLE_LC_FUNCTION_STARTS_K19_REPLAY_PASS:"
      " ULEB64 decode/terminator, nlist address boundary corroboration,"
      " forged byte/metadata and false security gates; synthetic-only fixture")
