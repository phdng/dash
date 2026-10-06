#pragma once

#import "DuoDashShared.h"
#include <stdint.h>

NS_ASSUME_NONNULL_BEGIN

typedef NS_ENUM(NSInteger, DDIntegerValidationStatus) {
    DDIntegerValidationMissing = 0,
    DDIntegerValidationNumber = 1,
    DDIntegerValidationString = 2,
    DDIntegerValidationError = 3,
};

typedef struct {
    double width;
    double height;
} DDHostSlotSize;

typedef struct {
    double frameX;
    double frameY;
    double frameWidth;
    double frameHeight;
    double windowX;
    double windowY;
    double windowWidth;
    double windowHeight;
    BOOL windowValid;
    uint8_t reserved[23];
    double carPlayWindowWidth;
    double carPlayWindowHeight;
} DDHostFrameMetrics;

FOUNDATION_EXPORT DDRole DDDetectRole(void);
FOUNDATION_EXPORT NSString *DDRoleName(DDRole role);
FOUNDATION_EXPORT NSDictionary *DDBuildKnownAppBridgeSnapshot(void);
FOUNDATION_EXPORT BOOL DDRepublishKnownAppBridgeSnapshot(NSError * _Nullable * _Nullable error);
FOUNDATION_EXPORT NSString * _Nullable DDCachedStringValue(NSString *key);
FOUNDATION_EXPORT NSArray<NSString *> *DDCachedCarPlayUIMore(void);
FOUNDATION_EXPORT BOOL DDCachedAutostartEnabled(void);
FOUNDATION_EXPORT NSInteger DDCachedFractionValue(NSString *key);
FOUNDATION_EXPORT NSInteger DDCachedFractionLayoutValue(void);
FOUNDATION_EXPORT BOOL DDReadKeyPaneEnabled(void);
FOUNDATION_EXPORT NSInteger DDReadBridgedFontFloor(void);
FOUNDATION_EXPORT NSInteger DDValidateIntegerValue(id _Nullable candidate,
                                                   NSInteger minimum,
                                                   NSInteger maximum,
                                                   NSInteger fallback,
                                                   DDIntegerValidationStatus * _Nullable status);
FOUNDATION_EXPORT NSInteger DDNormalizeIntegerSetting(NSDictionary *source,
                                                       NSString *key,
                                                       NSInteger minimum,
                                                       NSInteger maximum,
                                                       NSInteger fallback,
                                                       NSString *fixName,
                                                       NSMutableDictionary *writes,
                                                       NSMutableArray *fixes);
FOUNDATION_EXPORT BOOL DDSetAppBridgeLayout(NSInteger layout);
FOUNDATION_EXPORT BOOL DDSetCarPlayUI(NSString * _Nullable mainBundleIdentifier,
                                     id _Nullable additionalBundleIdentifiers);
FOUNDATION_EXPORT BOOL DDToggleAppBridgeAutostart(void);
FOUNDATION_EXPORT BOOL DDEvictCarPlayUIBundle(NSString *bundleIdentifier);
FOUNDATION_EXPORT NSInteger DDCountLiveSnapshotEntries(NSArray * _Nullable snapshot,
                                                       NSString * _Nullable bundleIdentifierFilter);
FOUNDATION_EXPORT BOOL DDPostDistributedNotification(NSString *name,
                                                     id _Nullable object,
                                                     NSDictionary * _Nullable userInfo);
FOUNDATION_EXPORT BOOL DDObserveDistributedNotification(NSString *name,
                                                        id observer,
                                                        SEL selector,
                                                        id _Nullable object);
FOUNDATION_EXPORT BOOL DDPostUIAppRequest(NSString * _Nullable bundleIdentifier);
FOUNDATION_EXPORT BOOL DDPostUIAppState(NSString * _Nullable bundleIdentifier,
                                       BOOL shouldBridge,
                                       NSInteger orientation,
                                       BOOL split,
                                       double displayWidth,
                                       double displayHeight);
FOUNDATION_EXPORT BOOL DDPostUIAppFontFloorState(NSString * _Nullable bundleIdentifier);
FOUNDATION_EXPORT BOOL DDPostUIAppKeyPaneState(NSString * _Nullable bundleIdentifier);
FOUNDATION_EXPORT NSDictionary *DDCurrentUIAppBridgeState(void);
FOUNDATION_EXPORT NSInteger DDReadHostOrientation(void);
FOUNDATION_EXPORT DDHostSlotSize DDResolveSingleHostMirrorSize(DDHostSlotSize renderSize,
                                                               DDHostSlotSize screenBoundsSize);
