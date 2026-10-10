// RECONSTRUCTION/DuoDashShared.h — buildable reconstruction surface
// Constants are backed by static evidence; runtime bodies remain explicitly APPROXIMATION
// unless a source record says otherwise.

#pragma once

#import <Foundation/Foundation.h>
#import <CoreFoundation/CoreFoundation.h>

NS_ASSUME_NONNULL_BEGIN

// Prefs domain chính (F-004)
#define DD_SETTINGS_DOMAIN @"com.sensetechlab.duodash.settings"
// Cache publish bởi sub_74C8 (F-004)
#define DD_APPBRIDGE_CACHE @"/var/tmp/com.sensetechlab.appbridge.plist"
// License base hardcode (F-006; license_endpoint dead — F-016)
#define DD_LICENSE_BASE @"https://license.sensetechlab.com"
#define DD_CLIENT_VERSION @"1.1.5+b1d14e0"

// Notify names (F-005 + sweep session-002 §4; xem API_MAP.md)
#define DD_N_SETTINGS_CHANGED @"com.sensetechlab.settings.changed"
#define DD_N_APPBRIDGE_RESOLVED @"com.sensetechlab.appbridge.resolved"
#define DD_N_APPBRIDGE_LISTCHANGED @"com.sensetechlab.appbridge.listchanged"
#define DD_N_AUTOSTART_CHANGED @"com.sensetechlab.autostart.changed"
#define DD_N_FONTFLOOR_CHANGED @"com.sensetechlab.fontfloor.changed"
#define DD_N_KEYPANE_CHANGED @"com.sensetechlab.keypane.changed"
#define DD_N_APPBRIDGE_EXIT @"com.sensetechlab.appbridge.exit"
#define DD_N_CPROLEUP @"com.sensetechlab.appbridge.cproleup"
#define DD_N_CPCONNECT @"com.sensetechlab.appbridge.cpconnect"
#define DD_N_CPDISCONNECT @"com.sensetechlab.appbridge.cpdisconnect"
#define DD_N_KEYINPUT_SEED @"com.sensetechlab.keyinput.seed"
#define DD_N_LANGUAGE_CHANGED @"com.sensetechlab.language.changed"

// File toggles: fileExists == feature DISABLED (mẫu duodash_cpui_noelemguard — F-011đ)
// Persistent (F-005)
#define DD_LICENSE_BLOB @"/var/mobile/Library/DuoDash/license.blob"
#define DD_REPORTS_OUTGOING @"/var/mobile/Library/DuoDash/reports/outgoing"
// IPC cache (volatile)
#define DD_KEYINPUT_SEED @"/var/tmp/duodash_keyinput_seed.plist"
#define DD_KEYINPUT_OUT @"/var/tmp/duodash_keyinput_out.plist"
#define DD_KEYINPUT_KB @"/var/tmp/duodash_keyinput_kb.plist"

// Init roles (F-012): values are the observed AC5FC role codes.
typedef NS_ENUM(NSInteger, DDRole) {
    DDRoleSpringBoard = 1,
    DDRolePreferences = 2,
    DDRoleCarPlayApp = 3,
    DDRoleMediaServerd = 4,
    DDRoleUIApp = 5,
    DDRoleKbd = 6,
};
FOUNDATION_EXPORT NSString * _Nullable DDRoleName(DDRole role);
FOUNDATION_EXPORT BOOL DDRoleCStringHasSuffix(const char * _Nullable value,
                                             const char * _Nullable suffix);
FOUNDATION_EXPORT DDRole DDRoleForExecutablePathCString(const char * _Nullable path);
FOUNDATION_EXPORT NSInteger DDAZCarPlaySpoofedResult(BOOL forceDisconnected,
                                                    NSInteger originalResult);
FOUNDATION_EXPORT BOOL DDKeepAwakeNavigationBundle(NSString * _Nullable bundleIdentifier);
FOUNDATION_EXPORT BOOL DDKeepAwakeShouldCountSlowBlank(double elapsedMilliseconds,
                                                       uint32_t currentCount);
