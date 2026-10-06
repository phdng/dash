// RECONSTRUCTION/ReconstructionRuntime.m — buildable static-evidence runtime (session-081)
// This file intentionally implements only behavior whose data-flow can be represented without
// unresolved private classes/functions. Unknown filtering/computation remains documented in the
// synthesis files rather than being silently guessed here.

#import "ReconstructionRuntime.h"

#import <dispatch/dispatch.h>
#import <mach-o/dyld.h>
#import <notify.h>
#import <objc/message.h>
#import <objc/runtime.h>
#include <fcntl.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

// libproc is linked explicitly by the Theos target. Keeping the declaration local avoids
// depending on private headers while matching the public libproc symbol used by sub_7764C.
extern int proc_pidpath(int pid, void *buffer, uint32_t buffersize);

_Static_assert(sizeof(DDHostFrameMetrics) == 104,
               "DDHostFrameMetrics must preserve the 8F34 104-byte snapshot layout");

static CFStringRef const kDDSettingsDomain = CFSTR("com.sensetechlab.duodash.settings");
static NSString * const kDDClearPanes = @"/var/tmp/duodash_ab_clearpanes";
static NSString * const kDDClearPanesDone = @"/var/tmp/duodash_ab_clearpanes.done";
static NSInteger gDDBridgedFontFloor = 0;
static BOOL gDDKeyPaneEnabled = YES;

// UIApp-side cached state reconstructed from 4407C/443FC/444C4/422D0.
static uint32_t gDDUIAppStateGeneration = 0;
static NSString *gDDUIAppStateSignature = nil;
static BOOL gDDUIAppBridging = NO;
static BOOL gDDUIAppSplit = NO;
static double gDDUIAppDisplayWidth = 0.0;
static double gDDUIAppDisplayHeight = 0.0;
static NSInteger gDDUIAppOrientation = 1;
static NSInteger gDDUIAppFontFloor = 0;
static BOOL gDDUIAppKeyPaneEnabled = YES;
static BOOL gDDUIAppFontFloorActive = NO;

// SpringBoard host-slot mirror. This models the raw DDz2 globals used by 3F224/3B738/3D4FC
// without hard-linking the private scene-host implementation. Future host builders populate it
// only after their size/orientation decisions are resolved.
static BOOL gDDHostMirrorActive = NO;
static BOOL gDDHostMirrorSplit = NO;
static NSUInteger gDDHostMirrorSlotCount = 0;
static uint64_t gDDHostMirrorGeneration = 0;
static NSInteger gDDHostMirrorOrientation = 1;
static NSString *gDDHostMirrorBids[3] = { nil, nil, nil };
static BOOL gDDHostMirrorCarPlayUI[3] = { NO, NO, NO };
static DDHostSlotSize gDDHostMirrorSizes[3] = { {0.0, 0.0}, {0.0, 0.0}, {0.0, 0.0} };
static NSInteger gDDHostLandscapeOverrideOrientation = 0;
static BOOL gDDHostLandscapeSwap = NO;
static BOOL gDDHostLandscapeCSwap = NO;
static double gDDHostLandscapeRotationDegrees = 0.0;

static NSString * const kDDLandscapeOverridePath = @"/var/tmp/duodash_ab_lscape";
static NSString * const kDDLandscapeTrippedPath = @"/var/tmp/duodash_ab_lscape.tripped";
static const char * const kDDLandscapeInflightPath = "/var/tmp/duodash_ab_lscape.inflight";
static const char * const kDDRespringPlannedPath = "/var/mobile/Library/DuoDash/respring_planned";

// off_154160: five NSConstantDoubleNumber values recovered directly from __objc_arraydata.
static const double kDDHostRetryDelays[] = { 0.0, 0.4, 0.9, 1.8, 3.5 };
static NSInteger gDDSceneGeometryEnabledCache = -1;
static NSInteger gDDSceneSettingsOrientationIvarCache = -1;
static uint64_t gDDGeometryStateGeneration = 0;
static BOOL gDDPaneOrientationDisabled = NO;

// Aux-scene mirror for the evidence-safe state committed by 3C368 only after the private
// application lookup succeeds. It deliberately does not represent SBAppViewController/view state.
static NSString *gDDAuxBundleIdentifier = nil;
static DDHostSlotSize gDDAuxNativeSize = {0.0, 0.0};
static NSInteger gDDAuxOrientation = 0;
static uint64_t gDDAuxGeneration = 0;
static BOOL gDDAuxSwapEnabled = YES;
static BOOL gDDAuxNoAuxSID = NO;
static BOOL gDDAuxNoApplyDiff = NO;
static BOOL gDDAuxSettingsInFlight = NO;
static BOOL gDDAuxSettingsApplied = NO;
static NSInteger gDDAuxSettingsAttemptCount = 0;
static NSInteger gDDAuxSettingsBudget = 0;
static BOOL gDDAuxSettingsExecutorReentrant = NO;
static uint64_t gDDAuxSettingsExecutingGeneration = 0;
static const double kDDAuxCreateKickRetryDelays[] = { 0.1, 0.5, 1.5 };

static id _Nullable DDCopyAppPreference(NSString *key) {
    CFTypeRef value = CFPreferencesCopyAppValue((__bridge CFStringRef)key, kDDSettingsDomain);
    return CFBridgingRelease(value);
}

static NSString *DDStringPreference(NSString *key) {
    id value = DDCopyAppPreference(key);
    return [value isKindOfClass:[NSString class]] ? value : @"";
}

static NSNumber *DDNumberPreference(NSString *key, NSInteger fallback) {
    id value = DDCopyAppPreference(key);
    return [value respondsToSelector:@selector(integerValue)] ? @([value integerValue]) : @(fallback);
}

static BOOL DDBoolPreference(NSString *key, BOOL fallback, BOOL *existsOut) {
    id value = DDCopyAppPreference(key);
    BOOL exists = (value != nil);
    if (existsOut) *existsOut = exists;
    return exists && [value respondsToSelector:@selector(boolValue)] ? [value boolValue] : fallback;
}

static NSArray<NSString *> *DDNormalizeCarPlayMore(id candidate, NSString *mainBundleIdentifier) {
    if (![candidate isKindOfClass:[NSArray class]]) return @[];

    NSMutableArray<NSString *> *result = [NSMutableArray array];
    for (id item in (NSArray *)candidate) {
        if (![item isKindOfClass:[NSString class]]) continue;
        NSString *bundleIdentifier = item;
        if (bundleIdentifier.length == 0) continue;
        if (mainBundleIdentifier.length && [bundleIdentifier isEqualToString:mainBundleIdentifier]) continue;
        if ([result containsObject:bundleIdentifier]) continue;
        [result addObject:[bundleIdentifier copy]];
    }
    return result;
}

static BOOL DDRawAutostartPreference(void) {
    // sub_85CDC: missing -> true; otherwise only a real CFBoolean can be true.
    // NSNumber/string values are not coerced here (the original deliberately differs
    // from CFPreferencesGetAppBooleanValue-style readers).
    id value = DDCopyAppPreference(@"appbridge_autostart");
    if (!value) return YES;
    CFTypeRef cfValue = (__bridge CFTypeRef)value;
    if (CFGetTypeID(cfValue) != CFBooleanGetTypeID()) return NO;
    return CFBooleanGetValue((CFBooleanRef)cfValue);
}

NSString * _Nullable DDCachedStringValue(NSString *key) {
    // sub_7044: read resolved plist and return only a non-empty NSString.
    NSDictionary *resolved = [NSDictionary dictionaryWithContentsOfFile:DD_APPBRIDGE_CACHE];
    id value = resolved[key];
    if (![value isKindOfClass:[NSString class]]) return nil;
    return [value length] ? value : nil;
}

NSArray<NSString *> *DDCachedCarPlayUIMore(void) {
    // sub_70FC: one resolved-plist read; normalize more against main via 7E730.
    NSDictionary *resolved = [NSDictionary dictionaryWithContentsOfFile:DD_APPBRIDGE_CACHE];
    id mainRaw = resolved[@"appbridge_split_carplay_ui"];
    NSString *main = [mainRaw isKindOfClass:[NSString class]] ? mainRaw : nil;
    return DDNormalizeCarPlayMore(resolved[@"appbridge_split_carplay_ui_more"], main);
}

BOOL DDCachedAutostartEnabled(void) {
    // sub_836C: resolved-plist value; boolValue if supported, otherwise false.
    NSDictionary *resolved = [NSDictionary dictionaryWithContentsOfFile:DD_APPBRIDGE_CACHE];
    id value = resolved[@"appbridge_autostart"];
    return [value respondsToSelector:@selector(boolValue)] ? [value boolValue] : NO;
}

NSInteger DDCachedFractionValue(NSString *key) {
    // sub_8154: generic resolved-plist key -> 7E63C(value, 0, 99, 0, NULL).
    NSDictionary *resolved = [NSDictionary dictionaryWithContentsOfFile:DD_APPBRIDGE_CACHE];
    id value = resolved[key];
    return DDValidateIntegerValue(value, 0, 99, 0, NULL);
}

NSInteger DDCachedFractionLayoutValue(void) {
    // sub_81EC: fixed appbridge_split_frac_layout -> 7E63C(value, 0, 8, 0, NULL).
    NSDictionary *resolved = [NSDictionary dictionaryWithContentsOfFile:DD_APPBRIDGE_CACHE];
    id value = resolved[@"appbridge_split_frac_layout"];
    return DDValidateIntegerValue(value, 0, 8, 0, NULL);
}

BOOL DDReadKeyPaneEnabled(void) {
    // sub_8058: missing/invalid-format defaults ON; explicit false stays OFF.
    CFPreferencesAppSynchronize(kDDSettingsDomain);
    Boolean valid = false;
    Boolean enabled = CFPreferencesGetAppBooleanValue(CFSTR("keypane_enabled"),
                                                       kDDSettingsDomain,
                                                       &valid);
    return enabled || !valid;
}

static NSInteger DDValidatedFontFloor(NSInteger value) {
    return (value >= 8 && value <= 96) ? value : 0;
}

NSInteger DDReadBridgedFontFloor(void) {
    // sub_7EA4 override semantics are intentionally unusual:
    // - empty override file => force 0;
    // - all-digits override => validated 8..96, otherwise 0 (no prefs fallback);
    // - non-empty override containing a non-digit => fall back to prefs.
    NSString *override = [NSString stringWithContentsOfFile:@"/var/tmp/duodash_ab_fontfloor_force"
                                                   encoding:NSUTF8StringEncoding
                                                      error:nil];
    if (override) {
        NSString *trimmed = [override stringByTrimmingCharactersInSet:
                             [NSCharacterSet whitespaceAndNewlineCharacterSet]];
        NSUInteger length = trimmed.length;
        if (length == 0) return 0;

        BOOL allDigits = YES;
        for (NSUInteger index = 0; index < length; index++) {
            unichar ch = [trimmed characterAtIndex:index];
            if (ch < '0' || ch > '9') {
                allDigits = NO;
                break;
            }
        }
        if (allDigits) return DDValidatedFontFloor(trimmed.integerValue);
    }

    id value = DDCopyAppPreference(@"bridged_font_floor");
    if (!value) return 0;
    CFTypeRef cfValue = (__bridge CFTypeRef)value;
    if (CFGetTypeID(cfValue) != CFNumberGetTypeID()) return 0;
    return DDValidatedFontFloor([value integerValue]);
}

static void DDRefreshCachedBridgeUISettings(void) {
    // sub_74C8 phase order: 7EA4 first, then 8058. These globals back sub_89D8.
    gDDBridgedFontFloor = DDReadBridgedFontFloor();
    gDDKeyPaneEnabled = DDReadKeyPaneEnabled();
}

NSInteger DDValidateIntegerValue(id _Nullable candidate,
                                 NSInteger minimum,
                                 NSInteger maximum,
                                 NSInteger fallback,
                                 DDIntegerValidationStatus * _Nullable status) {
    // sub_7E63C: nil=>status0/default; integer CFNumber=>1; NSString=>2;
    // float NSNumber/other/out-of-range=>3/default. NSString uses integerValue directly,
    // including its permissive coercion behavior.
    DDIntegerValidationStatus resultStatus = DDIntegerValidationMissing;
    NSInteger result = fallback;

    if (candidate) {
        DDIntegerValidationStatus candidateStatus = DDIntegerValidationError;
        BOOL supported = NO;

        if ([candidate isKindOfClass:[NSNumber class]]) {
            CFTypeRef cfValue = (__bridge CFTypeRef)candidate;
            if (CFGetTypeID(cfValue) == CFNumberGetTypeID() &&
                !CFNumberIsFloatType((CFNumberRef)cfValue)) {
                candidateStatus = DDIntegerValidationNumber;
                supported = YES;
            }
        } else if ([candidate isKindOfClass:[NSString class]]) {
            candidateStatus = DDIntegerValidationString;
            supported = YES;
        }

        if (supported) {
            NSInteger parsed = [candidate integerValue];
            if (parsed >= minimum && parsed <= maximum) {
                result = parsed;
                resultStatus = candidateStatus;
            } else {
                resultStatus = DDIntegerValidationError;
            }
        } else {
            resultStatus = DDIntegerValidationError;
        }
    }

    if (status) *status = resultStatus;
    return result;
}

NSInteger DDNormalizeIntegerSetting(NSDictionary *source,
                                    NSString *key,
                                    NSInteger minimum,
                                    NSInteger maximum,
                                    NSInteger fallback,
                                    NSString *fixName,
                                    NSMutableDictionary *writes,
                                    NSMutableArray *fixes) {
    // sub_7EEDC repairs only status 2/3: string coercion is canonicalized to NSNumber,
    // while invalid/out-of-range values are replaced with fallback. Missing and already-valid
    // integer NSNumber values do not produce a write/fix entry.
    DDIntegerValidationStatus status = DDIntegerValidationMissing;
    NSInteger value = DDValidateIntegerValue(source[key], minimum, maximum, fallback, &status);
    if ((((NSInteger)status) & ~((NSInteger)1)) == 2) {
        writes[key] = @(value);
        [fixes addObject:fixName];
    }
    return value;
}

static void DDClearPanesIfNeeded(void) {
    NSFileManager *fm = [NSFileManager defaultManager];
    NSDictionary *attrs = [fm attributesOfItemAtPath:kDDClearPanes error:nil];
    NSDate *mtime = attrs[NSFileModificationDate];
    if (!mtime) return;

    NSString *done = [NSString stringWithContentsOfFile:kDDClearPanesDone
                                               encoding:NSUTF8StringEncoding
                                                  error:nil];
    NSTimeInterval threshold = done.length ? done.doubleValue + 0.5 : 0.5;
    if (mtime.timeIntervalSince1970 <= threshold) return;

    NSString *stamp = [NSString stringWithFormat:@"%.3f", mtime.timeIntervalSince1970];
    [stamp writeToFile:kDDClearPanesDone atomically:YES encoding:NSUTF8StringEncoding error:nil];

    NSArray<NSString *> *keys = @[
        @"appbridge_split_left", @"appbridge_split_right", @"appbridge_split_third",
        @"appbridge_layout", @"appbridge_split_frac_a", @"appbridge_split_frac_b",
        @"appbridge_split_frac_layout", @"appbridge_split_carplay_ui",
        @"appbridge_split_carplay_ui_more"
    ];
    for (NSString *key in keys) {
        CFPreferencesSetValue((__bridge CFStringRef)key, NULL, kDDSettingsDomain,
                              kCFPreferencesCurrentUser, kCFPreferencesAnyHost);
    }
    CFPreferencesSynchronize(kDDSettingsDomain, kCFPreferencesCurrentUser,
                             kCFPreferencesAnyHost);
    [fm removeItemAtPath:kDDClearPanes error:nil];
}

DDRole DDDetectRole(void) {
    uint32_t capacity = 0;
    _NSGetExecutablePath(NULL, &capacity);
    if (capacity == 0) return DDRoleUIApp;

    char *buffer = calloc(capacity + 1, 1);
    if (!buffer) return DDRoleUIApp;
    if (_NSGetExecutablePath(buffer, &capacity) != 0) {
        free(buffer);
        return DDRoleUIApp;
    }

    NSString *path = [NSString stringWithUTF8String:buffer] ?: @"";
    free(buffer);

    if ([path hasSuffix:@"/SpringBoard.app/SpringBoard"]) return DDRoleSpringBoard;
    if ([path hasSuffix:@"/Preferences.app/Preferences"]) return DDRolePreferences;
    if ([path hasSuffix:@"/CarPlay.app/CarPlay"]) return DDRoleCarPlayApp;
    if ([path hasSuffix:@"/mediaserverd"]) return DDRoleMediaServerd;
    if ([path hasSuffix:@"/TextInput/kbd"] || [path hasSuffix:@"/kbd"]) return DDRoleKbd;
    return DDRoleUIApp;
}

NSString *DDRoleName(DDRole role) {
    switch (role) {
        case DDRoleSpringBoard: return @"SpringBoard";
        case DDRolePreferences: return @"Preferences";
        case DDRoleCarPlayApp: return @"CarPlay";
        case DDRoleMediaServerd: return @"mediaserverd";
        case DDRoleKbd: return @"kbd";
        case DDRoleUIApp: default: return @"UIApp";
    }
}

