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
