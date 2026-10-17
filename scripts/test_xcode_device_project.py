#!/usr/bin/env python3
"""Portable Xcode project contract: local-signing path without altering CI canaries.

Full plist/Xcode compiler/link validation occurs only on macOS Actions.
"""
from __future__ import annotations

import plistlib
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "scripts/protection_lab"
PROJECT = LAB / "ios_xcode" / "ProtectionLab.xcodeproj"
SOURCE = PROJECT / "project.pbxproj"
SCHEME = PROJECT / "xcshareddata" / "xcschemes" / "ProtectionLab.xcscheme"

c_files = (
    "canary.c", "vm.c", "sllvm_plain.c", "sllvm_protected.c",
    "igv_ibr_plain.c", "igv_ibr_protected.c", "device_suites.c",
    "perf_pilot.c", "perf_report.c",
)
obj_c_files = ("objc_ce_plain.m", "objc_ce_protected.m", "ios_app_main.m")
sources = c_files + obj_c_files

assert SOURCE.is_file() and SCHEME.is_file()
ignored = (PROJECT.parent / '.gitignore').read_text(encoding='utf-8')
assert 'xcuserdata/' in ignored and 'DerivedData/' in ignored
for name in sources:
    assert (LAB / name).is_file(), f"Source absent: {name}"

pbx = SOURCE.read_text(encoding="utf-8")
scheme = ET.fromstring(SCHEME.read_text(encoding="utf-8"))
with (LAB / "ios_app_Info.plist").open("rb") as f:
    info = plistlib.load(f)

assert pbx.startswith("// !$*UTF8*$!\n")
assert "objectVersion = 56;" in pbx
assert "compatibilityVersion = \"Xcode 14.0\";" in pbx
assert re.search(r"rootObject = [0-9A-F]{24}", pbx)

# All referenced PBX object identifiers must exist as an object definition,
# even if the build succeeds on synthetic fixture checks elsewhere.
ids_defined = re.findall(r"^\s*([0-9A-F]{24})(?:\s+/\*[^\n]*?\*/)?\s*=\s*\{", pbx, re.M)
assert ids_defined and len(ids_defined) == len(set(ids_defined))
ids_seen = set(re.findall(r"\b[0-9A-F]{24}\b", pbx))
assert ids_seen == set(ids_defined), (ids_seen - set(ids_defined))
for name in sources:
    assert len(re.findall(r"/\* " + re.escape(name) + r" in Sources \*/", pbx)) == 1
    assert f"path = {name};" in pbx
assert "lastKnownFileType = sourcecode.c.objc;" in pbx
assert "lastKnownFileType = sourcecode.c.c;" in pbx
assert "UIKit.framework in Frameworks" in pbx
assert "Foundation.framework in Frameworks" in pbx
assert "productType = \"com.apple.product-type.application\";" in pbx
assert "name = ProtectionLab;" in pbx

for expected in (
    "ARCHS = arm64;",
    "SUPPORTED_PLATFORMS = iphoneos;",
    "SDKROOT = iphoneos;",
    "CODE_SIGN_STYLE = Automatic;",
    'DEVELOPMENT_TEAM = "";',
    'INFOPLIST_FILE = "../ios_app_Info.plist";',
    "IPHONEOS_DEPLOYMENT_TARGET = 15.0;",
    "CLANG_ENABLE_OBJC_ARC = YES;",
    "HEADER_SEARCH_PATHS",
    "$(DERIVED_FILE_DIR)",
    "ENABLE_BITCODE = NO;",
    "GCC_OPTIMIZATION_LEVEL = 1;",
    "GENERATE_INFOPLIST_FILE = NO;",
    "Generate Public Canary Headers",
    'shellPath = /bin/bash;',
):
    assert expected in pbx, expected
for generator, header in (
    ("program.py", "vm_program.h"),
    ("sllvm_generator.py", "sllvm_encoded.h"),
    ("objc_ce_generator.py", "objc_ce_data.h"),
):
    assert generator in pbx and header in pbx
    assert f'$(SRCROOT)/../{generator}' in pbx
    assert f'$(DERIVED_FILE_DIR)/{header}' in pbx

# Build script occurs before compilation in the target's buildPhases.
native = pbx.split("isa = PBXNativeTarget;", 1)[1].split("/* End PBXNativeTarget section */", 1)[0]
ordered = re.search(r"buildPhases = \(([^)]*)\);", native)
assert ordered is not None
phases = ordered.group(1).split(", ")
assert len(phases) == 4
phase_objects = {key: value for key, value in re.findall(
    r"\b([0-9A-F]{24})\s+/\* (.*?) \*/ = \{isa = PBX(?:ShellScript|Sources|Resources|Frameworks)BuildPhase", pbx
)}
assert len(phase_objects) == 4
assert [phase_objects[x] for x in phases] == [
    "Generate Public Canary Headers", "Sources", "Frameworks", "Resources"
]

assert scheme.tag == "Scheme"
run = scheme.find("./LaunchAction/BuildableProductRunnable/BuildableReference")
assert run is not None
assert run.attrib["BuildableName"] == "ProtectionLab.app"
assert run.attrib["BlueprintName"] == "ProtectionLab"
assert run.attrib["ReferencedContainer"] == "container:ProtectionLab.xcodeproj"
assert "Debug" == scheme.find("./LaunchAction").attrib["buildConfiguration"]
assert info["CFBundleExecutable"] == "ProtectionLab"
assert info["CFBundleSupportedPlatforms"] == ["iPhoneOS"]
assert info["MinimumOSVersion"] == "15.0"

workflow = (ROOT / ".github/workflows/protection-ios-app.yml").read_text(encoding="utf-8")
for expected in (
    "python3 scripts/test_xcode_device_project.py",
    "Validate local-signing Xcode project without credentials",
    'project="$lab/ios_xcode/ProtectionLab.xcodeproj"',
    'plutil -lint "$project/project.pbxproj"',
    "xcodebuild -project",
    "-scheme ProtectionLab",
    "CODE_SIGNING_ALLOWED=NO build",
    "'generic/platform=iOS'",
    '"$out/xcode-arm64-build.log"',
    '"$out/xcode-arm64-macho.txt"',
    'inspect_executable',
    "No CI signing, installation",
):
    assert expected in workflow, expected
for forbidden in (
    "codesign -s", "ldid -S", "devicectl device install",
    "DEVELOPMENT_TEAM=ABCDE", "PROVISIONING_PROFILE", "signingCertificate",
):
    assert forbidden.lower() not in workflow.lower(), forbidden

print("Xcode on-device project: 12 real C/ObjC sources, header dependency "
      "phase, shared scheme, arm64 local signing, CI no-signing gates PASS")
