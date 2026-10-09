#import "DuoDashShared.h"

// Exact decision-only core shared by AZ CarPlay hooks 49870..49990 (F-017), promoted session-252.
// Exact 4DE48 keep-awake nav-only bundle classifier promoted session-253.
// Hook installation, per-hook counters, byte_163ED8 acquisition, live display/backlight reads, and original-function invocation remain excluded.

NSInteger DDAZCarPlaySpoofedResult(BOOL forceDisconnected, NSInteger originalResult) {
    return forceDisconnected ? 0 : originalResult;
}

BOOL DDKeepAwakeNavigationBundle(NSString *bundleIdentifier) {
    if (bundleIdentifier.length == 0)
        return NO;
    if ([bundleIdentifier isEqualToString:@"com.google.Maps"])
        return YES;
    return [bundleIdentifier isEqualToString:@"com.waze.iphone"];
}
