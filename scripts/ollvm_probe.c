/* Deterministic OLLVM fixture. Only dd_ollvm_probe* functions match the
 * full-strength policy; main remains unobfuscated for comparison.
 * All arithmetic with possible overflow uses unsigned integers.
 */
#include <stdint.h>

#if defined(OLLVM_PROBE_MAIN)
#include <stdio.h>
#endif

__attribute__((noinline))
int dd_ollvm_probe(int input) {
    uint32_t value = (uint32_t)input;
    for (uint32_t i = 0; i < 5; ++i) {
        value = value * 3U + i;
        if ((value & 1U) != 0U)
            value ^= 0x5A5A5A5AU;
        else
            value += 17U;
    }
    return (int)(value & 0x7FFFFFFFU);
}

__attribute__((noinline))
int dd_ollvm_probe_branch(int input) {
    uint32_t bits = (uint32_t)input;
    uint32_t result = bits ^ 0xA5A5A5A5U;
    for (unsigned i = 0; i < 7; ++i) {
        if ((result & (1U << i)) != 0U)
            result = result * 5U + i;
        else
            result = (result ^ (0x9E3779B9U >> i)) + 3U;
    }
    switch (bits & 3U) {
        case 0: result ^= 0x0000FFFFU; break;
        case 1: result += 73U; break;
        case 2: result = (result << 1) | (result >> 31); break;
        default: result -= 11U; break;
    }
    return (int)(result & 0x7FFFFFFFU);
}

__attribute__((noinline))
int dd_ollvm_probe_check(int input) {
    uint32_t bits = (uint32_t)input;
    uint32_t result = 1U;
    for (unsigned i = 1; i <= 9; ++i) {
        uint32_t part = (bits >> (i % 16U)) & 0xFFU;
        if (part > 100U)
            result += part * i;
        else if (part != 0U)
            result ^= part + i;
        else
            result += 1U;
    }
    return (int)(result & 0x7FFFFFFFU);
}

#if defined(OLLVM_PROBE_MAIN)
int main(void) {
    for (int value = -256; value <= 256; ++value) {
        printf("%d:%d:%d:%d\n", value,
               dd_ollvm_probe(value),
               dd_ollvm_probe_branch(value),
               dd_ollvm_probe_check(value));
    }
    return 0;
}
#endif
