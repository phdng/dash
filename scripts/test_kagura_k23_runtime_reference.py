#!/usr/bin/env python3
"""K23 synthetic-only IPA packaging + mutation gates; never device evidence."""
from __future__ import annotations

import json
import pathlib
import plistlib
import sys
import tempfile
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/custom_ollvm/kagura_k23"))
import test_kagura_k22_reproducibility as k22fixture
import package as k23
import device_log_audit as device


def rejects(fn, reason: str) -> None:
    try:
        fn()
    except (AssertionError, ValueError, KeyError, OSError):
        return
    raise AssertionError("K23 accepted " + reason)


with tempfile.TemporaryDirectory(prefix="K23-SYNTHETIC-UNSIGNED-ONLY-") as tmp:
    out = pathlib.Path(tmp) / "build"
    k22fixture.prepare(out)
    info = k23.prepare(out)
    assert info["reference_uuid"] == "7c0cb853-77aa-3ccb-9f20-560e5f40e587"
    rejects(lambda: k23.prepare(out), "overwrite app")
    app = out / f"{k23.APP}.app"
    expected = out / "K23Expected.swift"
    reference = app / k23.REFERENCE
    original = reference.read_bytes()
    assert expected.read_text(encoding="utf-8") == k23.generated_expected(
        k23.source(out)[1], k23.source(out)[2])
    # Synthetic executable only; real Swift app remains macOS CI unverified.
    (app / k23.APP).write_bytes(k22fixture.fixtures.baseline)
    report = k23.package(out)
    assert report["bundled_reference_checked_at_packaging"] is True
    assert report["compiled_digests_not_immutable_trust_anchor"] is True
    assert report["iphone_runtime"] == "NOT_TESTED_BY_CI"
    assert report["running_app_self_integrity"] is False
    assert report["security_anti_tamper_proven"] is False
    assert report["k18_dependency"] is False
    assert report["signing"] == "UNSIGNED"
    assert len(report["reference_target_region_sha256"]) == 2
    with zipfile.ZipFile(out / k23.IPA) as z:
        assert len(z.infolist()) == 3
        assert z.testzip() is None
        for name in k23.EXPECTED_MEMBERS:
            assert z.read(k23.PREFIX + name) == (app / name).read_bytes()
    rejects(lambda: k23.package(out), "existing IPA")
    valid_log = (
        "DD_K23_SCHEMA=1\n"
        "DD_K23_CONTEXT=IOS_DEVICE_USER_INITIATED\n"
        "DD_K23_SCOPE=BUNDLED_REFERENCE_ONLY\n"
        f"DD_K23_REFERENCE_UUID={report['reference_uuid']}\n"
        "DD_K23_REFERENCE_SHA256=PASS\n"
        "DD_K23_CODE_INTERVALS=2\n"
        "DD_K23_MUTATED_CODE=REJECTED\n"
        "DD_K23_TRUNCATED_REFERENCE=REJECTED\n"
        "DD_K23_SELF_INTEGRITY=NOT_IMPLEMENTED\n"
        "DD_K23_COMPLETE=PASS\n"
    )
    user_log = out / "SYNTHETIC-NOT-DEVICE.log"
    user_log.write_text(valid_log, encoding="ascii")
    reviewed = device.validate(user_log, out / k23.REPORT)
    assert reviewed["user_shared_ten_lines_matched"] is True
    assert reviewed["device_execution_independently_observed"] is False
    for malformed in (
        valid_log.replace(report["reference_uuid"], "0" * 36),
        valid_log.replace("MUTATED_CODE=REJECTED", "MUTATED_CODE=PASS"),
        valid_log.replace("SELF_INTEGRITY=NOT_IMPLEMENTED", "SELF_INTEGRITY=PASS"),
        valid_log.replace("IOS_DEVICE_USER_INITIATED", "IOS_SIMULATOR"),
        valid_log + "DD_K23_EXTRA=PASS\n",
        valid_log[:-1],
    ):
        user_log.write_text(malformed, encoding="ascii")
        rejects(lambda: device.validate(user_log, out / k23.REPORT),
                "forged user-shared iPhone log")
    user_log.write_text(valid_log, encoding="ascii")

    # Direct byte corruption must fail in packager before any runtime claims.
    reference.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
    rejects(lambda: k23.collect(out), "changed source binary")
    reference.write_bytes(original[:-1])
    rejects(lambda: k23.collect(out), "truncated source binary")
    reference.write_bytes(original)

    saved = expected.read_text(encoding="utf-8")
    expected.write_text(saved.replace(k23.sha(original), "0" * 64))
    rejects(lambda: k23.collect(out), "changed compile-bound SHA reference")
    expected.write_text(saved)
    manifest = app / "Info.plist"
    original_info = manifest.read_bytes()
    info_obj = plistlib.loads(original_info)
    info_obj["CFBundleIdentifier"] = "com.duodash.research.kagurak14"
    manifest.write_bytes(plistlib.dumps(info_obj))
    rejects(lambda: k23.collect(out), "wrong iOS bundle identifier")
    manifest.write_bytes(original_info)
    extra = app / "sideloaded.dylib"
    extra.write_bytes(b"X")
    rejects(lambda: k23.collect(out), "unexpected app member")
    extra.unlink()
    assert k23.collect(out)["reference_binary_sha256"] == k23.sha(original)

swift = (ROOT / "scripts/custom_ollvm/kagura_k23/K23RuntimeLab.swift").read_text(
    encoding="utf-8")
for token in (
    "import CryptoKit", "try verify(raw)", "try? verify(mutated)",
    "try? verify(truncated)", "mutated[first.0] ^= 0x01",
    "DD_K23_COMPLETE=FAIL", "DD_K23_COMPLETE=PASS",
    "DD_K23_SELF_INTEGRITY=NOT_IMPLEMENTED",
    "DD_K23_SCOPE=BUNDLED_REFERENCE_ONLY",
    "#if targetEnvironment(simulator)", "#if !arch(arm64)",
):
    assert token in swift, token
workflow = (ROOT / ".github/workflows/kagura-k23-runtime-reference-lab.yml").read_text(
    encoding="utf-8")
for token in (
    "workflow_dispatch:", "runs-on: macos-14",
    "scripts/test_kagura_k23_runtime_reference.py",
    "scripts/custom_ollvm/kagura_k23/package.py prepare",
    "scripts/custom_ollvm/kagura_k23/package.py package",
    "K23Expected.swift", "xcrun swiftc -parse-as-library",
    "DuoDash-Kagura-K23-IOS-RUNTIME-REFERENCE-LAB-EXPERIMENTAL",
    "if: always()",
):
    assert token in workflow, token
for banned in (
    "kagura_k18/", "K18_ED25519_PRIVATE_KEY_PEM",
    "kagura-bbcheck", "devicectl", "codesign -s", "git push",
):
    assert banned not in workflow, banned
for name in ("Makefile", "policy.json", ".github/workflows/build.yml"):
    assert "kagura_k23" not in (ROOT / name).read_text(encoding="utf-8")
print("K23_PORTABLE_UNSIGNED_BUNDLED_REFERENCE_RUNTIME_LAB_PASS:"
      " K21-linked SHA inputs, mutated/truncated/forged/extra resources"
      " rejected, app runtime iPhone NOT_TESTED")