FOUNDATION_EXPORT NSUInteger DDFontFloorOverrideValue(NSString * _Nullable value);
FOUNDATION_EXPORT double DDReapDelayOverrideValue(NSString * _Nullable value);
FOUNDATION_EXPORT double DDHoldSecondsOverrideValue(NSString * _Nullable value);
FOUNDATION_EXPORT double DDDisconnectCloseSecondsOverrideValue(NSString * _Nullable value);
FOUNDATION_EXPORT double DDSplashSecondsOverrideValue(NSString * _Nullable value);
FOUNDATION_EXPORT double DDDashSettleSecondsOverrideValue(NSString * _Nullable value);
FOUNDATION_EXPORT double DDDashLaunchSecondsOverrideValue(NSString * _Nullable value);
FOUNDATION_EXPORT double DDKeypaneHideGapOverrideValue(NSString * _Nullable value);
FOUNDATION_EXPORT BOOL DDSimulatedSpeedOverrideValue(NSString * _Nullable value,
                                                      uint8_t * _Nullable outValue);
FOUNDATION_EXPORT BOOL DDForceIOOverrideEnabled(NSString * _Nullable value);
FOUNDATION_EXPORT double DDMatAlphaOverrideValue(NSString * _Nullable value);
FOUNDATION_EXPORT NSInteger DDOrientationOverrideValue(NSString * _Nullable value);
FOUNDATION_EXPORT double DDRenderScaleOverrideValue(NSString * _Nullable value);
FOUNDATION_EXPORT float DDLivePresentAlphaOverrideValue(NSString * _Nullable value);
FOUNDATION_EXPORT NSString *DDLivePresentTargetOverrideValue(NSString * _Nullable value);
FOUNDATION_EXPORT BOOL DDLivePresentAnimationAlphaTokenValue(NSString * _Nullable value,
                                                              float * _Nullable outValue);
FOUNDATION_EXPORT BOOL DDLivePresentAnimationUsesLinearEasing(NSString * _Nullable value);
FOUNDATION_EXPORT BOOL DDCanvasPortraitOverrideEnabled(NSString * _Nullable value);
FOUNDATION_EXPORT NSString *DDGPSBundleOverrideValue(NSString * _Nullable value);
FOUNDATION_EXPORT NSInteger DDRotateQuarterTurnDegrees(NSString * _Nullable value);
FOUNDATION_EXPORT BOOL DDContentInsetOverrideValue(NSString * _Nullable value,
                                                    double width,
                                                    double height,
                                                    double * _Nullable outLeft,
                                                    double * _Nullable outTop,
                                                    double * _Nullable outRight,
                                                    double * _Nullable outBottom);
FOUNDATION_EXPORT double DDPanePaddingOverrideValue(NSString * _Nullable value);
FOUNDATION_EXPORT double DDPaneCornerRadiusForNoRoundMarker(BOOL markerPresent);
// Call only when a layout override value is present; absent values use 73E8() fallback.
FOUNDATION_EXPORT NSInteger DDHostLayoutProvidedOverrideValue(NSString * _Nonnull value);
FOUNDATION_EXPORT BOOL DDPaneFractionsOverrideValue(NSString * _Nullable value,
                                                    NSInteger * _Nullable outFractionA,
                                                    NSInteger * _Nullable outFractionB);

// Compile-safe recovery-routing integration seam (session-176+).
// This consumes ReconstructionRuntime evidence contracts without executing
// private selectors/UIKit/global recovery side effects.
typedef NS_OPTIONS(NSUInteger, DDRecoveryRoutingCapability) {
    DDRecoveryRoutingCapabilityLayoutInitialEnumeration = 1ull << 0,
    DDRecoveryRoutingCapabilityLayoutSubsequentEnumeration = 1ull << 1,
    DDRecoveryRoutingCapabilityLayoutSetRoot = 1ull << 2,
    DDRecoveryRoutingCapabilityLayoutPostCommit = 1ull << 3,
    DDRecoveryRoutingCapabilityReapplyMaximize = 1ull << 4,
    DDRecoveryRoutingCapabilityPresentOverlayCleanup = 1ull << 5,
};
FOUNDATION_EXPORT void DDRecoveryRoutingStart(void);
FOUNDATION_EXPORT NSUInteger DDRecoveryRoutingCapabilities(void);

