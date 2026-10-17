/* K11 separate five Kagura-pass iOS arm64 runtime canary.
 * Uses K9 independent vectors; functions come ONLY from K10 05-ci/ios.o. */
#include <inttypes.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

extern uint64_t dd_k8_evaluate(uint64_t, uint64_t);
extern uint64_t dd_k9_mvo_probe(uint64_t, uint64_t);

static uint64_t rot9(uint64_t x) { return (x << 9) | (x >> 55); }

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

int dd_k11_ios_parity(char *output, size_t size, const char *uuid) {
    if (!output || size < 512 || !valid_uuid(uuid)) return 0;
    uint64_t c = 0, mvo = 0;
    for (unsigned i = 0; i < 4096U; i++) {
        const uint64_t n = UINT64_C(0x123456789abcdef0) ^
            (uint64_t)i * UINT64_C(0x9e3779b97f4a7c15);
        const uint64_t salt = UINT64_C(0x5a17c3e9d4b02f61) ^
            ((uint64_t)i * 7U + 3U) * UINT64_C(0xbf58476d1ce4e5b9);
        c = rot9(c ^ dd_k8_evaluate(n, salt)) + i;
        mvo = rot9(mvo ^ dd_k9_mvo_probe(n, salt)) + i;
    }
    if (c != UINT64_C(0x25a3318e3d7d6525) ||
        mvo != UINT64_C(0x64e61045bbc4a250)) {
        (void)snprintf(output, size,
            "DD_K11_IOS_ERROR=NATIVE_CHECKSUM_MISMATCH\n");
        return 0;
    }
    int len = snprintf(output, size,
        "DD_K11_IOS_SCHEMA=1\n"
        "DD_K11_IOS_CONTEXT=IOS_DEVICE\n"
        "DD_K11_IOS_ARCH=arm64:0x00000000\n"
        "DD_K11_IOS_APP_UUID=%s\n"
        "DD_K11_IOS_PIPELINE=MVO_GENC_FSPLIT_IBR_CI\n"
        "DD_K11_IOS_VECTORS_PER_FUNCTION=4096\n"
        "DD_K11_IOS_C_CHECKSUM=%016" PRIx64 "\n"
        "DD_K11_IOS_MVO_CHECKSUM=%016" PRIx64 "\n"
        "DD_K11_IOS_COMPLETE=PASS\n", uuid, c, mvo);
    return len > 0 && (size_t)len < size;
}