NSDictionary *DDBuildKnownAppBridgeSnapshot(void) {
    CFPreferencesAppSynchronize(kDDSettingsDomain);
    DDRefreshCachedBridgeUISettings();

    BOOL enabledExists = NO;
    BOOL enabled = DDBoolPreference(@"appbridge_enabled", NO, &enabledExists);

    id bridgedRaw = DDCopyAppPreference(@"bridgedApps");
    NSArray *bridgedApps = [bridgedRaw isKindOfClass:[NSArray class]] ? bridgedRaw : @[];

    // sub_7E568 exclusion filtering is unresolved. Preserve the type-gated list rather than
    // inventing a blacklist.
    NSString *left = DDStringPreference(@"appbridge_split_left");
    NSString *right = DDStringPreference(@"appbridge_split_right");
    NSString *third = DDStringPreference(@"appbridge_split_third");
    NSNumber *ratio = DDNumberPreference(@"appbridge_split_ratio", 0);
    NSNumber *layout = DDNumberPreference(@"appbridge_layout", 0);
    NSNumber *fracA = DDNumberPreference(@"appbridge_split_frac_a", 0);
    NSNumber *fracB = DDNumberPreference(@"appbridge_split_frac_b", 0);
    NSNumber *fracLayout = DDNumberPreference(@"appbridge_split_frac_layout", 0);

    BOOL autostart = DDRawAutostartPreference();
    NSString *cpuiMain = DDStringPreference(@"appbridge_split_carplay_ui");
    id cpuiMoreRaw = DDCopyAppPreference(@"appbridge_split_carplay_ui_more");
    NSArray *cpuiMore = [cpuiMoreRaw isKindOfClass:[NSArray class]] ? cpuiMoreRaw : @[];

    NSMutableDictionary *snapshot = [@{
        @"appbridge_enabled": @((enabledExists && enabled) ? 1 : 0),
        @"bridgedApps": bridgedApps,
        @"appbridge_split_enabled": @YES,
        @"appbridge_split_left": left,
        @"appbridge_split_right": right,
        @"appbridge_split_third": third,
        @"appbridge_split_ratio": ratio,
        @"appbridge_layout": layout,
        @"appbridge_split_frac_a": fracA,
        @"appbridge_split_frac_b": fracB,
        @"appbridge_split_frac_layout": fracLayout,
        @"appbridge_autostart": @(autostart),
        @"appbridge_split_carplay_ui": cpuiMain,
        @"appbridge_split_carplay_ui_more": cpuiMore,
    } mutableCopy];

    snapshot[@"navprovider_selected"] = DDStringPreference(@"navprovider_selected");
    BOOL navExists = NO;
    BOOL navAutostart = DDBoolPreference(@"navprovider_autostart", NO, &navExists);
    snapshot[@"navprovider_autostart"] = @((navExists && navAutostart) ? 1 : 0);
    return snapshot;
}

BOOL DDRepublishKnownAppBridgeSnapshot(NSError * _Nullable * _Nullable error) {
    DDClearPanesIfNeeded();
    NSDictionary *snapshot = DDBuildKnownAppBridgeSnapshot();

    BOOL ok = [snapshot writeToFile:DD_APPBRIDGE_CACHE atomically:YES];
    notify_post("com.sensetechlab.appbridge.resolved");

    if (!ok && error) {
        *error = [NSError errorWithDomain:@"com.sensetechlab.duodash.reconstruction"
                                    code:1
                                userInfo:@{NSLocalizedDescriptionKey:
                                    @"Unable to write appbridge reconstruction cache"}];
    }
    return ok;
}

BOOL DDSetAppBridgeLayout(NSInteger layout) {
    // sub_746C accepts exactly 1..8, otherwise returns without sync/republish.
    if (layout < 1 || layout > 8) return NO;

    NSNumber *value = @(layout);
    CFPreferencesSetAppValue(CFSTR("appbridge_layout"),
                             (__bridge CFPropertyListRef)value,
                             kDDSettingsDomain);
    CFPreferencesAppSynchronize(kDDSettingsDomain);
    return DDRepublishKnownAppBridgeSnapshot(NULL);
}

BOOL DDSetCarPlayUI(NSString * _Nullable mainBundleIdentifier,
                    id _Nullable additionalBundleIdentifiers) {
    // sub_84D8: empty/nil main -> @""; nil/non-array more -> []; then 7E730
    // filters to non-empty unique NSString values excluding main, preserving order.
    NSString *main = mainBundleIdentifier.length ? [mainBundleIdentifier copy] : @"";
    NSArray<NSString *> *more = DDNormalizeCarPlayMore(additionalBundleIdentifiers, main);

    CFPreferencesSetAppValue(CFSTR("appbridge_split_carplay_ui"),
                             (__bridge CFPropertyListRef)main,
                             kDDSettingsDomain);
    CFPreferencesSetAppValue(CFSTR("appbridge_split_carplay_ui_more"),
                             (__bridge CFPropertyListRef)more,
                             kDDSettingsDomain);
    CFPreferencesAppSynchronize(kDDSettingsDomain);
    return DDRepublishKnownAppBridgeSnapshot(NULL);
}

BOOL DDToggleAppBridgeAutostart(void) {
    // DDz3 637E8 reads 836C from the resolved plist (missing/non-bool -> NO),
    // flips the value, stores a CFBoolean, synchronizes, then calls 74C8.
    BOOL enabled = !DDCachedAutostartEnabled();
    CFPreferencesSetAppValue(CFSTR("appbridge_autostart"),
                             enabled ? kCFBooleanTrue : kCFBooleanFalse,
                             kDDSettingsDomain);
    CFPreferencesAppSynchronize(kDDSettingsDomain);
    DDRepublishKnownAppBridgeSnapshot(NULL);
    return enabled;
}

BOOL DDEvictCarPlayUIBundle(NSString *bundleIdentifier) {
    // sub_85B8 is prefs-only logical eviction: no process kill, no view teardown.
    if (bundleIdentifier.length == 0) return NO;

    NSString *main = DDCachedStringValue(@"appbridge_split_carplay_ui") ?: @"";
    NSArray<NSString *> *more = DDCachedCarPlayUIMore();

    BOOL isMain = [main isEqualToString:bundleIdentifier];
    BOOL isAdditional = [more containsObject:bundleIdentifier];
    if (!isMain && !isAdditional) return NO;

    NSMutableArray<NSString *> *nextMore = [more mutableCopy];
    [nextMore removeObject:bundleIdentifier];
    return DDSetCarPlayUI(isMain ? @"" : main, nextMore);
}

NSInteger DDCountLiveSnapshotEntries(NSArray * _Nullable snapshot,
                                     NSString * _Nullable bundleIdentifierFilter) {
    // sub_7764C is a read-only liveness probe. Its once gate (771D4) resolves to an exact
    // main-bundle identifier comparison, not the executable-suffix role detector.
    NSString *bundleIdentifier = [NSBundle mainBundle].bundleIdentifier ?: @"";
    if (![bundleIdentifier isEqualToString:@"com.apple.springboard"]) {
        // The decompile returns 0xFFFFFFFFLL here. Preserve that 64-bit numeric sentinel;
        // original callers truncate to unsigned int and treat any nonzero value as truthy.
        return (NSInteger)UINT32_MAX;
    }

    uint32_t liveCount = 0;
    for (id item in snapshot) {
        if (![item isKindOfClass:[NSDictionary class]]) continue;

        NSDictionary *entry = item;
        id pidValue = entry[@"pid"];
        id pathValue = entry[@"path"];
        id bidValue = entry[@"bid"];
        if (![pidValue isKindOfClass:[NSNumber class]]) continue;
        if (![pathValue isKindOfClass:[NSString class]]) continue;

        if (bundleIdentifierFilter.length > 0) {
            if (![bidValue isKindOfClass:[NSString class]]) continue;
            if (![bidValue isEqualToString:bundleIdentifierFilter]) continue;
        }

        int pid = [pidValue intValue];
        if (pid < 2) continue;

        char buffer[4096] = {0};
        if (proc_pidpath(pid, buffer, (uint32_t)sizeof(buffer)) < 1) continue;

        const char *expectedPath = [pathValue UTF8String];
        if (expectedPath && strcmp(buffer, expectedPath) == 0) {
            liveCount++;
        }
    }
    return (NSInteger)liveCount;
}

static id _Nullable DDDistributedNotificationCenter(void) {
    // sub_8900: runtime class lookup keeps this build free of private-framework linkage.
    Class centerClass = NSClassFromString(@"NSDistributedNotificationCenter");
    SEL defaultCenter = NSSelectorFromString(@"defaultCenter");
    if (!centerClass || ![centerClass respondsToSelector:defaultCenter]) return nil;

    id (*sendDefaultCenter)(id, SEL) = (void *)objc_msgSend;
    return sendDefaultCenter(centerClass, defaultCenter);
}

BOOL DDPostDistributedNotification(NSString *name,
                                   id _Nullable object,
                                   NSDictionary * _Nullable userInfo) {
    // sub_8C28 / sub_8D78: same post selector; callers differ only by object nil/non-nil.
    id center = DDDistributedNotificationCenter();
    SEL postSelector = NSSelectorFromString(@"postNotificationName:object:userInfo:deliverImmediately:");
    if (!center || ![center respondsToSelector:postSelector]) return NO;

    void (*post)(id, SEL, id, id, id, BOOL) = (void *)objc_msgSend;
    post(center, postSelector, name, object, userInfo, YES);
    return YES;
}

BOOL DDObserveDistributedNotification(NSString *name,
                                      id observer,
                                      SEL selector,
                                      id _Nullable object) {
    // sub_887C/sub_8934: addObserver:selector:name:object: with either nil or explicit object.
    id center = DDDistributedNotificationCenter();
    SEL addSelector = NSSelectorFromString(@"addObserver:selector:name:object:");
    if (!center || ![center respondsToSelector:addSelector]) return NO;

    void (*addObserver)(id, SEL, id, SEL, id, id) = (void *)objc_msgSend;
    addObserver(center, addSelector, observer, selector, name, object);
    return YES;
}

BOOL DDPostUIAppRequest(NSString * _Nullable bundleIdentifier) {
    // sub_8CC0: nil canonicalizes to the empty string.
    NSDictionary *payload = @{ @"bundleIdentifier": bundleIdentifier ?: @"" };
    return DDPostDistributedNotification(@"com.sensetechlab.appbridge.uiapp.request", nil, payload);
}

BOOL DDPostUIAppState(NSString * _Nullable bundleIdentifier,
                      BOOL shouldBridge,
                      NSInteger orientation,
                      BOOL split,
                      double displayWidth,
                      double displayHeight) {
    // sub_89D8 reads qword_163448 / byte_162DDC cached by 7EA4 / 8058. Do not replace
    // these with fresh reads here: notify/update timing is part of the recovered contract.
    NSString *bundle = bundleIdentifier ?: @"";
    NSDictionary *payload = @{
        @"shouldBridge": @(shouldBridge),
        @"displayWidth": @(displayWidth),
        @"displayHeight": @(displayHeight),
        @"orientation": @(orientation),
        @"isSplit": @(split),
        @"bundleIdentifier": bundle,
        @"bridged_font_floor": @(gDDBridgedFontFloor),
        @"keypane_enabled": @(gDDKeyPaneEnabled),
    };
    return DDPostDistributedNotification(@"com.sensetechlab.appbridge.uiapp.state", bundle, payload);
}

static NSInteger DDNormalizeHostOrientation(NSInteger orientation) {
    // sub_422D0 clamps anything outside the recovered 1..4 range to 1.
    return (orientation >= 1 && orientation <= 4) ? orientation : 1;
}

static void DDSetCachedUIAppBridgeState(BOOL bridging,
                                        double width,
                                        double height,
                                        NSInteger orientation) {
    BOOL wasBridging = gDDUIAppBridging;
    gDDUIAppBridging = bridging;
    gDDUIAppOrientation = DDNormalizeHostOrientation(orientation);
    if (bridging) {
        gDDUIAppDisplayWidth = width;
        gDDUIAppDisplayHeight = height;
        gDDUIAppFontFloorActive = gDDUIAppFontFloor > 0;
    } else {
        gDDUIAppDisplayWidth = 0.0;
        gDDUIAppDisplayHeight = 0.0;
        gDDUIAppFontFloorActive = NO;
    }
    (void)wasBridging;
    // sub_422D0 additionally relayouts windows and applies/restores raised fonts. Those UIKit
    // mutations remain outside this compile-safe state cache until their private UI graph is promoted.
}

NSDictionary *DDCurrentUIAppBridgeState(void) {
    return @{
        @"generation": @(gDDUIAppStateGeneration),
        @"signature": gDDUIAppStateSignature ?: @"",
        @"bridging": @(gDDUIAppBridging),
        @"displayWidth": @(gDDUIAppDisplayWidth),
        @"displayHeight": @(gDDUIAppDisplayHeight),
        @"orientation": @(gDDUIAppOrientation),
        @"isSplit": @(gDDUIAppSplit),
        @"bridged_font_floor": @(gDDUIAppFontFloor),
        @"keypane_enabled": @(gDDUIAppKeyPaneEnabled),
        @"fontFloorActive": @(gDDUIAppFontFloorActive),
    };
}

NSInteger DDReadHostOrientation(void) {
    // sub_3DFC8: NSString integerValue from the override file; anything outside 1..4 -> 1.
    NSString *raw = [NSString stringWithContentsOfFile:@"/var/tmp/duodash_ab_orient"
                                              encoding:NSUTF8StringEncoding
                                                 error:nil];
    NSInteger value = raw ? raw.integerValue : 0;
    return (value >= 1 && value <= 4) ? value : 1;
}

DDHostSlotSize DDResolveSingleHostMirrorSize(DDHostSlotSize renderSize,
                                             DDHostSlotSize screenBoundsSize) {
    // Pure pre-private half of 3B2D8. duodash_ab_canvas=portrait ignores rscale and stores
    // portrait-normalized screen bounds. Otherwise rscale accepts 1..3 and defaults to 2.
    NSString *scaleText = [NSString stringWithContentsOfFile:@"/var/tmp/duodash_ab_rscale"
                                                    encoding:NSUTF8StringEncoding
                                                       error:nil];
    double scale = scaleText ? scaleText.doubleValue : 0.0;

    NSString *canvasText = [NSString stringWithContentsOfFile:@"/var/tmp/duodash_ab_canvas"
                                                     encoding:NSUTF8StringEncoding
                                                        error:nil];
    NSString *canvas = [canvasText stringByTrimmingCharactersInSet:
                        [NSCharacterSet whitespaceAndNewlineCharacterSet]];
    if ([canvas isEqualToString:@"portrait"]) {
        double width = MIN(screenBoundsSize.width, screenBoundsSize.height);
        double height = MAX(screenBoundsSize.width, screenBoundsSize.height);
        return (DDHostSlotSize){width, height};
    }

    if (scale < 1.0 || scale > 3.0) scale = 2.0;
    return (DDHostSlotSize){renderSize.width * scale, renderSize.height * scale};
}

BOOL DDParseLandscapeOverride(NSString * _Nullable text,
                              NSInteger * _Nullable orientation,
                              BOOL * _Nullable swap,
                              BOOL * _Nullable cSwap,
                              double * _Nullable rotationDegrees) {
    // Pure parser inside 3CC44 after the inflight/tripped coordination has allowed the file.
    // First non-empty token must be strict integer 3 or 4. Later non-empty tokens are only
    // swap, cswap, or strict finite rot=<double> with |rotation| <= 360. Empty tokens are ignored.
    if (!text) return NO;

    NSArray<NSString *> *tokens = [text componentsSeparatedByCharactersInSet:
                                   [NSCharacterSet whitespaceAndNewlineCharacterSet]];
    NSInteger parsedOrientation = 0;
    BOOL parsedSwap = NO;
    BOOL parsedCSwap = NO;
    double parsedRotation = 0.0;

    for (NSString *token in tokens) {
        if (token.length == 0) continue;
        if (parsedOrientation == 0) {
            const char *utf8 = token.UTF8String;
            if (!utf8) return NO;
            char *end = NULL;
            long value = strtol(utf8, &end, 10);
            if (!end || *end != '\0' || value < 3 || value > 4) return NO;
            parsedOrientation = (NSInteger)value;
            continue;
        }

        if ([token isEqualToString:@"swap"]) {
            parsedSwap = YES;
            continue;
        }
        if ([token isEqualToString:@"cswap"]) {
            parsedCSwap = YES;
            continue;
        }
        if (![token hasPrefix:@"rot="]) return NO;

        NSString *number = [token substringFromIndex:4];
        const char *utf8 = number.UTF8String;
        if (!utf8) return NO;
        char *end = NULL;
        double value = strtod(utf8, &end);
        if (!end || *end != '\0' || !isfinite(value) || fabs(value) > 360.0) return NO;
        parsedRotation = value;
    }

    if (parsedOrientation == 0) return NO;
    if (orientation) *orientation = parsedOrientation;
    if (swap) *swap = parsedSwap;
    if (cSwap) *cSwap = parsedCSwap;
    if (rotationDegrees) *rotationDegrees = parsedRotation;
    return YES;
}

NSInteger DDResolveSplitHostOrientationFromAcceptedOverride(NSString * _Nullable text) {
    // In 3CC44 a successfully accepted/parsed lscape override supplies qword_163D58 (3 or 4);
    // otherwise qword_162F08 falls back to 3DFC8.
    NSInteger orientation = 0;
    return DDParseLandscapeOverride(text, &orientation, NULL, NULL, NULL)
        ? orientation
        : DDReadHostOrientation();
}

static void DDClearHostLandscapeOverrideState(BOOL unlinkInflightIfActive) {
    if (unlinkInflightIfActive && gDDHostLandscapeOverrideOrientation != 0) {
        unlink(kDDLandscapeInflightPath);
    }
    gDDHostLandscapeOverrideOrientation = 0;
    gDDHostLandscapeSwap = NO;
    gDDHostLandscapeCSwap = NO;
    gDDHostLandscapeRotationDegrees = 0.0;
}

