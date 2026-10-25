#!/usr/bin/env python3
"""K22 portable dual-K21 specimen reproducibility plus fail-closed gates."""
from __future__ import annotations

import copy
import json
import pathlib
import struct
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/custom_ollvm/kagura_k22"))
import test_kagura_k20_function_starts as fixtures  # reuses synthetic parser gates
import reproducibility as k22


def rejects(fn, label: str) -> None:
    try:
        fn()
    except (AssertionError, ValueError, KeyError, struct.error):
        return
    raise AssertionError("K22 wrongly accepted " + label)


def prepare(out: pathlib.Path, *, change_code: bool = False) -> None:
    protected = fixtures.protected
    if change_code:
        changed = (b"\xc0\x03\x5f\xd6" * 7 + b"\x1f\x20\x03\xd5" +
                   b"\xc0\x03\x5f\xd6" * 12 + b"\x1f\x20\x03\xd5" * 12)
        protected = fixtures.specimen(changed, ("_dd_k8_evaluate",))
    for name, contents in (
        ("macos-baseline", fixtures.baseline),
        ("macos-cse-break", protected),
        ("KaguraCSEBreakLab.app/KaguraCSEBreakLab", fixtures.ios),
    ):
        dest = out / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(contents)
    k21 = k22.k21
    ios = k21.k20.k19.k16.inspect_macho(fixtures.ios)
    k13 = {
        "scope": "K13_SINGLE_ISOLATED_PINNED_CSE_BREAK_NATIVE_MACOS_AND_IOS_OBJECT_ONLY",
        "pass": "kagura-cse-break", "pass_class": "kagura::CSEBreakPass",
        "targets": {"macos": {"native_parity": "PASS", "native_vectors": 4096,
                              "baseline_checksum": "25a3318e3d7d6525",
                              "protected_checksum": "25a3318e3d7d6525"}},
        "security_strength_claim": False,
    }
    k14 = {
        "scope": "STANDALONE_K14_SINGLE_CSE_BREAK_IOS_ARM64_UNSIGNED_LAB",
        "signing": "UNSIGNED", "app_macho_uuid": ios["uuid"],
        "ipa_sha256": "a" * 64, "binary_sha256": ios["binary_sha256"],
    }
    ev = {
        "k13_cse_break_ios_object_embedded": True,
        "ipa_sha256": k14["ipa_sha256"], "app_binary_sha256": ios["binary_sha256"],
        "ios_device_execution": "NOT_TESTED_BY_CI", "security_attestation": False,
    }
    for name, manifest in (
        ("Kagura-K13-REPORT.json", k13),
        ("Kagura-K14-IPA-report.json", k14),
        ("Kagura-K14-IPA-EVIDENCE.json", ev),
    ):
        (out / name).write_text(json.dumps(manifest, sort_keys=True) + "\n",
                                encoding="utf-8")
    k21.k20.k19.k16.measure(out)
    k21.k20.k19.record(out)
    k21.k20.record(out)
    k21.record(out)


with tempfile.TemporaryDirectory(prefix="K22-synthetic-repro-only-") as tmp:
    root = pathlib.Path(tmp)
    a, b, report = root / "build-a", root / "build-b", root / "report"
    prepare(a)
    prepare(b)
    saved = k22.record(a, b, report)
    assert saved["tested_code_intervals"] == 4
    assert saved["authenticated_distinct_ci_runs"] is False
    assert saved["runtime_integrity_verifier"] is False
    assert saved["code_intervals_reproducible"] is True
    assert k22.verify(a, b, report) == saved
    rejects(lambda: k22.record(a, b, report), "overwriting report")
    rejects(lambda: k22.regenerate(a, a), "same build dir")
    assert all(x["matched_instruction_word_patterns_not_cfg"]
               for specimen in saved["targets"].values() for x in specimen.values())

    p = report / k22.NAME
    original = p.read_bytes()
    forged = copy.deepcopy(saved)
    forged["iphone_device_execution"] = True
    p.write_text(json.dumps(forged), encoding="utf-8")
    rejects(lambda: k22.verify(a, b, report), "forged device execution")
    p.write_bytes(original)
    forged = copy.deepcopy(saved)
    forged["targets"]["macos_baseline"]["_dd_k8_evaluate"]["code_sha256"] = "0" * 64
    p.write_text(json.dumps(forged), encoding="utf-8")
    rejects(lambda: k22.verify(a, b, report), "forged code SHA")
    p.write_bytes(original)

    src = b / k22.k21.NAME
    unmodified = src.read_bytes()
    src.write_bytes(unmodified + b" ")
    rejects(lambda: k22.verify(a, b, report), "different K21 JSON bytes")
    src.write_bytes(unmodified)
    assert k22.verify(a, b, report) == saved

    p2 = root / "build-changed"
    prepare(p2, change_code=True)
    assert k22.k21.verify(p2)
    rejects(lambda: k22.regenerate(a, p2), "genuine but changed AArch64 region")
    wrong = b / "macos-cse-break"
    bytes_before = wrong.read_bytes()
    wrong.write_bytes(bytes_before[:290] + bytes([bytes_before[290] ^ 1])
                      + bytes_before[291:])
    rejects(lambda: k22.regenerate(a, b), "mutated Mach-O no longer K21 valid")
    wrong.write_bytes(bytes_before)
    assert k22.verify(a, b, report) == saved

wf = (ROOT / ".github/workflows/kagura-k22-reproducibility.yml").read_text(
    encoding="utf-8")
for expected in ("workflow_dispatch:", "runs-on: macos-14",
                 "scripts/test_kagura_k22_reproducibility.py",
                 "scripts/custom_ollvm/kagura_k21/opcode_inventory.py",
                 "scripts/custom_ollvm/kagura_k22/reproducibility.py",
                 "DuoDash-Kagura-K22-TWO-BUILD-REPRODUCIBILITY-OFFLINE-EXPERIMENTAL",
                 "if: always()", "K22_LEFT", "K22_RIGHT"):
    assert expected in wf, expected
for forbidden in ("kagura_k18/", "K18_ED25519_PRIVATE_KEY_PEM",
                  "kagura-bbcheck", "devicectl", "codesign -s", "git push"):
    assert forbidden not in wf, forbidden

print("K22_PORTABLE_TWO_BUILD_CODE_REPRODUCIBILITY_PASS:"
      " 4 matching raw target intervals, varied code and tampered JSON fail,"
      " no actual macOS dual-build CI/device/security")
