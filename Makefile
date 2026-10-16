ARCHS = arm64
TARGET = iphone:clang:latest:14.0

include $(THEOS)/makefiles/common.mk

TWEAK_NAME = DuoDashReconstruction

DuoDashReconstruction_FILES = \
	re/RECONSTRUCTION/Tweak.x \
	re/RECONSTRUCTION/ReconstructionRuntime.m \
	re/RECONSTRUCTION/RecoveryRouting.m \
	re/RECONSTRUCTION/HostFlowAdapter.m \
	re/RECONSTRUCTION/DDzPicker.m \
	re/RECONSTRUCTION/CrashReporting.m \
	re/RECONSTRUCTION/LicenseHelpers.m \
	re/RECONSTRUCTION/LocaleFlow.m \
	re/RECONSTRUCTION/PrefsResolver.m \
	re/RECONSTRUCTION/Migration.m \
	re/RECONSTRUCTION/SiriProbe.m \
	re/RECONSTRUCTION/KeyinputGate.m \
	re/RECONSTRUCTION/AppBridgeTuning.m \
	re/RECONSTRUCTION/NavProviderHelpers.m \
	re/RECONSTRUCTION/CameraRelayHelpers.m \
	re/RECONSTRUCTION/PerfTuning.m \
	re/RECONSTRUCTION/VersionDeviceHelpers.m \
	re/RECONSTRUCTION/InitRoleHelpers.m \
	re/RECONSTRUCTION/CarPlaySpoofHelpers.m \
	re/RECONSTRUCTION/ToggleValueHelpers.m
DuoDashReconstruction_CFLAGS = -fobjc-arc -Wall -Wextra

# OLLVM is opt-in: use a matching external LLVM clang + pass plugin.
# The pipeline must supply OLLVM_PLUGIN and override TARGET_CC/TARGET_CXX.
ifeq ($(OLLVM),1)
ifeq ($(strip $(OLLVM_PLUGIN)),)
$(error OLLVM=1 requires OLLVM_PLUGIN (path to a built LLVM pass plugin))
endif
DuoDashReconstruction_CFLAGS += -O1 -fpass-plugin=$(OLLVM_PLUGIN)
endif

DuoDashReconstruction_FRAMEWORKS = Foundation CoreFoundation CoreGraphics
DuoDashReconstruction_LIBRARIES = proc

include $(THEOS_MAKE_PATH)/tweak.mk
