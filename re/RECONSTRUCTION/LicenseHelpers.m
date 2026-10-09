// RECONSTRUCTION/LicenseHelpers.m — executable evidence-safe license helpers
// Exact A4208 base64url decoding promoted session-235.
// Full A397C verification, key iteration, filesystem, network, and verdict state remain excluded.

#import "DuoDashShared.h"

NSData *DDLicenseDecodeBase64URL(NSString *value) {
    if (!value.length)
        return nil;

    NSString *plusNormalized = [value stringByReplacingOccurrencesOfString:@"-" withString:@"+"];
    NSMutableString *base64 = [plusNormalized mutableCopy];
    [base64 replaceOccurrencesOfString:@"_"
                            withString:@"/"
                               options:0
                                 range:NSMakeRange(0, base64.length)];
    while ((base64.length & 3) != 0)
        [base64 appendString:@"="];

    return [[NSData alloc] initWithBase64EncodedString:base64 options:0];
}