FOUNDATION_EXPORT BOOL DDParseLandscapeOverride(NSString * _Nullable text,
                                                NSInteger * _Nullable orientation,
                                                BOOL * _Nullable swap,
                                                BOOL * _Nullable cSwap,
                                                double * _Nullable rotationDegrees);
FOUNDATION_EXPORT NSInteger DDResolveSplitHostOrientationFromAcceptedOverride(NSString * _Nullable text);
FOUNDATION_EXPORT NSInteger DDResolveCoordinatedSplitHostOrientation(void);
FOUNDATION_EXPORT uint64_t DDPrepareSplitHostMirrorFromEnvironment(NSArray *bundleIdentifiers,
                                                                   const DDHostSlotSize *slotSizes,
                                                                   NSUInteger slotSizeCount,
                                                                   NSArray * _Nullable carPlayUIFlags);
FOUNDATION_EXPORT uint64_t DDPrepareSingleHostMirror(NSString * _Nullable bundleIdentifier,
                                                      DDHostSlotSize renderSize,
                                                      DDHostSlotSize screenBoundsSize);
FOUNDATION_EXPORT uint64_t DDPrepareSplitHostMirror(NSArray *bundleIdentifiers,
                                                     const DDHostSlotSize *slotSizes,
                                                     NSUInteger slotSizeCount,
                                                     NSArray * _Nullable carPlayUIFlags,
                                                     NSInteger resolvedOrientation);
FOUNDATION_EXPORT uint64_t DDUpdateHostSlotMirror(NSArray *bundleIdentifiers,
                                                  const DDHostSlotSize *slotSizes,
                                                  NSUInteger slotSizeCount,
                                                  NSArray * _Nullable carPlayUIFlags,
                                                  NSInteger orientation,
                                                  BOOL split);
FOUNDATION_EXPORT void DDResetHostSlotMirror(void);
FOUNDATION_EXPORT NSDictionary *DDCurrentHostSlotMirror(void);
FOUNDATION_EXPORT DDHostSlotSize DDApplyLandscapeSwapToSize(DDHostSlotSize size);
FOUNDATION_EXPORT BOOL DDUpdateHostSlotRenderSize(NSUInteger slotIndex, DDHostSlotSize size);
FOUNDATION_EXPORT void DDSetHostSlotCarPlayUI(NSUInteger slotIndex, BOOL carPlayUI);
FOUNDATION_EXPORT BOOL DDConvertHostSlotToCarPlayUI(NSUInteger slotIndex);
FOUNDATION_EXPORT void DDDismissHostMirror(void);
FOUNDATION_EXPORT void DDScheduleAppSideHandshake(void);
FOUNDATION_EXPORT void DDScheduleGeometryPushesForSlot(NSUInteger slotIndex);
FOUNDATION_EXPORT void DDAppendHostFrameMetrics(NSMutableDictionary *payload,
                                                const DDHostFrameMetrics *metrics);
FOUNDATION_EXPORT BOOL DDPostHostRequest(NSString * _Nullable bundleIdentifier,
                                         BOOL activate,
                                         const DDHostFrameMetrics *metrics);
FOUNDATION_EXPORT BOOL DDPostSplitHostRequest(NSString * _Nullable leftBundleIdentifier,
                                              NSString * _Nullable rightBundleIdentifier,
                                              NSString * _Nullable centerBundleIdentifier,
                                              NSInteger layout,
                                              BOOL activate,
                                              BOOL skipEvict,
                                              BOOL environmentOnly,
                                              const DDHostFrameMetrics *metrics);
FOUNDATION_EXPORT BOOL DDPostCarPlayUIStatus(uint64_t generation,
                                             NSString * _Nullable bundleIdentifier,
                                             BOOL ok,
                                             NSString * _Nullable reason);
FOUNDATION_EXPORT BOOL DDPostHostRefusedState(NSString * _Nullable reason);
FOUNDATION_EXPORT BOOL DDPostHostState(BOOL activated,
                                       NSString * _Nullable bundleIdentifier,
                                       NSString * _Nullable carPlayUIBundleIdentifier,
                                       NSArray * _Nullable carPlayUIMore,
                                       NSArray * _Nullable killedBundleIdentifiers,
                                       uint64_t carPlayUIGeneration,
                                       double rectX,
                                       double rectY,
                                       double rectWidth,
                                       double rectHeight);
FOUNDATION_EXPORT void DDReconstructionStart(void);

NS_ASSUME_NONNULL_END