typedef NS_ENUM(NSInteger, DDPostPresentHostFlowExceptionSite) {
    DDPostPresentHostFlowExceptionSiteNone = 0,
    DDPostPresentHostFlowExceptionSiteSharedAcquisition = 1,
    DDPostPresentHostFlowExceptionSiteTeardown = 2,
    DDPostPresentHostFlowExceptionSiteBuildInHost = 3,
};

typedef struct {
    BOOL adapterEnabled;
    BOOL shouldSwallowExpectedException;
    BOOL shouldContinueAfterHostBlock;
    BOOL nonmatchingTypeWouldResumeUnwind;
    BOOL sharedControllerDefinitelyAcquiredBeforeSite;
    BOOL teardownDefinitelyCompletedBeforeSite;
    BOOL teardownCouldHaveAppliedBeforeException;
    BOOL buildInHostCouldHaveAppliedBeforeException;
    BOOL remainingHostBlockDefinitelySkipped;
    BOOL sharedControllerNormalReleaseDefinitelySkipped;
    BOOL retainedHostDefinitelyReleasedOnContinuation;
} DDPostPresentHostFlowDecision;

// Pure 218D8:307-313 route predicate; callers supply the observed gate states.
FOUNDATION_EXPORT BOOL DDHostRequiresFullHost(BOOL deactivateDismissPresent,
                                               BOOL active,
                                               BOOL splitHosting,
                                               BOOL visible,
                                               BOOL geometryMismatch,
                                               BOOL dirty,
                                               BOOL canPresent);
// Pure 218D8:315-327 no-display refusal predicate, without posting host.state.
FOUNDATION_EXPORT BOOL DDHostShouldRefuseNoDisplay(BOOL usableBoundsEmpty,
                                                   BOOL prepareShellSucceeded);
FOUNDATION_EXPORT BOOL DDHostHasDegenerateContent(double width, double height);
FOUNDATION_EXPORT BOOL DDHostDelayedGenerationIsCurrent(uint64_t capturedGeneration,
                                                       uint64_t currentGeneration);
FOUNDATION_EXPORT BOOL DDHostSwitchSlotCountIsValid(NSInteger hostedSlotCount);
FOUNDATION_EXPORT BOOL DDHostSwitchModeFlagsAllow(NSUInteger hostMode,
                                                 NSUInteger hostPhase,
                                                 NSUInteger stateFlags);
FOUNDATION_EXPORT BOOL DDHostSwitchSlotCountsMatch(NSInteger hostedSlotCount,
                                                  NSInteger runtimeSlotCount,
                                                  NSInteger layoutSlotCount,
                                                  NSInteger preparedSlotCapacity);
FOUNDATION_EXPORT BOOL DDHostSwitchInteractionStateAllows(BOOL active,
                                                          BOOL splitHosting,
                                                          BOOL visible,
                                                          BOOL swapInFlight,
                                                          NSInteger maximizedPosition,
                                                          BOOL maximizeInFlight);
FOUNDATION_EXPORT BOOL DDHostSwitchConsistencyAllows(uint64_t pendingGeneration,
                                                     NSInteger requestedGeometryVersion,
                                                     NSInteger appliedGeometryVersion,
                                                     NSInteger activeLayout,
                                                     NSInteger preferredLayout);
FOUNDATION_EXPORT BOOL DDHostSwitchContinuationStateAllows(BOOL active,
                                                           BOOL splitHosting,
                                                           BOOL visible,
                                                           BOOL carPlayConnected);
FOUNDATION_EXPORT BOOL DDHostSwitchShellBoundsAllow(BOOL shellBoundsMismatch);
FOUNDATION_EXPORT BOOL DDHostSwitchNeedsDelayedContinuation(NSUInteger pendingBidCount);
FOUNDATION_EXPORT NSString * _Nonnull DDHostSplitBidOrEmpty(NSString * _Nullable bid);
// 217EC:26-37: construct the two-element ordered BID array without private host calls.
FOUNDATION_EXPORT NSArray<NSString *> * _Nonnull DDHostSplitBids(NSString * _Nullable leftBid,
                                                                 NSString * _Nullable rightBid);
