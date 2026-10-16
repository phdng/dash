/* CE/ICALL-inspired source-level canary, compiled by genuine Apple Clang.
 * No SLLVM proprietary plugin, raw pointer conversion, JIT or runtime patching.
 */
#include "sllvm_pilot.h"
#include "sllvm_encoded.h"
#include <stddef.h>

/* Volatile source prevents the compiler from trivially folding decoded bytes
 * into a second plaintext literal. This is NOT cryptographic encryption. */
static const volatile unsigned char dd_encoded_marker[] = DD_CE_DATA;

DD_PILOT_EXPORT
uint32_t dd_pilot_protected_hash(uint32_t seed) {
    uint32_t state = seed ^ UINT32_C(2166136261);
    for (size_t i = 0; i < sizeof(dd_encoded_marker); ++i) {
        unsigned char decoded = (unsigned char)(
            dd_encoded_marker[i] ^ (unsigned char)
            (DD_CE_KEY + (unsigned)(i * DD_CE_STEP)));
        state = (state ^ decoded) * UINT32_C(16777619);
    }
    return state;
}

static __attribute__((noinline))
uint64_t dd_pilot_handler_zero(uint64_t a, uint64_t b) {
    return (a ^ UINT64_C(0x9e3779b97f4a7c15)) +
           (b * UINT64_C(0x00000100000001b3));
}

static __attribute__((noinline))
uint64_t dd_pilot_handler_one(uint64_t a, uint64_t b) {
    return ((a + b) ^ UINT64_C(0xd1b54a32d192ed03)) + (b >> 11);
}

/* Typed function-pointer table: compiler emits correct pointer-authenticated
 * indirect calls for Apple arm64e. No uintptr_t cast/signature stripping. */
static dd_pilot_calculator const dd_pilot_dispatch_table[2] = {
    dd_pilot_handler_zero, dd_pilot_handler_one
};

DD_PILOT_EXPORT
uint64_t dd_pilot_protected_dispatch(uint64_t a, uint64_t b, unsigned mode) {
    dd_pilot_calculator fn = dd_pilot_dispatch_table[mode & 1U];
    return fn(a, b);
}