NSInteger DDResolveCoordinatedSplitHostOrientation(void) {
    // Full evidence-safe coordination from 3CC44. State resets before inspecting lscape.
    DDClearHostLandscapeOverrideState(NO);

    NSString *overrideText = [NSString stringWithContentsOfFile:kDDLandscapeOverridePath
                                                       encoding:NSUTF8StringEncoding
                                                          error:nil];
    if (!overrideText) return DDReadHostOrientation();

    NSFileManager *fm = [NSFileManager defaultManager];
    if ([fm fileExistsAtPath:kDDLandscapeTrippedPath]) return DDReadHostOrientation();

    NSString *inflightPath = [NSString stringWithUTF8String:kDDLandscapeInflightPath];
    NSString *inflightText = [NSString stringWithContentsOfFile:inflightPath
                                                       encoding:NSUTF8StringEncoding
                                                          error:nil];
    if (inflightText.length > 0 && inflightText.intValue >= 1) {
        pid_t inflightPID = (pid_t)inflightText.intValue;
        if (inflightPID != getpid()) {
            struct stat plannedStat = {0};
            struct stat inflightStat = {0};
            if (stat(kDDRespringPlannedPath, &plannedStat) == 0 &&
                stat(kDDLandscapeInflightPath, &inflightStat) == 0 &&
                plannedStat.st_mtimespec.tv_sec >= inflightStat.st_mtimespec.tv_sec) {
                unlink(kDDLandscapeInflightPath);
                inflightText = nil;
            }
        }
    }

    if (inflightText.length > 0 && inflightText.intValue >= 1 &&
        (pid_t)inflightText.intValue != getpid()) {
        [@"tripped\n" writeToFile:kDDLandscapeTrippedPath
                         atomically:NO
                           encoding:NSUTF8StringEncoding
                              error:nil];
        unlink(kDDLandscapeInflightPath);
        return DDReadHostOrientation();
    }

    NSInteger orientation = 0;
    BOOL swap = NO;
    BOOL cSwap = NO;
    double rotation = 0.0;
    if (!DDParseLandscapeOverride(overrideText, &orientation, &swap, &cSwap, &rotation)) {
        return DDReadHostOrientation();
    }

    gDDHostLandscapeOverrideOrientation = orientation;
    gDDHostLandscapeSwap = swap;
    gDDHostLandscapeCSwap = cSwap;
    gDDHostLandscapeRotationDegrees = rotation;

    int fd = open(kDDLandscapeInflightPath, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd >= 0) {
        char buffer[32] = {0};
        int length = snprintf(buffer, sizeof(buffer), "%d\n", getpid());
        if (length >= 1) write(fd, buffer, (size_t)length);
        close(fd);
    }

    // Original 3CC44 calls sub_372CC here to hook _UIKeyboardLayerHostView. That private
    // display/input side effect remains excluded; state/file coordination is preserved.
    return orientation;
}

uint64_t DDPrepareSplitHostMirrorFromEnvironment(NSArray *bundleIdentifiers,
                                                  const DDHostSlotSize *slotSizes,
                                                  NSUInteger slotSizeCount,
                                                  NSArray * _Nullable carPlayUIFlags) {
    // 3CC44 rejects effective slot counts outside 1..3 before touching lscape coordination.
    NSUInteger effectiveCount = MIN(bundleIdentifiers.count, slotSizeCount);
    if (!slotSizes || effectiveCount < 1 || effectiveCount > 3) return 0;

    NSInteger orientation = DDResolveCoordinatedSplitHostOrientation();
    return DDPrepareSplitHostMirror(bundleIdentifiers, slotSizes, slotSizeCount,
                                    carPlayUIFlags, orientation);
}

uint64_t DDPrepareSingleHostMirror(NSString * _Nullable bundleIdentifier,
                                   DDHostSlotSize renderSize,
                                   DDHostSlotSize screenBoundsSize) {
    // 3B2D8 state boundary after the private-class availability gate and before scene creation.
    // The original stores a scaled/canvas-adjusted size in slot0, clears slots1/2 + CarPlay flags,
    // marks single-host mode, bumps generation, and resolves orientation through 3DFC8.
    DDHostSlotSize mirrorSize = DDResolveSingleHostMirrorSize(renderSize, screenBoundsSize);
    NSString *bundle = bundleIdentifier ?: @"";
    // 3B2D8 unlinks an active split-lscape inflight marker before clearing that state.
    DDClearHostLandscapeOverrideState(YES);
    return DDUpdateHostSlotMirror(@[bundle], &mirrorSize, 1, nil, DDReadHostOrientation(), NO);
}

uint64_t DDPrepareSplitHostMirror(NSArray *bundleIdentifiers,
                                  const DDHostSlotSize *slotSizes,
                                  NSUInteger slotSizeCount,
                                  NSArray * _Nullable carPlayUIFlags,
                                  NSInteger resolvedOrientation) {
    // 3CC44 pure state boundary: native per-slot sizes are stored unchanged; normalization and
    // default CarPlay flags are handled by DDUpdateHostSlotMirror. Landscape override/inflight
    // coordination resolves orientation before this boundary and remains separate.
    return DDUpdateHostSlotMirror(bundleIdentifiers, slotSizes, slotSizeCount,
                                  carPlayUIFlags, resolvedOrientation, YES);
}

uint64_t DDUpdateHostSlotMirror(NSArray *bundleIdentifiers,
                                const DDHostSlotSize *slotSizes,
                                NSUInteger slotSizeCount,
                                NSArray * _Nullable carPlayUIFlags,
                                NSInteger orientation,
                                BOOL split) {
    // Compile-safe mirror of the post-3DD4C DDz2 state used by 3F224/3B738/3D4FC.
    // 3CC44 accepts min(bids,natives) == 1..3. sub_3DD4C(a3=0) canonicalizes
    // non-NSString/duplicates to @"" while preserving order.
    NSUInteger count = MIN(bundleIdentifiers.count, slotSizeCount);
    if (count < 1 || count > 3 || !slotSizes) return 0;

    NSMutableArray<NSString *> *normalized = [NSMutableArray arrayWithCapacity:count];
    for (NSUInteger index = 0; index < count; index++) {
        id raw = bundleIdentifiers[index];
        NSString *bid = [raw isKindOfClass:[NSString class]] ? raw : @"";
        if (bid.length > 0 && [normalized containsObject:bid]) bid = @"";
        [normalized addObject:[bid copy]];
    }

    gDDHostMirrorGeneration++;
    gDDHostMirrorActive = YES;
    gDDHostMirrorSplit = split;
    gDDHostMirrorSlotCount = count;
    gDDHostMirrorOrientation = (orientation >= 1 && orientation <= 4) ? orientation : 1;

    for (NSUInteger index = 0; index < 3; index++) {
        if (index < count) {
            gDDHostMirrorBids[index] = [normalized[index] copy];
            gDDHostMirrorSizes[index] = slotSizes[index];
            gDDHostMirrorCarPlayUI[index] = index < carPlayUIFlags.count
                ? [carPlayUIFlags[index] boolValue]
                : NO;
        } else {
            gDDHostMirrorBids[index] = @"";
            gDDHostMirrorSizes[index] = (DDHostSlotSize){0.0, 0.0};
            gDDHostMirrorCarPlayUI[index] = NO;
        }
    }
    return gDDHostMirrorGeneration;
}

void DDResetHostSlotMirror(void) {
    // 3AAF8 resetHostingState clears active/bids/sizes/flags/count/split but does not advance
    // qword_163DC8; stale retry blocks therefore fail on the active gate until a new generation.
    gDDHostMirrorActive = NO;
    gDDHostMirrorSplit = NO;
    gDDHostMirrorSlotCount = 0;
    for (NSUInteger index = 0; index < 3; index++) {
        gDDHostMirrorBids[index] = @"";
        gDDHostMirrorSizes[index] = (DDHostSlotSize){0.0, 0.0};
        gDDHostMirrorCarPlayUI[index] = NO;
    }
    // 3AAF8 unlinks inflight only when qword_163D58 (accepted lscape orientation) is nonzero,
    // then clears orientation/swap/cswap/rotation override state without advancing generation.
    DDClearHostLandscapeOverrideState(YES);
}

DDHostSlotSize DDApplyLandscapeSwapToSize(DDHostSlotSize size) {
    // Repeated exact transform in 3F3F0/400D0/40C5C/40DA8: swap only when an accepted
    // landscape override is active, swap is enabled, and both dimensions are positive.
    if (gDDHostLandscapeOverrideOrientation != 0 && gDDHostLandscapeSwap &&
        size.width > 0.0 && size.height > 0.0) {
        return (DDHostSlotSize){size.height, size.width};
    }
    return size;
}

DDHostLandscapeGeometryPlan DDComputeHostLandscapeGeometryPlan(NSUInteger slotIndex,
                                                                  DDHostSlotSize nativeSize,
                                                                  double slotX,
                                                                  double slotY,
                                                                  double slotWidth,
                                                                  double slotHeight) {
    // Pure geometry extracted from the lscape override block inside 3257C. The scale is always
    // computed from the unswapped native dimensions; cswap changes bounds only. Rotation is then
    // concatenated after scale, and center is the midpoint of the target slot rectangle.
    DDHostLandscapeGeometryPlan plan = {0};
    if (slotIndex > 2 || gDDHostLandscapeOverrideOrientation == 0 ||
        (gDDHostMirrorBids[slotIndex] ?: @"").length == 0 ||
        nativeSize.width <= 0.0 || nativeSize.height <= 0.0 ||
        slotWidth <= 0.0 || slotHeight <= 0.0) {
        return plan;
    }

    plan.valid = YES;
    plan.scale = MIN(slotWidth / nativeSize.width, slotHeight / nativeSize.height);
    plan.boundsWidth = gDDHostLandscapeCSwap ? nativeSize.height : nativeSize.width;
    plan.boundsHeight = gDDHostLandscapeCSwap ? nativeSize.width : nativeSize.height;
    plan.rotationRadians = gDDHostLandscapeRotationDegrees * 3.14159265 / 180.0;
    plan.centerX = slotX + slotWidth * 0.5;
    plan.centerY = slotY + slotHeight * 0.5;
    return plan;
}

BOOL DDSceneGeometryUpdatesEnabled(void) {
    // sub_3E9A8 memoizes the inverse of /var/tmp/duodash_ab_noscenegeom on first read.
    if (gDDSceneGeometryEnabledCache < 0) {
        BOOL disabled = [[NSFileManager defaultManager]
            fileExistsAtPath:@"/var/tmp/duodash_ab_noscenegeom"];
        gDDSceneGeometryEnabledCache = disabled ? 0 : 1;
    }
    return gDDSceneGeometryEnabledCache == 1;
}

static void DDRefreshGenerationScopedGeometryStateIfNeeded(void) {
    // Evidence-safe subset of 41C24: the nopaneorient flag is refreshed once per host
    // generation. Private retry counters/slot-applied flags are intentionally not modeled here.
    if (gDDGeometryStateGeneration == gDDHostMirrorGeneration) return;
    gDDGeometryStateGeneration = gDDHostMirrorGeneration;
    gDDPaneOrientationDisabled = [[NSFileManager defaultManager]
        fileExistsAtPath:@"/var/tmp/duodash_ab_nopaneorient"];
}

BOOL DDSceneSettingsHasInterfaceOrientationIvar(void) {
    // sub_3E534 memoizes whether private UIApplicationSceneSettings exposes
    // the _interfaceOrientation ivar. Runtime lookup avoids a hard private-framework link.
    if (gDDSceneSettingsOrientationIvarCache < 0) {
        Class settingsClass = objc_getClass("UIApplicationSceneSettings");
        gDDSceneSettingsOrientationIvarCache =
            settingsClass && class_getInstanceVariable(settingsClass, "_interfaceOrientation")
                ? 1 : 0;
    }
    return gDDSceneSettingsOrientationIvarCache == 1;
}

static BOOL DDClassHasVoidIntegerSetter(Class cls, const char *selectorName) {
    // sub_3ECD0: exactly three Objective-C arguments, void return, and q/Q setter argument.
    if (!cls || !selectorName) return NO;
    Method method = class_getInstanceMethod(cls, sel_registerName(selectorName));
    if (!method || method_getNumberOfArguments(method) != 3) return NO;

    char returnType[8] = {0};
    char argumentType[8] = {0};
    method_getReturnType(method, returnType, sizeof(returnType));
    method_getArgumentType(method, 2, argumentType, sizeof(argumentType));
    return returnType[0] == 'v' && (((unsigned char)argumentType[0] & 0xDFu) == 'Q');
}

BOOL DDAuxSceneOrientationMutationSupported(void) {
    // sub_3E590. This is intentionally not memoized: the original probes each createAux call.
    Class sceneClass = objc_getClass("FBScene");
    if (!sceneClass) return NO;

    Method updateMethod = class_getInstanceMethod(sceneClass, sel_registerName("updateSettingsWithBlock:"));
    if (!updateMethod) return NO;
    const char *typeEncoding = method_getTypeEncoding(updateMethod);
    if (!typeEncoding || typeEncoding[0] != 'v' || !strstr(typeEncoding, "@?")) return NO;

    Class mutableSettingsClass = objc_getClass("UIMutableApplicationSceneSettings");
    return DDClassHasVoidIntegerSetter(mutableSettingsClass, "setInterfaceOrientation:");
}

static BOOL DDHostMirrorRejectsAuxBundle(NSString *bundleIdentifier) {
    // sub_3E4A8: reject a bid already present in any non-CarPlay hosted slot.
    if (bundleIdentifier.length == 0) return NO;
    for (NSUInteger index = 0; index < 3; index++) {
        NSString *hosted = gDDHostMirrorBids[index] ?: @"";
        if (hosted.length == 0 || gDDHostMirrorCarPlayUI[index]) continue;
        if ([bundleIdentifier isEqualToString:hosted]) return YES;
    }
    return NO;
}

DDAuxScenePreparation DDPrepareAuxSceneCandidate(NSString * _Nullable bundleIdentifier,
                                                  DDHostSlotSize nativeSize,
                                                  NSInteger requestedOrientation,
                                                  BOOL auxControllerAlreadyExists) {
    // Exact pre-private half of 3C368. The private self->_auxVC state is supplied explicitly
    // because this reconstruction intentionally does not own an SBAppViewController instance.
    DDAuxScenePreparation preparation = {0};
    NSString *bundle = bundleIdentifier ?: @"";
    if (bundle.length == 0 || nativeSize.width < 1.0 || nativeSize.height < 1.0 ||
        auxControllerAlreadyExists || DDHostMirrorRejectsAuxBundle(bundle)) {
        return preparation;
    }

    preparation.valid = YES;
    preparation.nativeSize = nativeSize;
    preparation.orientation = requestedOrientation;

    if ((requestedOrientation == 3 || requestedOrientation == 4) &&
        !DDSceneSettingsHasInterfaceOrientationIvar() &&
        !DDAuxSceneOrientationMutationSupported()) {
        preparation.orientation = 0;
        preparation.nativeSize.width = MIN(nativeSize.width, nativeSize.height);
        preparation.nativeSize.height = MAX(nativeSize.width, nativeSize.height);
    }
    return preparation;
}

static void DDRefreshAuxSceneStateGeneration(void) {
    // Exact state subset of sub_3E428.
    gDDAuxGeneration++;
    gDDAuxSettingsInFlight = NO;
    gDDAuxSettingsApplied = NO;
    gDDAuxSettingsAttemptCount = 0;
    gDDAuxSettingsBudget = 10;
    // sub_3E428 does not touch byte_163E9D (executor reentrancy); preserve it exactly.
    gDDAuxSwapEnabled = ![[NSFileManager defaultManager]
        fileExistsAtPath:@"/var/tmp/duodash_kp_auxnoswap"];
}

BOOL DDCommitAuxSceneMirrorAfterApplicationLookup(NSString * _Nullable bundleIdentifier,
                                                   DDAuxScenePreparation preparation,
                                                   BOOL applicationLookupSucceeded) {
    // 3C368 commits qword_163D70/xmmword_163DD0/qword_163DE0 only after
    // SBApplicationController applicationWithBundleIdentifier: returns a valid application.
    NSString *bundle = bundleIdentifier ?: @"";
    if (!preparation.valid || !applicationLookupSucceeded || bundle.length == 0) return NO;

    gDDAuxBundleIdentifier = [bundle copy];
    gDDAuxNativeSize = preparation.nativeSize;
    gDDAuxOrientation = preparation.orientation;
    DDRefreshAuxSceneStateGeneration();
    gDDAuxNoAuxSID = [[NSFileManager defaultManager]
        fileExistsAtPath:@"/var/tmp/duodash_kp_noauxsid"];
    gDDAuxNoApplyDiff = [[NSFileManager defaultManager]
        fileExistsAtPath:@"/var/tmp/duodash_kp_noapplydiff"];
    return YES;
}

void DDClearAuxSceneMirror(void) {
    // Evidence-safe state half of 3C808. With no private aux controller/view owned by this target,
    // an empty aux bid is the exact no-op condition; otherwise clear state then run 3E428 state.
    if (gDDAuxBundleIdentifier.length == 0) return;
    gDDAuxBundleIdentifier = nil;
    gDDAuxNativeSize = (DDHostSlotSize){0.0, 0.0};
    gDDAuxOrientation = 0;
    DDRefreshAuxSceneStateGeneration();
}

NSDictionary *DDCurrentAuxSceneMirror(void) {
    return @{
        @"active": @(gDDAuxBundleIdentifier.length > 0),
        @"bundleIdentifier": gDDAuxBundleIdentifier ?: @"",
        @"width": @(gDDAuxNativeSize.width),
        @"height": @(gDDAuxNativeSize.height),
        @"orientation": @(gDDAuxOrientation),
        @"generation": @(gDDAuxGeneration),
        @"swapEnabled": @(gDDAuxSwapEnabled),
        @"noAuxSID": @(gDDAuxNoAuxSID),
        @"noApplyDiff": @(gDDAuxNoApplyDiff),
        @"settingsInFlight": @(gDDAuxSettingsInFlight),
        @"settingsApplied": @(gDDAuxSettingsApplied),
        @"settingsAttemptCount": @(gDDAuxSettingsAttemptCount),
        @"settingsBudget": @(gDDAuxSettingsBudget),
        @"settingsExecutorReentrant": @(gDDAuxSettingsExecutorReentrant),
    };
}

DDAuxSceneSettingsPlan DDCurrentAuxSceneSettingsPlan(void) {
    // Pure desired-settings state from 3E670 before its private updateSettingsWithBlock executor.
    DDAuxSceneSettingsPlan plan = {0};
    if (gDDAuxBundleIdentifier.length == 0 || DDSceneSettingsHasInterfaceOrientationIvar() ||
        (gDDAuxOrientation != 3 && gDDAuxOrientation != 4) ||
        gDDAuxNativeSize.width < 1.0 || gDDAuxNativeSize.height < 1.0) {
        return plan;
    }

    plan.valid = YES;
    plan.orientation = gDDAuxOrientation;
    plan.frameSize.width = gDDAuxSwapEnabled ? gDDAuxNativeSize.height : gDDAuxNativeSize.width;
    plan.frameSize.height = gDDAuxSwapEnabled ? gDDAuxNativeSize.width : gDDAuxNativeSize.height;
    return plan;
}

