// RECONSTRUCTION/LocaleFlow.m — executable language-resolution core + synthesis notes
// Original synthesis: session-053. Foundation/CoreFoundation-safe resolution core promoted session-183.
// Exact evidence: 9AFB0 resolution precedence, 9B284 whitelist, off_130E88 code/name table.
// Original unfair-lock cache and observer fan-out remain excluded until separately promoted.

#import "DuoDashShared.h"
#import <notify.h>
#import <os/lock.h>

static BOOL gDDLocaleFlowReady;
static os_unfair_lock gDDLocaleCacheLock = OS_UNFAIR_LOCK_INIT;
static NSString *gDDLocaleResolvedLanguage;
static NSMutableDictionary *gDDLocaleLookupCache;
static NSString * const DDLocaleForcePath = @"/var/tmp/duodash_lang_force";
static NSArray<NSString *> *DDLocaleSupportedCodes(void) {
    static NSArray<NSString *> *codes;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        codes = @[@"en", @"zh-Hans", @"es", @"ja", @"ko", @"de", @"fr", @"pt-BR",
                  @"ru", @"ar", @"zh-Hant", @"it", @"tr", @"vi", @"pl", @"id", @"th"];
    });
    return codes;
}

static NSArray<NSString *> *DDLocaleLanguageNames(void) {
    static NSArray<NSString *> *names;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        names = @[@"English", @"简体中文", @"Español", @"日本語", @"한국어", @"Deutsch", @"Français",
                  @"Português (Brasil)", @"Русский", @"العربية", @"繁體中文", @"Italiano", @"Türkçe",
                  @"Tiếng Việt", @"Polski", @"Bahasa Indonesia", @"ไทย"];
    });
    return names;
}

static void DDLocaleLanguageChangedCallback(CFNotificationCenterRef center,
                                            void *observer,
                                            CFStringRef name,
                                            const void *object,
                                            CFDictionaryRef userInfo) {
    (void)center;
    (void)observer;
    (void)name;
    (void)object;
    (void)userInfo;
    DDLocaleInvalidateCaches();
}

void DDLocaleFlowStart(void) {
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        gDDLocaleFlowReady = (DDLocaleSupportedCodes().count == 17);
        CFNotificationCenterAddObserver(CFNotificationCenterGetDarwinNotifyCenter(),
                                        &gDDLocaleCacheLock,
                                        DDLocaleLanguageChangedCallback,
                                        (__bridge CFStringRef)DD_N_LANGUAGE_CHANGED,
                                        NULL,
                                        CFNotificationSuspensionBehaviorDeliverImmediately);
    });
}

BOOL DDLocaleFlowReady(void) {
    DDLocaleFlowStart();
    return gDDLocaleFlowReady;
}

BOOL DDLocaleIsSupportedLanguage(NSString *language) {
    if (!language.length)
        return NO;
    return [DDLocaleSupportedCodes() containsObject:language];
}

NSArray<NSString *> *DDLocaleSupportedLanguages(void) {
    return DDLocaleSupportedCodes();
}

NSString *DDLocaleLanguageDisplayName(NSString *language) {
    if (!language.length)
        return @"en";
    NSUInteger index = [DDLocaleSupportedCodes() indexOfObject:language];
    if (index == NSNotFound)
        return language;
    return DDLocaleLanguageNames()[index];
}

BOOL DDLocaleSetLanguage(NSString *language) {
    if (!DDLocaleIsSupportedLanguage(language))
        return NO;

    CFPreferencesSetAppValue(CFSTR("duodash_language"),
                             (__bridge CFStringRef)language,
                             (__bridge CFStringRef)DD_SETTINGS_DOMAIN);
    CFPreferencesAppSynchronize((__bridge CFStringRef)DD_SETTINGS_DOMAIN);
    DDLocaleInvalidateCaches();
    notify_post([DD_N_LANGUAGE_CHANGED UTF8String]);
    return YES;
}

static NSString *DDLocaleTypedAppString(CFStringRef key) {
    CFPropertyListRef raw = CFPreferencesCopyAppValue(key, (__bridge CFStringRef)DD_SETTINGS_DOMAIN);
    if (!raw)
        return nil;
    NSString *value = CFGetTypeID(raw) == CFStringGetTypeID() ? [(__bridge NSString *)raw copy] : nil;
    CFRelease(raw);
    return value;
}

