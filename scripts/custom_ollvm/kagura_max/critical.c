/* Public, synthetic canary only. No credentials, UDID, license key or hooks. */
#include <stdint.h>
#include <stddef.h>

/* Volatile loads keep the public string alive through LLVM19 -O1 so
   literal removal can be measured in actual Mach-O objects. */
static const char dd_public_marker[] = "DD_KAGURA_PUBLIC_CANARY_CE_STRING_V1";

__attribute__((noinline, used))
uint64_t dd_kagura_critical(uint64_t x, uint64_t salt) {
    const volatile unsigned char *bytes =
        (const volatile unsigned char *)dd_public_marker;
    uint64_t acc = x ^ salt ^ UINT64_C(0x6a09e667f3bcc909);
    for (unsigned i = 0; i != 8; ++i) {
        acc ^= (uint64_t)bytes[i];
        acc = (acc << 7) | (acc >> 57);
        acc += UINT64_C(0x9e3779b97f4a7c15) ^ (uint64_t)i;
    }
    if ((x & UINT64_C(1)) != 0) {
        acc ^= (salt * UINT64_C(0x100000001b3));
        acc = (acc << 11) | (acc >> 53);
    } else {
        acc += (salt ^ UINT64_C(0xbf58476d1ce4e5b9));
        acc ^= acc >> 13;
    }
    if ((salt & UINT64_C(7)) == 3) {
        acc = (acc * UINT64_C(0x94d049bb133111eb)) ^ x;
    }
    return acc ^ (acc >> 29);
}
