/* K8 independent, public-data-only five-pass LLVM19 Kagura canary.
 * No Crane runtime, Objective-C, hook, secret, PAC or device identifier. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>

#if defined(__clang__)
#define DD_NOINLINE __attribute__((noinline))
#else
#define DD_NOINLINE
#endif

/* GENC requires a private/internal *constant* integer global with a load.
 * The indexing is runtime-variable so LLVM cannot fold away the load. */
static const uint64_t dd_k8_table[8] = {
    UINT64_C(0x10939a2b377a5a03), UINT64_C(0xc35e91d487f0a217),
    UINT64_C(0x7f4a1d6652d9b188), UINT64_C(0xe91c3b025478fad1),
    UINT64_C(0xa7d4382e601fb9c3), UINT64_C(0x315f84c9bb2c76a0),
    UINT64_C(0x9bed152a7fc07348), UINT64_C(0x46a229b8dc351f70),
};

/* IBR rewrites direct calls to another function defined in this module. */
DD_NOINLINE static uint64_t dd_k8_internal(uint64_t n, uint64_t t) {
    uint64_t v = n ^ (t + UINT64_C(0x9e3779b97f4a7c15));
    v ^= v >> 27;
    return v * UINT64_C(0xbf58476d1ce4e5b9);
}

/* The named external strlen() declaration drives CI's dlsym thunk table;
 * never route callbacks/hooks through the experiment. */
DD_NOINLINE uint64_t dd_k8_evaluate(uint64_t n, uint64_t salt) {
    char token[4] = {
        (char)('A' + (n & 7U)),
        (char)('a' + (salt & 7U)), 'Z', '\0'
    };
    const size_t length = strlen(token);
    /* Volatile integer alloca preserves a genuine stack load/store at -O1
     * for MVO, without forcing -O0/optnone on the whole module. */
    volatile uint64_t box = dd_k8_internal(n ^ salt, (uint64_t)length);
    uint64_t r = box ^ dd_k8_table[(n ^ (salt >> 3)) & 7U];
    /* Several control-flow blocks with safe direct calls for FSPLIT. */
    if (n & 1U) r ^= dd_k8_internal(r, n);
    if (n & 2U) r += dd_k8_internal(r, salt);
    if (n & 4U) r ^= dd_k8_internal(r ^ n, salt);
    if (n & 8U) r += dd_k8_internal(r, n + salt);
    if (n & 16U) r ^= dd_k8_internal(r + salt, n);
    return r + ((uint64_t)length << 32);
}
