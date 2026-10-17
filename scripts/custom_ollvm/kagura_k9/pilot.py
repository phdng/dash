#!/usr/bin/env python3
"""Kagura K9 manual LLVM19 *composition* truth test (never production).

The source K8 canaries intentionally exercise different eligibility:
- C fixture: four independently proven K8 passes, compile at LLVM19 -O1.
- explicit IR MVO fixture: direct nonescaping i64 alloca with store/load.

K9 renames only the MVO entry and llvm-links BOTH into one module. It
applies five real upstream Kagura passes IN SEQUENCE, requiring each
stage to change IR AND object and run 4096 native vectors for BOTH
functions. iOS arm64 emits real Mach-O objects only; NO IPA/device claim.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
K8 = ROOT / "scripts/custom_ollvm/kagura_k8"
UPSTREAM_PIN = "ac2136ee0408677cf7cdee55307e9b16edd5f4d5"
SEED = "82712"
STAGES = ("mvo", "genc", "fsplit", "ibr", "ci")
K8_C_DIGEST = "25a3318e3d7d6525"
K8_MVO_DIGEST = "64e61045bbc4a250"
LOG_PATTERN = re.compile(
    r"\ADD_K9_SCHEMA=1\n"
    r"DD_K9_VECTORS_PER_FUNCTION=4096\n"
    r"DD_K9_C_CHECKSUM=([0-9a-f]{16})\n"
    r"DD_K9_MVO_CHECKSUM=([0-9a-f]{16})\n"
    r"DD_K9_COMPLETE=PASS\n\Z"
)

spec = importlib.util.spec_from_file_location("k9_k8_reused_auditor", K8 / "pilot.py")
if spec is None or spec.loader is None:
    raise RuntimeError("Missing the pinned K8 compiler audit implementation")
k8 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(k8)


def sh(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_command(args: list[str], log: Path | None = None) -> str:
    proc = subprocess.run(args, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=False)
    if log is not None:
        log.write_text(proc.stdout + proc.stderr, encoding="utf-8")
    if proc.returncode:
        raise RuntimeError(
            f"K9 command exit={proc.returncode}: {args[0]} "
            f"details={proc.stderr[-1100:]}")
    return proc.stdout


def mvo_module(template: str, target: str) -> str:
    source = k8.materialize_mvo_ir(template, target)
    if source.count("define i64 @dd_k8_evaluate(") != 1:
        raise AssertionError("K9 MVO template not exactly one known ABI function")
    source = source.replace(
        "define i64 @dd_k8_evaluate(", "define i64 @dd_k9_mvo_probe(")
    if "define i64 @dd_k8_evaluate(" in source:
        raise AssertionError("K9 duplicate unrenamed MVO entry")
    k8.validate_mvo_input_ir(source)
    return source


def get_target_metadata(ir: str, *, ios: bool) -> tuple[str, str]:
    """Read authoritative target datalayout/triple from the Clang C IR.

    LLVM 19 Clang's -print-target-triple can differ from the actual
    deployment triple emitted into the compiled bitcode. Never guess
    target metadata from the SDK path or copy the host triple to iOS.
    """
    layout_matches = re.findall(
        r'(?m)^target datalayout = "([^"\n]+)"\s*$', ir)
    triple_matches = re.findall(
        r'(?m)^target triple = "([^"\n]+)"\s*$', ir)
    if len(layout_matches) != 1 or len(triple_matches) != 1:
        raise AssertionError("K10 C IR requires exactly one target datalayout/triple")
    layout, triple = layout_matches[0], triple_matches[0]
    if (not re.fullmatch(r"[A-Za-z0-9:._-]+", layout) or
            not layout.startswith("e-m:o-") or
            not re.fullmatch(r"[A-Za-z0-9._-]+", triple)):
        raise AssertionError("K10 unexpected Darwin data layout or target syntax")
    if ios:
        if not re.fullmatch(r"arm64-apple-ios\d+(?:\.\d+)*", triple):
            raise AssertionError("K10 iOS baseline must be genuine arm64 iOS")
    elif not re.fullmatch(
            r"(?:arm64|x86_64)-apple-macosx\d+(?:\.\d+)*", triple):
        raise AssertionError("K10 host baseline must be Apple macOS")
    return layout, triple


def align_mvo_to_c_module(template: str, c_ir: str,
                          *, ios: bool) -> str:
    """K10 ONLY: set *generated* MVO IR target metadata exactly as C IR.

    Never edit the K8 source fixture or replace C module metadata.
    The probe body/alloca/load/store remains the same as K9.
    """
    layout, triple = get_target_metadata(c_ir, ios=ios)
    source = mvo_module(template, triple)
    if source.count(f'target triple = "{triple}"') != 1:
        raise AssertionError("K10 missing generated MVO triple")
    if "target datalayout" in source:
        raise AssertionError("K10 MVO template unexpectedly already has datalayout")
    source = source.replace(
        f'target triple = "{triple}"',
        f'target datalayout = "{layout}"\n'
        f'target triple = "{triple}"')
    if get_target_metadata(source, ios=ios) != (layout, triple):
        raise AssertionError("K10 failed to normalize MVO target metadata")
    k8.validate_mvo_input_ir(source)
    return source


def validate_llvm_link_metadata(c_ir: str, mvo_ir: str,
                                merged_ir: str, log: str,
                                *, ios: bool) -> dict:
    """Treat llvm-link metadata warnings as hard failure in K10."""
    expected = get_target_metadata(c_ir, ios=ios)
    if (get_target_metadata(mvo_ir, ios=ios) != expected or
            get_target_metadata(merged_ir, ios=ios) != expected):
        raise AssertionError("K10 llvm-link altered/mismatched triple or datalayout")
    if re.search(r"(?im)\b(?:warning|error):", log):
        raise AssertionError("K10 llvm-link emitted warning/error; no silent pass")
    return {"triple": expected[1], "datalayout": expected[0],
            "llvm_link_warning_count": 0}


def validate_merged(ir: str) -> None:
    defined = k8.functions(ir)
    if not {"dd_k8_evaluate", "dd_k9_mvo_probe"}.issubset(defined):
        raise AssertionError("K9 both public canary ABI entries must survive llvm-link")
    if "dd_k8_genc_scalar" not in ir:
        raise AssertionError("K9 C constant global disappeared before GENC")
    k8.validate_mvo_input_ir(ir)
    k8.validate_genc_input_ir(ir)


def validate_logs(content: str) -> tuple[str, str]:
    match = LOG_PATTERN.fullmatch(content)
    if not match:
        raise AssertionError("K9 malformed or incomplete native 2-function log")
    c, mvo = match.groups()
    if (c, mvo) != (K8_C_DIGEST, K8_MVO_DIGEST):
        raise AssertionError(
            "K9 native divergence from independently verified K8 source + MVO oracle")
    return c, mvo


def validate_stage(pass_name: str, previous_ir: str, current_ir: str,
                   previous_obj: bytes, current_obj: bytes, opt_trace: str
                   ) -> dict:
    if pass_name not in STAGES:
        raise AssertionError("K9 unexpected pass in five-stage allowlist")
    # Use the exact pass-specific K8 gates, unchanged in strength.
    evidence = k8.validate_delta(
        pass_name, previous_ir, current_ir,
        previous_obj, current_obj, opt_trace)
    public = k8.functions(current_ir)
    if not {"dd_k8_evaluate", "dd_k9_mvo_probe"}.issubset(public):
        raise AssertionError("K9 pipeline discarded a public function")
    if pass_name == "mvo":
        # Avoid accidental success from transformed C only:
        # both explicit MVO alloca XOR names must be present.
        if not (re.search(r"%mixed\.mvo\b", current_ir) and
                re.search(r"%value\.mvo\b", current_ir)):
            raise AssertionError("K9 MVO failed to transform explicit IR probe")
    return evidence


def validate_composition_report(report: dict) -> None:
    """Fail-closed post-CI report gate independent of JSON dictionary ordering.

    The writer serializes with sort_keys=True. Reconstruct pass chronology
    using stage.index instead of list(report["stages"]) insertion order.
    """
    if not isinstance(report, dict):
        raise AssertionError("K9 report must be a JSON object")
    if (report.get("status") !=
            "MACOS_NATIVE_ALL_FIVE_COMPOSED_STAGES_PASS_IOS_BUILD_ONLY" or
            report.get("schema") != 1 or
            report.get("stage_order") != list(STAGES) or
            report.get("native_vectors_per_function") != 4096 or
            report.get("native_digest_c") != K8_C_DIGEST or
            report.get("native_digest_mvo") != K8_MVO_DIGEST or
            report.get("mvo_independent_oracle") != K8_MVO_DIGEST or
            report.get("ios_arm64") != "OBJECT_BUILD_ONLY_NOT_EXECUTED" or
            report.get("iphone_runtime_executed") is not False or
            report.get("arm64e_pac_runtime_executed") is not False or
            report.get("crane_production_modified") is not False or
            report.get("performance_evaluated") is not False):
        raise AssertionError("K9 final report status, independent checksums or scope invalid")
    stages = report.get("stages")
    if not isinstance(stages, dict) or set(stages) != set(STAGES):
        raise AssertionError("K9 final report missing/duplicated/extra stage")
    observed_order: list[str] = []
    for index, name in enumerate(STAGES, 1):
        stage = stages[name]
        kind, cls, _ = k8.CANDIDATES[name]
        if (not isinstance(stage, dict) or
                type(stage.get("index")) is not int or
                stage["index"] != index or
                stage.get("pass") != name or
                stage.get("macos_native_4096_per_function") != "PASS" or
                not re.fullmatch(
                    r"[a-f0-9]{64}", stage.get("native_log_sha256", ""))):
            raise AssertionError(f"K9 corrupted order/native evidence for {name}")
        observed_order.append(stage["pass"])
        for target in ("macos", "ios"):
            entry = stage.get(target)
            if (not isinstance(entry, dict) or
                    entry.get("class") != cls or
                    entry.get("kind") != kind or
                    entry.get("ir_and_object_changed") is not True or
                    any(not isinstance(entry.get(field), str) or
                        not re.fullmatch(r"[a-f0-9]{64}", entry[field])
                        for field in (
                            "previous_object_sha256", "object_sha256",
                            "opt_log_sha256", "ir_sha256")) or
                    entry.get("previous_object_sha256") ==
                    entry.get("object_sha256")):
                raise AssertionError(
                    f"K9 {name}/{target}: fake pass class or IR/object evidence")
    if observed_order != list(STAGES):
        raise AssertionError("K9 report stage indices not chronological")


def verify_inputs(root: Path = ROOT) -> dict:
    registry = json.loads(
        (root / "scripts/custom_ollvm/pass_registry.json").read_text(encoding="utf-8")
    )["experimental_kagura_pipeline"]
    if registry.get("k8_five_pass_status") != "MACOS_CI_ARTIFACT_VERIFIED_ISOLATED_FIVE_PASS":
        raise AssertionError("K9 requires independently verified K8 upstream sources")
    expected = {
        "fixture.c": "k8_source_fixture_sha256",
        "runner.c": "k8_source_runner_sha256",
        "mvo.ll": "k8_source_mvo_ir_sha256",
    }
    for filename, field in expected.items():
        actual = sh(root / "scripts/custom_ollvm/kagura_k8" / filename)
        if actual != registry[field]:
            raise AssertionError("K9 K8 source changed without revalidating artifact: " + filename)
    if tuple(registry.get("k8_five_passes", [])) != ("ibr", "mvo", "genc", "fsplit", "ci"):
        raise AssertionError("K9 pinned K8 pass inventory changed")
    if k8.mvo_expected_checksum() != K8_MVO_DIGEST:
        raise AssertionError("K9 MVO independent oracle unexpectedly drifted")
    return {"source_fixture_sha256": registry[expected["fixture.c"]],
            "source_mvo_sha256": registry[expected["mvo.ll"]],
            "source_runner_sha256": registry[expected["runner.c"]]}


def main_run(llvm: Path, plugin: Path, src: Path, out: Path,
             *, strict_link_metadata: bool = False) -> dict:
    provenance = verify_inputs()
    registry = src / "include/kagura/PassRegistry.def"
    k8.validate_registry(registry.read_text(encoding="utf-8"))
    if not plugin.is_file() or not (src / "LICENSE").is_file():
        raise AssertionError("K9 pinned Kagura plugin/license unavailable")
    runtime = src.parent / "kagura-k9-build/runtime/libkagura_runtime.a"
    if not runtime.is_file():
        raise AssertionError("K9 pinned runtime library missing (CI resolver)")
    out.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src / "LICENSE", out / "KAGURA-UPSTREAM-LICENSE")
    clang = str(llvm / "bin/clang")
    dis = str(llvm / "bin/llvm-dis")
    assemble = str(llvm / "bin/llvm-as")
    link_ir = str(llvm / "bin/llvm-link")
    opt = str(llvm / "bin/opt")
    sdk_host = run_command(["xcrun", "--sdk", "macosx", "--show-sdk-path"]).strip()
    sdk_ios = run_command(["xcrun", "--sdk", "iphoneos", "--show-sdk-path"]).strip()
    host_triple = (run_command([clang, "-print-target-triple"]).strip()
                   if not strict_link_metadata else None)
    template = (K8 / "mvo.ll").read_text(encoding="utf-8")
    runner = out / "runner.o"
    run_command(["xcrun", "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                 "-O1", "-c", str(HERE / "runner.c"), "-o", str(runner)])

    def native_object(bc: Path, dest: Path, ios: bool) -> None:
        args = [clang, "-O0"]
        if ios:
            args += ["-target", "arm64-apple-ios15.0", "-isysroot", sdk_ios]
        run_command([*args, "-c", str(bc), "-o", str(dest)])
        if ios:
            k8.verify_apple_arm64_object(dest.read_bytes())

    def build_merged(label: str, ios: bool) -> tuple[Path, Path, Path]:
        folder = out / label
        folder.mkdir(exist_ok=True)
        c_bc = folder / "c.bc"
        c_ir = folder / "c.ll"
        mvo_ir = folder / "mvo-source.ll"
        mvo_bc = folder / "mvo.bc"
        merged = folder / "merged.bc"
        merged_ir = folder / "merged.ll"
        obj = folder / "merged.o"
        flags = [clang, "-O1", "-std=c11", "-Wall", "-Wextra",
                 "-Werror", "-fno-builtin-strlen"]
        if ios:
            flags += ["-target", "arm64-apple-ios15.0", "-isysroot", sdk_ios]
        else:
            flags += ["-isysroot", sdk_host]
        run_command([*flags, "-emit-llvm", "-c", str(K8 / "fixture.c"),
                     "-o", str(c_bc)])
        # Strict K10 path reads the Clang-emitted *module header* instead
        # of using -print-target-triple, which may spell macOS differently.
        if strict_link_metadata:
            run_command([dis, str(c_bc), "-o", str(c_ir)])
            c_text = c_ir.read_text(encoding="utf-8")
            generated = align_mvo_to_c_module(template, c_text, ios=ios)
        else:
            generated = mvo_module(
                template, "arm64-apple-ios15.0" if ios else host_triple)
        mvo_ir.write_text(generated, encoding="utf-8")
        run_command([assemble, str(mvo_ir), "-o", str(mvo_bc)])
        link_log = folder / "llvm-link.log"
        run_command([link_ir, str(c_bc), str(mvo_bc), "-o", str(merged)],
                    log=link_log)
        run_command([dis, str(merged), "-o", str(merged_ir)])
        merged_text = merged_ir.read_text(encoding="utf-8")
        validate_merged(merged_text)
        if strict_link_metadata:
            evidence = validate_llvm_link_metadata(
                c_text, generated, merged_text,
                link_log.read_text(encoding="utf-8"), ios=ios)
            (folder / "target-metadata.json").write_text(
                json.dumps({**evidence,
                            "c_ir_sha256": sh(c_ir),
                            "mvo_ir_sha256": sh(mvo_ir),
                            "merged_ir_sha256": sh(merged_ir)},
                           indent=2, sort_keys=True) + "\n", encoding="utf-8")
        native_object(merged, obj, ios)
        return merged, merged_ir, obj

    host_bc, host_ir, host_obj = build_merged("macos", ios=False)
    ios_bc, ios_ir, ios_obj = build_merged("ios", ios=True)
    plain_exe = out / "plain"
    run_command(["xcrun", "clang", str(host_obj), str(runner), "-o", str(plain_exe)],
                log=out / "plain-link.log")
    plain_log = out / "plain-native.log"
    plain_log.write_text(run_command([str(plain_exe)]), encoding="ascii")
    validate_logs(plain_log.read_text(encoding="ascii"))

    report = {
        "schema": 1, "scope": "K9_PINNED_KAGURA_FIVE_PASS_ONE_MODULE_COMPOSITION",
        "status": "INCOMPLETE_UNTIL_ALL_STAGES_PASS",
        "pinned_commit": UPSTREAM_PIN, "stage_order": list(STAGES),
        "source_scope": "K8_C_PLUS_MVO_IR_SINGLE_LLVM_LINKED_MODULE",
        "native_vectors_per_function": 4096,
        "native_digest_c": K8_C_DIGEST,
        "native_digest_mvo": K8_MVO_DIGEST,
        "mvo_independent_oracle": k8.mvo_expected_checksum(),
        "ios_arm64": "OBJECT_BUILD_ONLY_NOT_EXECUTED",
        "iphone_runtime_executed": False,
        "arm64e_pac_runtime_executed": False,
        "performance_evaluated": False,
        "crane_production_modified": False,
        "k8_provenance": provenance,
        "k9_runner_sha256": sh(HERE / "runner.c"),
        "registry_sha256": sh(registry),
        "plain_host_object_sha256": sh(host_obj),
        "plain_ios_object_sha256": sh(ios_obj),
        "stages": {},
        **({"link_metadata": {
            target: json.loads(
                (out / target / "target-metadata.json").read_text(encoding="utf-8"))
            for target in ("macos", "ios")}
           } if strict_link_metadata else {}),
    }
    report_path = out / "Kagura-K9-COMPOSITION-REPORT.json"

    def save() -> None:
        report_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    save()
    previous = {
        "macos": (host_bc, host_ir, host_obj),
        "ios": (ios_bc, ios_ir, ios_obj),
    }
    for index, name in enumerate(STAGES, start=1):
        folder = out / f"{index:02d}-{name}"
        folder.mkdir(exist_ok=True)
        evidence: dict[str, object] = {"pass": name, "index": index}
        for target in ("macos", "ios"):
            prev_bc, prev_ir, prev_obj = previous[target]
            tagged_bc = folder / f"{target}.bc"
            tagged_ir = folder / f"{target}.ll"
            tagged_obj = folder / f"{target}.o"
            trace = folder / f"{target}-opt.log"
            kind, cls, pipeline = k8.CANDIDATES[name]
            run_command([opt, f"--load-pass-plugin={plugin}",
                         f"-kagura-seed={SEED}", f"-kagura-{name}",
                         "-debug-pass-manager", f"-passes={pipeline},verify",
                         str(prev_bc), "-o", str(tagged_bc)], log=trace)
            run_command([dis, str(tagged_bc), "-o", str(tagged_ir)])
            native_object(tagged_bc, tagged_obj, ios=(target == "ios"))
            audit = validate_stage(
                name, prev_ir.read_text(encoding="utf-8"),
                tagged_ir.read_text(encoding="utf-8"),
                prev_obj.read_bytes(), tagged_obj.read_bytes(),
                trace.read_text(encoding="utf-8"))
            evidence[target] = {
                "class": cls, "kind": kind,
                "previous_object_sha256": sh(prev_obj),
                "object_sha256": sh(tagged_obj),
                "opt_log_sha256": sh(trace),
                "ir_sha256": sh(tagged_ir),
                "ir_and_object_changed": True, **audit,
            }
            previous[target] = tagged_bc, tagged_ir, tagged_obj
        host_candidate = previous["macos"][2]
        candidate_exe = folder / "native"
        linker = ["xcrun", "clang", str(host_candidate), str(runner)]
        if name == "ci":
            linker.append(str(runtime))
        # Crucial: once CI constructor/dlsym has been added it MUST link
        # with pinned upstream runtime; no missing-symbol workaround.
        run_command([*linker, "-o", str(candidate_exe)],
                    log=folder / "link.log")
        native_log = folder / "native.log"
        native_log.write_text(run_command([str(candidate_exe)]), encoding="ascii")
        validate_logs(native_log.read_text(encoding="ascii"))
        if native_log.read_bytes() != plain_log.read_bytes():
            raise AssertionError(f"K9 {name}: two-function parity mismatch")
        evidence["macos_native_4096_per_function"] = "PASS"
        evidence["native_log_sha256"] = sh(native_log)
        report["stages"][name] = evidence
        save()
    if tuple(report["stages"]) != STAGES:
        raise AssertionError("K9 missing combined pass stage")
    report["status"] = "MACOS_NATIVE_ALL_FIVE_COMPOSED_STAGES_PASS_IOS_BUILD_ONLY"
    validate_composition_report(report)
    save()
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--llvm", type=Path)
    p.add_argument("--plugin", type=Path)
    p.add_argument("--src", type=Path)
    p.add_argument("--out", type=Path)
    p.add_argument("--verify-report", type=Path,
                   help="Independently validate a serialized K9 JSON report")
    a = p.parse_args()
    if a.verify_report is not None:
        if any(v is not None for v in (a.llvm, a.plugin, a.src, a.out)):
            p.error("--verify-report cannot run a compiler build")
        validate_composition_report(json.loads(
            a.verify_report.read_text(encoding="utf-8")))
        print("KAGURA_K9_SERIALIZED_REPORT_ORDER_AND_NATIVE_EVIDENCE_PASS")
        return
    if any(v is None for v in (a.llvm, a.plugin, a.src, a.out)):
        p.error("--llvm, --plugin, --src and --out are required for build")
    result = main_run(a.llvm, a.plugin, a.src, a.out)
    validate_composition_report(result)
    print("KAGURA_K9_COMPOSED_FIVE_STAGE_MACOS_NATIVE_AND_ARM64_OBJECTS_PASS")


if __name__ == "__main__":
    main()
