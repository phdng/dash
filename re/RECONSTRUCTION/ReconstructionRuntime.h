#pragma once

#import "DuoDashShared.h"

NS_ASSUME_NONNULL_BEGIN

FOUNDATION_EXPORT DDRole DDDetectRole(void);
FOUNDATION_EXPORT NSString *DDRoleName(DDRole role);
FOUNDATION_EXPORT NSDictionary *DDBuildKnownAppBridgeSnapshot(void);
FOUNDATION_EXPORT BOOL DDRepublishKnownAppBridgeSnapshot(NSError * _Nullable * _Nullable error);
FOUNDATION_EXPORT void DDReconstructionStart(void);

NS_ASSUME_NONNULL_END
