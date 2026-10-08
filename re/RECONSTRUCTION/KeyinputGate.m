#import "DuoDashShared.h"
#import <objc/message.h>

BOOL DDKeyinputFieldMayRelay(id field) {
    if (!field)
        return NO;
    SEL secureSelector = NSSelectorFromString(@"isSecureTextEntry");
    if (![field respondsToSelector:secureSelector])
        return YES;
    BOOL secure = ((BOOL (*)(id, SEL))objc_msgSend)(field, secureSelector);
    return !secure;
}

NSString *DDKeyinputResolvedTemporaryKnobPath(NSString *name) {
    NSString *temporaryDirectory = NSTemporaryDirectory();
    if (!temporaryDirectory.length || !name.length)
        return nil;

    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSString *primary = [temporaryDirectory stringByAppendingPathComponent:name];
    if ([fileManager fileExistsAtPath:primary])
        return primary;

    if ([name hasPrefix:@"duodash_"]) {
        NSString *suffix = [name substringFromIndex:8];
        NSString *legacyName = [@"carnav_" stringByAppendingString:suffix];
        NSString *legacy = [temporaryDirectory stringByAppendingPathComponent:legacyName];
        if ([fileManager fileExistsAtPath:legacy])
            return legacy;
    }
    return nil;
}

BOOL DDKeyinputKnobPresentCached(NSString *name, int *cachedState, double *cachedTimestamp) {
    double now = [[NSProcessInfo processInfo] systemUptime];
    if (*cachedState < 0 || now - *cachedTimestamp >= 1.0) {
        NSFileManager *fileManager = [NSFileManager defaultManager];
        NSString *globalPath = [@"/var/tmp" stringByAppendingPathComponent:name];
        BOOL present = [fileManager fileExistsAtPath:globalPath];
        if (!present)
            present = DDKeyinputResolvedTemporaryKnobPath(name) != nil;
        *cachedState = present;
        *cachedTimestamp = now;
        return present;
    }
    return *cachedState != 0;
}