BOOL DDAuxSceneSettingsNeedUpdate(DDAuxSceneSettingsPlan plan,
                                   BOOL previouslyApplied,
                                   BOOL hasCurrentSettings,
                                   DDHostSlotSize currentFrameSize,
                                   NSInteger currentOrientation) {
    // 3E670's pure early-out check before geometry/method/reentrancy/attempt gates.
    if (!plan.valid) return NO;
    if (!previouslyApplied) return YES;
    if (!hasCurrentSettings) return NO;

    BOOL sizeMatches = fabs(currentFrameSize.width - plan.frameSize.width) <= 0.5 &&
                       fabs(currentFrameSize.height - plan.frameSize.height) <= 0.5;
    BOOL orientationMatches = currentOrientation == 0 || currentOrientation == plan.orientation;
    return !(sizeMatches && orientationMatches);
}

NSArray<NSNumber *> *DDAuxCreateKickRetryDelays(void) {
    // 3C368 schedules exactly 0.1s, 0.5s and 1.5s create-kick callbacks.
    return @[
        @(kDDAuxCreateKickRetryDelays[0]),
        @(kDDAuxCreateKickRetryDelays[1]),
        @(kDDAuxCreateKickRetryDelays[2]),
    ];
}

BOOL DDAuxCreateKickRetriesEnabled(void) {
    // 3C368 schedules create-kicks only after a view exists when aux orientation is nonzero and
    // UIApplicationSceneSettings does not expose the direct _interfaceOrientation ivar.
    return gDDAuxOrientation != 0 && !DDSceneSettingsHasInterfaceOrientationIvar();
}

BOOL DDAuxCreateKickShouldRequestPrivateSceneObject(uint64_t capturedGeneration) {
    // sub_3E604 gate before the private auxSceneObject lookup.
    return capturedGeneration == gDDAuxGeneration && !gDDAuxSettingsApplied;
}

DDAuxSceneSettingsAttempt DDBeginAuxSceneSettingsAttempt(BOOL settingsNeedUpdate,
                                                         BOOL privateExecutorMethodSupported) {
    // Evidence-safe state-machine half of 3E670 after its scene/current-settings early-outs.
    // The caller supplies the private updateSettingsWithBlock signature/capability result.
    DDAuxSceneSettingsAttempt attempt = {0};
    DDAuxSceneSettingsPlan plan = DDCurrentAuxSceneSettingsPlan();
    attempt.settingsPlan = plan;

    if (!settingsNeedUpdate || !plan.valid || !DDSceneGeometryUpdatesEnabled() ||
        gDDAuxSettingsExecutorReentrant || gDDAuxSettingsInFlight) {
        return attempt;
    }

    if (gDDAuxSettingsAttemptCount >= 8) {
        if (gDDAuxSettingsBudget >= 1) gDDAuxSettingsBudget = 0;
        return attempt;
    }

    if (!privateExecutorMethodSupported) {
        if (gDDAuxSettingsBudget >= 1) gDDAuxSettingsBudget--;
        return attempt;
    }

    gDDAuxSettingsAttemptCount++;
    gDDAuxSettingsInFlight = YES;
    attempt.shouldDispatch = YES;
    attempt.generation = gDDAuxGeneration;
    attempt.attemptNumber = gDDAuxSettingsAttemptCount;
    return attempt;
}

BOOL DDBeginAuxSceneSettingsApply(uint64_t capturedGeneration) {
    // Entry state of sub_3EA0C. Generation mismatch is a total no-op. Matching generation first
    // clears the in-flight flag, then honors the executor reentrancy guard.
    if (capturedGeneration != gDDAuxGeneration) return NO;
    gDDAuxSettingsInFlight = NO;
    if (gDDAuxSettingsExecutorReentrant) return NO;

    gDDAuxSettingsExecutorReentrant = YES;
    gDDAuxSettingsExecutingGeneration = capturedGeneration;
    return YES;
}

BOOL DDCompleteAuxSceneSettingsApply(uint64_t capturedGeneration) {
    // Call only after the external/private updateSettingsWithBlock invocation actually returned.
    // Original 3EA0C marks applied regardless of whether frame/orientation setters inside 3EB9C
    // were available; therefore completion means executor invocation happened, not setter success.
    if (!gDDAuxSettingsExecutorReentrant ||
        gDDAuxSettingsExecutingGeneration != capturedGeneration) {
        return NO;
    }

    gDDAuxSettingsApplied = YES;
    if (gDDAuxSettingsBudget >= 1) gDDAuxSettingsBudget--;
    gDDAuxSettingsExecutorReentrant = NO;
    gDDAuxSettingsExecutingGeneration = 0;
    return YES;
}

static NSInteger DDConfiguredHostSlotIndexForBundleIdentifier(NSString *bundleIdentifier,
                                                               BOOL includeCarPlayUI) {
    // Post-identity half shared by 41E08/4138C. The caller supplies the already-resolved
    // bundle identity; this deliberately does not reproduce 3FBC8 scene/client traversal.
    if (bundleIdentifier.length == 0) return NSNotFound;
    for (NSUInteger index = 0; index < 3; index++) {
        NSString *hosted = gDDHostMirrorBids[index] ?: @"";
        if (hosted.length == 0) continue;
        if (!includeCarPlayUI && gDDHostMirrorCarPlayUI[index]) continue;
        if ([bundleIdentifier isEqualToString:hosted]) return (NSInteger)index;
    }
    return NSNotFound;
}

BOOL DDBundleIdentifierMatchesAux(NSString *bundleIdentifier) {
    // Exact post-identity equality from 3FFC0: both strings must be non-empty.
    return bundleIdentifier.length > 0 && gDDAuxBundleIdentifier.length > 0 &&
           [bundleIdentifier isEqualToString:gDDAuxBundleIdentifier];
}

static DDSceneIdentityRoute DDSceneIdentityRouteNoneValue(void) {
    DDSceneIdentityRoute route = { DDSceneIdentityRouteNone, -1 };
    return route;
}

DDSceneIdentityRoute DDResolveFBSUpdateIdentityRoute(NSString *bundleIdentifier) {
    // 400D0 first gates on active hosting + 41CBC. After 3FBC8 has supplied identity,
    // host routing accepts only non-CarPlay slots (41E08), with aux as the fallback (3FB54/3FFC0).
    DDSceneIdentityRoute route = DDSceneIdentityRouteNoneValue();
    if (!gDDHostMirrorActive || bundleIdentifier.length == 0) return route;

    NSInteger slotIndex = DDConfiguredHostSlotIndexForBundleIdentifier(bundleIdentifier, NO);
    if (slotIndex != NSNotFound) {
        route.kind = DDSceneIdentityRouteHostSlot;
        route.slotIndex = slotIndex;
        return route;
    }
    if (DDBundleIdentifierMatchesAux(bundleIdentifier)) route.kind = DDSceneIdentityRouteAux;
    return route;
}

DDSceneIdentityRoute DDResolveAVCSceneHandleIdentityRoute(NSString *bundleIdentifier) {
    // 4138C differs from 400D0: its first slot loop does not exclude CarPlay slots.
    // Only when no configured slot matches does the callback route the identity to aux.
    DDSceneIdentityRoute route = DDSceneIdentityRouteNoneValue();
    if (!gDDHostMirrorActive || bundleIdentifier.length == 0) return route;

    NSInteger slotIndex = DDConfiguredHostSlotIndexForBundleIdentifier(bundleIdentifier, YES);
    if (slotIndex != NSNotFound) {
        route.kind = DDSceneIdentityRouteHostSlot;
        route.slotIndex = slotIndex;
        return route;
    }
    if (DDBundleIdentifierMatchesAux(bundleIdentifier)) route.kind = DDSceneIdentityRouteAux;
    return route;
}

DDAVCSceneHandleUpdateDecision DDResolveAVCSceneHandleUpdateDecision(NSString *bundleIdentifier,
                                                                    BOOL scenePresent,
                                                                    BOOL slotSettingsMarked,
                                                                    BOOL sceneSettingsSelectorSupported) {
    // Pure 4138C routing after the caller has already resolved identity/scene capability. Host-slot
    // matching deliberately includes CarPlay slots; aux is considered only when no configured slot
    // matches. This helper reports the pending 3F5C0/3E670 action but never invokes either executor.
    DDAVCSceneHandleUpdateDecision decision = {
        DDAVCSceneHandleUpdateNone,
        -1,
        {0.0, 0.0},
        NO,
        NO,
    };
    if (!scenePresent) return decision;

    DDSceneIdentityRoute route = DDResolveAVCSceneHandleIdentityRoute(bundleIdentifier);
    if (route.kind == DDSceneIdentityRouteHostSlot) {
        if (slotSettingsMarked || route.slotIndex < 0 || route.slotIndex > 2) return decision;
        DDHostSlotSize target = gDDHostMirrorSizes[(NSUInteger)route.slotIndex];
        if (!(target.width > 0.0)) return decision;

        decision.kind = DDAVCSceneHandleUpdateHostSlot;
        decision.slotIndex = route.slotIndex;
        decision.targetSize = DDApplyLandscapeSwapToSize(target);
        decision.shouldAttemptGeneralCounterDecrement = YES;
        return decision;
    }

    if (route.kind == DDSceneIdentityRouteAux) {
        decision.kind = DDAVCSceneHandleUpdateAux;
        decision.shouldReadSceneSettingsForAux = sceneSettingsSelectorSupported;
    }
    return decision;
}

DDAVCSceneHandleCallbackDecision DDResolveAVCSceneHandleCallbackDecision(NSString *bundleIdentifier,
                                                                         BOOL scenePresent,
                                                                         BOOL sceneSettingsSelectorSupported,
                                                                         BOOL settingsObjectPresent,
                                                                         BOOL foregroundSelectorSupported,
                                                                         BOOL isForeground,
                                                                         uint64_t suppressionCount) {
    // Exact post-routing 4138C callback gate. Suppression is narrower than the update route: the
    // foreground=false identity must match a configured NON-CarPlay host slot (3E4A8 semantics).
    DDAVCSceneHandleCallbackDecision decision = {
        YES,
        NO,
        NO,
        suppressionCount,
    };
    if (!gDDHostMirrorActive || !scenePresent || !sceneSettingsSelectorSupported ||
        !settingsObjectPresent || !foregroundSelectorSupported || isForeground) {
        return decision;
    }

    NSInteger slotIndex = DDConfiguredHostSlotIndexForBundleIdentifier(bundleIdentifier, NO);
    if (slotIndex == NSNotFound) return decision;

    decision.shouldCallOriginal = NO;
    decision.shouldSuppressOriginal = YES;
    if (suppressionCount <= 9) {
        decision.shouldIncrementSuppressionCount = YES;
        decision.nextSuppressionCount = suppressionCount + 1;
    }
    return decision;
}

DDHostSlotResizePrivateFollowup DDResolveHostSlotResizePrivateFollowup(NSInteger slotIndex,
                                                                       DDHostSlotSize acceptedRawSize,
                                                                       NSInteger attemptCount,
                                                                       NSInteger generalCounter,
                                                                       BOOL privateScenePresent) {
    // Exact post-acceptance half of 3F3F0. The caller reaches this only after the resize passed the
    // main-thread/active/slot/bid/non-CarPlay/size>=1 gates and raw mirror+IPC state was updated.
    // Counter changes and probeSceneForSlot:/3F5C0 invocation are deliberately reported as data.
    DDHostSlotResizePrivateFollowup followup = {
        NO,
        attemptCount,
        NO,
        generalCounter,
        NO,
        NO,
        slotIndex,
        {0.0, 0.0},
    };
    followup.shouldProbePrivateScene = YES;

    if (attemptCount >= 1) {
        followup.shouldResetAttemptCount = YES;
        followup.nextAttemptCount = 0;
    }
    if (generalCounter <= 3) {
        followup.shouldRaiseGeneralCounterFloor = YES;
        followup.nextGeneralCounter = 4;
    }

    if (privateScenePresent) {
        followup.shouldRequestPrivateSceneUpdate = YES;
        followup.targetSize = DDApplyLandscapeSwapToSize(acceptedRawSize);
    }
    return followup;
}

DDHostSlotSize DDResolveIdentityNativeSize(NSString *bundleIdentifier) {
    // Exact post-identity 41D80 selection. 41E08 takes precedence and only maps non-CarPlay
    // configured slots; aux is consulted only when no such host slot matches.
    NSInteger slotIndex = DDConfiguredHostSlotIndexForBundleIdentifier(bundleIdentifier, NO);
    if (slotIndex != NSNotFound) return gDDHostMirrorSizes[(NSUInteger)slotIndex];
    if (DDBundleIdentifierMatchesAux(bundleIdentifier)) return gDDAuxNativeSize;
    return (DDHostSlotSize){0.0, 0.0};
}

DDHostSlotSize DDResolveIdentityAdjustedSize(NSString *bundleIdentifier) {
    // Raw ARM64 at 41E94 confirms a two-double return even though the decompiler typed it void.
    // Aux orientation 3/4 portrait-normalizes a landscape-shaped native size. Non-aux uses the
    // same accepted-landscape swap gate recovered from 3F3F0/400D0/40C5C/40DA8.
    DDHostSlotSize size = DDResolveIdentityNativeSize(bundleIdentifier);
    if (DDBundleIdentifierMatchesAux(bundleIdentifier)) {
        if ((gDDAuxOrientation == 3 || gDDAuxOrientation == 4) && size.width > size.height) {
            return (DDHostSlotSize){size.height, size.width};
        }
        return size;
    }
    return DDApplyLandscapeSwapToSize(size);
}

NSInteger DDResolveIdentityRawSettingsOrientation(NSString *bundleIdentifier) {
    // Exact post-identity 3FAF8 choice used directly by 40514/41F50: aux orientation wins only
    // when nonzero and the supplied identity is aux; otherwise use the host orientation.
    if (gDDAuxOrientation != 0 && DDBundleIdentifierMatchesAux(bundleIdentifier)) {
        return gDDAuxOrientation;
    }
    return gDDHostMirrorOrientation;
}

BOOL DDShouldAttemptDirectInterfaceOrientationRepair(NSString *bundleIdentifier,
                                                      BOOL forceInterfaceOrientation) {
    // Pure decision before 40514 calls the private 9C3BC ivar writer. The aux branch does not
    // take this path. Caller supplies the already-resolved force-IO toggle result.
    if (DDBundleIdentifierMatchesAux(bundleIdentifier)) return NO;
    NSInteger desiredOrientation = DDResolveIdentityRawSettingsOrientation(bundleIdentifier);
    return forceInterfaceOrientation || gDDHostLandscapeOverrideOrientation != 0 ||
           desiredOrientation != gDDHostMirrorOrientation;
}

BOOL DDSceneSettingsSnapshotsEquivalent(DDSceneSettingsSnapshot before,
                                        DDSceneSettingsSnapshot after) {
    // Exact 40514 post-41F50 comparison: orientation + foreground exact, frame width/height
    // independently within +/-0.5. Missing selectors are represented by caller-supplied zeros.
    return before.orientation == after.orientation && before.foreground == after.foreground &&
           fabs(before.frameSize.width - after.frameSize.width) <= 0.5 &&
           fabs(before.frameSize.height - after.frameSize.height) <= 0.5;
}

BOOL DDShouldClearAuxSceneSettingsDiff(BOOL settingsDiffPresent,
                                       BOOL settingsDiffSetterSupported,
                                       DDSceneSettingsSnapshot before,
                                       DDSceneSettingsSnapshot after) {
    // Pure 40514 decision only. The reconstruction never sends setSettingsDiff:.
    return settingsDiffPresent && settingsDiffSetterSupported && !gDDAuxNoApplyDiff &&
           !DDSceneSettingsSnapshotsEquivalent(before, after);
}

DDSceneCallbackSizeRewrite DDResolveSceneCallbackSizeRewrite(NSString *bundleIdentifier,
                                                              DDHostSlotSize originalSize) {
    // Exact caller-supplied-identity rewrite shared by 40C5C/40DA8 after 41CBC has accepted
    // either a non-CarPlay hosted bid or aux. Strict-positive tests intentionally reject NaN.
    DDSceneCallbackSizeRewrite rewrite = { originalSize, NO, NO, 0 };
    if (!gDDHostMirrorActive || !(originalSize.width > 0.0 && originalSize.height > 0.0)) {
        return rewrite;
    }

    DDSceneIdentityRoute route = DDResolveFBSUpdateIdentityRoute(bundleIdentifier);
    if (route.kind == DDSceneIdentityRouteNone) return rewrite;

    DDHostSlotSize replacement = DDApplyLandscapeSwapToSize(DDResolveIdentityNativeSize(bundleIdentifier));
    if (!(replacement.width > 0.0 && replacement.height > 0.0)) return rewrite;

    rewrite.size = replacement;
    rewrite.substituted = YES;
    return rewrite;
}

DDSceneCallbackSizeRewrite DDResolveSceneCallbackSizeRewriteWithSuccessCounter(NSString *bundleIdentifier,
                                                                                DDHostSlotSize originalSize,
                                                                                NSInteger successCounter) {
    // 40DA8 only: its successful substitution path attempts dword_162F40-- when the signed
    // current counter is >=1. 40C5C uses the base helper and therefore carries no counter action.
    DDSceneCallbackSizeRewrite rewrite = DDResolveSceneCallbackSizeRewrite(bundleIdentifier,
                                                                           originalSize);
    rewrite.nextSuccessCounter = successCounter;
    if (rewrite.substituted && successCounter >= 1) {
        rewrite.shouldAttemptSuccessCounterDecrement = YES;
        rewrite.nextSuccessCounter = successCounter - 1;
    }
    return rewrite;
}

