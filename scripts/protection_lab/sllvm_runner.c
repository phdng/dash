/* Host-only differential proof. No string marker embedded in this runner. */
#include "sllvm_pilot.h"
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

int main(void) {
    uint64_t state = UINT64_C(0x8273beafe1235679);
    for (unsigned i = 0; i < 8192; ++i) {
        state ^= state << 13;
        state ^= state >> 7;
        state ^= state << 17;
        uint64_t a = state, b = (state ^ UINT64_C(0x123456789abcdef0)) + i;
        uint32_t seed = (uint32_t)(state >> 32);
        unsigned mode = i ^ (unsigned)state;
        uint32_t plain_hash = dd_pilot_plain_hash(seed);
        uint32_t encrypted_hash = dd_pilot_protected_hash(seed);
        uint64_t plain_dispatch = dd_pilot_plain_dispatch(a, b, mode);
        uint64_t indirect_dispatch = dd_pilot_protected_dispatch(a, b, mode);
        if (plain_hash != encrypted_hash || plain_dispatch != indirect_dispatch) {
            fprintf(stderr, "PILOT_MISMATCH i=%u hash=%08" PRIx32 "/%08" PRIx32
                    " dispatch=%016" PRIx64 "/%016" PRIx64 "\n",
                    i, plain_hash, encrypted_hash, plain_dispatch,
                    indirect_dispatch);
            return 1;
        }
    }
    printf("SLLVM_PILOT_HOST_PASS: 8192 CE/ICALL parity vectors\n");
    return 0;
}
