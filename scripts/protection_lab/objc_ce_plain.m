/* Unprotected Objective-C NSString literals: baseline for Mach-O audit. */
#import "objc_ce.h"

DD_OBJC_CE_EXPORT
NSString *DDObjCPlainValue(uint32_t choice) {
    switch (choice & 3U) {
        case 0: return @"DUODASH_OBJC_CE_CANARY_V2_A64E_38C10E7F";
        case 1: return @"DuoDash | Tiếng Việt | arm64e | 🔐";
        case 2: return @"Credits & Licenses";
        default: return @"";
    }
}
