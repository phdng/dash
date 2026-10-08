// RECONSTRUCTION/DuoDashShared.h — buildable reconstruction surface
// Constants are backed by static evidence; runtime bodies remain explicitly APPROXIMATION
// unless a source record says otherwise.

#pragma once

#import <Foundation/Foundation.h>
#import <CoreFoundation/CoreFoundation.h>

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

// License verify codes (F-006/B-09): 0 OK,1 empty,2 format,3 no-pubkey,
// 4 kid,5 device-mismatch,6 expired,7 clock-skew,8 v!=1,10 product-mismatch (9 vắng).
