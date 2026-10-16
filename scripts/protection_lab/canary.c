/* Apple Clang baseline: no OLLVM, no VM plugin, no ObjC/hook ABI. */
#include "canary.h"

__attribute__((noinline))
uint64_t dd_canary_native(uint64_t a, uint64_t b) {
    const uint64_t x = (a ^ UINT64_C(0x9e3779b97f4a7c15))
                     + b * UINT64_C(0x00000100000001b3);
    return ((x << 13) | (x >> 51)) ^ (a >> 7);
}

/* Native function pointers exercise the compiler's arm64e PAC ABI. */
__attribute__((noinline))
uint64_t dd_canary_indirect(dd_eval_fn fn, uint64_t a, uint64_t b) {
    if (fn == 0) return 0;
    return fn(a, b);
}
