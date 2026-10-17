#!/usr/bin/env python3
"""Locate the REAL pinned Kagura CI runtime C function definition, not mentions.

K11 must never substitute a shim for kagura_rtld_default_handle. The original
text-only scan matched calls/prototypes and could reject a valid upstream
checkout because multiple translation units merely mentioned the symbol.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SYMBOL = "kagura_rtld_default_handle"
# This is an intentionally strict C function *definition*, not a declaration:
# signature (...) followed by a body brace; tolerate attributes between.
DEF_RE = re.compile(
    r"\b" + SYMBOL +
    r"\s*\(\s*(?:void\s*)?\)\s*(?:__attribute__\s*\(\([^{};]*\)\)\s*)?\{",
    re.MULTILINE,
)


def without_comments(source: str) -> str:
    # Ignore comments and string/character literals so documentation or
    # source diagnostics containing a fake function signature cannot pass.
    return re.sub(
        r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
        lambda m: "\n" * m.group(0).count("\n"),
        source, flags=re.DOTALL,
    )


def select(root: Path) -> dict:
    """Require exactly one real C source defining the resolver in runtime/."""
    if not (root / "LICENSE").is_file() or not (root / "runtime").is_dir():
        raise AssertionError("K11 pinned Kagura checkout/runtime missing")
    candidates, definitions, non_definitions = [], [], []
    files = sorted((root / "runtime").rglob("*.c"))
    if not files:
        raise AssertionError("K11 no pinned upstream runtime C files")
    for path in files:
        if path.is_symlink() or not path.is_file():
            raise AssertionError("K11 runtime sources must be regular upstream files")
        relative = path.relative_to(root).as_posix()
        if not relative.startswith("runtime/") or ".." in Path(relative).parts:
            raise AssertionError("K11 source escaped pinned runtime tree")
        content = path.read_text(encoding="utf-8")
        if SYMBOL not in content:
            continue
        candidates.append(relative)
        if DEF_RE.search(without_comments(content)):
            definitions.append(relative)
        else:
            non_definitions.append(relative)
    return {
        "schema": 1,
        "symbol": SYMBOL,
        "source_files_scanned": len(files),
        "mention_candidates": candidates,
        "function_definitions": definitions,
        "mentions_without_definition": non_definitions,
        "selection_strategy": "ONLY_UPSTREAM_C_FUNCTION_DEFINITION_NO_PROTOTYPE_OR_COMMENT",
        "selected_source": definitions[0] if len(definitions) == 1 else None,
        "selected_source_sha256": (
            hashlib.sha256((root / definitions[0]).read_bytes()).hexdigest()
            if len(definitions) == 1 else None),
    }


def require_selected(root: Path) -> dict:
    report = select(root)
    if len(report["function_definitions"]) != 1:
        raise AssertionError(
            "K11 requires exactly ONE pinned upstream definition of "
            + SYMBOL + "; found=" +
            str(len(report["function_definitions"])) +
            " (mentions=" + repr(report["mention_candidates"]) +
            ", definitions=" + repr(report["function_definitions"]) + ")")
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--src", required=True, type=Path)
    p.add_argument("--report", required=True, type=Path)
    p.add_argument("--selected-path", required=True, type=Path)
    x = p.parse_args()
    report = select(x.src)
    x.report.parent.mkdir(parents=True, exist_ok=True)
    x.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    if len(report["function_definitions"]) != 1:
        raise AssertionError(
            "K11 upstream CI resolver source ambiguous: "
            + json.dumps(report["mention_candidates"]) +
            ", actual definitions=" + json.dumps(report["function_definitions"]))
    x.selected_path.write_text(
        report["selected_source"] + "\n", encoding="utf-8")
    print("K11_UPSTREAM_CI_RESOLVER_SOURCE_DEFINED=" + report["selected_source"])


if __name__ == "__main__":
    main()
