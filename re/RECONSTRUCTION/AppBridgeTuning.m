#import "DuoDashShared.h"

double DDAppBridgeDashSettleSeconds(void) {
    NSString *raw = [NSString stringWithContentsOfFile:@"/var/tmp/duodash_ab_dashsettle"
                                               encoding:NSUTF8StringEncoding
                                                  error:nil];
    if (!raw.length)
        return 0.45;

    double value = [raw doubleValue];
    if (value > 5.0 || value < 0.2)
        return 0.45;
    return value;
}

double DDAppBridgeMaterialAlpha(void) {
    NSString *raw = [NSString stringWithContentsOfFile:@"/var/tmp/duodash_ab_mat_alpha"
                                               encoding:NSUTF8StringEncoding
                                                  error:nil];
    if (!raw.length)
        return 0.996078431;

    double value = [raw doubleValue];
    if (value > 1.0 || value <= 0.0)
        return 0.996078431;
    return value;
}

int DDReadAirPlayMediaServerPendingPID(void) {
    NSString *raw = [NSString stringWithContentsOfFile:@"/var/mobile/Library/DuoDash/airplay_msrv_pending"
                                               encoding:NSUTF8StringEncoding
                                                  error:nil];
    if (![raw isKindOfClass:[NSString class]])
        return -1;

    NSString *trimmed = [raw stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    if (!trimmed.length)
        return -1;

    NSCharacterSet *digits = [NSCharacterSet decimalDigitCharacterSet];
    for (NSUInteger index = 0; index < trimmed.length; index++) {
        if (![digits characterIsMember:[trimmed characterAtIndex:index]])
            return -1;
    }

    int value = [trimmed intValue];
    return value > 1 ? value : -1;
}
