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