DDSceneCallbackExceptionOutcome DDResolveSceneCallbackExceptionOutcome(DDSceneCallbackExceptionSite site,
                                                                       uint64_t diagnosticCount) {
    // Exact LSDA/call-site-table behavior shared by 40C5C and 40DA8. Exceptions from 41CBC and
    // 41D80 are caught/swallowed and execution resumes at the original callback. An exception from
    // the original callback itself is swallowed, never retried, and advances its per-hook diagnostic
    // counter only while the unsigned current value is <=9 (EA8 for 40C5C, EB0 for 40DA8).
    DDSceneCallbackExceptionOutcome outcome = {
        NO,
        NO,
        NO,
        diagnosticCount,
    };

    if (site == DDSceneCallbackExceptionSiteRouteEligibility ||
        site == DDSceneCallbackExceptionSiteNativeSizeResolution) {
        outcome.shouldSwallowException = YES;
        outcome.shouldCallOriginalAfterCatch = YES;
        return outcome;
    }

    if (site == DDSceneCallbackExceptionSiteOriginalCallback) {
        outcome.shouldSwallowException = YES;
        if (diagnosticCount <= 9) {
            outcome.shouldIncrementDiagnosticCount = YES;
            outcome.nextDiagnosticCount = diagnosticCount + 1;
        }
    }
    return outcome;
}

BOOL DDResolveSceneOrientationEqualityResult(NSString *bundleIdentifier,
                                             NSInteger requestedOrientation,
                                             BOOL originalResult) {
    // 40F0C overrides the original callback result only while hosting is active and 41CBC accepts
    // the supplied identity; otherwise the original implementation result is preserved verbatim.
    if (!gDDHostMirrorActive) return originalResult;
    DDSceneIdentityRoute route = DDResolveFBSUpdateIdentityRoute(bundleIdentifier);
    if (route.kind == DDSceneIdentityRouteNone) return originalResult;
    return DDResolveIdentityRawSettingsOrientation(bundleIdentifier) == requestedOrientation;
}

BOOL DDShouldForceMutableSceneForeground(NSString *bundleIdentifier,
                                         BOOL mutableSettingsClassAvailable,
                                         BOOL settingsIsMutableApplicationSceneSettings,
                                         BOOL foregroundSetterSupported) {
    // Pure 40FF4 eligibility after the original implementation already ran. The caller supplies
    // runtime class/kind/setter capability results; this reconstruction never sends setForeground:.
    if (!gDDHostMirrorActive) return NO;
    DDSceneIdentityRoute route = DDResolveFBSUpdateIdentityRoute(bundleIdentifier);
    return route.kind != DDSceneIdentityRouteNone && mutableSettingsClassAvailable &&
           settingsIsMutableApplicationSceneSettings && foregroundSetterSupported;
}

static DDSceneDestroyDecision DDSceneDestroyDecisionValue(DDSceneDestroyDecisionKind kind,
                                                           NSInteger slotIndex) {
    DDSceneDestroyDecision decision = { kind, slotIndex };
    return decision;
}

DDSceneDestroyDecision DDResolveSceneDestroyDecision(NSString *primaryBundleIdentifier,
                                                      NSString *secondaryBundleIdentifier) {
    // Pure post-identity half of 41138. 41CBC gates on either callback object, but identity
    // selection still prefers the primary identity whenever it is non-empty, even when only the
    // secondary object made the gate true. This subtle precedence is preserved intentionally.
    DDSceneDestroyDecision none = DDSceneDestroyDecisionValue(DDSceneDestroyDecisionNone, -1);
    if (!gDDHostMirrorActive) return none;

    DDSceneIdentityRoute primaryRoute = DDResolveFBSUpdateIdentityRoute(primaryBundleIdentifier);
    DDSceneIdentityRoute secondaryRoute = DDResolveFBSUpdateIdentityRoute(secondaryBundleIdentifier);
    if (primaryRoute.kind == DDSceneIdentityRouteNone &&
        secondaryRoute.kind == DDSceneIdentityRouteNone) {
        return none;
    }

    NSString *selected = primaryBundleIdentifier.length > 0
        ? primaryBundleIdentifier
        : secondaryBundleIdentifier;
    if (DDBundleIdentifierMatchesAux(selected)) {
        return DDSceneDestroyDecisionValue(DDSceneDestroyDecisionAuxDestroyedNotice, -1);
    }

    if (!gDDHostMirrorSplit || selected.length == 0) {
        return DDSceneDestroyDecisionValue(DDSceneDestroyDecisionDismissHost, -1);
    }

    NSInteger matchCount = 0;
    NSInteger matchedSlotIndex = -1;
    for (NSUInteger index = 0; index < 3; index++) {
        NSString *hosted = gDDHostMirrorBids[index] ?: @"";
        if (hosted.length > 0 && [selected isEqualToString:hosted]) {
            matchCount++;
            matchedSlotIndex = (NSInteger)index;
        }
    }
    if (matchCount == 1) {
        return DDSceneDestroyDecisionValue(DDSceneDestroyDecisionClearHostSlot, matchedSlotIndex);
    }
    return DDSceneDestroyDecisionValue(DDSceneDestroyDecisionDismissHost, -1);
}

DDToAppsYieldDecision DDResolveToAppsYieldDecision(NSArray<NSString *> *destinationBundleIdentifiers,
                                                   BOOL yieldInProgress,
                                                   BOOL swallowOriginalCallback) {
    // Pure post-enumeration half of 41730. The caller supplies already-extracted destination
    // bundle identities plus the external swallow-file state. Private scene-entity traversal and
    // dismiss/cpdisconnect/hide/log side effects remain outside the reconstruction runtime.
    DDToAppsYieldDecision none = { DDToAppsYieldDecisionNone, -1 };
    if (!gDDHostMirrorActive || yieldInProgress) return none;

    for (NSString *bundleIdentifier in destinationBundleIdentifiers ?: @[]) {
        NSInteger slotIndex = DDConfiguredHostSlotIndexForBundleIdentifier(bundleIdentifier, NO);
        if (slotIndex == NSNotFound) continue;

        DDToAppsYieldDecision decision = {
            swallowOriginalCallback
                ? DDToAppsYieldDecisionSwallowOriginal
                : DDToAppsYieldDecisionYieldThenCallOriginal,
            slotIndex,
        };
        return decision;
    }
    return none;
}

DDToAppsYieldExceptionOutcome DDResolveToAppsYieldExceptionOutcome(DDToAppsYieldExceptionSite site,
                                                                   uint64_t currentProbeCount,
                                                                   BOOL reasonSelectorSupported) {
    // 41730 uses a broad catch-to-original path for pre-yield routing/enumeration/toggle probes,
    // but its individual yield side effects have distinct continuations. DDz2 dismiss exceptions are
    // swallowed and continue with disconnect/hide/log; disconnect exceptions jump directly to original
    // and notably bypass the byte_163EC0 clear; DDz1 hide exceptions continue at the yield log; yield-log
    // exceptions continue at cleanup/reset. The original callback has its own 41BA0 catch/no-retry path,
    // while cleanup-only LSDA entries resume unwind rather than swallowing.
    DDExceptionReasonProbeDecision emptyProbe = { NO, NO, currentProbeCount };
    DDToAppsYieldExceptionOutcome outcome = {
        NO,
        DDToAppsYieldExceptionContinuationNone,
        NO,
        NO,
        NO,
        emptyProbe,
    };

    if (site == DDToAppsYieldExceptionSitePreYieldRouting) {
        outcome.shouldSwallowException = YES;
        outcome.continuation = DDToAppsYieldExceptionContinuationCallOriginal;
        return outcome;
    }

    if (site == DDToAppsYieldExceptionSiteDismissSideEffect ||
        site == DDToAppsYieldExceptionSiteHideSideEffect) {
        outcome.shouldSwallowException = YES;
        outcome.continuation = DDToAppsYieldExceptionContinuationContinueYieldSideEffects;
        return outcome;
    }

    if (site == DDToAppsYieldExceptionSiteDisconnectSideEffect) {
        outcome.shouldSwallowException = YES;
        outcome.continuation = DDToAppsYieldExceptionContinuationCallOriginal;
        outcome.yieldInProgressWouldRemainSet = YES;
        return outcome;
    }

    if (site == DDToAppsYieldExceptionSiteYieldLogSideEffect) {
        outcome.shouldSwallowException = YES;
        outcome.continuation = DDToAppsYieldExceptionContinuationContinueYieldCleanup;
        return outcome;
    }

    if (site == DDToAppsYieldExceptionSiteOriginalCallback) {
        outcome.shouldSwallowException = YES;
        outcome.continuation = DDToAppsYieldExceptionContinuationCleanupReturn;
        outcome.shouldApplyReasonProbeDecision = YES;
        outcome.probeExceptionWouldResumeUnwind = YES;
        outcome.reasonProbeDecision = DDResolveExceptionReasonProbeDecision(currentProbeCount,
                                                                             reasonSelectorSupported);
        return outcome;
    }

    if (site == DDToAppsYieldExceptionSiteCleanup) {
        outcome.continuation = DDToAppsYieldExceptionContinuationResumeUnwind;
    }
    return outcome;
}

DDOtherSettingsFlagClearDecision DDResolveOtherSettingsFlagClearDecision(BOOL settingsObjectPresent,
                                                                         BOOL otherSettingsPresent,
                                                                         BOOL flagSetterSupported) {
    // Exact pure eligibility from 421CC. The original sends _setFlag:0 forSetting:6 only when the
    // settings object exists, its private _otherSettings object resolves, and that object supports
    // the private setter. This reconstruction returns the fixed arguments but never sends them.
    DDOtherSettingsFlagClearDecision decision = { NO, 0, 6 };
    decision.shouldClear = settingsObjectPresent && otherSettingsPresent && flagSetterSupported;
    return decision;
}

DDOtherSettingsFlagClearExceptionOutcome DDResolveOtherSettingsFlagClearExceptionOutcome(void) {
    // 421CC protects exactly the private _otherSettings resolution/capability/_setFlag:forSetting:
    // range. Its typed catch swallows and jumps directly to outer-object cleanup. No reason probe,
    // setter retry, or alternate mutation path occurs.
    DDOtherSettingsFlagClearExceptionOutcome outcome = { YES, YES, YES };
    return outcome;
}

DDExceptionReasonProbeDecision DDResolveExceptionReasonProbeDecision(uint64_t currentProbeCount,
                                                                      BOOL reasonSelectorSupported) {
    // Raw ARM64 confirms the three exception catch paths eventually call 41BA0. Its global counter
    // allows exactly 20 attempts: counts 0..19 increment once; counts >19 do nothing. Reading the
    // exception's reason is separately gated by respondsToSelector:, and is not performed here.
    DDExceptionReasonProbeDecision decision = { NO, NO, currentProbeCount };
    if (currentProbeCount > 19) return decision;

    decision.withinBudget = YES;
    decision.shouldReadReason = reasonSelectorSupported;
    decision.nextProbeCount = currentProbeCount + 1;
    return decision;
}

DDSceneOrientationExceptionOutcome DDResolveSceneOrientationExceptionOutcome(DDSceneOrientationExceptionSite site,
                                                                              uint64_t currentProbeCount,
                                                                              BOOL reasonSelectorSupported) {
    // 40F0C LSDA maps the combined 41CBC + 3FAF8 decision range to a catch that resumes at the
    // original callback. A throw from the original callback has a distinct catch: the caught
    // exception is passed through 41BA0's bounded reason-probe path, then the hook forces false.
    DDExceptionReasonProbeDecision emptyProbe = { NO, NO, currentProbeCount };
    DDSceneOrientationExceptionOutcome outcome = {
        NO,
        NO,
        NO,
        NO,
        NO,
        emptyProbe,
    };

    if (site == DDSceneOrientationExceptionSiteDecisionPath) {
        outcome.shouldSwallowException = YES;
        outcome.shouldCallOriginalAfterCatch = YES;
        return outcome;
    }

    if (site == DDSceneOrientationExceptionSiteOriginalCallback) {
        outcome.shouldSwallowException = YES;
        outcome.shouldApplyReasonProbeDecision = YES;
        outcome.probeExceptionWouldResumeUnwind = YES;
        outcome.shouldForceFalseResultAfterProbe = YES;
        outcome.reasonProbeDecision = DDResolveExceptionReasonProbeDecision(currentProbeCount,
                                                                             reasonSelectorSupported);
    }
    return outcome;
}

DDSceneForegroundExceptionOutcome DDResolveSceneForegroundExceptionOutcome(DDSceneForegroundExceptionSite site,
                                                                            uint64_t currentProbeCount,
                                                                            BOOL reasonSelectorSupported) {
    // 40FF4 catches an original-callback throw separately from the foreground-forcing path. After
    // the original catch completes 41BA0 normally, execution resumes at the post-original host gate
    // and may still evaluate 41CBC plus the mutable-settings foreground path. Throws from 41CBC or
    // that mutable-settings path are swallowed and jump directly to cleanup, skipping the rest of
    // foreground forcing. A nested throw from 41BA0 ends the outer catch and resumes unwind.
    DDExceptionReasonProbeDecision emptyProbe = { NO, NO, currentProbeCount };
    DDSceneForegroundExceptionOutcome outcome = {
        NO,
        NO,
        NO,
        NO,
        NO,
        emptyProbe,
    };

    if (site == DDSceneForegroundExceptionSiteOriginalCallback) {
        outcome.shouldSwallowException = YES;
        outcome.shouldApplyReasonProbeDecision = YES;
        outcome.probeExceptionWouldResumeUnwind = YES;
        outcome.shouldContinueForegroundEvaluationAfterCatch = YES;
        outcome.reasonProbeDecision = DDResolveExceptionReasonProbeDecision(currentProbeCount,
                                                                             reasonSelectorSupported);
        return outcome;
    }

    if (site == DDSceneForegroundExceptionSiteRouteEligibility ||
        site == DDSceneForegroundExceptionSiteMutableSettingsPath) {
        outcome.shouldSwallowException = YES;
        outcome.shouldSkipRemainingForegroundForcing = YES;
    }
    return outcome;
}

DDSceneDestroyExceptionOutcome DDResolveSceneDestroyExceptionOutcome(DDSceneDestroyExceptionSite site,
                                                                      BOOL destroyRoutingPrepared,
                                                                      uint64_t currentProbeCount,
                                                                      BOOL reasonSelectorSupported) {
    // 41138 uses three materially different exception regions. The pre-original route/identity
    // range catches and rejoins at the original callback after restoring the saved identity register,
    // while preserving whatever destroy-routing gate state had already been established. The original
    // callback has its own catch, applies the existing 41BA0 reason probe, and then continues post-call
    // destroy routing only when that saved gate was prepared. The post-callback destroy-routing range
    // has no landing pad in 41138, so exceptions there leave this function and continue unwinding.
    DDExceptionReasonProbeDecision emptyProbe = { NO, NO, currentProbeCount };
    DDSceneDestroyExceptionOutcome outcome = {
        NO,
        NO,
        NO,
        NO,
        NO,
        NO,
        NO,
        NO,
        emptyProbe,
    };

    if (site == DDSceneDestroyExceptionSitePreOriginalRouting) {
        outcome.shouldSwallowException = YES;
        outcome.shouldCallOriginalAfterCatch = YES;
        outcome.shouldRestoreSavedIdentityAfterCatch = YES;
        outcome.preservesPreparedDestroyRoutingState = YES;
        outcome.shouldContinuePreparedDestroyRoutingAfterOriginal = destroyRoutingPrepared;
        return outcome;
    }

    if (site == DDSceneDestroyExceptionSiteOriginalCallback) {
        outcome.shouldSwallowException = YES;
        outcome.shouldApplyReasonProbeDecision = YES;
        outcome.probeExceptionWouldResumeUnwind = YES;
        outcome.preservesPreparedDestroyRoutingState = YES;
        outcome.shouldContinuePreparedDestroyRoutingAfterOriginal = destroyRoutingPrepared;
        outcome.reasonProbeDecision = DDResolveExceptionReasonProbeDecision(currentProbeCount,
                                                                             reasonSelectorSupported);
        return outcome;
    }

    if (site == DDSceneDestroyExceptionSitePostCallbackDestroyRouting) {
        outcome.exceptionWouldResumeUnwind = YES;
    }
    return outcome;
}

DDAVCSceneHandleExceptionOutcome DDResolveAVCSceneHandleExceptionOutcome(DDAVCSceneHandleExceptionSite site,
                                                                         BOOL scenePresent,
                                                                         uint64_t currentProbeCount,
                                                                         BOOL reasonSelectorSupported) {
    // 4138C has three catch continuations before its original callback. An exception while first
    // fetching the scene object skips all custom update/suppression work and calls original. Throws
    // during update routing (including 3F5C0/3E670) skip the rest of that update route but, when the
    // scene object is still present, rejoin at foreground-suppression evaluation; without a scene they
    // call original. Throws while evaluating suppression are swallowed and force the original call.
    // The original callback itself has a separate catch that applies 41BA0 and never retries it.
    DDExceptionReasonProbeDecision emptyProbe = { NO, NO, currentProbeCount };
    DDAVCSceneHandleExceptionOutcome outcome = {
        NO,
        NO,
        NO,
        NO,
        NO,
        NO,
        emptyProbe,
    };

    if (site == DDAVCSceneHandleExceptionSiteInitialSceneLookup) {
        outcome.shouldSwallowException = YES;
        outcome.shouldSkipRemainingUpdateRouting = YES;
        outcome.shouldCallOriginalAfterCatch = YES;
        return outcome;
    }

    if (site == DDAVCSceneHandleExceptionSiteUpdateRouting) {
        outcome.shouldSwallowException = YES;
        outcome.shouldSkipRemainingUpdateRouting = YES;
        outcome.shouldContinueSuppressionEvaluationAfterCatch = scenePresent;
        outcome.shouldCallOriginalAfterCatch = !scenePresent;
        return outcome;
    }

    if (site == DDAVCSceneHandleExceptionSiteSuppressionDecision) {
        outcome.shouldSwallowException = YES;
        outcome.shouldCallOriginalAfterCatch = YES;
        return outcome;
    }

    if (site == DDAVCSceneHandleExceptionSiteOriginalCallback) {
        outcome.shouldSwallowException = YES;
        outcome.shouldApplyReasonProbeDecision = YES;
        outcome.probeExceptionWouldResumeUnwind = YES;
        outcome.reasonProbeDecision = DDResolveExceptionReasonProbeDecision(currentProbeCount,
                                                                             reasonSelectorSupported);
    }
    return outcome;
}

