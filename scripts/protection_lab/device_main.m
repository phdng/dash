/* Read-only test executable: macOS host OR a separately provisioned iOS device.
 * All inputs are synthetic and public. No production Crane code is linked.
 */
#import "objc_ce.h"
#import <Foundation/Foundation.h>
#import <TargetConditionals.h>
#include "device_suites.h"
#include <mach-o/dyld.h>
#include <mach-o/loader.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#if TARGET_OS_IPHONE && !TARGET_OS_SIMULATOR
#define DD_EXPECT_IOS_DEVICE 1
#else
#define DD_EXPECT_IOS_DEVICE 0
#endif

static int dd_device_check_architecture(void) {
#if DD_EXPECT_IOS_DEVICE
    const struct mach_header *header = _dyld_get_image_header(0);
    if (!header || header->magic != MH_MAGIC_64 ||
        header->cputype != CPU_TYPE_ARM64) {
        fputs("DD_RUNTIME_ERROR=WRONG_MAIN_MACHO\n", stderr);
        return 0;
    }
    uint32_t raw_subtype = (uint32_t)header->cpusubtype;
    uint32_t subtype = raw_subtype & UINT32_C(0x00ffffff);
#if defined(__arm64e__)
    if (subtype != 2 || !(raw_subtype & UINT32_C(0x80000000)) ||
        (raw_subtype & UINT32_C(0x40000000))) {
        fputs("DD_RUNTIME_ERROR=ARM64E_PAC_ABI_MISMATCH\n", stderr);
        return 0;
    }
    printf("DD_RUNTIME_ABI=arm64e:0x%08x\n", raw_subtype);
#else
    if (subtype != 0) {
        fputs("DD_RUNTIME_ERROR=ARM64_ABI_MISMATCH\n", stderr);
        return 0;
    }
    printf("DD_RUNTIME_ABI=arm64:0x%08x\n", raw_subtype);
#endif
#else
    puts("DD_RUNTIME_ABI=NOT_APPLICABLE");
#endif
    return 1;
}

static int dd_device_test_objc(void) {
    for (unsigned i = 0; i < DD_DEVICE_VECTORS; ++i) {
        @autoreleasepool {
            uint32_t choice = (uint32_t)i;
            NSString *plain = DDObjCPlainValue(choice);
            NSString *protected = DDObjCProtectedValue(choice);
            if (!plain || !protected ||
                ![plain isEqualToString:protected] ||
                plain.length != protected.length ||
                [plain lengthOfBytesUsingEncoding:NSUTF8StringEncoding] !=
                    [protected lengthOfBytesUsingEncoding:NSUTF8StringEncoding] ||
                strcmp([plain UTF8String], [protected UTF8String]) != 0) {
                fprintf(stderr, "DD_RUNTIME_ERROR=OBJC_CE:%u\n", i);
                return 0;
            }
        }
    }
    puts("DD_RUNTIME_OBJC_CE_PASS=8192");
    return 1;
}

int main(void) {
    @autoreleasepool {
#if DD_EXPECT_IOS_DEVICE
        puts("DD_RUNTIME_CONTEXT=IOS_DEVICE");
#else
        puts("DD_RUNTIME_CONTEXT=MACOS_HOST");
#endif
        if (!dd_device_check_architecture() ||
            !dd_device_test_vm() ||
            !dd_device_test_ce_icall() ||
            !dd_device_test_igv_ibr() ||
            !dd_device_test_objc()) {
            return 1;
        }
        puts("DD_RUNTIME_COMPLETE=PASS");
        fflush(stdout);
    }
    return 0;
}
