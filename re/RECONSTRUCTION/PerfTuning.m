#import "DuoDashShared.h"

// Exact A81B14 read-only AirPlay integer preference helper promoted session-243.
// Exact A8009C decision-only perf target/current-match semantics promoted session-244.
// A8009C backup/write/restore/notify/global-state behavior remains excluded.

NSInteger DDAirPlayIntegerPreference(NSString *key) {
    NSInteger result = -1;
    int value = -1;
    CFTypeRef copied = CFPreferencesCopyValue((__bridge CFStringRef)key,
                                              CFSTR("com.apple.airplay"),
                                              kCFPreferencesCurrentUser,
                                              kCFPreferencesAnyHost);
    if (!copied)
        return result;

    if (CFGetTypeID(copied) != CFNumberGetTypeID()
        || !CFNumberGetValue((CFNumberRef)copied, kCFNumberIntType, &value)) {
        value = -2;
    }
    CFRelease(copied);
    return value;
}

BOOL DDPerfTweakEnabledFromPreferenceValue(CFTypeRef value) {
    return value != NULL
        && CFGetTypeID(value) == CFBooleanGetTypeID()
        && CFBooleanGetValue((CFBooleanRef)value);
}

NSInteger DDAirPlayTargetFPSForPerfEnabled(BOOL enabled) {
    return enabled ? 15 : -1;
}

BOOL DDAirPlayFPSPreferencesMatchTarget(NSInteger maxFPS,
                                        NSInteger encoderFPSFixed,
                                        BOOL enabled) {
    NSInteger target = DDAirPlayTargetFPSForPerfEnabled(enabled);
    return maxFPS == target && encoderFPSFixed == target;
}
