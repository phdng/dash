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
	re/RECONSTRUCTION/LocaleFlow.m \
	re/RECONSTRUCTION/PrefsResolver.m \
	re/RECONSTRUCTION/Migration.m \
	re/RECONSTRUCTION/SiriProbe.m \
	re/RECONSTRUCTION/KeyinputGate.m \
	re/RECONSTRUCTION/AppBridgeTuning.m \
	re/RECONSTRUCTION/NavProviderHelpers.m
DuoDashReconstruction_CFLAGS = -fobjc-arc -Wall -Wextra
DuoDashReconstruction_FRAMEWORKS = Foundation CoreFoundation
DuoDashReconstruction_LIBRARIES = proc

include $(THEOS_MAKE_PATH)/tweak.mk
