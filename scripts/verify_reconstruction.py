#!/usr/bin/env python3
from __future__ import annotations

import plistlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECON = ROOT / "re" / "RECONSTRUCTION"

REQUIRED_SYNTHESIS = {
    "CarPlayCloak.m", "CarSleeper.m", "CNABConn.m", "Cpuigen.m",
    "CrashReporting.m", "DataRouter.m", "DDzCommit.m", "DDzCore.m",
    "DDzPicker.m", "EventLaunch.m", "Evict.m", "FastRelayout.m",
    "HostedCallbacks.m", "HostSplit.m", "HudBle.m", "KBObservers.m",
    "KeyboardHooks.m", "KeyinputRelay.m", "License.m", "LocaleFlow.m",
    "Migration.m", "PollFlush.m", "PrefsResolver.m", "PresentCommitAck.m",
    "Respring.m", "SiriProbe.m", "SpawnLaunch.m", "SpawnMisc.m",
    "SpawnTeardown.m", "SpikeHosting.m",
}

missing = sorted(name for name in REQUIRED_SYNTHESIS if not (RECON / name).is_file())
if missing:
    raise SystemExit(f"missing reconstruction synthesis files: {', '.join(missing)}")

for required in [
    ROOT / "Makefile",
    ROOT / "control",
    ROOT / "DuoDashReconstruction.plist",
    RECON / "DuoDashShared.h",
    RECON / "ReconstructionRuntime.h",
    RECON / "ReconstructionRuntime.m",
    RECON / "Tweak.x",
]:
    if not required.is_file():
        raise SystemExit(f"missing build input: {required.relative_to(ROOT)}")

makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
for source in ["Tweak.x", "ReconstructionRuntime.m"]:
    if source not in makefile:
        raise SystemExit(f"Makefile does not include {source}")
if "DuoDashReconstruction_LIBRARIES = proc" not in makefile:
    raise SystemExit("Makefile must link libproc for the reconstructed 7764C liveness probe")

with (ROOT / "DuoDashReconstruction.plist").open("rb") as fh:
    filter_plist = plistlib.load(fh)

filter_dict = filter_plist.get("Filter", {})
expected_bundles = {
    "com.apple.springboard",
    "com.apple.Preferences",
    "com.apple.CarPlayApp",
    "com.apple.UIKit",
}
if set(filter_dict.get("Bundles", [])) != expected_bundles:
    raise SystemExit("Substrate bundle filter drifted from reconstructed artifact")
if set(filter_dict.get("Executables", [])) != {"mediaserverd", "kbd"}:
    raise SystemExit("Substrate executable filter drifted from reconstructed artifact")

runtime = (RECON / "ReconstructionRuntime.m").read_text(encoding="utf-8")
for contract in [
    "DDDetectRole",
    "DDBuildKnownAppBridgeSnapshot",
    "DDRepublishKnownAppBridgeSnapshot",
    "DDCachedStringValue",
    "DDCachedCarPlayUIMore",
    "DDCachedAutostartEnabled",
    "DDCachedFractionValue",
    "DDCachedFractionLayoutValue",
    "DDValidateIntegerValue(value, 0, 99, 0, NULL)",
    "DDValidateIntegerValue(value, 0, 8, 0, NULL)",
    "DDReadKeyPaneEnabled",
    "DDReadBridgedFontFloor",
    "DDValidateIntegerValue",
    "DDNormalizeIntegerSetting",
    "CFNumberIsFloatType",
    "DDIntegerValidationString",
    "DDIntegerValidationError",
    "DDSetAppBridgeLayout",
    "DDSetCarPlayUI",
    "DDToggleAppBridgeAutostart",
    "DDEvictCarPlayUIBundle",
    "DDCountLiveSnapshotEntries",
    "DDPostDistributedNotification",
    "DDObserveDistributedNotification",
    "DDPostHostRefusedState",
    "DDPostHostState",
    "NSDistributedNotificationCenter",
    "postNotificationName:object:userInfo:deliverImmediately:",
    "addObserver:selector:name:object:",
    "com.sensetechlab.appbridge.host.state",
    "cpuiKilled",
    "proc_pidpath",
    "com.apple.springboard",
    "UINT32_MAX",
    "strcmp(buffer, expectedPath) == 0",
    "DDReconstructionStart",
    "appbridge_split_enabled",
    "com.sensetechlab.appbridge.resolved",
    "DD_N_AUTOSTART_CHANGED",
    "CFNotificationSuspensionBehaviorDeliverImmediately",
    "CFBooleanGetTypeID",
    "return enabled || !valid",
    "value >= 8 && value <= 96",
    "duodash_ab_fontfloor_force",
]:
    if contract not in runtime:
        raise SystemExit(f"runtime contract missing: {contract}")

shared = (RECON / "DuoDashShared.h").read_text(encoding="utf-8")
if 'DD_N_AUTOSTART_CHANGED @"com.sensetechlab.autostart.changed"' not in shared:
    raise SystemExit("autostart Darwin notification constant drifted from decompile")

print(
    f"OK: {len(REQUIRED_SYNTHESIS)} synthesis modules present; "
    "build scaffold and Substrate filter verified"
)
