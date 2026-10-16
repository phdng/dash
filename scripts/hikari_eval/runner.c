/*
 * Native macOS runner is compiled WITHOUT any LLVM obfuscation pass.
 * No canary plaintext exists in this translation unit.
 */
#include <stdint.h>
#include <stdio.h>

extern uint32_t dd_hikari_probe_string(uint32_t seed);
extern uint32_t dd_hikari_probe_const(uint32_t seed);

int main(void) {
    for (int value = -256; value <= 256; ++value) {
        const uint32_t input = (uint32_t)value;
        printf("%d:%08x:%08x\n", value,
               (unsigned)dd_hikari_probe_string(input),
               (unsigned)dd_hikari_probe_const(input));
    }
    return 0;
}
