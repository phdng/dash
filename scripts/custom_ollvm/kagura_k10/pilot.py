#!/usr/bin/env python3
"""K10 STRICT metadata alignment + full REAL K9 five-pass native composition.

Only the transient MVO LLVM IR gets the exact target datalayout/triple
taken from the LLVM19 Clang C bitcode of EACH target. The K8 MVO .ll
template/three prior source hashes and K9 five-pass pipeline are frozen.
Failure to match module headers or llvm-link warning => CI hard FAIL.
macOS native 2x4096 parity and iOS arm64 OBJECT ONLY; no IPA/device.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
K9 = ROOT / "scripts/custom_ollvm/kagura_k9"
STAGES = ("mvo", "genc", "fsplit", "ibr", "ci")
STATUS = "MACOS_FIVE_COMPOSED_STAGES_STRICT_METADATA_NATIVE_PASS_IOS_BUILD_ONLY"
SCOPE = "K10_STRICT_LLVM19_CLANG_MODULE_METADATA_ALIGNMENT"
spec = importlib.util.spec_from_file_location("k10_k9_shared_pilot", K9 / "pilot.py")
if spec is None or spec.loader is None:
    raise RuntimeError("Missing pinned K9 pilot")
k9 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(k9)


def verify_report(report: dict, out: Path) -> dict:
    """Fail-closed serialized report AND actual file evidence at each target."""
    k9.validate_composition_report(report)
    if report.get("scope") != "K9_PINNED_KAGURA_FIVE_PASS_ONE_MODULE_COMPOSITION":
        raise AssertionError("K10 source composition scope changed")
    if report.get("pinned_commit") != k9.UPSTREAM_PIN:
        raise AssertionError("K10 upstream source SHA changed")
    data = report.get("link_metadata")
    if not isinstance(data, dict) or set(data) != {"macos", "ios"}:
        raise AssertionError("K10 requires both matched target metadata reports")
    for target in ("macos", "ios"):
        section = data[target]
        if not isinstance(section, dict) or section.get("llvm_link_warning_count") != 0:
            raise AssertionError("K10 no-warning metadata report missing")
        folder = out / target
        c_path = folder / "c.ll"
        mvo_path = folder / "mvo-source.ll"
        merged_path = folder / "merged.ll"
        link_path = folder / "llvm-link.log"
        if any(not file.is_file() for file in
               (c_path, mvo_path, merged_path, link_path)):
            raise AssertionError("K10 missing raw IR/link log provenance")
        c = c_path.read_text(encoding="utf-8")
        mvo = mvo_path.read_text(encoding="utf-8")
        merged = merged_path.read_text(encoding="utf-8")
        log = link_path.read_text(encoding="utf-8")
        true = k9.validate_llvm_link_metadata(
            c, mvo, merged, log, ios=target == "ios")
        if any(section.get(key) != val for key, val in true.items()):
            raise AssertionError("K10 report metadata does not match actual IR")
        for key, path in (("c_ir_sha256", c_path),
                          ("mvo_ir_sha256", mvo_path),
                          ("merged_ir_sha256", merged_path)):
            if section.get(key) != k9.sh(path):
                raise AssertionError("K10 report source or output IR SHA mismatch")
        encoded = json.loads(
            (folder / "target-metadata.json").read_text(encoding="utf-8"))
        if encoded != section:
            raise AssertionError("K10 target metadata sidecar mismatch")
        # This template still has precisely one direct MVO alloca.
        k9.k8.validate_mvo_input_ir(mvo)
        k9.validate_merged(merged)
    if (report.get("native_digest_c") != k9.K8_C_DIGEST or
            report.get("native_digest_mvo") != k9.K8_MVO_DIGEST):
        raise AssertionError("K10 native known-good oracle missing")
    baseline = (out / "plain-native.log").read_bytes()
    k9.validate_logs(baseline.decode("ascii"))
    for idx, name in enumerate(STAGES, 1):
        folder = out / f"{idx:02d}-{name}"
        stage = report["stages"][name]
        actual = (folder / "native.log").read_bytes()
        if actual != baseline or stage["native_log_sha256"] != k9.sh(
                folder / "native.log"):
            raise AssertionError(f"K10 {name}: raw native log mismatch")
        for target in ("macos", "ios"):
            obj = folder / f"{target}.o"
            ir = folder / f"{target}.ll"
            trace = folder / f"{target}-opt.log"
            previous_folder = (out / target if idx == 1 else
                               out / f"{idx-1:02d}-{STAGES[idx-2]}")
            previous_obj = (previous_folder / "merged.o" if idx == 1
                            else previous_folder / f"{target}.o")
            previous_ir = (previous_folder / "merged.ll" if idx == 1
                           else previous_folder / f"{target}.ll")
            if (k9.sh(obj) != stage[target]["object_sha256"] or
                    k9.sh(previous_obj) != stage[target]["previous_object_sha256"] or
                    k9.sh(ir) != stage[target]["ir_sha256"] or
                    k9.sh(trace) != stage[target]["opt_log_sha256"]):
                raise AssertionError(f"K10 {name}/{target}: artifact hash mismatch")
            if target == "ios":
                k9.k8.verify_apple_arm64_object(obj.read_bytes())
                k9.k8.verify_apple_arm64_object(previous_obj.read_bytes())
            current = ir.read_text(encoding="utf-8")
            if k9.get_target_metadata(current, ios=target == "ios") != (
                    data[target]["datalayout"], data[target]["triple"]):
                raise AssertionError(f"K10 {name}/{target}: target metadata drift")
            # Re-run K9's strict marker, real class, native object/IR
            # delta and two public ABI gates against actual stage files.
            k9.validate_stage(
                name, previous_ir.read_text(encoding="utf-8"),
                current, previous_obj.read_bytes(), obj.read_bytes(),
                trace.read_text(encoding="utf-8"))
    return {
        "schema": 1,
        "status": STATUS,
        "scope": SCOPE,
        "pinned_commit": k9.UPSTREAM_PIN,
        "stage_order": list(STAGES),
        "native_vectors_per_function": 4096,
        "native_checksum_c": k9.K8_C_DIGEST,
        "native_checksum_mvo": k9.K8_MVO_DIGEST,
        "llvm_link_metadata_aligned": True,
        "llvm_link_warning_count": 0,
        "macos": data["macos"],
        "ios": data["ios"],
        "k9_composed_report_sha256": k9.sh(out / "Kagura-K9-COMPOSITION-REPORT.json"),
        "ios_arm64": "OBJECT_BUILD_ONLY_NOT_EXECUTED",
        "iphone_runtime_executed": False,
        "arm64e_pac_runtime_executed": False,
        "crane_production_modified": False,
        "performance_evaluated": False,
        "source_k8_fixture_sha256": k9.sh(k9.K8 / "fixture.c"),
        "source_k8_mvo_sha256": k9.sh(k9.K8 / "mvo.ll"),
        "source_k9_runner_sha256": k9.sh(K9 / "runner.c"),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--llvm", type=Path)
    p.add_argument("--plugin", type=Path)
    p.add_argument("--src", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--verify-report", action="store_true")
    a = p.parse_args()
    if a.verify_report:
        if any(x is not None for x in (a.llvm, a.plugin, a.src)):
            p.error("Verification cannot run the compiler simultaneously")
        report = json.loads(
            (a.out / "Kagura-K9-COMPOSITION-REPORT.json").read_text(encoding="utf-8"))
        summary = verify_report(report, a.out)
        recorded = json.loads(
            (a.out / "Kagura-K10-METADATA-REPORT.json").read_text(encoding="utf-8"))
        if summary != recorded:
            raise AssertionError("K10 report differs from real artifact")
        print("KAGURA_K10_SERIALIZED_METADATA_AND_NATIVE_EVIDENCE_PASS")
        return
    if any(x is None for x in (a.llvm, a.plugin, a.src)):
        p.error("--llvm --plugin and --src are required for compiler run")
    report = k9.main_run(
        llvm=a.llvm, plugin=a.plugin, src=a.src, out=a.out,
        strict_link_metadata=True)
    summary = verify_report(report, a.out)
    (a.out / "Kagura-K10-METADATA-REPORT.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("KAGURA_K10_STRICT_LLVM_LINK_METADATA_FIVE_PASS_NATIVE_AND_ARM64_OBJECTS_PASS")


if __name__ == "__main__":
    main()
