/*
 * Isolated, non-production Hikari evaluation canary.
 * The string literal is intentionally test-only: NEVER embed credentials.
 */
#include <stdint.h>

static const unsigned char dd_hikari_marker[] =
    "DUODASH_HIKARI_CANARY_ONLY_7F29D1B3";

__attribute__((noinline))
uint32_t dd_hikari_probe_string(uint32_t seed) {
    uint32_t value = seed ^ 0x9e3779b9U;
    /* Volatile reads keep the test marker observable even under -O1. */
    const volatile unsigned char *bytes = dd_hikari_marker;
    for (unsigned index = 0; bytes[index] != 0; ++index) {
        value = (value * 33U) ^ (uint32_t)bytes[index];
    }
    return value;
}

__attribute__((noinline))
uint32_t dd_hikari_probe_const(uint32_t input) {
    uint32_t value = input;
    for (uint32_t i = 1; i <= 9; ++i) {
        if ((value & 3U) == 0U) {
            value = (value ^ 0x6d2b79f5U) + 0x1f123bb5U + i;
        } else if ((value & 3U) == 1U) {
            value = (value * 0x045d9f3bU) ^ 0x13579bdfU;
        } else {
            value = (value + 0x31415927U) ^ (i * 0x27182819U);
        }
    }
    return value;
}