DDPrivateIntegerIvarWritePlan DDResolvePrivateIntegerIvarWritePlan(BOOL ivarFound,
                                                                   NSInteger typeEncodingFirstByte) {
    // Pure 9C3BC write-width decision after 9C24C has already resolved the ivar/type encoding.
    // The original accepts only signed/unsigned char, short, int, and long long encodings.
    DDPrivateIntegerIvarWritePlan plan = {
        NO,
        NO,
        DDPrivateIvarWriteWidthUnsupported,
    };
    if (!ivarFound) return plan;

    switch (typeEncodingFirstByte) {
        case 'c':
        case 'C':
            plan.writeWidth = DDPrivateIvarWriteWidthByte;
            break;
        case 's':
        case 'S':
            plan.writeWidth = DDPrivateIvarWriteWidthWord;
            break;
        case 'i':
        case 'I':
            plan.writeWidth = DDPrivateIvarWriteWidthDWord;
            break;
        case 'q':
        case 'Q':
            plan.writeWidth = DDPrivateIvarWriteWidthQWord;
            break;
        default:
            plan.shouldRecordUnsupportedType = YES;
            return plan;
    }

    plan.shouldWrite = YES;
    return plan;
}

DDPrivateObjectIvarAccessPlan DDResolvePrivateObjectIvarAccessPlan(BOOL ivarFound,
                                                                   NSInteger typeEncodingFirstByte) {
    // Pure 9C4AC access decision after 9C24C. Only an Objective-C object encoding ('@') is read;
    // existing ivars with missing/non-object encodings are reported as unsupported by the original.
    DDPrivateObjectIvarAccessPlan plan = { NO, NO };
    if (!ivarFound) return plan;
    if (typeEncodingFirstByte == '@') {
        plan.shouldReadObject = YES;
    } else {
        plan.shouldRecordUnsupportedType = YES;
    }
    return plan;
}

NSString *DDBuildPrivateIvarDiagnosticKey(NSString *className, NSString *ivarName) {
    // Pure key construction from 9C2C4. The original falls back to "nil" when the object is nil
    // and to "?" when the ivar-name pointer is null, then formats the pair as <class>.<ivar>.
    NSString *resolvedClassName = className ?: @"nil";
    NSString *resolvedIvarName = ivarName ?: @"?";
    return [NSString stringWithFormat:@"%@.%@", resolvedClassName, resolvedIvarName];
}

BOOL DDShouldInsertPrivateIvarDiagnostic(BOOL alreadyRecorded) {
    // 9C2C4 lazily creates a mutable set and inserts only when containsObject: is false. The caller
    // supplies that membership result; this helper never touches the original set or unfair lock.
    return !alreadyRecorded;
}

DDSceneSettingsPrivateIvarPlan DDResolveSceneSettingsPrivateIvarPlan(double frameWidth,
                                                                     double frameHeight,
                                                                     BOOL frameIvarFound,
                                                                     NSString *frameTypeEncoding,
                                                                     BOOL foregroundIvarFound,
                                                                     NSString *foregroundTypeEncoding) {
    // Raw ARM64 for 41F50 reveals direct private-ivar writes omitted by the decompiler. Preserve the
    // exact decisions as data only: frame accepts a {CGRect= prefix; foreground accepts exact c/B.
    DDSceneSettingsPrivateIvarPlan plan = {
        DDPrivateSceneIvarActionNone,
        DDPrivateSceneIvarActionNone,
        { frameWidth, frameHeight },
        YES,
        NO,
    };

    BOOL frameHandled = frameWidth <= 0.0;
    if (frameWidth > 0.0) {
        if (!frameIvarFound) {
            frameHandled = NO;
        } else if (frameTypeEncoding != nil && [frameTypeEncoding hasPrefix:@"{CGRect="]) {
            plan.frameAction = DDPrivateSceneIvarActionWrite;
            frameHandled = YES;
        } else {
            plan.frameAction = DDPrivateSceneIvarActionRecordUnsupported;
            frameHandled = NO;
        }
    }

    BOOL foregroundHandled = NO;
    if (!foregroundIvarFound) {
        foregroundHandled = NO;
    } else if ([foregroundTypeEncoding isEqualToString:@"c"] ||
               [foregroundTypeEncoding isEqualToString:@"B"]) {
        plan.foregroundAction = DDPrivateSceneIvarActionWrite;
        foregroundHandled = YES;
    } else {
        plan.foregroundAction = DDPrivateSceneIvarActionRecordUnsupported;
    }

    plan.shouldAttemptFailureBudgetDecrement = !(frameHandled && foregroundHandled);
    return plan;
}

DDSceneSettingsPrivateIvarExceptionOutcome DDResolveSceneSettingsPrivateIvarExceptionOutcome(void) {
    // 41F50 has several typed protected ranges spanning frame/foreground ivar lookup and diagnostics,
    // force-IO/orientation repair, 9C3BC, nested 421CC, and direct foreground-offset resolution. Every
    // typed catch converges on 0x4210C and branches to 0x420C8, skipping the remaining private mutation
    // sequence and the dword_162F34 failure-budget decrement before normal retain/cleanup/return.
    DDSceneSettingsPrivateIvarExceptionOutcome outcome = { YES, YES, YES, YES };
    return outcome;
}

DDFBSUpdateExceptionOutcome DDResolveFBSUpdateExceptionOutcome(DDFBSUpdateExceptionSite site,
                                                                uint64_t currentProbeCount,
                                                                BOOL reasonSelectorSupported) {
    // 400D0 has stage-specific typed catches. Pre-settings preparation falls back to original;
    // the scene-settings catch rejoins at mutableSettings; the mutable-settings catch rejoins at
    // post-settings routing; later routing/frame/orientation/private-executor catches fall back to
    // original. The original callback itself has a separate 41BA0 catch/no-retry path. A nested
    // 41BA0 exception ends the catch and resumes unwind.
    DDExceptionReasonProbeDecision emptyProbe = { NO, NO, currentProbeCount };
    DDFBSUpdateExceptionOutcome outcome = {
        NO,
        DDFBSUpdateExceptionContinuationNone,
        NO,
        NO,
        emptyProbe,
    };

    if (site == DDFBSUpdateExceptionSitePreSettingsPreparation ||
        site == DDFBSUpdateExceptionSiteRoutingDecisionOrExecution) {
        outcome.shouldSwallowException = YES;
        outcome.continuation = DDFBSUpdateExceptionContinuationCallOriginal;
        return outcome;
    }

    if (site == DDFBSUpdateExceptionSiteSceneSettingsPath) {
        outcome.shouldSwallowException = YES;
        outcome.continuation = DDFBSUpdateExceptionContinuationContinueMutableSettings;
        return outcome;
    }

    if (site == DDFBSUpdateExceptionSiteMutableSettingsPath) {
        outcome.shouldSwallowException = YES;
        outcome.continuation = DDFBSUpdateExceptionContinuationContinuePostSettingsRouting;
        return outcome;
    }

    if (site == DDFBSUpdateExceptionSiteOriginalCallback) {
        outcome.shouldSwallowException = YES;
        outcome.continuation = DDFBSUpdateExceptionContinuationCleanupReturn;
        outcome.shouldApplyReasonProbeDecision = YES;
        outcome.probeExceptionWouldResumeUnwind = YES;
        outcome.reasonProbeDecision = DDResolveExceptionReasonProbeDecision(currentProbeCount,
                                                                             reasonSelectorSupported);
    }
    return outcome;
}

DDFBSSettingsCallbackExceptionOutcome DDResolveFBSSettingsCallbackExceptionOutcome(DDFBSSettingsCallbackExceptionSite site,
                                                                                    uint64_t currentProbeCount,
                                                                                    BOOL reasonSelectorSupported) {
    // 40514 sends every protected custom-path exception to one typed catch at 40A88, which swallows
    // and jumps directly to the original callback. The original callback itself has a separate catch
    // at 40AA4 that applies 41BA0 and, if the probe completes normally, resumes only final cleanup.
    // A nested 41BA0 throw lands at cleanup-only 40AD8 and resumes unwind.
    DDExceptionReasonProbeDecision emptyProbe = { NO, NO, currentProbeCount };
    DDFBSSettingsCallbackExceptionOutcome outcome = {
        NO,
        NO,
        NO,
        NO,
        NO,
        emptyProbe,
    };

    if (site == DDFBSSettingsCallbackExceptionSiteCustomPath) {
        outcome.shouldSwallowException = YES;
        outcome.shouldCallOriginalAfterCatch = YES;
        return outcome;
    }

    if (site == DDFBSSettingsCallbackExceptionSiteOriginalCallback) {
        outcome.shouldSwallowException = YES;
        outcome.shouldApplyReasonProbeDecision = YES;
        outcome.probeExceptionWouldResumeUnwind = YES;
        outcome.shouldContinueCleanupAfterProbe = YES;
        outcome.reasonProbeDecision = DDResolveExceptionReasonProbeDecision(currentProbeCount,
                                                                             reasonSelectorSupported);
    }
    return outcome;
}

DDFBSPresentationUpdateExceptionOutcome DDResolveFBSPresentationUpdateExceptionOutcome(DDFBSPresentationUpdateExceptionSite site,
                                                                                        uint64_t currentProbeCount,
                                                                                        BOOL reasonSelectorSupported) {
    // 40AE8 protects three materially different stages. An original-callback exception is swallowed,
    // probed through 41BA0, and then rejoins post-original nopresupdate/updateFrame evaluation if the
    // probe completes. The file-manager nopresupdate probe itself has no landing pad and propagates.
    // _updateFrameAndTransform capability/send exceptions are swallowed and jump directly to cleanup.
    DDExceptionReasonProbeDecision emptyProbe = { NO, NO, currentProbeCount };
    DDFBSPresentationUpdateExceptionOutcome outcome = {
        NO,
        NO,
        NO,
        NO,
        NO,
        NO,
        emptyProbe,
    };

    if (site == DDFBSPresentationUpdateExceptionSiteOriginalCallback) {
        outcome.shouldSwallowException = YES;
        outcome.shouldApplyReasonProbeDecision = YES;
        outcome.probeExceptionWouldResumeUnwind = YES;
        outcome.shouldContinuePostOriginalEvaluationAfterProbe = YES;
        outcome.reasonProbeDecision = DDResolveExceptionReasonProbeDecision(currentProbeCount,
                                                                             reasonSelectorSupported);
        return outcome;
    }

    if (site == DDFBSPresentationUpdateExceptionSiteNoPresentationUpdateFileProbe) {
        outcome.exceptionWouldResumeUnwind = YES;
        return outcome;
    }

    if (site == DDFBSPresentationUpdateExceptionSiteUpdateFrameAndTransform) {
        outcome.shouldSwallowException = YES;
        outcome.shouldContinueCleanupAfterCatch = YES;
    }
    return outcome;
}

DDCurrentInterfaceOrientationExceptionOutcome DDResolveCurrentInterfaceOrientationExceptionOutcome(void) {
    // 3FA90 LSDA 0x114A00 protects only respondsToSelector:interfaceOrientation plus the selector
    // send. Its landing at 0x3FAD4 unconditionally begins/ends catch and then returns zero.
    DDCurrentInterfaceOrientationExceptionOutcome outcome = { YES, 0 };
    return outcome;
}

NSInteger DDResolveCurrentInterfaceOrientation(BOOL settingsObjectPresent,
                                               BOOL interfaceOrientationSelectorSupported,
                                               NSInteger currentOrientation) {
    // Exact 3FA90 fallback: return the supplied orientation only when the settings object exists
    // and responds to interfaceOrientation; otherwise the original returns nil/zero.
    return (settingsObjectPresent && interfaceOrientationSelectorSupported) ? currentOrientation : 0;
}

DDFBSSceneSettingsUpdateDecision DDResolveFBSSceneSettingsUpdateDecision(DDHostSlotSize targetSize,
                                                                         BOOL slotSettingsMarked,
                                                                         BOOL frameSelectorSupported,
                                                                         double currentFrameWidth,
                                                                         NSInteger desiredOrientation,
                                                                         NSInteger currentOrientation) {
    // Pure post-41F50 decision from 400D0. This reports whether the original would request 3F5C0;
    // it never calls the private updateSettings executor or mutates the per-slot/counter state.
    DDFBSSceneSettingsUpdateDecision decision = {
        NO,
        DDFBSSceneSettingsUpdateReasonNone,
        targetSize,
    };
    if (targetSize.width <= 0.0) return decision;

    if (!slotSettingsMarked) {
        decision.shouldRequestUpdate = YES;
        decision.reason = DDFBSSceneSettingsUpdateReasonSlotNotMarked;
        return decision;
    }

    double effectiveCurrentFrameWidth = frameSelectorSupported ? currentFrameWidth : 0.0;
    if (fabs(effectiveCurrentFrameWidth - targetSize.width) > 0.5) {
        decision.shouldRequestUpdate = YES;
        decision.reason = DDFBSSceneSettingsUpdateReasonFrameWidthMismatch;
        return decision;
    }

    if (desiredOrientation != 0 && currentOrientation != 0 &&
        currentOrientation != desiredOrientation) {
        decision.shouldRequestUpdate = YES;
        decision.reason = DDFBSSceneSettingsUpdateReasonOrientationMismatch;
    }
    return decision;
}

BOOL DDPrivateUpdateSettingsMethodSignatureSupported(BOOL methodFound,
                                                     NSString *methodTypeEncoding) {
    // Exact 3F5C0 signature gate: method must exist, encoding must begin with void ('v'), and the
    // full encoding must contain the Objective-C block token "@?". No runtime method lookup here.
    return methodFound && methodTypeEncoding.length > 0 &&
        [methodTypeEncoding characterAtIndex:0] == 'v' &&
        [methodTypeEncoding containsString:@"@?"];
}

BOOL DDPrivateVoidIntegerSetterSignatureSupported(BOOL methodFound,
                                                  NSUInteger argumentCount,
                                                  NSInteger returnTypeFirstByte,
                                                  NSInteger valueArgumentTypeFirstByte) {
    // Exact data-only half of 3ECD0: 3 Objective-C args, void return, and q/Q value argument.
    return methodFound && argumentCount == 3 && returnTypeFirstByte == 'v' &&
        (((unsigned char)valueArgumentTypeFirstByte & 0xDFu) == 'Q');
}

DDFBSSceneSettingsExecutorDecision DDResolveFBSSceneSettingsExecutorDecision(BOOL sceneObjectPresent,
                                                                             DDHostSlotSize targetSize,
                                                                             BOOL executorReentrant,
                                                                             NSInteger attemptCount,
                                                                             BOOL geometryUpdatesEnabled,
                                                                             BOOL updateSettingsSelectorSupported,
                                                                             BOOL updateMethodFound,
                                                                             NSString *updateMethodTypeEncoding) {
    DDFBSSceneSettingsExecutorDecision decision = {
        DDFBSSceneSettingsExecutorAdmissionNone,
        DDFBSSceneSettingsExecutorCounterNone,
        NO,
        targetSize,
    };

    if (!sceneObjectPresent || !(targetSize.width > 0.0 && targetSize.height > 0.0)) {
        decision.kind = DDFBSSceneSettingsExecutorAdmissionInvalidInput;
        return decision;
    }
    if (executorReentrant) {
        decision.kind = DDFBSSceneSettingsExecutorAdmissionReentrant;
        decision.counterKind = DDFBSSceneSettingsExecutorCounterGeneralFailure;
        return decision;
    }
    if (attemptCount >= 13) {
        decision.kind = DDFBSSceneSettingsExecutorAdmissionAttemptLimit;
        decision.counterKind = DDFBSSceneSettingsExecutorCounterAttemptLimit;
        return decision;
    }
    if (!geometryUpdatesEnabled || !updateSettingsSelectorSupported) {
        decision.kind = DDFBSSceneSettingsExecutorAdmissionCapabilityUnavailable;
        return decision;
    }
    if (!DDPrivateUpdateSettingsMethodSignatureSupported(updateMethodFound,
                                                         updateMethodTypeEncoding)) {
        decision.kind = DDFBSSceneSettingsExecutorAdmissionInvalidMethodSignature;
        decision.counterKind = DDFBSSceneSettingsExecutorCounterSignatureFailure;
        return decision;
    }

    decision.kind = DDFBSSceneSettingsExecutorAdmissionDispatch;
    decision.shouldIncrementAttemptCount = YES;
    return decision;
}

DDFBSSceneSettingsMutationPlan DDResolveFBSSceneSettingsMutationPlan(BOOL settingsObjectPresent,
                                                                     DDHostSlotSize targetSize,
                                                                     BOOL frameSetterSupported,
                                                                     NSInteger desiredOrientation,
                                                                     BOOL orientationSetterSignatureSupported,
                                                                     NSInteger currentOrientation) {
    DDFBSSceneSettingsMutationPlan plan = {
        NO,
        targetSize,
        NO,
        desiredOrientation,
        0,
        NO,
    };
    if (!settingsObjectPresent) return plan;

    plan.shouldSetFrame = frameSetterSupported;
    if (desiredOrientation == 0 || !orientationSetterSignatureSupported ||
        currentOrientation == 0 || currentOrientation == desiredOrientation) {
        return plan;
    }

    plan.shouldSetInterfaceOrientation = YES;
    plan.previousOrientation = currentOrientation;
    plan.shouldRecordOrientationChange = YES;
    return plan;
}

DDFBSSceneSettingsMutationExceptionOutcome DDResolveFBSSceneSettingsMutationExceptionOutcome(DDFBSSceneSettingsMutationExceptionSite site) {
    // 3F990 LSDA 0x1149D4 has one frame-path catch that rejoins orientation processing and one
    // common orientation catch that skips the remainder of mutation and returns through cleanup.
    // Both landing bodies resume unwind for a nonmatching catch discriminator.
    DDFBSSceneSettingsMutationExceptionOutcome outcome = { NO, NO, NO, NO };
    if (site == DDFBSSceneSettingsMutationExceptionSiteFramePath) {
        outcome.shouldSwallowException = YES;
        outcome.shouldContinueOrientationAfterCatch = YES;
        outcome.nonmatchingCatchTypeWouldResumeUnwind = YES;
        return outcome;
    }
    if (site == DDFBSSceneSettingsMutationExceptionSiteOrientationPath) {
        outcome.shouldSwallowException = YES;
        outcome.shouldContinueCleanupAfterCatch = YES;
        outcome.nonmatchingCatchTypeWouldResumeUnwind = YES;
    }
    return outcome;
}

