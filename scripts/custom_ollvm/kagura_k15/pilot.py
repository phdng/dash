#!/usr/bin/env python3
"""K15: actual BBCheck IR/object and upstream runtime-provider DISCOVERY only.

Never execute the tamper callback: it may terminate or change a process.
There is no host checksum claim, IPA, device test or Crane integration.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts/custom_ollvm/kagura_k12"))
from inventory import PIN, parse_registry, normalized_ir_sha  # noqa: E402
sys.path.insert(0, str(ROOT / "scripts/custom_ollvm/kagura_k11"))
from ci_runtime_closure import parse_nm, parse_undefined_names  # noqa: E402

PASS_NAME = "kagura-bbcheck"
PASS_CLASS = "kagura::BasicBlockChecksumPass"
PIPELINE = "function(kagura-bbcheck),verify"
REGISTRY_SHA = "6f15bc2b432a6d1d84e83ecdb6221cc359e42adee40d0f93f36d75b2c363b5fa"
REQUIRED = ("_kagura_bb_check", "_kagura_on_tamper_detected")
MAX_MENTION_CANDIDATES = 32
SCAN_TIMEOUT = 65
FN_IR = re.compile(r"(?m)^define\s+[^\n]*@dd_k8_evaluate\(")
TRACE = re.compile(r"(?m)^Running pass: kagura::BasicBlockChecksumPass on dd_k8_evaluate \(")
CALLS = tuple(re.compile(r"\bcall\s+[^@\n]*@" + re.escape(name[1:]) + r"\(")
              for name in REQUIRED)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entry_from_registry(text: str) -> dict:
    items = [x for x in parse_registry(text) if x["name"] == PASS_NAME]
    if len(items) != 1 or items[0]["kind"] != "FN" or (
            items[0]["enable_flag"] != "BBCheck"):
        raise AssertionError("K15 actual pinned BBCheck FN/flag drift")
    return items[0]


def validate_pass(trace: str, baseline: str, after: str) -> None:
    if (not TRACE.search(trace) or
            "Running pass: VerifierPass on [module]" not in trace or
            "Running pass: BitcodeWriterPass on [module]" not in trace):
        raise AssertionError("K15 wrong actual LLVM19 BBCheckPass/VerifierPass trace")
    if not FN_IR.search(baseline) or not FN_IR.search(after):
        raise AssertionError("K15 original/protected canary ABI not present")
    if any(not rx.search(after) for rx in CALLS):
        raise AssertionError("K15 did not produce both real BBCheck runtime calls")
    if any(rx.search(baseline) for rx in CALLS):
        raise AssertionError("K15 baseline already contains BBCheck runtime calls")


def macho_arm64_object(raw: bytes) -> None:
    if (len(raw) < 32 or int.from_bytes(raw[0:4], "little") != 0xFEEDFACF or
            int.from_bytes(raw[4:8], "little") != 0x0100000C or
            int.from_bytes(raw[8:12], "little") != 0 or
            int.from_bytes(raw[12:16], "little") != 1):
        raise AssertionError("K15 expected arm64 subtype0 MH_OBJECT not executable/arm64e")


def cmd(args: list[str], log: Path, *, can_fail=False, timeout=SCAN_TIMEOUT) -> tuple[bool, str]:
    try:
        p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True, check=False, timeout=timeout)
        log.write_text(p.stdout + p.stderr, encoding="utf-8")
        if p.returncode and not can_fail:
            raise AssertionError(
                "K15 tool failed with exit " + str(p.returncode) + ": " +
                args[0] + " " + p.stderr[-1000:])
        return p.returncode == 0, p.stdout
    except subprocess.TimeoutExpired:
        log.write_text("K15_COMMAND_TIMEOUT\n", encoding="utf-8")
        if not can_fail:
            raise AssertionError("K15 mandatory LLVM command timed out: " + args[0])
        return False, ""


def mentions_sources(src: Path) -> list[dict]:
    runtime = src / "runtime"
    if not runtime.is_dir():
        raise AssertionError("K15 missing exact pinned runtime source directory")
    entries = []
    for path in sorted(runtime.rglob("*.c")):
        if path.is_symlink() or not path.is_file():
            raise AssertionError("K15 unexpected symlink/broken C runtime source")
        text = path.read_text(encoding="utf-8")
        names = [name for name in REQUIRED
                 if re.search(r"\b" + re.escape(name.lstrip("_")) + r"\b", text)]
        if names:
            entries.append({"source": path.relative_to(src).as_posix(),
                            "source_sha256": sha(path),
                            "mentions_required": names})
    if len(entries) > MAX_MENTION_CANDIDATES:
        raise AssertionError("K15 too many runtime C candidates; manual review needed")
    return entries


def summarize_providers(results: list[dict]) -> dict:
    providers = {}
    for name in REQUIRED:
        providers[name] = [row["source"] for row in results
                           if name in row["actual_defined_kagura_symbols"]]
    missing = sorted(name for name, sources in providers.items() if not sources)
    duplicate = sorted(name for name, sources in providers.items()
                       if len(sources) > 1)
    selected = [r for r in results if r["source"] in
                {source for sources in providers.values() for source in sources}]
    all_defs = {name for row in selected for name in
                row["actual_defined_kagura_symbols"]}
    unresolved = sorted({name for row in selected for name in
                         row["actual_undefined_kagura_symbols"]} - all_defs)
    status = ("NOT_RESOLVED_UNIQUE_RUNTIME_PROVIDER" if missing or duplicate else
              "UNIQUE_PROVIDERS_WITH_UNRESOLVED_TRANSITIVE_SYMBOLS"
              if unresolved else
              "UNIQUE_DIRECT_PROVIDERS_NO_KAGURA_TRANSITIVE_SYMBOLS_NOT_EXECUTED")
    return {"required_symbol_providers": providers,
            "missing_symbols": missing, "duplicate_symbols": duplicate,
            "transitive_unresolved_kagura_symbols": unresolved,
            "status": status}


def resolve_candidates(entries: list[dict], src: Path, out: Path, sdk: str,
                       llvm: Path, target: str) -> dict:
    results = []
    options = (["-target", "arm64-apple-ios15.0"] if target == "ios" else [])
    clang = llvm / "bin/clang"
    for i, row in enumerate(entries, 1):
        obj = out / f"{target}-runtime-candidate-{i:02d}.o"
        compile_log = out / f"{target}-runtime-candidate-{i:02d}-compile.log"
        args = [str(clang), "-std=c11", "-O1", "-Wall", "-Wextra",
                *options, "-isysroot", sdk,
                "-I" + str(src / "include"),
                "-I" + str(src / "runtime"), "-I" + str(src),
                "-c", str(src / row["source"]), "-o", str(obj)]
        ok, _ = cmd(args, compile_log, can_fail=True)
        record = {**row, "compile_log": compile_log.name,
                  "compile_log_sha256": sha(compile_log),
                  "compile_success": ok,
                  "object": obj.name if ok else None,
                  "object_sha256": sha(obj) if ok else None,
                  "actual_defined_kagura_symbols": [],
                  "actual_undefined_kagura_symbols": [],
                  "defined_nm_sha256": None,
                  "undefined_nm_sha256": None}
        if ok:
            if not obj.is_file() or not obj.stat().st_size:
                raise AssertionError("K15 compiler returned success without actual object")
            if target == "ios":
                macho_arm64_object(obj.read_bytes())
            dlog = out / f"{target}-runtime-candidate-{i:02d}-defined-nm.log"
            ulog = out / f"{target}-runtime-candidate-{i:02d}-undefined-nm.log"
            _ok, defined = cmd(["xcrun", "nm", "-gU", str(obj)], dlog)
            _ok, undefined = cmd(["xcrun", "nm", "-u", "-j", str(obj)], ulog)
            record["actual_defined_kagura_symbols"] = sorted(
                x for x in parse_nm(defined, defined=True) if x.startswith("_kagura_"))
            record["actual_undefined_kagura_symbols"] = sorted(
                x for x in parse_undefined_names(undefined) if x.startswith("_kagura_"))
            record["defined_nm_sha256"] = sha(dlog)
            record["undefined_nm_sha256"] = sha(ulog)
        results.append(record)
    # Transitive undefined Kagura deps remain explicit blockers. Do not
    # link guessed system shims or execute anti-tamper runtime.
    return {"candidate_sources": results, **summarize_providers(results),
            "native_execution_attempted": False, "ios_ipa_link_attempted": False}


def run(src: Path, llvm: Path, plugin: Path, out: Path) -> dict:
    if out.exists() and any(out.iterdir()):
        raise AssertionError("K15 output path must be fresh to prevent stale PASS logs")
    out.mkdir(parents=True, exist_ok=True)
    registry = src / "include/kagura/PassRegistry.def"
    license_file = src / "LICENSE"
    if not registry.is_file() or not license_file.is_file() or (
            not license_file.stat().st_size):
        raise AssertionError("K15 missing pinned Kagura source/LICENSE")
    if sha(registry) != REGISTRY_SHA:
        raise AssertionError("K15 upstream source differs from K12 verified registry")
    entry = entry_from_registry(registry.read_text(encoding="utf-8"))
    if not plugin.is_file() or not plugin.stat().st_size:
        raise AssertionError("K15 actual pinned LLVM19 plugin missing")
    clang = llvm / "bin/clang"
    opt = llvm / "bin/opt"
    dis = llvm / "bin/llvm-dis"
    if any(not x.is_file() for x in (clang, opt, dis)):
        raise AssertionError("K15 LLVM19 clang/opt/llvm-dis missing")
    fixture = ROOT / "scripts/custom_ollvm/kagura_k8/fixture.c"
    if not fixture.is_file():
        raise AssertionError("K15 public-data C fixture missing")
    (out / "pinned-registry.def").write_bytes(registry.read_bytes())
    (out / "pinned-LICENSE").write_bytes(license_file.read_bytes())
    candidates = mentions_sources(src)
    for i, row in enumerate(candidates, 1):
        archive = out / f"k15-runtime-source-{i:02d}.c"
        archive.write_bytes((src / row["source"]).read_bytes())
        if sha(archive) != row["source_sha256"]:
            raise AssertionError("K15 archived pinned C runtime source changed")
        row["archived_source"] = archive.name
    targets = {}
    for target, sdk in (("macos", "macosx"), ("ios", "iphoneos")):
        _, sdk_path = cmd(["xcrun", "--sdk", sdk, "--show-sdk-path"],
                          out / f"{target}-sdk.log")
        sdk_path = sdk_path.strip()
        if "\n" in sdk_path or not sdk_path or not Path(sdk_path).is_dir():
            raise AssertionError("K15 Apple SDK missing: " + sdk)
        args = ["-target", "arm64-apple-ios15.0"] if target == "ios" else []
        base = out / f"{target}-baseline.bc"
        after = out / f"{target}-bbcheck.bc"
        base_ll = out / f"{target}-baseline.ll"
        after_ll = out / f"{target}-bbcheck.ll"
        base_obj = out / f"{target}-baseline.o"
        after_obj = out / f"{target}-bbcheck.o"
        flags = [str(clang), "-O1", "-std=c11", "-Wall", "-Wextra",
                 "-Werror", "-fno-builtin-strlen", *args, "-isysroot", sdk_path]
        cmd([*flags, "-emit-llvm", "-c", str(fixture), "-o", str(base)],
            out / f"{target}-baseline-clang.log")
        cmd([str(dis), str(base), "-o", str(base_ll)],
            out / f"{target}-baseline-dis.log")
        cmd([str(opt), "--load-pass-plugin=" + str(plugin),
             "-kagura-seed=82712", "-kagura-bbcheck", "-debug-pass-manager",
             "-passes=" + PIPELINE, str(base), "-o", str(after)],
            out / f"{target}-pass-manager.log")
        cmd([str(dis), str(after), "-o", str(after_ll)],
            out / f"{target}-bbcheck-dis.log")
        validate_pass((out / f"{target}-pass-manager.log").read_text(
            encoding="utf-8"), base_ll.read_text(encoding="utf-8"),
            after_ll.read_text(encoding="utf-8"))
        if normalized_ir_sha(base_ll) == normalized_ir_sha(after_ll):
            raise AssertionError("K15 normalized LLVM IR failed genuine BBCheck delta")
        for bc, obj, label in ((base, base_obj, "baseline"),
                               (after, after_obj, "bbcheck")):
            cmd([str(clang), "-O0", *args, "-isysroot", sdk_path,
                 "-c", str(bc), "-o", str(obj)],
                out / f"{target}-{label}-clang-object.log")
            if target == "ios":
                macho_arm64_object(obj.read_bytes())
        if sha(base_obj) == sha(after_obj):
            raise AssertionError("K15 actual Mach-O object delta missing")
        defined_nm = out / f"{target}-bbcheck-defined-nm.log"
        undefined_nm = out / f"{target}-bbcheck-undefined-nm.log"
        _, defined = cmd(["xcrun", "nm", "-gU", str(after_obj)], defined_nm)
        _, undefined = cmd(["xcrun", "nm", "-u", "-j", str(after_obj)], undefined_nm)
        if "_dd_k8_evaluate" not in parse_nm(defined, defined=True):
            raise AssertionError("K15 Mach-O BBCheck lost public canary symbol")
        actual_deps = {x for x in parse_undefined_names(undefined)
                       if x.startswith("_kagura_")}
        if not set(REQUIRED).issubset(actual_deps):
            raise AssertionError("K15 BBCheck real object did not import both guards")
        provider_info = resolve_candidates(candidates, src, out, sdk_path, llvm, target)
        targets[target] = {
            "baseline_bc_sha256": sha(base),
            "protected_bc_sha256": sha(after),
            "baseline_ir_sha256": sha(base_ll),
            "protected_ir_sha256": sha(after_ll),
            "normalized_baseline_ir_sha256": normalized_ir_sha(base_ll),
            "normalized_protected_ir_sha256": normalized_ir_sha(after_ll),
            "baseline_object_sha256": sha(base_obj),
            "protected_object_sha256": sha(after_obj),
            "pass_manager_log_sha256": sha(out / f"{target}-pass-manager.log"),
            "bbcheck_nm_defined_sha256": sha(defined_nm),
            "bbcheck_nm_undefined_sha256": sha(undefined_nm),
            "actual_undefined_kagura_symbols": sorted(actual_deps),
            "real_pass_class": PASS_CLASS,
            "pass_ir_object_delta": True,
            "providers": provider_info,
            "native_checksum": "NOT_TESTED",
            "iphone_runtime": "NOT_TESTED",
        }
    report = {
        "schema": 1,
        "scope": "K15_BBCHECK_PINNED_LLVM19_DEPENDENCY_DISCOVERY_NO_NATIVE_EXECUTION",
        "pin": PIN,
        "registry_sha256": REGISTRY_SHA,
        "license_sha256": sha(out / "pinned-LICENSE"),
        "source_fixture_sha256": sha(fixture),
        "pass": PASS_NAME,
        "pass_kind": entry["kind"],
        "pass_flag": entry["enable_flag"],
        "actual_pass_class": PASS_CLASS,
        "pipeline": PIPELINE,
        "required_bbcheck_runtime_symbols": list(REQUIRED),
        "mentioned_source_count": len(candidates),
        "targets": targets,
        "native_4096_parity": "NOT_TESTED_GUARD_HAS_TAMPER_CALLBACK",
        "ios_ipa_built": False,
        "ios_device_executed": False,
        "arm64e_pac_tested": False,
        "crane_production_modified": False,
        "security_strength_claim": False,
    }
    (out / "Kagura-K15-REPORT.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("K15_BBCHECK_RUNTIME_CANDIDATES_SCREEN_COMPLETE_NOT_NATIVE: " +
          json.dumps({target: targets[target]["providers"]["status"]
                      for target in targets}, sort_keys=True))
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ("src", "llvm", "plugin", "out"):
        p.add_argument("--" + k, type=Path, required=True)
    a = p.parse_args()
    run(a.src, a.llvm, a.plugin, a.out)


if __name__ == "__main__":
    main()
