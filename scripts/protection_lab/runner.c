/* Runs natively in the CI host only. Does not prove iOS/PAC runtime. */
#include "canary.h"
#include <inttypes.h>
#include <stdio.h>
#include <stdint.h>
int main(void) {
    uint64_t x = UINT64_C(0x8273beafe1235679);
    for (unsigned i = 0; i < 8192; ++i) {
        x ^= x << 13;
        x ^= x >> 7;
        x ^= x << 17;
        uint64_t a = x;
        uint64_t b = (x ^ UINT64_C(0x123456789abcdef0)) + i;
        uint64_t expected = dd_canary_native(a, b);
        uint64_t virtualized = dd_canary_vm(a, b);
        uint64_t indirect = dd_canary_indirect(dd_canary_native, a, b);
        if (expected != virtualized || expected != indirect) {
            fprintf(stderr, "VM MISMATCH vector %u native=%" PRIx64
                    " vm=%" PRIx64 " pointer=%" PRIx64 "\n",
                    i, expected, virtualized, indirect);
            return 1;
        }
    }
    printf("PROTECTION_LAB_HOST_PASS: 8192 native/VM/indirect vectors\n");
    return 0;
}
