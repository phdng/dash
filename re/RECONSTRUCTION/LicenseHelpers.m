// RECONSTRUCTION/LicenseHelpers.m — executable evidence-safe license helpers
// Exact A4208 base64url decoding promoted session-235.
// Exact A4304 hexadecimal decoding promoted session-236.
// Exact A54A4 decision-only status mapping promoted session-237.
// Exact A4744 printable-ASCII validator promoted session-238.
// Exact A4688 key-prefix classifier promoted session-239.
// Exact A5F60 terminal status-action mapping promoted session-240.
// Exact A774C verdict-text decision promoted session-241.
// Full A397C verification, key iteration, filesystem, network, retry/backoff, and verdict state acquisition remain excluded.

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

BOOL DDLicenseIsPrintableASCIIString(id value) {
    if (![value isKindOfClass:[NSString class]] || [value length] == 0)
        return NO;

    NSString *string = value;
    for (NSUInteger index = 0; index < string.length; ++index) {
        unichar character = [string characterAtIndex:index];
        if (character < 33 || character > 126)
            return NO;
    }
    return YES;
}

NSInteger DDLicenseKeyPrefixIndex(id value) {
    if (![value isKindOfClass:[NSString class]])
        return -1;

    NSString *string = value;
    if ([string hasPrefix:@"duodash-key v1 "])
        return 0;
    if ([string hasPrefix:@"truedash-key v1 "])
        return 1;
    return -1;
}

NSString *DDLicenseStatusTextForAction(NSUInteger action,
                                       NSInteger verificationStatus,
                                       BOOL refusalMatches) {
    switch (action) {
        case 1:
            return @"Licence revoked";
        case 2:
            return @"Check date and time";
        case 3:
            return @"Update DuoDash";
        case 4:
            return @"Licence invalid";
        case 5:
            return @"Cannot identify this device";
        default:
            return DDLicenseStatusTextForVerification(verificationStatus, refusalMatches);
    }
}

NSString *DDLicenseVerdictText(NSUInteger verificationStatus,
                               BOOL licenseNoncePresent,
                               BOOL refusalMatches,
                               BOOL deviceHashPresent) {
    if (licenseNoncePresent && refusalMatches)
        return @"refused";
    if (verificationStatus != 0 && !deviceHashPresent)
        return @"no_device_id";

    switch (verificationStatus) {
        case 0: return @"valid";
        case 1: return @"absent";
        case 2: return @"malformed";
        case 3: return @"unknown_key";
        case 4: return @"bad_signature";
        case 5: return @"wrong_device";
        case 6: return @"expired";
        case 7: return @"future_dated";
        case 8: return @"unsupported";
        case 9: return @"store_failed";
        case 10: return @"wrong_product";
        default: return @"unknown";
    }
}
