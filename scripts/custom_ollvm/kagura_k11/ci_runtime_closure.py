#!/usr/bin/env python3
"""Resolve iOS arm64 Kagura runtime object dependencies from real pinned C.

Do not fake unresolved symbols, link a macOS static library, or include
unrelated platform runtime objects. The exact C files selected are those
whose iOS clang object DEFINES (nm -gU) each unresolved _kagura_ symbol.
A recursive closure prevents introducing further unresolved Kagura symbols.
The final Apple linker remains authoritative for system/SDK references.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

NM_LINE = re.compile(r"^\s*(?:(?:[0-9A-Fa-f]+)\s+)?([A-Za-z])\s+(_[A-Za-z0-9_.$]+)\s*$")
# Apple 'nm -u' may output ONLY the symbol names, without a "U" column.
# Request -j explicitly so parsing does not depend on nm output style.
NM_SYMBOL = re.compile(r"_[A-Za-z0-9_.$]+")
MAX_SOURCES = 12
MAX_CANDIDATES = 72


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def parse_nm(content: str, *, defined: bool) -> set[str]:
    result: set[str] = set()
    for line in content.splitlines():
        m = NM_LINE.fullmatch(line)
        if not m:
            continue
        kind, symbol = m.groups()
        if (kind != "U" if defined else kind == "U"):
            result.add(symbol)
    return result


def parse_undefined_names(content: str) -> set[str]:
    """Consume Apple nm -u -j *names only*; reject malformed/mixed output."""
    result: set[str] = set()
    for raw in content.splitlines():
        name = raw.strip()
        if not name:
            continue
        if not NM_SYMBOL.fullmatch(name):
            raise AssertionError(
                "K11 unexpected Apple nm -u -j symbol line: " + repr(raw))
        result.add(name)
    return result


def run(args: list[str], *, log: Path | None = None) -> str:
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       text=True, check=False)
    if log is not None:
        log.write_text(p.stdout + p.stderr, encoding="utf-8")
    if p.returncode:
        raise RuntimeError(
            "K11 iOS runtime dependency command failed: "
            + args[0] + " rc=" + str(p.returncode) + ": "
            + p.stderr[-1500:])
    return p.stdout


def undefined_of(obj: Path) -> set[str]:
    # 'nm -u' is not consistently 'U _name' across Apple toolchains;
    # '-j' gives exactly one symbol NAME per line by contract.
    return parse_undefined_names(
        run(["xcrun", "nm", "-u", "-j", str(obj)]))


def defined_of(obj: Path) -> set[str]:
    return parse_nm(run(["xcrun", "nm", "-gU", str(obj)]), defined=True)


def required_symbols(objects: list[Path]) -> set[str]:
    defs: set[str] = set()
    undefs: set[str] = set()
    for obj in objects:
        if not obj.is_file() or not obj.stat().st_size:
            raise AssertionError("K11 missing genuine iOS Mach-O object " + str(obj))
        defs |= defined_of(obj)
        undefs |= undefined_of(obj)
    return {s for s in undefs - defs if s.startswith("_kagura_")}


def contains_token(text: str, name: str) -> bool:
    # A prototype/comment alone is NOT proof, only a candidate for
    # compiling. The arm64 nm definition is the decisive gate.
    return re.search(r"\b" + re.escape(name) + r"\b", text) is not None


def make_closure(src: Path, out: Path, sdk: str,
                 originals: list[Path], resolver_rel: str) -> dict:
    if not (src / "LICENSE").is_file():
        raise AssertionError("K11 requires pinned Kagura source checkout")
    if not resolver_rel.startswith("runtime/") or ".." in Path(resolver_rel).parts:
        raise AssertionError("K11 resolver provenance invalid")
    from ci_runtime_resolver import without_comments

    # Preserve exact unfiltered raw Apple nm stdout per original iOS object:
    # when the fail-closed check fires, artifact should show whether the
    # linker input or symbol parsing disagreed with the observed ld error.
    raw_nm = {}
    for obj in originals:
        if not obj.is_file() or not obj.stat().st_size:
            raise AssertionError("K11 missing original iOS object " + str(obj))
        raw = run(["xcrun", "nm", "-u", "-j", str(obj)])
        label = obj.relative_to(out).as_posix().replace("/", "-")
        # Retain raw nm output even when parsing rejects an unexpected
        # Apple toolchain output; GitHub uploads the directory on failure.
        (out / ("ios-nm-undefined-" + label + ".txt")).write_text(
            raw, encoding="utf-8")
        raw_nm[obj.relative_to(out).as_posix()] = {
            "nm_command": "xcrun nm -u -j",
            "raw_stdout": raw,
            "parsed_kagura_symbols": sorted(
                symbol for symbol in parse_undefined_names(raw)
                if symbol.startswith("_kagura_")),
        }
    (out / "ios-runtime-initial-nm.json").write_text(
        json.dumps(raw_nm, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    initial = required_symbols(originals)
    # The preceding real CI anti_debug object MUST have these two missing
    # providers in this pinned K11 revision. Future changes need review.
    expected = {"_kagura_image_list_contains",
                "_kagura_suspicious_image_patterns"}
    if not expected.issubset(initial):
        raise AssertionError(
            "K11 expected CI anti_debug object dependencies missing: "
            + repr(sorted(expected - initial)) + "; actual " + repr(sorted(initial)))
    all_sources: list[tuple[str, str, Path]] = []
    for f in sorted((src / "runtime").rglob("*.c")):
        if f.is_symlink() or not f.is_file():
            raise AssertionError("K11 unexpected symlink in pinned C runtime")
        rel = f.relative_to(src).as_posix()
        if rel == resolver_rel or not rel.startswith("runtime/"):
            continue
        all_sources.append((rel, without_comments(f.read_text(encoding="utf-8")), f))
    if not all_sources:
        raise AssertionError("K11 upstream runtime provider sources missing")

    cache: dict[str, dict] = {}
    selected: dict[str, dict] = {}
    objects = originals[:]
    per_symbol: dict[str, str] = {}
    initial_list = sorted(initial)
    iteration = 0
    while True:
        missing = required_symbols(objects)
        if not missing:
            break
        if len(selected) >= MAX_SOURCES:
            raise AssertionError("K11 runtime dependency closure exceeded source limit")
        iteration += 1
        if iteration > MAX_CANDIDATES:
            raise AssertionError("K11 runtime dependency closure failed to converge")
        symbol = sorted(missing)[0]
        short = symbol.lstrip("_")
        candidates = [(rel, content, f) for rel, content, f in all_sources
                      if contains_token(content, short)]
        if not candidates:
            raise AssertionError(
                "K11 no pinned C source even mentions unresolved " + symbol)
        if len(candidates) > MAX_CANDIDATES:
            raise AssertionError("K11 too many upstream providers for " + symbol)

        definers: list[dict] = []
        for rel, _content, path in candidates:
            if rel not in cache:
                number = len(cache) + 1
                name = f"ios-runtime-candidate-{number:02d}"
                obj = out / (name + ".o")
                clog = out / (name + "-compile.log")
                args = ["xcrun", "clang", "-std=c11", "-O1",
                        "-Wall", "-Wextra", "-target", "arm64-apple-ios15.0",
                        "-isysroot", sdk, "-I" + str(src / "include"),
                        "-I" + str(src / "runtime"), "-I" + str(src),
                        "-c", str(path), "-o", str(obj)]
                try:
                    run(args, log=clog)
                except RuntimeError as exc:
                    cache[rel] = {"source": rel, "failed_to_compile": True,
                                  "diagnostic": str(exc), "compile_log": clog.name}
                    continue
                d = defined_of(obj)
                cache[rel] = {
                    "source": rel, "source_sha256": sha(path),
                    "object": obj,
                    "object_sha256": sha(obj),
                    "defined_symbols": d, "undefined_symbols": undefined_of(obj),
                    "compile_log": clog.name,
                    "failed_to_compile": False,
                }
            info = cache[rel]
            if not info["failed_to_compile"] and symbol in info["defined_symbols"]:
                definers.append(info)
        if len(definers) != 1:
            raise AssertionError(
                "K11 unique actual ARM64 provider for " + symbol +
                " missing/duplicated: " +
                repr([d["source"] for d in definers]) +
                "; scanned " + repr([x[0] for x in candidates]) +
                "; failed candidates " + repr([
                    d["source"] for d in (cache[x[0]] for x in candidates)
                    if d["failed_to_compile"]]))
        chosen = definers[0]
        # One C translation unit can genuinely define BOTH missing Kagura
        # globals. Record every symbol resolved by that single provider.
        for covered in (chosen["defined_symbols"] & missing):
            per_symbol[covered] = chosen["source"]
        if chosen["source"] in selected:
            raise AssertionError("K11 closure logic selected same TU without resolution")
        selected[chosen["source"]] = chosen
        objects.append(chosen["object"])

    final_objects = []
    info_list = []
    for index, (rel, record) in enumerate(sorted(selected.items()), 1):
        target = out / f"ios-kagura-dependency-{index:02d}.o"
        shutil.copyfile(record["object"], target)
        final_objects.append(target)
        info_list.append({
            "source": rel,
            "source_sha256": record["source_sha256"],
            "object": target.name,
            "object_sha256": sha(target),
            "defines": sorted(s for s in record["defined_symbols"]
                              if s.startswith("_kagura_")),
            "undefined": sorted(s for s in record["undefined_symbols"]
                                if s.startswith("_kagura_")),
            "compile_log": record["compile_log"],
        })
    if not set(per_symbol).issuperset(expected):
        raise AssertionError("K11 did not resolve both originally missing symbols")
    if required_symbols(originals + final_objects):
        raise AssertionError("K11 unresolved Kagura symbols remain after closure")
    report = {
        "schema": 1,
        "scope": "PINNED_IOS_ARM64_RUNTIME_C_SYMBOL_CLOSURE_NOT_SHIMS",
        "upstream_source": "KAGURA_PINNED_COMMIT",
        "resolver_source": resolver_rel,
        "initial_undefined_kagura_symbols": initial_list,
        "required_historical_missing_symbols": sorted(expected),
        "initial_nm_format": "APPLE_NM_UNDEFINED_JUST_SYMBOL_NAMES",
        "initial_nm_raw_report_sha256": sha(out / "ios-runtime-initial-nm.json"),
        "providers_by_undefined_symbol": dict(sorted(per_symbol.items())),
        "selected_provider_sources": info_list,
        "final_unresolved_kagura_symbols": [],
        "macos_library_linked_to_ios": False,
        "stubs_inserted": False,
    }
    (out / "ios-runtime-closure.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    (out / "ios-runtime-extra-objects.txt").write_text(
        "".join(str(p) + "\n" for p in final_objects), encoding="utf-8")
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--src", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--sdk", required=True)
    x = p.parse_args()
    base = x.out
    resolver_file = base / "ios-rtld-source.txt"
    resolver = resolver_file.read_text(encoding="utf-8").strip()
    originals = [base / "05-ci/ios.o", base / "ios-kagura-rtld.o",
                 base / "ios-probe.o", base / "ios-app-main.o"]
    report = make_closure(x.src, base, x.sdk, originals, resolver)
    print("K11_IOS_CI_RUNTIME_DEPENDENCIES_RESOLVED=" +
          json.dumps(report["providers_by_undefined_symbol"], sort_keys=True))
    print("K11_IOS_REAL_RUNTIME_EXTRA_OBJECTS=" +
          str(len(report["selected_provider_sources"])))


if __name__ == "__main__":
    main()