static NSString *DDLocaleResolveLanguageUncached(void) {
    NSString *forced = [NSString stringWithContentsOfFile:DDLocaleForcePath
                                                  encoding:NSUTF8StringEncoding
                                                     error:nil];
    forced = [forced stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    if (forced && forced.length == 0)
        return @"en";
    if (DDLocaleIsSupportedLanguage(forced))
        return forced;

    CFPreferencesAppSynchronize((__bridge CFStringRef)DD_SETTINGS_DOMAIN);
    NSString *current = DDLocaleTypedAppString(CFSTR("duodash_language"));
    if (DDLocaleIsSupportedLanguage(current))
        return current;

    NSString *legacy = DDLocaleTypedAppString(CFSTR("carnav_language"));
    if (DDLocaleIsSupportedLanguage(legacy)) {
        CFPreferencesSetValue(CFSTR("duodash_language"),
                              (__bridge CFStringRef)legacy,
                              (__bridge CFStringRef)DD_SETTINGS_DOMAIN,
                              kCFPreferencesCurrentUser,
                              kCFPreferencesAnyHost);
        CFPreferencesAppSynchronize((__bridge CFStringRef)DD_SETTINGS_DOMAIN);
        return legacy;
    }
    return @"en";
}

NSString *DDLocaleResolveLanguage(void) {
    if (!DDLocaleFlowReady())
        return @"en";

    os_unfair_lock_lock(&gDDLocaleCacheLock);
    NSString *cached = gDDLocaleResolvedLanguage;
    os_unfair_lock_unlock(&gDDLocaleCacheLock);
    if (cached)
        return cached;

    NSString *resolved = DDLocaleResolveLanguageUncached();
    os_unfair_lock_lock(&gDDLocaleCacheLock);
    if (!gDDLocaleResolvedLanguage)
        gDDLocaleResolvedLanguage = resolved;
    cached = gDDLocaleResolvedLanguage;
    os_unfair_lock_unlock(&gDDLocaleCacheLock);
    return cached;
}

void DDLocaleInvalidateCaches(void) {
    // Exact 9B314 boundary: resolved-language and lookup caches are cleared under one unfair lock.
    os_unfair_lock_lock(&gDDLocaleCacheLock);
    gDDLocaleResolvedLanguage = nil;
    gDDLocaleLookupCache = nil;
    os_unfair_lock_unlock(&gDDLocaleCacheLock);
}
// Q-10 info-schema bodies: License.m §DDInfo (cross-ref, không duplicate).
// CF<1946.102 selector branch: Evict.m §3AE50-Bước 5 (branch version duy nhất).
// device_hash (A3558): License.m (UDID-hash đính chính — không duplicate).
// Prefs infra: PrefsResolver.m (SetAppValue/Sync/74C8).

// ---- Version/device: hầu hết NEGATIVE (không branch, fail-soft) ----
// Documentary-only notes (no executable function).
    // 4008(a1..a4) generic "OS>=X.Y.Z?": đường nhanh _availability_version_check khi
    //   đã init (163430!=0); fallback so thủ công với 163410/414/418 (parse từ
    //   SystemVersion.plist ProductVersion qua 4198). Caller duy nhất 46340 (threshold UNKNOWN).
    // iOS floor khai báo 14.0 (external Info.plist). Runtime weak-link + plist fallback.
    // operatingSystemVersion chỉ telemetry (A574C/ios_version, 9EE88/os_version). Không if.
    // hw.machine: sysctl → sanitize [A-Za-z0-9,_-] len<=0x20 → dict model; fail → bỏ key.
    // device_hash rỗng → fail-soft no_device_id/no_blob. bootsessionuuid fail → bỏ boot_id
    //   (CarSleeper state.plist). UIDevice.name rỗng → bỏ qua (BLE packet).
    // ACF1C: announce "role=%s pid=%d stage=installed armed_wall=%.0f boot=%s" khi
    //   168D18&&168D19&&164C88 (callers 4A08/4A80/4C34). Không branch version/device/locale.
    // MinimumOS/systemVersion/AppleLanguages: 0 hit decompile (không đọc).

// ---- Language write (L1: 6A4E4:21-24, duy nhất) ----
// Documentary-only write flow (no executable function).
    // Guard 9B284 whitelist (:19) → SetAppValue(duodash_language) → Sync →
    //   9B314 (clear cache) → post language.changed.

// ---- Language read 4-tầng + cache (L2-L4: 9AFB0/9B284/9B314) ----
// Documentary-only language read flow (no executable fallback).
    // (1) /var/tmp/duodash_lang_force trim (:34-59); (2) prefs duodash_language (:62);
    // (3) legacy carnav_language migrate → ghi lại (:67-86); (4) default en (:90).
    // Validate 9B284 mỗi bước: strcmp off_130E88 step 2 đến 32 → 17 entries
    //   (NỘI DUNG 16 strings còn lại UNKNOWN, chỉ lộ "en").
    // Cache 164C38 + lock 164C58 (:26-33,105-115). 9B314 clear 164C38/40 dưới unfair_lock.
    // Không AppleLanguages. truedash_language: 0 hit decompile — dead/legacy giữ nguyên.
    // Previous placeholder returned @"en" (APPROXIMATION); intentionally not executable.

// ---- Observers + fan-out (L5-L11: 6 observers, clear + main-reload) ----
// Documentary-only observer map (no executable function).
    // Toàn cục 9B848 → 9B87C()=9B314 (chỉ clear). Settings 948C0:96220 (9B314 + async main 96D70).
    // License 8C41C, NavBubble 8EFE4→91DCC (9B314 + async 91E58), VoiceCmd 920C0→933FC,
    //   TweakMgmt 93A3C→93B3C (9B314 + async 93BC8) — mẫu clear+reload (bodies CN* UNKNOWN).
    // 9B314 fan-out callers: 6A4E4,8EE04,91DCC,91EE0,933FC,9394C,93B3C,948C0,96220,9B87C.
    // 9EE88 dùng NSLocale en_US_POSIX chỉ cho NSDateFormatter — không branch locale user.
