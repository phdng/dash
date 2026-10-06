ARCHS = arm64
TARGET = iphone:clang:latest:14.0

include $(THEOS)/makefiles/common.mk

TWEAK_NAME = DuoDashReconstruction

DuoDashReconstruction_FILES = \
	re/RECONSTRUCTION/Tweak.x \
	re/RECONSTRUCTION/ReconstructionRuntime.m
DuoDashReconstruction_CFLAGS = -fobjc-arc -Wall -Wextra
DuoDashReconstruction_FRAMEWORKS = Foundation CoreFoundation
DuoDashReconstruction_LIBRARIES = proc

include $(THEOS_MAKE_PATH)/tweak.mk
