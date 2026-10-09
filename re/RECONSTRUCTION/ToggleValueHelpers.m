#import "DuoDashShared.h"

// Exact pure string-value branch from 7EA4 promoted session-255.
// Exact pure reapdelay string parser from 202D0 promoted session-256.
// File reads, CFPreferences fallback, scheduling/host state, and cache/global mutation remain excluded.

NSUInteger DDFontFloorOverrideValue(NSString *value) {
    NSCharacterSet *whitespace = [NSCharacterSet whitespaceAndNewlineCharacterSet];
    NSString *trimmed = [value stringByTrimmingCharactersInSet:whitespace];
    if (trimmed.length == 0)
        return 0;

    for (NSUInteger i = 0; i < trimmed.length; i++) {
        unichar c = [trimmed characterAtIndex:i];
        if (c < '0' || c > '9')
            return 0;
    }

    NSInteger parsed = trimmed.integerValue;
    if (parsed < 8 || parsed > 96)
        return 0;
    return (NSUInteger)parsed;
}

double DDReapDelayOverrideValue(NSString *value) {
    NSCharacterSet *whitespace = [NSCharacterSet whitespaceAndNewlineCharacterSet];
    NSString *trimmed = [value stringByTrimmingCharactersInSet:whitespace];
    if (trimmed.length == 0)
        return 0.0;

    double parsed = trimmed.doubleValue;
    if (parsed > 60.0 || parsed <= 0.0)
        return 0.0;
    return parsed;
}