FOUNDATION_EXPORT BOOL DDHostSwitchHostedSlotSizeValid(double hostedSlotSize);
// 208F4:207-237 validates every hosted slot, not only slot zero.
// All measurements are caller-supplied; no private slot state is accessed.
FOUNDATION_EXPORT BOOL DDHostSwitchAllSlotSizesValid(NSArray<NSNumber *> * _Nullable sizes,
                                                    NSInteger expectedSlotCount);
// 208F4:207-237: compare caller-normalized BIDs in slot order only.
// Does not implement private 3DD4C normalization or inspect slot geometry.
FOUNDATION_EXPORT BOOL DDHostSwitchBidsMatch(NSArray<NSString *> * _Nullable requestedBids,
                                             NSArray<NSString *> * _Nullable hostedBids,
                                             NSInteger expectedSlotCount);

// Caller-supplied snapshot for the evidenced 208F4 early switch guards.
// This does not inspect private host state or authorize a complete UI switch.
typedef struct {
    BOOL active;
    BOOL splitHosting;
    BOOL visible;
    BOOL swapInFlight;
    NSInteger maximizedPosition;
    BOOL maximizeInFlight;
    uint64_t pendingGeneration;
    NSInteger requestedGeometryVersion;
    NSInteger appliedGeometryVersion;
    NSInteger activeLayout;
    NSInteger preferredLayout;
    NSInteger hostedSlotCount;
    NSInteger runtimeSlotCount;
    NSInteger layoutSlotCount;
    NSInteger preparedSlotCapacity;
    NSUInteger hostMode;
    NSUInteger hostPhase;
    NSUInteger stateFlags;
} DDHostSwitchEarlyGuardSnapshot;
// Diagnostic-only bitmask of failed early gates; zero means these gates pass,
// not that a complete switch is authorized.
typedef NS_OPTIONS(NSUInteger, DDHostSwitchEarlyGuardFailure) {
    DDHostSwitchEarlyGuardFailureInteraction = 1u << 0,
    DDHostSwitchEarlyGuardFailureConsistency = 1u << 1,
    DDHostSwitchEarlyGuardFailureSlotCounts = 1u << 2,
    DDHostSwitchEarlyGuardFailureModeFlags = 1u << 3,
};
FOUNDATION_EXPORT NSUInteger DDHostSwitchEarlyGuardFailures(DDHostSwitchEarlyGuardSnapshot snapshot);
FOUNDATION_EXPORT BOOL DDHostSwitchEarlyGuardsAllow(DDHostSwitchEarlyGuardSnapshot snapshot);
// Additional 208F4:207-242 gates checked only after the early predicates.
// Inputs are observations from the caller; BID identity comparison stays external.
typedef NS_OPTIONS(NSUInteger, DDHostSwitchPostEarlyFailure) {
    DDHostSwitchPostEarlyFailureHostedSlotSize = 1u << 0,
    DDHostSwitchPostEarlyFailureShellBounds = 1u << 1,
};
FOUNDATION_EXPORT NSUInteger DDHostSwitchPostEarlyFailures(double hostedSlotSize,
                                                           BOOL shellBoundsMismatch);
// Result for a caller-supplied, already-normalized 208F4 switch preflight.
// Passing this preflight is necessary, never sufficient to mutate CarPlay UI.
typedef struct {
    NSUInteger earlyFailures;
    BOOL bidsMatch;
    NSUInteger postEarlyFailures;
    BOOL canProceedToPrivateSwitchChecks;
} DDHostSwitchPreflightResult;
FOUNDATION_EXPORT DDHostSwitchPreflightResult DDHostSwitchPreflight(
    DDHostSwitchEarlyGuardSnapshot snapshot,
    NSArray<NSString *> * _Nullable requestedBids,
    NSArray<NSString *> * _Nullable hostedBids,
    double hostedSlotSize,
    BOOL shellBoundsMismatch);
// Optional, side-effect-free Objective-C smoke test of preflight semantics.
// Never invoked automatically from tweak startup.
FOUNDATION_EXPORT BOOL DDHostSwitchPreflightSelfTest(void);
FOUNDATION_EXPORT void DDHostFlowAdapterStart(void);
FOUNDATION_EXPORT BOOL DDHostFlowAdapterReady(void);
FOUNDATION_EXPORT DDPostPresentHostFlowDecision DDPostPresentHostFlowDecisionForSite(DDPostPresentHostFlowExceptionSite site);

