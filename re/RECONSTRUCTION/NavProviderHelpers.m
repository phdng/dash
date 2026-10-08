#import "DuoDashShared.h"

double DDNavProviderTimestamp(NSDictionary *payload) {
    id value = [payload objectForKeyedSubscript:@"timestamp"];
    if (![value isKindOfClass:[NSNumber class]])
        return 0.0;
    return [value doubleValue];
}
