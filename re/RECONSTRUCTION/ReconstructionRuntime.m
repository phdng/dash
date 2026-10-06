// RECONSTRUCTION/ReconstructionRuntime.m — buildable static-evidence runtime (session-075)
// This file intentionally implements only behavior whose data-flow can be represented without
// unresolved private classes/functions. Unknown filtering/computation remains documented in the
// synthesis files rather than being silently guessed here.

#import "ReconstructionRuntime.h"

#import <dispatch/dispatch.h>
#import <mach-o/dyld.h>
#import <notify.h>
#import <objc/message.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
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
    if (!ddz2) return @[];

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
    if (!ddz2 || ![ddz2 respondsToSelector:activeSelector]) return NO;
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
        DDObserveImmediate(DD_N_SETTINGS_CHANGED);
        DDObserveImmediate(DD_N_APPBRIDGE_LISTCHANGED);
        DDObserveImmediate(DD_N_AUTOSTART_CHANGED);
        DDObserveImmediateWithCallback(DD_N_FONTFLOOR_CHANGED, DDRefreshFontFloorCache);
        DDObserveImmediateWithCallback(DD_N_KEYPANE_CHANGED, DDRefreshKeyPaneCache);
        DDRepublishKnownAppBridgeSnapshot(NULL);
    });
}