DDFBSSceneSettingsExecutionAdmission DDResolveFBSSceneSettingsExecutionAdmission(uint64_t capturedGeneration,
                                                                                 uint64_t currentGeneration,
                                                                                 BOOL executorReentrant) {
    // Exact 3F7C8 entry gate: stale generation stops silently; matching generation still stops
    // when the executor-reentrant bit is already set. Only the accepted path enters reentrancy.
    DDFBSSceneSettingsExecutionAdmission admission = {
        DDFBSSceneSettingsExecutionAdmissionGenerationMismatch,
        NO,
    };
    if (capturedGeneration != currentGeneration) return admission;
    if (executorReentrant) {
        admission.kind = DDFBSSceneSettingsExecutionAdmissionReentrant;
        return admission;
    }

    admission.kind = DDFBSSceneSettingsExecutionAdmissionInvoke;
    admission.shouldEnterReentrantState = YES;
    return admission;
}

DDFBSSceneSettingsInvocationOutcome DDResolveFBSSceneSettingsInvocationOutcome(NSInteger slotIndex,
                                                                                BOOL invocationThrewException,
                                                                                BOOL orientationChanged) {
    // Raw ARM64 confirms the 3F7C8 post-invocation behavior. Exception exits use a dedicated
    // counter and never mark the slot. Normal returns mark unsigned slots 0..2, then choose the
    // orientation-changed or general counter. All entered paths clear the reentrant state.
    DDFBSSceneSettingsInvocationOutcome outcome = {
        NO,
        slotIndex,
        DDFBSSceneSettingsInvocationCounterNone,
        NO,
        NO,
    };
    outcome.shouldClearReentrantState = YES;

    if (invocationThrewException) {
        outcome.counterKind = DDFBSSceneSettingsInvocationCounterException;
        outcome.shouldAttemptCounterDecrement = YES;
        return outcome;
    }

    outcome.shouldMarkSlot = ((NSUInteger)slotIndex <= 2);
    outcome.counterKind = orientationChanged
        ? DDFBSSceneSettingsInvocationCounterOrientationChanged
        : DDFBSSceneSettingsInvocationCounterGeneral;
    outcome.shouldAttemptCounterDecrement = YES;
    return outcome;
}

DDFBSSceneSettingsExecutorExceptionOutcome DDResolveFBSSceneSettingsExecutorExceptionOutcome(DDFBSSceneSettingsExecutorExceptionSite site,
                                                                                              NSInteger currentExceptionCounter) {
    // 3F5C0 has no LSDA entry of its own, so exceptions from its Objective-C/runtime/helper calls
    // propagate to the caller. If the throw occurs after dword_163E88 was incremented, that attempt
    // count is not rolled back. 3F7C8 does have LSDA 0x1149B4: only the private selector invocation
    // at 3F890..3F8A0 is typed-caught. The expected catch decrements dword_162F2C only when positive,
    // never marks a slot, then clears reentrancy and disposes captures. A nonmatching catch type takes
    // the cleanup/resume-unwind path and notably does not clear byte_163E9B before unwinding.
    DDFBSSceneSettingsExecutorExceptionOutcome outcome = {
        NO,
        NO,
        NO,
        NO,
        DDFBSSceneSettingsInvocationCounterNone,
        NO,
        currentExceptionCounter,
        NO,
        NO,
        NO,
        NO,
    };

    if (site == DDFBSSceneSettingsExecutorExceptionSiteOuterBeforeAttemptIncrement) {
        outcome.exceptionWouldResumeUnwind = YES;
        return outcome;
    }

    if (site == DDFBSSceneSettingsExecutorExceptionSiteOuterAfterAttemptIncrement) {
        outcome.exceptionWouldResumeUnwind = YES;
        outcome.attemptCountWouldRemainIncremented = YES;
        return outcome;
    }

    if (site == DDFBSSceneSettingsExecutorExceptionSitePrivateInvocation) {
        outcome.shouldSwallowException = YES;
        outcome.counterKind = DDFBSSceneSettingsInvocationCounterException;
        outcome.shouldDecrementExceptionCounter = currentExceptionCounter > 0;
        if (outcome.shouldDecrementExceptionCounter) {
            outcome.nextExceptionCounter = currentExceptionCounter - 1;
        }
        outcome.shouldClearReentrantState = YES;
        outcome.shouldDisposeInvocationCaptures = YES;
        outcome.nonmatchingCatchTypeWouldResumeUnwind = YES;
        outcome.nonmatchingCatchTypeWouldClearReentrantState = NO;
    }
    return outcome;
}

NSInteger DDResolvePaneSettingsOrientation(BOOL isAuxScene, NSInteger auxOrientation) {
    // Pure decision from 3F75C + 3FAF8 after the caller has already determined whether the
    // settings/scene belongs to the aux bundle. Landscape override and nopaneorient both force 0.
    DDRefreshGenerationScopedGeometryStateIfNeeded();
    if (gDDPaneOrientationDisabled || gDDHostLandscapeOverrideOrientation != 0) return 0;
    if (DDSceneSettingsHasInterfaceOrientationIvar()) return 0;

    NSInteger candidate = (isAuxScene && auxOrientation != 0)
        ? auxOrientation
        : gDDHostMirrorOrientation;
    return (candidate >= 1 && candidate <= 4) ? candidate : 0;
}

BOOL DDUpdateHostSlotRenderSize(NSUInteger slotIndex, DDHostSlotSize size) {
    // Evidence-safe state/IPC half of 3F3F0. Raw size + uiapp.state use the unswapped size;
    // only the subsequent private scene-layout call applies the landscape swap transform.
    if (slotIndex > 2 || ![NSThread isMainThread] || !gDDHostMirrorActive ||
        gDDHostMirrorSlotCount <= slotIndex || gDDHostMirrorCarPlayUI[slotIndex] ||
        size.width < 1.0 || size.height < 1.0) {
        return NO;
    }

    NSString *bundleIdentifier = gDDHostMirrorBids[slotIndex] ?: @"";
    if (bundleIdentifier.length == 0) return NO;

    gDDHostMirrorSizes[slotIndex] = size;
    DDPostUIAppState(bundleIdentifier, YES, gDDHostMirrorOrientation, YES,
                     size.width, size.height);

    // Original 3F3F0 then resets two private counters, probes the hosted scene, applies
    // DDApplyLandscapeSwapToSize-equivalent dimensions, and calls sub_3F5C0. Omitted here.
    return YES;
}

void DDSetHostSlotCarPlayUI(NSUInteger slotIndex, BOOL carPlayUI) {
    // 3D6EC writes the raw CarPlay-UI flag for any physical slot 0..2, independent of slotCount.
    if (slotIndex <= 2) gDDHostMirrorCarPlayUI[slotIndex] = carPlayUI;
}

BOOL DDConvertHostSlotToCarPlayUI(NSUInteger slotIndex) {
    // Evidence-safe state/IPC half of 3D704. Return value is the precondition result, so an
    // already-CarPlay slot still returns YES. Private hosted-view remove/invalidate is omitted.
    BOOL valid = slotIndex < 3 && [NSThread isMainThread] && gDDHostMirrorSlotCount > slotIndex;
    if (valid && !gDDHostMirrorCarPlayUI[slotIndex]) {
        NSString *bundleIdentifier = [gDDHostMirrorBids[slotIndex] copy] ?: @"";
        if (bundleIdentifier.length > 0) {
            DDPostUIAppState(bundleIdentifier, NO, gDDHostMirrorOrientation, YES, 0.0, 0.0);
        }
        gDDHostMirrorBids[slotIndex] = bundleIdentifier;
        gDDHostMirrorCarPlayUI[slotIndex] = YES;
    }
    return valid;
}

void DDDismissHostMirror(void) {
    // Evidence-safe state/IPC half of 3D8A8/3D990. The original first tears down private
    // hosted/aux views; this reconstruction owns no such objects, so it preserves the exact
    // per-slot bridge-off broadcasts and reset ordering only.
    void (^dismissBlock)(void) = ^{
        for (NSUInteger index = 0; index < 3; index++) {
            NSString *bundleIdentifier = gDDHostMirrorBids[index] ?: @"";
            if (bundleIdentifier.length == 0 || gDDHostMirrorCarPlayUI[index]) continue;
            DDPostUIAppState(bundleIdentifier, NO, gDDHostMirrorOrientation,
                             index == 0 ? NO : YES, 0.0, 0.0);
        }
        DDResetHostSlotMirror();
    };

    if ([NSThread isMainThread]) {
        dismissBlock();
    } else {
        dispatch_async(dispatch_get_main_queue(), dismissBlock);
    }
}

NSDictionary *DDCurrentHostSlotMirror(void) {
    NSMutableArray *bids = [NSMutableArray arrayWithCapacity:gDDHostMirrorSlotCount];
    NSMutableArray *sizes = [NSMutableArray arrayWithCapacity:gDDHostMirrorSlotCount];
    NSMutableArray *carPlay = [NSMutableArray arrayWithCapacity:gDDHostMirrorSlotCount];
    for (NSUInteger index = 0; index < gDDHostMirrorSlotCount && index < 3; index++) {
        [bids addObject:gDDHostMirrorBids[index] ?: @""];
        [sizes addObject:@{
            @"width": @(gDDHostMirrorSizes[index].width),
            @"height": @(gDDHostMirrorSizes[index].height),
        }];
        [carPlay addObject:@(gDDHostMirrorCarPlayUI[index])];
    }
    return @{
        @"active": @(gDDHostMirrorActive),
        @"split": @(gDDHostMirrorSplit),
        @"slotCount": @(gDDHostMirrorSlotCount),
        @"generation": @(gDDHostMirrorGeneration),
        @"orientation": @(gDDHostMirrorOrientation),
        @"landscapeOverrideOrientation": @(gDDHostLandscapeOverrideOrientation),
        @"landscapeSwap": @(gDDHostLandscapeSwap),
        @"landscapeCSwap": @(gDDHostLandscapeCSwap),
        @"landscapeRotationDegrees": @(gDDHostLandscapeRotationDegrees),
        @"bundleIdentifiers": bids,
        @"sizes": sizes,
        @"carPlayUI": carPlay,
    };
}

static NSInteger DDHostMirrorIndexForBundle(NSString *bundleIdentifier) {
    if (!gDDHostMirrorActive) return NSNotFound;
    return DDConfiguredHostSlotIndexForBundleIdentifier(bundleIdentifier, NO);
}

static NSArray<NSString *> *DDHostMirrorNonCarPlayBundleIdentifiers(void) {
    NSMutableArray<NSString *> *result = [NSMutableArray array];
    if (!gDDHostMirrorActive) return result;
    for (NSUInteger index = 0; index < gDDHostMirrorSlotCount && index < 3; index++) {
        NSString *bid = gDDHostMirrorBids[index] ?: @"";
        if (!gDDHostMirrorCarPlayUI[index] && bid.length > 0) [result addObject:bid];
    }
    return result;
}

void DDScheduleAppSideHandshake(void) {
    // 3B738 + 3ED88: capture slot0 bid/size/orientation/generation, then retry at the
    // five off_154160 delays. Each block requires same generation + active + same slot0 bid.
    NSString *bundleIdentifier = [gDDHostMirrorBids[0] copy] ?: @"";
    DDHostSlotSize capturedSize = gDDHostMirrorSizes[0];
    NSInteger capturedOrientation = gDDHostMirrorOrientation;
    uint64_t capturedGeneration = gDDHostMirrorGeneration;

    for (NSUInteger index = 0; index < sizeof(kDDHostRetryDelays) / sizeof(kDDHostRetryDelays[0]); index++) {
        double delay = kDDHostRetryDelays[index];
        dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(delay * (double)NSEC_PER_SEC)),
                       dispatch_get_main_queue(), ^{
            if (gDDHostMirrorGeneration != capturedGeneration || !gDDHostMirrorActive) return;
            NSString *current = gDDHostMirrorBids[0] ?: @"";
            if (![current isEqualToString:bundleIdentifier]) return;
            DDPostUIAppState(bundleIdentifier, YES, capturedOrientation, NO,
                             capturedSize.width, capturedSize.height);
        });
    }
}

void DDScheduleGeometryPushesForSlot(NSUInteger slotIndex) {
    // 3D4FC + 3DC38: schedule only a valid, non-CarPlay slot with a non-empty bid.
    if (slotIndex > 2) return;
    NSString *bundleIdentifier = [gDDHostMirrorBids[slotIndex] copy] ?: @"";
    if (bundleIdentifier.length == 0 || gDDHostMirrorCarPlayUI[slotIndex]) return;

    DDHostSlotSize capturedSize = gDDHostMirrorSizes[slotIndex];
    NSInteger capturedOrientation = gDDHostMirrorOrientation;
    uint64_t capturedGeneration = gDDHostMirrorGeneration;

    for (NSUInteger index = 0; index < sizeof(kDDHostRetryDelays) / sizeof(kDDHostRetryDelays[0]); index++) {
        double delay = kDDHostRetryDelays[index];
        dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(delay * (double)NSEC_PER_SEC)),
                       dispatch_get_main_queue(), ^{
            if (gDDHostMirrorGeneration != capturedGeneration || !gDDHostMirrorActive) return;
            NSInteger currentIndex = DDHostMirrorIndexForBundle(bundleIdentifier);
            if (currentIndex == NSNotFound) return;

            DDHostSlotSize size = gDDHostMirrorSizes[(NSUInteger)currentIndex];
            if (size.width < 1.0 || size.height < 1.0) size = capturedSize;
            DDPostUIAppState(bundleIdentifier, YES, capturedOrientation, YES,
                             size.width, size.height);
        });
    }
}

static NSString * _Nullable DDTemporaryMarkerPath(NSString *name) {
    // sub_42F10: look in NSTemporaryDirectory; for duodash_* also accept legacy carnav_*.
    NSString *temporaryDirectory = NSTemporaryDirectory();
    if (temporaryDirectory.length == 0 || name.length == 0) return nil;

    NSFileManager *fm = [NSFileManager defaultManager];
    NSString *path = [temporaryDirectory stringByAppendingPathComponent:name];
    if ([fm fileExistsAtPath:path]) return path;
    if (![name hasPrefix:@"duodash_"]) return nil;

    NSString *legacyName = [@"carnav_" stringByAppendingString:[name substringFromIndex:8]];
    NSString *legacyPath = [temporaryDirectory stringByAppendingPathComponent:legacyName];
    return [fm fileExistsAtPath:legacyPath] ? legacyPath : nil;
}

static void DDConsumeUIAppStateUserInfo(NSDictionary *userInfo) {
    // 4407C parsing/defaults; UI mutation calls are represented by the compile-safe cache only.
    gDDUIAppStateGeneration++;
    NSDictionary *info = [userInfo isKindOfClass:[NSDictionary class]] ? userInfo : @{};

    BOOL shouldBridge = [info[@"shouldBridge"] boolValue];
    double width = [info[@"displayWidth"] doubleValue];
    double height = [info[@"displayHeight"] doubleValue];
    id orientationValue = info[@"orientation"];
    NSInteger orientation = orientationValue ? [orientationValue integerValue] : 1;
    BOOL split = [info[@"isSplit"] boolValue];

    NSString *signature = [NSString stringWithFormat:@"%d|%.1fx%.1f|%ld|%d",
                           shouldBridge, width, height, (long)orientation, split];
    if (![signature isEqualToString:gDDUIAppStateSignature]) gDDUIAppStateSignature = [signature copy];
    gDDUIAppSplit = split;

    id floorValue = info[@"bridged_font_floor"];
    NSInteger floor = [floorValue isKindOfClass:[NSNumber class]] ? [floorValue integerValue] : 0;
    gDDUIAppFontFloor = MAX((NSInteger)0, floor);

    id keyPaneValue = info[@"keypane_enabled"];
    gDDUIAppKeyPaneEnabled = [keyPaneValue isKindOfClass:[NSNumber class]] ? [keyPaneValue boolValue] : YES;
    DDSetCachedUIAppBridgeState(shouldBridge, width, height, orientation);
}

static void DDConsumeUIAppFontFloorUserInfo(NSDictionary *userInfo) {
    NSDictionary *info = [userInfo isKindOfClass:[NSDictionary class]] ? userInfo : @{};
    id floorValue = info[@"bridged_font_floor"];
    NSInteger floor = [floorValue isKindOfClass:[NSNumber class]] ? [floorValue integerValue] : 0;
    NSInteger previous = gDDUIAppFontFloor;
    gDDUIAppFontFloor = MAX((NSInteger)0, floor);
    gDDUIAppFontFloorActive = gDDUIAppBridging && gDDUIAppFontFloor > 0;
    (void)previous;
    // 444C4 also restores/reapplies tracked UIFont objects via 434C4/4346C; omitted here.
}

static void DDConsumeUIAppKeyPaneUserInfo(NSDictionary *userInfo) {
    NSDictionary *info = [userInfo isKindOfClass:[NSDictionary class]] ? userInfo : @{};
    id value = info[@"keypane_enabled"];
    gDDUIAppKeyPaneEnabled = [value isKindOfClass:[NSNumber class]] ? [value boolValue] : YES;
    // 443FC routes this into 448B4 keyboard/window teardown state; private UI effects omitted.
}

BOOL DDPostUIAppFontFloorState(NSString * _Nullable bundleIdentifier) {
    // Per-bundle payload inside sub_291F4 after the cached 7EA4 refresh.
    NSString *bundle = bundleIdentifier ?: @"";
    NSDictionary *payload = @{
        @"bridged_font_floor": @(gDDBridgedFontFloor),
        @"bundleIdentifier": bundle,
    };
    return DDPostDistributedNotification(@"com.sensetechlab.appbridge.uiapp.fontfloor", bundle, payload);
}

