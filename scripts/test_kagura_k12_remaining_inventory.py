#!/usr/bin/env python3
"""K12 portable tests: exact pinned registry X-macro inventory & safety.

No synthetic fixture is evidence that a Kagura pass was natively executed.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import pathlib
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/custom_ollvm/kagura_k12"
SPEC = importlib.util.spec_from_file_location("k12_inventory", LAB / "inventory.py")
assert SPEC and SPEC.loader
k12 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(k12)


def rejects(fn, label):
    try:
        fn()
    except (AssertionError, ValueError, KeyError, IndexError):
        return
    raise AssertionError("K12 fail-closed audit accepted: " + label)


# Synthetic pinned macro file exercises both old K1/K8 coverage and
# unknown additional real FN/MOD/INFRA registrations. Do not derive the
# unknown names in production from this fixture; CI reads upstream git.
previous = list(k12.COVERED)
assert len(previous) == len(set(previous)) == 13
assert len(k12.COVERED_K1) == 7
assert len(k12.COVERED_K8_K11) == 5
assert k12.COVERED_VM == ("vm",)
rows = []
for n in previous:
    kind = k12.K8_KINDS.get(n[7:], "FN")
    if n == "kagura-vm":
        rows.append('KAGURA_INFRA_PASS("kagura-vm", VmRuntimePass())')
    else:
        rows.append('KAGURA_' + kind + '_PASS(EnableTest, "' + n +
                    '", "description", PassCtor(1, 2))')
rows.append('KAGURA_FN_PASS(EnableAudit, "kagura-new-fn", "test", FnPass())')
rows.append('KAGURA_MOD_PASS(EnableCipher,\n    "kagura-new-module",\n    "note",\n    ModulePass(Opt(1, 2)))')
rows.append('KAGURA_INFRA_PASS("kagura-new-infra", DebugOnlyPass())')
synthetic = ('// KAGURA_FN_PASS(Fake, "kagura-comment", "x", FakePass())\n'
             '/* KAGURA_MOD_PASS(Fake, "kagura-false", "x", FakePass()) */\n'
             '#define KAGURA_FN_PASS(X, Name, Description, Pass) useless\n' +
             '\n'.join(rows) + '\n')
parsed = k12.parse_registry(synthetic)
assert len(parsed) == 16
names = [x["name"] for x in parsed]
assert "kagura-comment" not in names and "kagura-false" not in names
assert names[-3:] == [
    "kagura-new-fn", "kagura-new-module", "kagura-new-infra"]
fake_sha = hashlib.sha256(synthetic.encode("utf-8")).hexdigest()
license_sha = hashlib.sha256(b"test MIT text").hexdigest()
report = k12.build_report(synthetic, fake_sha, license_sha)
assert report["registered_pass_count"] == 16
assert report["historically_evidenced_distinct_pass_count"] == 13
assert report["remaining_registered_unverified_count"] == 3
assert all(x["validation"] == "REGISTERED_UNVERIFIED" for x in
           report["remaining_registered_unverified"])
assert report["infra_passes_never_auto_executed"] is True
assert report["new_pass_native_parity_verified"] is False
assert report["new_pass_iphone_executed"] is False
assert report["arm64e_pac_verified"] is False
assert report["crane_production_modified"] is False
assert report["security_strength_claim"] is False
assert report["remaining_registered_unverified"][2]["kind"] == "INFRA"
assert report["remaining_registered_unverified"][1]["kind"] == "MOD"
rejects(lambda: k12.parse_registry(synthetic.replace(
    '"kagura-mvo"', '"kagura-mvo-fake"')),
    "historically evidenced pass missing")
rejects(lambda: k12.parse_registry(synthetic.replace(
    "KAGURA_FN_PASS(EnableTest, \"kagura-ibr\"",
    "KAGURA_MOD_PASS(EnableTest, \"kagura-ibr\"")),
    "K8 pass changed module/function type")
rejects(lambda: k12.parse_registry(
    synthetic + rows[-2] + '\n'), "duplicated new pass")
rejects(lambda: k12.parse_registry(
    synthetic + 'KAGURA_FN_PASS(EnableBad, "kagura-evil!name", "x", X())\n'),
    "invalid name")
rejects(lambda: k12.parse_registry(
    synthetic + 'KAGURA_MOD_PASS(EnableX, "kagura-unclosed", "x", X(\n'),
    "unbalanced pass macro")
rejects(lambda: k12.parse_registry(
    synthetic.replace("KAGURA_INFRA_PASS(\"kagura-vm\"",
                      "KAGURA_INFRA_PASS(\"broken-vm\"")),
    "missing actual pinned VM pass")
rejects(lambda: k12.build_report(synthetic, "x" * 64, license_sha),
        "invalid registry digest")
rejects(lambda: k12.build_report(synthetic, fake_sha, "bad"),
        "invalid upstream license digest")

with tempfile.TemporaryDirectory(prefix="K12-fixture-source-") as directory:
    root = pathlib.Path(directory)
    src = root / "pin"
    out = root / "audit"
    (src / "include/kagura").mkdir(parents=True)
    (src / "LICENSE").write_bytes(b"test MIT text")
    (src / "include/kagura/PassRegistry.def").write_bytes(synthetic.encode("utf-8"))
    current = k12.inventory(src, out)
    assert current == report
    assert k12.verify(out) == report
    item = json.loads(
        (out / "Kagura-K12-REMAINING-PASS-INVENTORY.json").read_text())
    item["remaining_registered_unverified_count"] = 0
    (out / "Kagura-K12-REMAINING-PASS-INVENTORY.json").write_text(json.dumps(item))
    rejects(lambda: k12.verify(out), "inventory count inflated")
    (out / "Kagura-K12-PINNED-PASS-REGISTRY.def").write_text(
        synthetic.replace("kagura-new-fn", "kagura-renamed-fn"))
    rejects(lambda: k12.verify(out), "upstream registry tampered")

# Actual llvm-dis writes a different ModuleID for baseline.bc versus
# post-opt.bc even if ALL IR instructions are identical. This must NOT
# masquerade as a new Kagura pass IR delta.
with tempfile.TemporaryDirectory(prefix="K12-llvm-moduleid-") as tmp:
    root = pathlib.Path(tmp)
    baseline = root / "baseline.ll"
    after = root / "after.ll"
    body = (
        'source_filename = "fixture.c"\n'
        'define i64 @dd_k8_evaluate(i64 %n) { ret i64 %n }\n'
    )
    baseline.write_text("; ModuleID = 'before.bc'\n" + body,
                        encoding="utf-8")
    after.write_text("; ModuleID = 'after.bc'\n" + body,
                     encoding="utf-8")
    assert k12.sha(baseline) != k12.sha(after)
    assert k12.normalized_ir_sha(baseline) == k12.normalized_ir_sha(after)
    after.write_text("; ModuleID = 'after.bc'\n" +
                     body.replace("ret i64 %n", "ret i64 7"),
                     encoding="utf-8")
    assert k12.normalized_ir_sha(baseline) != k12.normalized_ir_sha(after)
    after.write_text("define i64 @dd_k8_evaluate() {ret i64 0}\n",
                     encoding="utf-8")
    rejects(lambda: k12.normalized_ir_sha(after), "missing ModuleID header")
    after.write_text("; ModuleID = 'a'\n; ModuleID = 'b'\n" + body,
                     encoding="utf-8")
    rejects(lambda: k12.normalized_ir_sha(after), "duplicate ModuleID header")

workflow = (ROOT / ".github/workflows/kagura-k12-remaining-inventory.yml").read_text(
    encoding="utf-8")
smoke = (LAB / "smoke.py").read_text(encoding="utf-8")
for needle in (
    "workflow_dispatch:", "runs-on: macos-14",
    "ac2136ee0408677cf7cdee55307e9b16edd5f4d5",
    "scripts/test_kagura_k12_remaining_inventory.py",
    "scripts/custom_ollvm/kagura_k12/inventory.py",
    "scripts/custom_ollvm/kagura_k12/smoke.py",
    "--verify-report",
    "DuoDash-Kagura-K12-PINNED-REMAINING-PASS-INVENTORY-EXPERIMENTAL",
    "if: always()",
):
    assert needle in workflow, needle
assert "native_parity_proven" in smoke and '"NOT_TESTED"' in smoke
assert "SKIPPED_INFRA_NOT_AUTO_RUN" in smoke
assert "OPT_EXECUTED_IR_DELTA_UNVERIFIED" in smoke
assert "ios-arm64-build-only" in smoke
for file in (workflow, smoke, (LAB / "inventory.py").read_text()):
    for forbidden in ("ptrauth_strip", "MSHook", "devicectl device install",
                      "codesign -s", "make clean package",
                      "THEOS_PACKAGE_SCHEME", "git push"):
        assert forbidden not in file, forbidden
for path in ("Makefile", "policy.json", ".github/workflows/build.yml"):
    assert "kagura_k12" not in (ROOT / path).read_text(encoding="utf-8")
print("KAGURA_K12_PORTABLE_INVENTORY_PASS: pinned macro registry, 13 prior"
      " evidenced vs remaining unverified, tamper/missing/dup checks;"
      " new native/IPA/device passes NOT CLAIMED")
