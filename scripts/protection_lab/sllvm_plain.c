/* Unprotected control, deliberately preserves a test-only plaintext marker. */
#include "sllvm_pilot.h"
#include <stddef.h>

/* Volatile reads avoid constant-folding the plaintext marker out of this
   binary; the plain/protected binary audit expects this exact canary. */
static const volatile unsigned char dd_plaintext_marker[] =
    "DUODASH_CE_PILOT_CANARY_V1_7F29D1B3";

DD_PILOT_EXPORT
uint32_t dd_pilot_plain_hash(uint32_t seed) {
    uint32_t state = seed ^ UINT32_C(2166136261);
    for (size_t i = 0; i < sizeof(dd_plaintext_marker) - 1; ++i)
        state = (state ^ dd_plaintext_marker[i]) * UINT32_C(16777619);
    return state;
}

DD_PILOT_EXPORT
uint64_t dd_pilot_plain_dispatch(uint64_t a, uint64_t b, unsigned mode) {
    if ((mode & 1U) == 0)
        return (a ^ UINT64_C(0x9e3779b97f4a7c15)) +
               (b * UINT64_C(0x00000100000001b3));
    return ((a + b) ^ UINT64_C(0xd1b54a32d192ed03)) + (b >> 11);
}
