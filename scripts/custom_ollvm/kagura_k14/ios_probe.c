/* K14 isolated CSEBreak iPhone canary. Link only K13 ios-cse-break.o.
 * 4096 public-data vectors identical to frozen K8 native runner.
 * No Crane hooks, iOS secrets, anti-debug or arm64e PAC. */
#include <inttypes.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
extern uint64_t dd_k8_evaluate(uint64_t, uint64_t);
static uint64_t rot(uint64_t n) { return (n << 9) | (n >> 55); }

static int valid_uuid(const char *s) {
    if (!s || strlen(s) != 36) return 0;
    for (unsigned i = 0; i < 36; ++i) {
        if (i == 8 || i == 13 || i == 18 || i == 23) {
            if (s[i] != '-') return 0;
        } else if (!((s[i] >= '0' && s[i] <= '9') ||
                     (s[i] >= 'a' && s[i] <= 'f'))) return 0;
    }
    return 1;
}

int dd_k14_ios_parity(char *output, size_t size, const char *uuid) {
    if (!output || size < 512 || !valid_uuid(uuid)) return 0;
    uint64_t checksum = 0;
    for (unsigned i = 0; i < 4096U; ++i) {
        const uint64_t x = UINT64_C(0x123456789abcdef0) ^
            ((uint64_t)i * UINT64_C(0x9e3779b97f4a7c15));
        const uint64_t salt = UINT64_C(0x5a17c3e9d4b02f61) ^
            ((uint64_t)(i * 7U + 3U) * UINT64_C(0xbf58476d1ce4e5b9));
        checksum = rot(checksum ^ dd_k8_evaluate(x, salt)) + i;
    }
    /* Native macOS oracle separately observed in genuine K13 artifact. */
    if (checksum != UINT64_C(0x25a3318e3d7d6525)) {
        (void)snprintf(output, size,
            "DD_K14_IOS_ERROR=NATIVE_CHECKSUM_MISMATCH\n");
        return 0;
    }
    const int length = snprintf(output, size,
        "DD_K14_IOS_SCHEMA=1\n"
        "DD_K14_IOS_CONTEXT=IOS_DEVICE\n"
        "DD_K14_IOS_ARCH=arm64:0x00000000\n"
        "DD_K14_IOS_APP_UUID=%s\n"
        "DD_K14_IOS_PASS=CSE_BREAK\n"
        "DD_K14_IOS_VECTORS=4096\n"
        "DD_K14_IOS_CHECKSUM=%016" PRIx64 "\n"
        "DD_K14_IOS_COMPLETE=PASS\n", uuid, checksum);
    return length > 0 && (size_t)length < size;
}
