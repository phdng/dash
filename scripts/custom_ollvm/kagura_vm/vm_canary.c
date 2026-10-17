/* Kagura VM K6 research ONLY: one public, side-effect-free C function.
 * Two builds use the same source with different entrypoint symbols.
 * Never link or alter DuoDash/Crane production, hooks, secrets or device APIs.
 */
#include <stdint.h>

#ifndef DD_VM_ENTRY
#define DD_VM_ENTRY dd_vm_pilot
#endif
#ifndef DD_VM_GUARD
#define DD_VM_GUARD dd_vm_sentinel
#endif

__attribute__((noinline, used, annotate("kagura_vm")))
uint64_t DD_VM_ENTRY(uint64_t x, uint64_t salt) {
    uint64_t a = x ^ (salt + UINT64_C(0x6a09e667f3bcc909));
    a ^= a >> 21;
    a *= UINT64_C(0xbf58476d1ce4e5b9);
    if ((salt & UINT64_C(1)) != 0)
        a ^= x << 11;
    else
        a += (x >> 7) + UINT64_C(0x94d049bb133111eb);
    return a ^ (a >> 28);
}

/* Intentionally in the SAME TU, but not selected by -kagura-allow. */
__attribute__((noinline, used))
uint64_t DD_VM_GUARD(uint64_t x, uint64_t salt) {
    return (x ^ UINT64_C(0xd6e8feb86659fd93)) +
           (salt * UINT64_C(0x9e3779b97f4a7c15));
}