BOOL DDPostUIAppKeyPaneState(NSString * _Nullable bundleIdentifier) {
    // Per-bundle payload inside sub_29400 after the cached 8058 refresh.
    NSString *bundle = bundleIdentifier ?: @"";
    NSDictionary *payload = @{
        @"keypane_enabled": @(gDDKeyPaneEnabled),
        @"bundleIdentifier": bundle,
    };
    return DDPostDistributedNotification(@"com.sensetechlab.appbridge.uiapp.keypane", bundle, payload);
}

void DDAppendHostFrameMetrics(NSMutableDictionary *payload,
                              const DDHostFrameMetrics *metrics) {
    // sub_8F34 reads exactly these offsets from the 104-byte metrics snapshot.
    if (!payload || !metrics) return;
    payload[@"frameX"] = @(metrics->frameX);
    payload[@"frameY"] = @(metrics->frameY);
    payload[@"frameW"] = @(metrics->frameWidth);
    payload[@"frameH"] = @(metrics->frameHeight);
    payload[@"frameWinX"] = @(metrics->windowX);
    payload[@"frameWinY"] = @(metrics->windowY);
    payload[@"frameWinW"] = @(metrics->windowWidth);
    payload[@"frameWinH"] = @(metrics->windowHeight);
    payload[@"frameWinValid"] = @(metrics->windowValid);
    payload[@"cpWinW"] = @(metrics->carPlayWindowWidth);
    payload[@"cpWinH"] = @(metrics->carPlayWindowHeight);
}

BOOL DDPostHostRequest(NSString * _Nullable bundleIdentifier,
                       BOOL activate,
                       const DDHostFrameMetrics *metrics) {
    // sub_8DF8: base fields, then sub_8F34 frame metadata, then host.request post.
    NSMutableDictionary *payload = [@{
        @"bundleIdentifier": bundleIdentifier ?: @"",
        @"activate": @(activate),
    } mutableCopy];
    DDAppendHostFrameMetrics(payload, metrics);
    return DDPostDistributedNotification(@"com.sensetechlab.appbridge.host.request", nil, payload);
}

BOOL DDPostSplitHostRequest(NSString * _Nullable leftBundleIdentifier,
                            NSString * _Nullable rightBundleIdentifier,
                            NSString * _Nullable centerBundleIdentifier,
                            NSInteger layout,
                            BOOL activate,
                            BOOL skipEvict,
                            BOOL environmentOnly,
                            const DDHostFrameMetrics *metrics) {
    // sub_91B4: seven base fields, sub_8F34 frame metadata, then split request post.
    NSMutableDictionary *payload = [@{
        @"bundleIdL": leftBundleIdentifier ?: @"",
        @"bundleIdR": rightBundleIdentifier ?: @"",
        @"bundleIdC": centerBundleIdentifier ?: @"",
        @"layout": @(layout),
        @"activate": @(activate),
        @"skipEvict": @(skipEvict),
        @"envOnly": @(environmentOnly),
    } mutableCopy];
    DDAppendHostFrameMetrics(payload, metrics);
    return DDPostDistributedNotification(@"com.sensetechlab.appbridge.host.request.split", nil, payload);
}

BOOL DDPostCarPlayUIStatus(uint64_t generation,
                           NSString * _Nullable bundleIdentifier,
                           BOOL ok,
                           NSString * _Nullable reason) {
    // sub_986C exact four-field status payload.
    NSDictionary *payload = @{
        @"cpuiGen": @(generation),
        @"cpuiBid": bundleIdentifier ?: @"",
        @"cpuiOk": @(ok),
        @"cpuiWhy": reason ?: @"",
    };
    return DDPostDistributedNotification(@"com.sensetechlab.appbridge.cpui.status", nil, payload);
}

BOOL DDPostHostRefusedState(NSString * _Nullable reason) {
    // sub_97A0: nil reason canonicalizes to "?".
    NSDictionary *payload = @{
        @"hostRefused": @YES,
        @"refuseReason": reason ?: @"?",
    };
    return DDPostDistributedNotification(@"com.sensetechlab.appbridge.host.state", nil, payload);
}

BOOL DDPostHostState(BOOL activated,
                     NSString * _Nullable bundleIdentifier,
                     NSString * _Nullable carPlayUIBundleIdentifier,
                     NSArray * _Nullable carPlayUIMore,
                     NSArray * _Nullable killedBundleIdentifiers,
                     uint64_t carPlayUIGeneration,
                     double rectX,
                     double rectY,
                     double rectWidth,
                     double rectHeight) {
    // sub_9424 exact dictionary schema/order-independent semantics.
    NSMutableDictionary *payload = [@{
        @"activated": @(activated),
        @"bundleIdentifier": bundleIdentifier ?: @"",
        @"sbPid": @(getpid()),
    } mutableCopy];

    BOOL hasMain = carPlayUIBundleIdentifier.length > 0;
    BOOL hasMore = carPlayUIMore.count > 0;
    if (hasMain) {
        payload[@"cpuiBid"] = carPlayUIBundleIdentifier;
        payload[@"cpuiRectX"] = @(rectX);
        payload[@"cpuiRectY"] = @(rectY);
        payload[@"cpuiRectW"] = @(rectWidth);
        payload[@"cpuiRectH"] = @(rectHeight);
    }
    if (hasMore) payload[@"cpuiMore"] = [carPlayUIMore copy];
    if (hasMain || hasMore) payload[@"cpuiGen"] = @(carPlayUIGeneration);
    if (killedBundleIdentifiers.count > 0 && (hasMain || hasMore)) {
        payload[@"cpuiKilled"] = [killedBundleIdentifiers copy];
    }

    return DDPostDistributedNotification(@"com.sensetechlab.appbridge.host.state", nil, payload);
}

static void DDConsumeHostUIAppRequestUserInfo(NSDictionary *userInfo) {
    // 3F224: resolve the requested bundle against up to three active non-CarPlay slots and
    // publish uiapp.state only when the matched slot width is positive.
    NSDictionary *info = [userInfo isKindOfClass:[NSDictionary class]] ? userInfo : @{};
    id rawBundle = info[@"bundleIdentifier"];
    NSString *bundleIdentifier = [rawBundle isKindOfClass:[NSString class]] ? rawBundle : @"";
    NSInteger slotIndex = DDHostMirrorIndexForBundle(bundleIdentifier);
    if (slotIndex == NSNotFound) return;

    DDHostSlotSize size = gDDHostMirrorSizes[(NSUInteger)slotIndex];
    if (size.width > 0.0) {
        DDPostUIAppState(bundleIdentifier, YES, gDDHostMirrorOrientation, gDDHostMirrorSplit,
                         size.width, size.height);
    }
}

@interface DDReconstructionHostUIAppResponder : NSObject
@end

@implementation DDReconstructionHostUIAppResponder
- (void)onUIAppRequest:(NSNotification *)notification {
    DDConsumeHostUIAppRequestUserInfo(notification.userInfo);
}
@end

static DDReconstructionHostUIAppResponder *gDDHostUIAppResponder = nil;

static void DDStartSpringBoardUIAppResponder(void) {
    // 27E20 + 3F224 compile-safe receiver half. The host-slot mirror is intentionally separate
    // from private scene creation; until a host builder populates it, requests correctly no-op.
    if (gDDHostUIAppResponder) return;
    gDDHostUIAppResponder = [DDReconstructionHostUIAppResponder new];
    DDObserveDistributedNotification(@"com.sensetechlab.appbridge.uiapp.request",
                                     gDDHostUIAppResponder,
                                     @selector(onUIAppRequest:),
                                     nil);
}

@interface DDReconstructionUIAppObserver : NSObject
@end

@implementation DDReconstructionUIAppObserver

- (void)onState:(NSNotification *)notification {
    DDConsumeUIAppStateUserInfo(notification.userInfo);
}

- (void)onFontFloor:(NSNotification *)notification {
    DDConsumeUIAppFontFloorUserInfo(notification.userInfo);
}

- (void)onKeyPaneSwitch:(NSNotification *)notification {
    DDConsumeUIAppKeyPaneUserInfo(notification.userInfo);
}

- (void)onActive:(NSNotification *)notification {
    (void)notification;
    NSString *bundleIdentifier = [NSBundle mainBundle].bundleIdentifier ?: @"";
    DDPostUIAppRequest(bundleIdentifier);

    // 445F8/447C0: when currently bridging, require a fresh onState within 3 seconds unless
    // duodash_ab_nostatetimeout (or legacy carnav_ alias) exists in the app temp directory.
    if (gDDUIAppBridging) {
        uint32_t generation = gDDUIAppStateGeneration;
        dispatch_after(dispatch_time(DISPATCH_TIME_NOW, 3LL * NSEC_PER_SEC),
                       dispatch_get_main_queue(), ^{
            if (gDDUIAppStateGeneration != generation || !gDDUIAppBridging) return;
            if (DDTemporaryMarkerPath(@"duodash_ab_nostatetimeout")) return;
            DDSetCachedUIAppBridgeState(NO, 0.0, 0.0, gDDUIAppOrientation);
        });
    }
}

- (void)onBackground:(NSNotification *)notification {
    (void)notification;
    // 446E4: non-bridging always normalizes state; bridging stays alive in background unless
    // duodash_ab_bg_teardown (or the legacy carnav_ alias) is present.
    if (!gDDUIAppBridging || DDTemporaryMarkerPath(@"duodash_ab_bg_teardown")) {
        DDSetCachedUIAppBridgeState(NO, 0.0, 0.0, gDDUIAppOrientation);
    }
}

@end

static DDReconstructionUIAppObserver *gDDUIAppObserver = nil;

static void DDStartUIAppIPC(void) {
    // sub_4CBDC evidence-safe UIApp half. The key-probe/keyboard observers in the second half
    // remain excluded because their callbacks mutate private UIKit/input state.
    if (getenv("DUODASH_AB_UIAPP_IPC_HOOKED")) return;
    setenv("DUODASH_AB_UIAPP_IPC_HOOKED", "1", 1);

    NSString *bundleIdentifier = [NSBundle mainBundle].bundleIdentifier ?: @"";
    gDDUIAppObserver = [DDReconstructionUIAppObserver new];

    DDObserveDistributedNotification(@"com.sensetechlab.appbridge.uiapp.state",
                                     gDDUIAppObserver,
                                     @selector(onState:),
                                     bundleIdentifier);
    DDObserveDistributedNotification(@"com.sensetechlab.appbridge.uiapp.fontfloor",
                                     gDDUIAppObserver,
                                     @selector(onFontFloor:),
                                     bundleIdentifier);
    DDObserveDistributedNotification(@"com.sensetechlab.appbridge.uiapp.keypane",
                                     gDDUIAppObserver,
                                     @selector(onKeyPaneSwitch:),
                                     bundleIdentifier);

    NSNotificationCenter *center = [NSNotificationCenter defaultCenter];
    [center addObserver:gDDUIAppObserver
               selector:@selector(onActive:)
                   name:@"UIApplicationDidBecomeActiveNotification"
                 object:nil];
    [center addObserver:gDDUIAppObserver
               selector:@selector(onBackground:)
                   name:@"UIApplicationDidEnterBackgroundNotification"
                 object:nil];

    DDPostUIAppRequest(bundleIdentifier);
}

static void DDReloadAppBridge(CFNotificationCenterRef center,
                              void *observer,
                              CFStringRef name,
                              const void *object,
                              CFDictionaryRef userInfo) {
    (void)center; (void)observer; (void)name; (void)object; (void)userInfo;
    // Mirrors the evidence-safe half of sub_29198: 74C8 republish. The following
    // private 792C4 side effect remains out of the executable target until resolved.
    DDRepublishKnownAppBridgeSnapshot(NULL);
}

static id _Nullable DDSharedDDz2(void) {
    Class ddz2Class = NSClassFromString(@"DDz2");
    SEL sharedSelector = NSSelectorFromString(@"shared");
    if (!ddz2Class || ![ddz2Class respondsToSelector:sharedSelector]) return nil;
    id (*sendShared)(id, SEL) = (void *)objc_msgSend;
    return sendShared(ddz2Class, sharedSelector);
}

static NSArray<NSString *> *DDHostedNonCarPlayBundleIdentifiers(id ddz2) {
    // sub_29810: prefer hostedSlotBids; if empty, fall back to hostedBundleId/hostedBundleId2.
    // Exclude slot entries whose matching hostedSlotIsCarPlayUI flag is true; no dedup.
    if (!ddz2) return DDHostMirrorNonCarPlayBundleIdentifiers();

    id (*sendObject)(id, SEL) = (void *)objc_msgSend;
    NSArray *bids = nil;
    SEL bidsSelector = NSSelectorFromString(@"hostedSlotBids");
    if ([ddz2 respondsToSelector:bidsSelector]) bids = sendObject(ddz2, bidsSelector);
    if (![bids isKindOfClass:[NSArray class]]) bids = @[];

    if (bids.count == 0) {
        NSString *first = @"";
        NSString *second = @"";
        SEL firstSelector = NSSelectorFromString(@"hostedBundleId");
        SEL secondSelector = NSSelectorFromString(@"hostedBundleId2");
        id firstRaw = [ddz2 respondsToSelector:firstSelector] ? sendObject(ddz2, firstSelector) : nil;
        id secondRaw = [ddz2 respondsToSelector:secondSelector] ? sendObject(ddz2, secondSelector) : nil;
        if ([firstRaw isKindOfClass:[NSString class]]) first = firstRaw;
        if ([secondRaw isKindOfClass:[NSString class]]) second = secondRaw;
        bids = @[first, second];
    }

    NSArray *carPlayFlags = nil;
    SEL flagsSelector = NSSelectorFromString(@"hostedSlotIsCarPlayUI");
    if ([ddz2 respondsToSelector:flagsSelector]) carPlayFlags = sendObject(ddz2, flagsSelector);
    if (![carPlayFlags isKindOfClass:[NSArray class]]) carPlayFlags = @[];

    NSMutableArray<NSString *> *result = [NSMutableArray array];
    for (NSUInteger index = 0; index < bids.count; index++) {
        id bid = bids[index];
        BOOL isCarPlayUI = NO;
        if (index < carPlayFlags.count) {
            id flag = carPlayFlags[index];
            if ([flag respondsToSelector:@selector(boolValue)]) isCarPlayUI = [flag boolValue];
        }
        if (!isCarPlayUI && [bid isKindOfClass:[NSString class]] && [bid length] > 0) {
            [result addObject:bid];
        }
    }
    return result;
}

static BOOL DDIsDDz2Active(id ddz2) {
    SEL activeSelector = NSSelectorFromString(@"active");
    if (!ddz2) return gDDHostMirrorActive;
    if (![ddz2 respondsToSelector:activeSelector]) return NO;
    BOOL (*sendActive)(id, SEL) = (void *)objc_msgSend;
    return sendActive(ddz2, activeSelector);
}

static void DDRefreshFontFloorCache(CFNotificationCenterRef center,
                                    void *observer,
                                    CFStringRef name,
                                    const void *object,
                                    CFDictionaryRef userInfo) {
    (void)center; (void)observer; (void)name; (void)object; (void)userInfo;
    gDDBridgedFontFloor = DDReadBridgedFontFloor();
    id ddz2 = DDSharedDDz2();
    if (!DDIsDDz2Active(ddz2)) return;
    for (NSString *bundleIdentifier in DDHostedNonCarPlayBundleIdentifiers(ddz2)) {
        DDPostUIAppFontFloorState(bundleIdentifier);
    }
}

static void DDRefreshKeyPaneCache(CFNotificationCenterRef center,
                                  void *observer,
                                  CFStringRef name,
                                  const void *object,
                                  CFDictionaryRef userInfo) {
    (void)center; (void)observer; (void)name; (void)object; (void)userInfo;
    gDDKeyPaneEnabled = DDReadKeyPaneEnabled();
    // sub_29400 also invokes the private toast path 30960 when disabled; that UI-only side effect
    // remains intentionally omitted. The DDz2 active-host broadcast below is reconstructed.
    id ddz2 = DDSharedDDz2();
    if (!DDIsDDz2Active(ddz2)) return;
    for (NSString *bundleIdentifier in DDHostedNonCarPlayBundleIdentifiers(ddz2)) {
        DDPostUIAppKeyPaneState(bundleIdentifier);
    }
}

static void DDObserveImmediateWithCallback(NSString *name, CFNotificationCallback callback) {
    CFNotificationCenterAddObserver(CFNotificationCenterGetDarwinNotifyCenter(),
                                    NULL,
                                    callback,
                                    (__bridge CFStringRef)name,
                                    NULL,
                                    CFNotificationSuspensionBehaviorDeliverImmediately);
}

static void DDObserveImmediate(NSString *name) {
    CFNotificationCenterAddObserver(CFNotificationCenterGetDarwinNotifyCenter(),
                                    NULL,
                                    DDReloadAppBridge,
                                    (__bridge CFStringRef)name,
                                    NULL,
                                    CFNotificationSuspensionBehaviorDeliverImmediately);
}

void DDReconstructionStart(void) {
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        DDRole role = DDDetectRole();

        // session-075 promotes the evidence-safe UIApp IPC/state consumer path from 4CBDC.
        if (role == DDRoleUIApp) {
            DDStartUIAppIPC();
            return;
        }

        // Other non-SpringBoard roles still require private hook/runtime contracts.
        if (role != DDRoleSpringBoard) return;

        // 27E20 B12: settings.changed, appbridge.listchanged and autostart.changed
        // all use sub_29198 with Immediate suspension behavior.
        DDStartSpringBoardUIAppResponder();
        DDObserveImmediate(DD_N_SETTINGS_CHANGED);
        DDObserveImmediate(DD_N_APPBRIDGE_LISTCHANGED);
        DDObserveImmediate(DD_N_AUTOSTART_CHANGED);
        DDObserveImmediateWithCallback(DD_N_FONTFLOOR_CHANGED, DDRefreshFontFloorCache);
        DDObserveImmediateWithCallback(DD_N_KEYPANE_CHANGED, DDRefreshKeyPaneCache);
        DDRepublishKnownAppBridgeSnapshot(NULL);
    });
}
