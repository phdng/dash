#import "DuoDashShared.h"

double DDNavProviderTimestamp(NSDictionary *payload) {
    id value = [payload objectForKeyedSubscript:@"timestamp"];
    if (![value isKindOfClass:[NSNumber class]])
        return 0.0;
    return [value doubleValue];
}

BOOL DDNavProviderPayloadMatchesProvider(id payload, id provider) {
    if (![payload isKindOfClass:[NSDictionary class]])
        return NO;

    id version = [payload objectForKeyedSubscript:@"v"];
    if (![version isKindOfClass:[NSNumber class]] || [version intValue] != 2)
        return NO;

    id payloadProvider = [payload objectForKeyedSubscript:@"provider"];
    if (![payloadProvider isKindOfClass:[NSString class]])
        return NO;
    return [payloadProvider isEqualToString:provider];
}

BOOL DDNavProviderIsLegacyTrueDashNotification(CFStringRef name) {
    if (!name)
        return NO;
    if (CFEqual(name, CFSTR("com.sensetechlab.truedash.navUpdate")))
        return YES;
    if (CFEqual(name, CFSTR("com.sensetechlab.truedash.speedLimit")))
        return YES;
    return CFEqual(name, CFSTR("com.sensetechlab.truedash.cameraAlert"));
}

NSComparisonResult DDNavProviderCompareLastSeenDescending(id left, id right) {
    id rightLastSeen = [right objectForKeyedSubscript:@"lastSeen"];
    id leftLastSeen = [left objectForKeyedSubscript:@"lastSeen"];
    return (NSComparisonResult)[rightLastSeen compare:leftLastSeen];
}
