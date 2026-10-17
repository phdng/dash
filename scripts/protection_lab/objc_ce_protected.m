/* Objective-C CE-inspired, source-only; no SLLVM plugin and no secrets.
 * Volatile data loads force an observable runtime byte decoding path; Apple
 * Clang retains control of ARC and the correct arm64e/ptrauth object ABI.
 */
#import "objc_ce.h"
#import "objc_ce_data.h"
#include <stddef.h>

static __attribute__((noinline)) NSString *
DDObjCDecodeValue(const volatile unsigned char *encoded, size_t length,
                  uint32_t slot) {
    if (!encoded || length > DD_OBJC_CE_MAX_LEN)
        return nil;
    unsigned char decoded[DD_OBJC_CE_MAX_LEN];
    for (size_t pos = 0; pos < length; ++pos)
        decoded[pos] = (unsigned char)(
            encoded[pos] ^ (unsigned char)
            (DD_OBJC_CE_KEY + pos * DD_OBJC_CE_STEP +
             slot * DD_OBJC_CE_SLOT_STEP));
    /* initWithBytes copies into NSString before stack storage goes away. */
    return [[NSString alloc] initWithBytes:decoded length:length
                                  encoding:NSUTF8StringEncoding];
}

DD_OBJC_CE_EXPORT
NSString *DDObjCProtectedValue(uint32_t choice) {
    switch (choice & 3U) {
        case 0:
            return DDObjCDecodeValue(dd_objc_ce_data_0, DD_OBJC_CE_LEN_0, 0);
        case 1:
            return DDObjCDecodeValue(dd_objc_ce_data_1, DD_OBJC_CE_LEN_1, 1);
        case 2:
            return DDObjCDecodeValue(dd_objc_ce_data_2, DD_OBJC_CE_LEN_2, 2);
        default:
            return @"";
    }
}
