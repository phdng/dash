#import "DuoDashShared.h"

// Exact A81B14 read-only AirPlay integer preference helper promoted session-243.
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
