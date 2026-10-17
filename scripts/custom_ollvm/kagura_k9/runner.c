/* K9 REAL mixed-module composition canary.
 * 4096 native checksum vectors for BOTH independently defined functions. */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

extern uint64_t dd_k8_evaluate(uint64_t, uint64_t);
extern uint64_t dd_k9_mvo_probe(uint64_t, uint64_t);

static uint64_t rot9(uint64_t x) { return (x << 9) | (x >> 55); }

int main(void) {
    uint64_t c = 0, mvo = 0;
    for (unsigned i = 0; i < 4096U; i++) {
        const uint64_t n = UINT64_C(0x123456789abcdef0) ^
            (uint64_t)i * UINT64_C(0x9e3779b97f4a7c15);
        const uint64_t salt = UINT64_C(0x5a17c3e9d4b02f61) ^
            ((uint64_t)i * 7U + 3U) * UINT64_C(0xbf58476d1ce4e5b9);
        c = rot9(c ^ dd_k8_evaluate(n, salt)) + i;
        mvo = rot9(mvo ^ dd_k9_mvo_probe(n, salt)) + i;
    }
    printf("DD_K9_SCHEMA=1\nDD_K9_VECTORS_PER_FUNCTION=4096\n"
           "DD_K9_C_CHECKSUM=%016" PRIx64 "\n"
           "DD_K9_MVO_CHECKSUM=%016" PRIx64 "\n"
           "DD_K9_COMPLETE=PASS\n", c, mvo);
    return 0;
}
