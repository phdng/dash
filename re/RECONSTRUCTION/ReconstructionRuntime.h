#pragma once

#import "DuoDashShared.h"

NS_ASSUME_NONNULL_BEGIN

typedef NS_ENUM(NSInteger, DDIntegerValidationStatus) {
    DDIntegerValidationMissing = 0,
    DDIntegerValidationNumber = 1,
    DDIntegerValidationString = 2,
    DDIntegerValidationError = 3,
};

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
