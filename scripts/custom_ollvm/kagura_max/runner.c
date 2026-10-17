/* Host-only differential test. Never represented as iOS device execution. */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

extern uint64_t dd_kagura_critical(uint64_t x, uint64_t salt);

int main(void) {
    uint64_t seed = UINT64_C(0x123456789abcdef0);
    for (unsigned i = 0; i < 8192; ++i) {
        seed ^= seed << 13;
        seed ^= seed >> 7;
        seed ^= seed << 17;
        const uint64_t x = i < 16 ? (uint64_t)i : seed;
        const uint64_t salt = (seed >> 1) ^ ((uint64_t)i * UINT64_C(0x9e3779b97f4a7c15));
        const uint64_t got = dd_kagura_critical(x, salt);
        if (printf("%04u:%016" PRIx64 "\n", i, got) < 0)
            return 2;
    }
    if (puts("DD_KAGURA_HOST_PASS=8192") < 0)
        return 3;
    return 0;
}