typedef struct {
    BOOL adapterEnabled;
    BOOL hostPresent;
    BOOL pickerAllowed;
    BOOL pickerSuppressedByNoPickerFile;
    BOOL noWake;
    BOOL noSpin;
    BOOL paneSized;
    NSUInteger initialPickerBudget;
} DDPickerAdmissionDecision;

FOUNDATION_EXPORT void DDPickerAdapterStart(void);
FOUNDATION_EXPORT BOOL DDPickerAdapterReady(void);
FOUNDATION_EXPORT DDPickerAdmissionDecision DDResolvePickerAdmission(BOOL hostPresent);

FOUNDATION_EXPORT void DDCrashReportingAdapterStart(void);
FOUNDATION_EXPORT BOOL DDCrashReportingAdapterReady(void);
FOUNDATION_EXPORT BOOL DDCrashReportingMayCollect(void);
FOUNDATION_EXPORT BOOL DDCrashReportingDryRunEnabled(void);
FOUNDATION_EXPORT NSString * _Nullable DDCrashReportingEndpoint(void);
FOUNDATION_EXPORT NSString * _Nullable DDCrashReportingToken(void);
FOUNDATION_EXPORT BOOL DDCrashReportingShouldPrepareUpload(void);
FOUNDATION_EXPORT NSString * _Nullable DDCrashReportingReportsURLString(void);
FOUNDATION_EXPORT NSString * _Nullable DDCrashReportingAuthorizationValue(void);
FOUNDATION_EXPORT NSUInteger DDCrashReportingPruneOutgoingQueue(void);
FOUNDATION_EXPORT NSString * _Nullable DDCrashReportingRecoveryStatusSuggestion(void);

FOUNDATION_EXPORT void DDLocaleFlowStart(void);
FOUNDATION_EXPORT BOOL DDLocaleFlowReady(void);
FOUNDATION_EXPORT BOOL DDLocaleIsSupportedLanguage(NSString * _Nullable language);
FOUNDATION_EXPORT NSArray<NSString *> *DDLocaleSupportedLanguages(void);
FOUNDATION_EXPORT NSString *DDLocaleLanguageDisplayName(NSString * _Nullable language);
FOUNDATION_EXPORT BOOL DDLocaleSetLanguage(NSString * _Nullable language);
FOUNDATION_EXPORT NSString *DDLocaleResolveLanguage(void);
FOUNDATION_EXPORT void DDLocaleInvalidateCaches(void);

FOUNDATION_EXPORT BOOL DDClearAppBridgePanesIfRequested(void);
FOUNDATION_EXPORT NSUInteger DDResolveBridgedFontFloor(void);
FOUNDATION_EXPORT BOOL DDResolveKeyPaneEnabled(void);
FOUNDATION_EXPORT BOOL DDBooleanPreferenceDefaultTrue(CFTypeRef _Nullable value);
FOUNDATION_EXPORT NSString * _Nullable DDCopyNonemptyStringPreferenceAnyHost(NSString * _Nullable key);
FOUNDATION_EXPORT NSArray *DDCopyPickerArrayPreferenceAnyHost(NSString * _Nullable key);
FOUNDATION_EXPORT void DDPersistPickerArrayPreferenceAnyHost(NSString * _Nullable key,
                                                             NSArray *values);
FOUNDATION_EXPORT void DDPersistPickerScalarPreferenceAnyHost(NSString *key,
                                                              NSString * _Nullable selectedValue);
FOUNDATION_EXPORT BOOL DDAppBridgeIdentifierIsExcluded(id _Nullable identifier);
FOUNDATION_EXPORT NSDictionary<NSString *, id> *DDCopyAppBridgeConfigPreferences(void);
FOUNDATION_EXPORT NSArray<NSString *> *DDNormalizeCarPlayUIAdditional(id _Nullable candidate, NSString * _Nullable mainBundleIdentifier);
FOUNDATION_EXPORT NSInteger DDNormalizeAppBridgeIntegerSetting(NSDictionary *source,
                                                              NSString *key,
                                                              NSInteger minimum,
                                                              NSInteger maximum,
                                                              NSInteger fallback,
                                                              NSString *fixName,
                                                              NSMutableDictionary *writes,
                                                              NSMutableArray *fixes);
