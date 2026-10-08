#import "DuoDashShared.h"

NSInteger DDCameraRelaySourceCode(NSString *source) {
    if ([source isEqualToString:@"waze"])
        return 2;
    if ([source isEqualToString:@"google_maps"])
        return 1;
    if ([source isEqualToString:@"provider"])
        return 3;
    return 0;
}
