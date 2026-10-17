/* Portable C functional test suite for the standalone iOS/macOS runner.
 * No entitlements, injection, private APIs, network access or filesystem writes.
 */
#include "device_suites.h"
#include "canary.h"
#include "sllvm_pilot.h"
#include "igv_ibr.h"

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

static uint64_t dd_next(uint64_t *state) {
    *state ^= *state << 13;
    *state ^= *state >> 7;
    *state ^= *state << 17;
    return *state;
}

static void dd_inputs(unsigned i, uint64_t *state,
                      uint64_t *a, uint64_t *b, unsigned *mode) {
    *a = dd_next(state);
    *b = (*a ^ UINT64_C(0x123456789abcdef0)) + (uint64_t)i;
    *mode = (unsigned)(*a >> 23) ^ i;
    if (i == 0) { *a = 0; *b = 0; *mode = 0; }
    if (i == 1) { *a = UINT64_MAX; *b = UINT64_MAX; *mode = UINT32_MAX; }
    if (i == 2) { *a = UINT64_MAX; *b = 0; *mode = 2; }
    if (i == 3) { *a = 0; *b = UINT64_MAX; *mode = 3; }
}

int dd_device_test_vm(void) {
    uint64_t state = UINT64_C(0x8273beafe1235679);
    for (unsigned i = 0; i < DD_DEVICE_VECTORS; ++i) {
        uint64_t a, b;
        unsigned mode;
        dd_inputs(i, &state, &a, &b, &mode);
        (void)mode;
        uint64_t native = dd_canary_native(a, b);
        if (dd_canary_vm(a, b) != native ||
            dd_canary_indirect(dd_canary_native, a, b) != native) {
            fprintf(stderr, "DD_RUNTIME_ERROR=VM:%u\n", i);
            return 0;
        }
    }
    puts("DD_RUNTIME_VM_PASS=8192");
    return 1;
}

int dd_device_test_ce_icall(void) {
    uint64_t state = UINT64_C(0x8273beafe1235679);
    for (unsigned i = 0; i < DD_DEVICE_VECTORS; ++i) {
        uint64_t a, b;
        unsigned mode;
        dd_inputs(i, &state, &a, &b, &mode);
        uint32_t seed = (uint32_t)(a >> 32);
        if (dd_pilot_plain_hash(seed) != dd_pilot_protected_hash(seed) ||
            dd_pilot_plain_dispatch(a, b, mode) !=
                dd_pilot_protected_dispatch(a, b, mode)) {
            fprintf(stderr, "DD_RUNTIME_ERROR=CE_ICALL:%u\n", i);
            return 0;
        }
    }
    puts("DD_RUNTIME_CE_ICALL_PASS=8192");
    return 1;
}

int dd_device_test_igv_ibr(void) {
    uint64_t state = UINT64_C(0x8273beafe1235679);
    for (unsigned i = 0; i < DD_DEVICE_VECTORS; ++i) {
        uint64_t a, b;
        unsigned mode;
        dd_inputs(i, &state, &a, &b, &mode);
        if (dd_igv_plain(a, b, mode) != dd_igv_protected(a, b, mode) ||
            dd_ibr_plain(a, b, mode) != dd_ibr_protected(a, b, mode)) {
            fprintf(stderr, "DD_RUNTIME_ERROR=IGV_IBR:%u\n", i);
            return 0;
        }
    }
    puts("DD_RUNTIME_IGV_IBR_PASS=8192");
    return 1;
}
