// RECONSTRUCTION/LicenseHelpers.m — executable evidence-safe license helpers
// Exact A4208 base64url decoding promoted session-235.
// Exact A4304 hexadecimal decoding promoted session-236.
// Exact A54A4 decision-only status mapping promoted session-237.
// Full A397C verification, key iteration, filesystem, network, and verdict state acquisition remain excluded.

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

NSData *DDLicenseDecodeHex(NSString *value) {
    NSUInteger length = value.length;
    if ((length & 1) != 0 || length == 0)
        return nil;

    NSMutableData *data = [NSMutableData dataWithCapacity:length >> 1];
    const char *bytes = [value UTF8String];
    for (NSUInteger index = 0; index < length; index += 2) {
        unsigned char decoded = 0;
        for (NSUInteger half = 0; half < 2; ++half) {
            int character = bytes[index + half];
            unsigned char nibble;
            if ((unsigned int)(character - '0') < 10) {
                nibble = (unsigned char)(character - '0');
            } else if ((unsigned int)(character - 'a') < 6) {
                nibble = (unsigned char)(character - 'a' + 10);
            } else if ((unsigned int)(character - 'A') < 6) {
                nibble = (unsigned char)(character - 'A' + 10);
            } else {
                return nil;
            }
            decoded = half == 0 ? (unsigned char)(nibble << 4) : (unsigned char)(decoded | nibble);
        }
        [data appendBytes:&decoded length:1];
    }
    return data;
}

NSString *DDLicenseStatusTextForVerification(NSInteger verificationStatus, BOOL refusalMatches) {
    if (verificationStatus == 6)
        return @"Expired — connect to the internet";
    if (verificationStatus == 1)
        return @"Not activated";
    if (verificationStatus != 0)
        return @"Licence invalid";
    return refusalMatches ? @"Licence invalid" : @"Active";
}