FOUNDATION_EXPORT NSDictionary<NSString *, NSNumber *> *DDNormalizeAppBridgeNumericConfig(NSDictionary *source,
                                                                                         NSMutableDictionary *writes,
                                                                                         NSMutableArray *fixes);
FOUNDATION_EXPORT NSDictionary<NSString *, id> *DDNormalizeAppBridgeConfig(NSDictionary *source);
FOUNDATION_EXPORT BOOL DDRepublishAppBridgeResolvedSnapshot(void);
FOUNDATION_EXPORT BOOL DDRepairAppBridgeConfigIfNeeded(void);
FOUNDATION_EXPORT BOOL DDRepairAndRepublishAppBridge(void);
FOUNDATION_EXPORT BOOL DDRunDefaultsBootstrapIfNeeded(void);
FOUNDATION_EXPORT BOOL DDMigrateTrueDashFileNamed(NSString *name);
FOUNDATION_EXPORT NSArray<NSString *> * _Nullable DDMigrationUniqueNonemptyStrings(id _Nullable candidate);
FOUNDATION_EXPORT NSDictionary<NSString *, NSString *> * _Nullable DDMigrationStringDictionary(id _Nullable candidate);
FOUNDATION_EXPORT NSString *DDMigrationJoinOrNone(NSArray<NSString *> *values);
FOUNDATION_EXPORT NSDictionary<NSString *, NSString *> *DDMigrationRenameMap(void);
FOUNDATION_EXPORT NSSet<NSString *> *DDMigrationDeniedPreferenceKeys(void);
FOUNDATION_EXPORT NSArray<NSString *> *DDMigrationSourceCleanupKeys(void);
FOUNDATION_EXPORT NSString * _Nullable DDMigrationDestinationKeyForSourceKey(id _Nullable sourceKey);
FOUNDATION_EXPORT BOOL DDMigratePreferenceDomain(NSString *sourceDomain,
                                                NSString *destinationDomain,
                                                NSUInteger * _Nonnull counters);
FOUNDATION_EXPORT BOOL DDMigrateTrueDashPreferenceDomains(NSUInteger * _Nonnull settingsCounters,
                                                          NSUInteger * _Nonnull rescuerCounters);
FOUNDATION_EXPORT BOOL DDPrepareTrueDashImportIfNeeded(void);
FOUNDATION_EXPORT BOOL DDFinalizeTrueDashImportRecord(const NSUInteger * _Nonnull settingsCounters,
                                                      BOOL settingsMigrated,
                                                      const NSUInteger * _Nonnull rescuerCounters,
                                                      BOOL rescuerMigrated,
                                                      NSString *licenceStatus,
                                                      NSString *blobStatus,
                                                      NSString *keyStatus,
                                                      NSString *oldKeyStatus,
                                                      NSString *undoStatus);
FOUNDATION_EXPORT long long DDMigrationIssuedAtIfValid(NSInteger validationStatus,
                                                       NSDictionary * _Nullable payload);
FOUNDATION_EXPORT BOOL DDResolveVoiceCommandPreferences(NSString * _Nullable * _Nullable selectedOut);
FOUNDATION_EXPORT void DDReloadVoiceCommandPreferenceCache(void);
FOUNDATION_EXPORT BOOL DDVoiceCommandPreferenceCache(NSString * _Nullable * _Nullable selectedOut);
FOUNDATION_EXPORT BOOL DDSiriProbePressEligible(long long buttonIdentifier);
FOUNDATION_EXPORT BOOL DDSiriProbeShouldSwallow(long long buttonIdentifier);
FOUNDATION_EXPORT int DDPostVoiceCommandPress(void);
FOUNDATION_EXPORT BOOL DDKeyinputFieldMayRelay(id _Nullable field);
FOUNDATION_EXPORT NSString * _Nullable DDKeyinputResolvedTemporaryKnobPath(NSString * _Nullable name);
FOUNDATION_EXPORT BOOL DDKeyinputKnobPresentCached(NSString *name,
                                                   int *cachedState,
                                                   double *cachedTimestamp);
