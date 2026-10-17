/* Host-macOS ARC, UTF-8 and autoreleasepool parity; NOT iOS PAC runtime. */
#import "objc_ce.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    /* Repeating pools detects accidental lifetime assumptions. */
    for (unsigned pass = 0; pass < 128; ++pass) {
        @autoreleasepool {
            for (unsigned i = 0; i < 64; ++i) {
                uint32_t choice = (uint32_t)(pass * 64U + i);
                NSString *original = DDObjCPlainValue(choice);
                NSString *transformed = DDObjCProtectedValue(choice);
                if (!original || !transformed ||
                    ![original isEqualToString:transformed] ||
                    original.length != transformed.length ||
                    [original lengthOfBytesUsingEncoding:NSUTF8StringEncoding] !=
                    [transformed lengthOfBytesUsingEncoding:NSUTF8StringEncoding] ||
                    strcmp(original.UTF8String, transformed.UTF8String) != 0) {
                    fprintf(stderr, "OBJC_CE_MISMATCH: vector=%u\n", choice);
                    return 1;
                }
            }
        }
    }
    puts("OBJC_CE_HOST_PASS: 8192 NSString/ARC/UTF8 parity vectors");
    return 0;
}
