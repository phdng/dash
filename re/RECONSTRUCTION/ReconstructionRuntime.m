// RECONSTRUCTION/ReconstructionRuntime.m — buildable static-evidence runtime (session-072)
// This file intentionally implements only behavior whose data-flow can be represented without
// unresolved private classes/functions. Unknown filtering/computation remains documented in the
// synthesis files rather than being silently guessed here.

#import "ReconstructionRuntime.h"

#import <dispatch/dispatch.h>
#import <mach-o/dyld.h>
#import <notify.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

// libproc is linked explicitly by the Theos target. Keeping the declaration local avoids
// depending on private headers while matching the public libproc symbol used by sub_7764C.
extern int proc_pidpath(int pid, void *buffer, uint32_t buffersize);

static CFStringRef const kDDSettingsDomain = CFSTR("com.sensetechlab.duodash.settings");
static NSString * const kDDClearPanes = @"/var/tmp/duodash_ab_clearpanes";
static NSString * const kDDClearPanesDone = @"/var/tmp/duodash_ab_clearpanes.done";

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

        // Phase 1 runtime is intentionally limited to the statically reconstructed prefs
        // publisher in SpringBoard. Other role-specific private hooks remain evidence-only.
        if (role != DDRoleSpringBoard) return;

        // 27E20 B12: settings.changed, appbridge.listchanged and autostart.changed
        // all use sub_29198 with Immediate suspension behavior.
        DDObserveImmediate(DD_N_SETTINGS_CHANGED);
        DDObserveImmediate(DD_N_APPBRIDGE_LISTCHANGED);
        DDObserveImmediate(DD_N_AUTOSTART_CHANGED);
        DDRepublishKnownAppBridgeSnapshot(NULL);
    });
}