FOUNDATION_EXPORT BOOL DDKeyinputForceIOEnabled(void);
FOUNDATION_EXPORT BOOL DDKeyinputKnobPresentNow(NSString *name);
FOUNDATION_EXPORT double DDKeyinputParseWidthOverride(NSString * _Nullable rawValue);
FOUNDATION_EXPORT double DDAppBridgeDashSettleSeconds(void);
FOUNDATION_EXPORT double DDAppBridgeMaterialAlpha(void);
FOUNDATION_EXPORT int DDReadAirPlayMediaServerPendingPID(void);
FOUNDATION_EXPORT double DDNavProviderTimestamp(NSDictionary * _Nullable payload);
FOUNDATION_EXPORT BOOL DDNavProviderPayloadMatchesProvider(id _Nullable payload,
                                                          id _Nullable provider);
FOUNDATION_EXPORT BOOL DDNavProviderIsLegacyTrueDashNotification(CFStringRef _Nullable name);
FOUNDATION_EXPORT NSComparisonResult DDNavProviderCompareLastSeenDescending(id _Nullable left,
                                                                          id _Nullable right);
FOUNDATION_EXPORT NSInteger DDCameraRelaySourceCode(NSString * _Nullable source);
FOUNDATION_EXPORT BOOL DDDeepSleepEnabledCurrentHost(void);
FOUNDATION_EXPORT long DDLongValueForCFDictionaryKey(CFDictionaryRef dictionary,
                                                     const void *key);
FOUNDATION_EXPORT BOOL DDBooleanValueForCFDictionaryKey(CFDictionaryRef dictionary,
                                                        const void *key);
FOUNDATION_EXPORT NSInteger DDAppBridgeBaseClassification(id _Nullable identifier,
                                                          id _Nullable applicationType);
FOUNDATION_EXPORT NSDictionary<NSString *, NSString *> *DDCopyAppBridgeSectionOverrides(void);
FOUNDATION_EXPORT NSString * _Nullable DDCopyStringPreferenceAnyHostForCString(const char *key);
FOUNDATION_EXPORT NSString *DDCrashSHA256Hex(NSData *data, NSUInteger prefixLength);
FOUNDATION_EXPORT NSComparisonResult DDCrashStringLengthDescendingComparator(NSString *left,
                                                                            NSString *right);
FOUNDATION_EXPORT NSComparisonResult DDCrashDictionaryDateDescendingComparator(NSDictionary *left,
                                                                               NSDictionary *right);
FOUNDATION_EXPORT NSString * _Nullable DDCrashNormalizeIdentifier(NSString * _Nullable value);
FOUNDATION_EXPORT BOOL DDCrashShouldIncludeImageName(NSString * _Nullable name);
FOUNDATION_EXPORT NSString *DDCrashJailbreakFamilyForPrefixCString(const char * _Nullable prefix);
FOUNDATION_EXPORT NSString * _Nullable DDCrashJailbreakPrefixString(const char * _Nullable prefix);
FOUNDATION_EXPORT NSString *DDCrashArchitectureNameForCPUSubtype(uint32_t cpuSubtype);
FOUNDATION_EXPORT NSString *DDCrashMachOUUIDHex(const uint8_t * _Nonnull uuidBytes);
FOUNDATION_EXPORT BOOL DDCrashMachOIsFatMagic(uint32_t magic);
FOUNDATION_EXPORT uint32_t DDCrashMachOFatValueHostOrder(uint32_t magic, uint32_t value);
FOUNDATION_EXPORT BOOL DDCrashMachOIs64BitMagic(uint32_t magic);
FOUNDATION_EXPORT BOOL DDCrashMachOLoadCommandIsUUID(uint32_t command, uint32_t commandSize);
FOUNDATION_EXPORT BOOL DDCrashMachOLoadCommandFits(uint32_t commandSize,
                                                    uint64_t cumulativeSize,
                                                    uint64_t remainingSize);
