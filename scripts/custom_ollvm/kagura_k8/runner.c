/* K8 4096 deterministic native parity vectors; no performance claim. */
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
extern uint64_t dd_k8_evaluate(uint64_t, uint64_t);
static uint64_t rot(uint64_t n) { return (n << 9) | (n >> 55); }
int main(void) {
    uint64_t checksum = 0;
    for (unsigned i = 0; i < 4096U; ++i) {
        const uint64_t x = UINT64_C(0x123456789abcdef0) ^
            ((uint64_t)i * UINT64_C(0x9e3779b97f4a7c15));
        const uint64_t salt = UINT64_C(0x5a17c3e9d4b02f61) ^
            ((uint64_t)(i * 7U + 3U) * UINT64_C(0xbf58476d1ce4e5b9));
        checksum = rot(checksum ^ dd_k8_evaluate(x, salt)) + i;
    }
    printf("DD_K8_SCHEMA=1\nDD_K8_VECTORS=4096\n"
           "DD_K8_CHECKSUM=%016" PRIx64 "\nDD_K8_COMPLETE=PASS\n",
           checksum);
    return 0;
}
