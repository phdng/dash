#!/usr/bin/env python3
"""Portable CI invariants for the unsigned independent iPhone UIKit lab app."""
from __future__ import annotations

import importlib.util
import plistlib
import struct
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/protection_lab"
sys.path.insert(0, str(LAB))

src = (LAB / "ios_app_main.m").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/protection-ios-app.yml").read_text(
    encoding="utf-8"
)
docs = (ROOT / "docs/PROTECTION_IOS_APP.md")
with (LAB / "ios_app_Info.plist").open("rb") as handle:
    manifest = plistlib.load(handle)

assert manifest["CFBundleIdentifier"] == "com.duodash.research.protectionlab"
assert manifest["CFBundleExecutable"] == "ProtectionLab"
assert manifest["MinimumOSVersion"] == "15.0"
assert manifest["LSRequiresIPhoneOS"] is True
assert manifest["UIDeviceFamily"] == [1]
assert manifest["CFBundlePackageType"] == "APPL"
assert manifest["CFBundleSupportedPlatforms"] == ["iPhoneOS"]
assert manifest.get("UIRequiredDeviceCapabilities") in (None, [])
assert "NSAppTransportSecurity" not in manifest
assert "UIBackgroundModes" not in manifest

# UI must run only on an explicit tap, then display its true result.
for required in (
    "UIApplicationMain(argc, argv", "DDProtectionLabAppDelegate",
    "DDProtectionLabViewController", "UIKit/UIKit.h",
    "Run 4 suites × 8192", "startValidation", "shareReport",
    "UIActivityViewController", "dispatch_get_global_queue",
    "dispatch_get_main_queue", "self.runButton.enabled = NO",
    "self.shareButton.enabled = NO", "self.shareButton.enabled = YES",
    "DD_RUNTIME_CONTEXT=IOS_DEVICE", "DD_RUNTIME_ABI=",
    "DD_RUNTIME_COMPLETE=PASS", "TARGET_OS_SIMULATOR",
    "_dyld_get_image_header(0)", "__arm64e__",
    "raw & UINT32_C(0x80000000)", "raw & UINT32_C(0x40000000)",
    "DD_RUNTIME_ERROR=ARCH_OR_PAC_ABI_MISMATCH",
    "DD_RUNTIME_ERROR=VM", "DD_RUNTIME_ERROR=CE_ICALL",
    "DD_RUNTIME_ERROR=IGV_IBR", "DD_RUNTIME_ERROR=OBJC_CE",
    "dd_device_test_vm()", "dd_device_test_ce_icall()",
    "dd_device_test_igv_ibr()", "DDObjCPlainValue(i)",
    "DDObjCProtectedValue(i)", "isEqualToString:candidate",
    "lengthOfBytesUsingEncoding:NSUTF8StringEncoding",
    "@autoreleasepool", "[plain UTF8String]", "[candidate UTF8String]",
    "DD_DEVICE_VECTORS", "self.reportView.text = result",
):
    assert required in src, f"Missing app invariant: {required}"

# Check that failure always returns before the completion line, and
# that all four PASS marker strings appear in the required order.
stages = (
    "DD_RUNTIME_VM_PASS=8192",
    "DD_RUNTIME_CE_ICALL_PASS=8192",
    "DD_RUNTIME_IGV_IBR_PASS=8192",
    "DD_RUNTIME_OBJC_CE_PASS=8192",
    "DD_RUNTIME_COMPLETE=PASS",
)
assert [src.index(x) for x in stages] == sorted(src.index(x) for x in stages)
assert src.index("DD_RUNTIME_ERROR=ARCH_OR_PAC_ABI_MISMATCH") < src.index(stages[0])
assert src.count("DD_RUNTIME_COMPLETE=PASS") >= 3  # proof + UI gates (includes opt-in benchmark)
assert src.index("DD_RUNTIME_COMPLETE=PASS") < src.index("UIActivityViewController")
assert "NOT TESTED" in src
for forbidden in (
    "ptrauth_strip", "uintptr_t", "objc_msgSend(",
    "mprotect(", "mmap(", "syscall(", "dlopen(", "MSHook",
    "MobileSubstrate", "task_for_pid", "UIApplicationOpenSettingsURLString",
):
    assert forbidden not in src, f"Unsafe or production API: {forbidden}"

# Cross-platform verification of exactly the string export protocol
# accepted by the existing device_audit.py log parser.
spec = importlib.util.spec_from_file_location("device_audit", LAB / "device_audit.py")
assert spec.loader is not None
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / "shared-ios-text.txt"
    for arch in ("arm64", "arm64e"):
        lines = audit.expected_lines("IOS_DEVICE", arch)
        assert len(lines) == 7
        path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
        result = audit.verify_run_log(path, "IOS_DEVICE", arch)
        assert result["validated_stages"] == list(audit.STAGES)
        assert result["reported_architecture"] == arch
        for i in range(7):
            data = lines.copy()
            del data[i]
            path.write_bytes(("\n".join(data) + "\n").encode("utf-8"))
            try:
                audit.verify_run_log(path, "IOS_DEVICE", arch)
            except AssertionError:
                pass
            else:
                raise AssertionError("Accepted incomplete UI share payload")
        # Wrong architecture is never interchangeable.
        path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
        try:
            audit.verify_run_log(path, "IOS_DEVICE",
                                 "arm64" if arch == "arm64e" else "arm64e")
        except AssertionError:
            pass
        else:
            raise AssertionError("Accepted wrong Mach-O ABI in report")

# CI must compile and validate both native app slices, and must never
# try to sign, install, upload to App Store, or touch Crane.
for invariant in (
    "workflow_dispatch:", "runs-on: macos-14",
    "for arch in arm64 arm64e; do", 'app="$out/ProtectionLab-$arch.app"',
    '"$lab/ios_app_Info.plist"', "for name in objc_ce_plain objc_ce_protected ios_app_main",
    "for name in canary vm sllvm_plain sllvm_protected igv_ibr_plain igv_ibr_protected device_suites",
    "-framework UIKit -framework Foundation", "ios_app_main.m",
    '"$out/ProtectionLab-arm64.app/ProtectionLab"',
    '"$out/ProtectionLab-arm64e.app/ProtectionLab"',
    "device_audit.py", "ditto -c -k --sequesterRsrc --keepParent",
    "ProtectionLab-UNSIGNED-$arch.zip", "plutil -lint",
    "actions/upload-artifact@v4", "NOT TESTED", "No signing",
):
    # ios_app_main appears as loop token without extension: check file loop.
    if invariant == "ios_app_main.m":
        continue
    assert invariant in workflow, f"Missing workflow gate: {invariant}"
for prohibited in (
    "codesign -s", "ldid -S", "xcrun devicectl device install",
    "security import", "xcodebuild -exportArchive", "ssh ", "scp ",
    "dpkg ", "make clean package", "TARGET_CC=", "fpass-plugin",
):
    assert prohibited.lower() not in workflow.lower(), prohibited

assert docs.exists(), "Manual signing and device test instructions missing"
print("UIKit app: plist, 4-suite runtime UX, arm64/arm64e unsigned bundle "
      "workflow, share-log negative contracts PASS")