FOUNDATION_EXPORT BOOL DDCrashMachOFatHeaderFits(uint64_t fileLength, uint32_t architectureCount);
FOUNDATION_EXPORT BOOL DDCrashMachOSliceOffsetFits(uint64_t fileLength, uint32_t sliceOffset);
FOUNDATION_EXPORT BOOL DDCrashMachOHasMinimumHeaderBytes(uint64_t fileLength);
FOUNDATION_EXPORT BOOL DDRespringReenablePreferenceEnabled(CFTypeRef _Nullable value);
FOUNDATION_EXPORT double DDRespringCooldownSecondsForJailbreakPrefixCString(const char * _Nullable prefix);
FOUNDATION_EXPORT BOOL DDRespringCooldownAllowsElapsed(double elapsedSeconds,
                                                       const char * _Nullable prefix);
FOUNDATION_EXPORT BOOL DDRespringCarsleepGateAllows(int notifyRegisterResult,
                                                    uint64_t sleepingState);
FOUNDATION_EXPORT BOOL DDRespringUsesDirectExecutionForWorkerCount(int workerCount);
FOUNDATION_EXPORT BOOL DDRespringPlannedMarkerFresh(double elapsedSeconds);
FOUNDATION_EXPORT BOOL DDRespringUsesAlternatePlannedMarkerBasePath(NSString * _Nullable basePath);
FOUNDATION_EXPORT BOOL DDDataRouterIsTrueDashNotification(CFStringRef _Nullable name);
FOUNDATION_EXPORT NSInteger DDDataRouterSourceCode(NSString * _Nullable source);
FOUNDATION_EXPORT BOOL DDDataRouterProviderPayloadMatches(id _Nullable payload,
                                                         NSString * _Nullable provider);
FOUNDATION_EXPORT NSData * _Nullable DDLicenseDecodeBase64URL(NSString * _Nullable value);
FOUNDATION_EXPORT NSData * _Nullable DDLicenseDecodeHex(NSString * _Nullable value);
FOUNDATION_EXPORT NSString *DDLicenseStatusTextForVerification(NSInteger verificationStatus,
                                                              BOOL refusalMatches);
FOUNDATION_EXPORT BOOL DDLicenseIsPrintableASCIIString(id _Nullable value);
FOUNDATION_EXPORT NSInteger DDLicenseKeyPrefixIndex(id _Nullable value);
FOUNDATION_EXPORT NSString *DDLicenseStatusTextForAction(NSUInteger action,
                                                        NSInteger verificationStatus,
                                                        BOOL refusalMatches);
FOUNDATION_EXPORT NSString *DDLicenseVerdictText(NSUInteger verificationStatus,
                                                BOOL licenseNoncePresent,
                                                BOOL refusalMatches,
                                                BOOL deviceHashPresent);
FOUNDATION_EXPORT BOOL DDLicenseStatusRequiresIntervention(NSString * _Nullable status);
FOUNDATION_EXPORT NSInteger DDAirPlayIntegerPreference(NSString *key);
FOUNDATION_EXPORT BOOL DDPerfTweakEnabledFromPreferenceValue(CFTypeRef _Nullable value);
FOUNDATION_EXPORT NSInteger DDAirPlayTargetFPSForPerfEnabled(BOOL enabled);
FOUNDATION_EXPORT BOOL DDAirPlayFPSPreferencesMatchTarget(NSInteger maxFPS,
                                                         NSInteger encoderFPSFixed,
                                                         BOOL enabled);
FOUNDATION_EXPORT BOOL DDVersionTupleAtLeast(NSInteger installedMajor,
                                            NSInteger installedMinor,
                                            NSInteger installedPatch,
                                            NSInteger requiredMajor,
                                            NSInteger requiredMinor,
                                            NSInteger requiredPatch);
FOUNDATION_EXPORT NSString * _Nullable DDVersionDeviceSanitizeMachineModel(NSString * _Nullable value);
FOUNDATION_EXPORT NSString *DDVersionDeviceFormatClientVersion(NSString * _Nullable value);
FOUNDATION_EXPORT NSString *DDVersionDeviceFormatOSVersion(NSInteger major,
                                                          NSInteger minor,
                                                          NSInteger patch);

NS_ASSUME_NONNULL_END

// License verify codes (F-006/B-09): 0 OK,1 empty,2 format,3 no-pubkey,
// 4 kid,5 device-mismatch,6 expired,7 clock-skew,8 v!=1,10 product-mismatch (9 vắng).
