#import "DuoDashShared.h"

// Exact decision-only comparator from A4008 fallback promoted session-245.
// Exact A574C hw.machine sanitizer promoted session-246.
// Weak-import availability checks, global initialization, SystemVersion.plist parsing, sysctl acquisition, and telemetry remain excluded.

BOOL DDVersionTupleAtLeast(NSInteger installedMajor,
                           NSInteger installedMinor,
                           NSInteger installedPatch,
                           NSInteger requiredMajor,
                           NSInteger requiredMinor,
                           NSInteger requiredPatch) {
    if (installedMajor > requiredMajor)
        return YES;
    if (installedMajor < requiredMajor)
        return NO;
    if (installedMinor > requiredMinor)
        return YES;
    if (installedMinor < requiredMinor)
        return NO;
    return installedPatch >= requiredPatch;
}

NSString *DDVersionDeviceSanitizeMachineModel(NSString *value) {
    if (![value isKindOfClass:[NSString class]])
        return nil;

    NSCharacterSet *allowed = [NSCharacterSet characterSetWithCharactersInString:
                               @"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,_-"];
    if ([value rangeOfCharacterFromSet:[allowed invertedSet]].location != NSNotFound)
        return nil;
    if (value.length > 32)
        return nil;
    return value;
}
