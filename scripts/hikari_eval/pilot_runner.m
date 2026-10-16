/* Objective-C baseline harness: this translation unit never loads Hikari. */
#import <Foundation/Foundation.h>
#include <stdio.h>
#include <stdlib.h>

extern NSString *DDVersionDeviceSanitizeMachineModel(NSString *value);
extern NSString *DDVersionDeviceFormatClientVersion(NSString *value);

static void assert_equals(NSString *actual, NSString *expected, const char *label) {
    if (actual == expected || [actual isEqualToString:expected])
        return;
    fprintf(stderr, "Unexpected VersionDevice helper behavior: %s\n", label);
    exit(2);
}

static const char *encoded(NSString *value) {
    if (!value)
        return "-";
    NSData *utf8 = [value dataUsingEncoding:NSUTF8StringEncoding];
    return [[utf8 base64EncodedStringWithOptions:0] UTF8String];
}

static void report(unsigned index, NSString *value) {
    NSString *sanitized = DDVersionDeviceSanitizeMachineModel(value);
    NSString *formatted = DDVersionDeviceFormatClientVersion(value);
    printf("%03u:%s:%s\n", index, encoded(sanitized), encoded(formatted));
}

int main(void) {
    @autoreleasepool {
        assert_equals(DDVersionDeviceSanitizeMachineModel(@"iPhone15,2"),
                      @"iPhone15,2", "accepted model");
        assert_equals(DDVersionDeviceSanitizeMachineModel(@"iPhone 15"),
                      nil, "rejected whitespace");
        assert_equals(DDVersionDeviceSanitizeMachineModel(@"a/b"),
                      nil, "rejected slash");
        assert_equals(DDVersionDeviceSanitizeMachineModel(
                          @"abcdefghijklmnopqrstuvwxyzABCDEFG"),
                      nil, "rejected model length");
        assert_equals(DDVersionDeviceFormatClientVersion(@"!@?"), @"unknown",
                      "invalid version fallback");
        assert_equals(DDVersionDeviceFormatClientVersion(@"A+B.10_2"),
                      @"A+B.102", "client version filtering");
        assert_equals(DDVersionDeviceFormatClientVersion(@""), @"unknown",
                      "empty version fallback");

        NSString *samples[] = {
            @"", @"iPhone15,2", @"iPhone14_6", @"A_B-9", @"abc-def",
            @"some model", @"abc@def", @"abc/def", @"com.apple.test",
            @"abcdefghijklmnopqrstuvwxyzABCDEFG", @"AAAAAA", @"iPad7,11",
            @"abc+def", @"hello_world", @"1234", @"foo.bar", @"A+B.10_2",
            @"!@?", @"é", @"🚗", @"line\nfeed", @"test\tvalue",
        };
        unsigned index = 0;
        report(index++, nil);
        for (unsigned i = 0; i < sizeof(samples) / sizeof(samples[0]); ++i)
            report(index++, samples[i]);

        /* Exercise every printable ASCII codepoint and simple combinations. */
        for (int code = 32; code <= 126; ++code) {
            NSString *sample = [NSString stringWithFormat:@"%c", code];
            report(index++, sample);
            report(index++, [@"A" stringByAppendingString:sample]);
        }
    }
    return 0;
}
