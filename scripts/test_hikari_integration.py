#!/usr/bin/env python3
"""Static Hikari integration guards and fail-closed audit self-tests."""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRIAL = ROOT / "scripts" / "hikari_eval"
policy = json.loads((TRIAL / "policy.json").read_text(encoding="utf-8"))
assert set(policy) == {"policy_map", "policies"}
assert policy["policy_map"] == {
    "hikari_probe_string": {"enable-strcry": True, "strcry_prob": 100},
    "hikari_probe_const": {
        "enable-constenc": True,
        "constenc_subxor": True,
        "constenc_subxor_prob": 100,
        "constenc_togv": False,
        "constenc_togv_prob": 50,
        "constenc_times": 1,
    },
}
assert len(policy["policies"]) == 2
for rule, func, pol in (
    (policy["policies"][0], "dd_hikari_probe_string", "hikari_probe_string"),
    (policy["policies"][1], "dd_hikari_probe_const", "hikari_probe_const"),
):
    assert re.fullmatch(rule["module"], "probe.c")
    assert re.fullmatch(rule["func"], func)
    assert rule["policy"] == pol
    assert not re.fullmatch(rule["func"], "dd_hikari_probe_other")

source = (TRIAL / "probe.c").read_text(encoding="utf-8")
runner = (TRIAL / "runner.c").read_text(encoding="utf-8")
assert "DUODASH_HIKARI_CANARY_ONLY_7F29D1B3" in source
assert "DUODASH_HIKARI_CANARY_ONLY_7F29D1B3" not in runner
for func in ("dd_hikari_probe_string", "dd_hikari_probe_const"):
    assert re.search(r"\b" + func + r"\s*\(", source)
assert "for (int value = -256; value <= 256; ++value)" in runner

workflow = (ROOT / ".github/workflows/hikari-evaluation.yml").read_text(
    encoding="utf-8"
)
assert "workflow_dispatch:" in workflow
assert not re.search(r"^  (?:push|pull_request):", workflow, re.MULTILINE)
assert "runs-on: macos-latest" in workflow
assert "working-directory: scripts/hikari_eval" in workflow
assert "git -C \"$source_dir\" checkout -q --detach FETCH_HEAD" in workflow
assert "592f215f852e3957da01b2b15024dc63713a462e" in workflow
assert '-S "$source_dir/hikari"' in workflow
assert "-DLLVM_DIR=" in workflow and "llvm@19" in workflow
assert "fpass-plugin=\"$HIKARI_PLUGIN\"" in workflow
assert "python3 audit.py native" in workflow
assert "--protected-executable out/probe-native-hikari" in workflow
assert "python3 audit.py ios" in workflow
assert "arm64-apple-ios14.0" in workflow
assert "DuoDash-Hikari-Evaluation-Diagnostics" in workflow
assert "DuoDashReconstruction-OLLVM" not in workflow
assert "make clean all" not in workflow
assert "DuoDashReconstruction_FILES" not in workflow

existing_policy = json.loads((ROOT / "policy.json").read_text(encoding="utf-8"))
assert "full_strength_eval" in existing_policy["policy_map"]
assert all("enable-strcry" not in item for item in existing_policy["policy_map"].values())
assert all("enable-constenc" not in item for item in existing_policy["policy_map"].values())

spec = importlib.util.spec_from_file_location("hikari_audit", TRIAL / "audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
log = "\n".join(audit.PASS_LINES)
plain_bytes = b"prefix" + audit.MARKER + b"suffix"
protected_bytes = b"transformed non-plaintext object"
audit.audit_object(plain_bytes, protected_bytes, log)


def expect_failure(callback, *args):
    try:
        callback(*args)
    except AssertionError:
        return
    raise AssertionError("Expected the fail-closed audit to reject bad data")


expect_failure(audit.audit_object, plain_bytes, protected_bytes, "")
expect_failure(audit.audit_object, plain_bytes, plain_bytes, log)
expect_failure(audit.audit_object, b"missing", protected_bytes, log)
expect_failure(audit.audit_object, plain_bytes, protected_bytes,
               audit.PASS_LINES[0])

vectors = "\n".join(f"{index}:{index & 0xffffffff:08x}:00000000"
                    for index in range(-256, 257)) + "\n"
audit.audit_output(vectors, vectors)
expect_failure(audit.audit_output, vectors, vectors.replace("00000000", "11111111", 1))
expect_failure(audit.audit_output, vectors, "not enough")
expect_failure(audit.audit_output, vectors, "")

print("Isolated Hikari CI policy, 2 passes, 513 vectors and fail-closed auditing: PASS")
