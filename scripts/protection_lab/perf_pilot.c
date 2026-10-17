/* Synthetic, repeatable, observation-only host/device benchmark.
 * Public input values; no network, JIT, memory patching or private API.
 * Same workload in each pair, compiler-owned typed callbacks (arm64e PAC).
 */
#include "perf_pilot.h"
#include "canary.h"
#include "sllvm_pilot.h"
#include "igv_ibr.h"
#include <stddef.h>
#include <stdint.h>
#include <time.h>

typedef uint64_t (*dd_perf_fn)(uint64_t, uint64_t, unsigned);
static volatile uint64_t dd_perf_sink = 0;

static __attribute__((noinline))
uint64_t dd_perf_vm_native(uint64_t a, uint64_t b, unsigned mode) {
    (void)mode;
    return dd_canary_native(a, b);
}
static __attribute__((noinline))
uint64_t dd_perf_vm_transformed(uint64_t a, uint64_t b, unsigned mode) {
    (void)mode;
    return dd_canary_vm(a, b);
}
static __attribute__((noinline))
uint64_t dd_perf_ce_native(uint64_t a, uint64_t b, unsigned mode) {
    (void)b; (void)mode;
    return dd_pilot_plain_hash((uint32_t)(a >> 32));
}
static __attribute__((noinline))
uint64_t dd_perf_ce_transformed(uint64_t a, uint64_t b, unsigned mode) {
    (void)b; (void)mode;
    return dd_pilot_protected_hash((uint32_t)(a >> 32));
}
static __attribute__((noinline))
uint64_t dd_perf_icall_native(uint64_t a, uint64_t b, unsigned mode) {
    return dd_pilot_plain_dispatch(a, b, mode);
}
static __attribute__((noinline))
uint64_t dd_perf_icall_transformed(uint64_t a, uint64_t b, unsigned mode) {
    return dd_pilot_protected_dispatch(a, b, mode);
}
static __attribute__((noinline))
uint64_t dd_perf_igv_native(uint64_t a, uint64_t b, unsigned mode) {
    return dd_igv_plain(a, b, mode);
}
static __attribute__((noinline))
uint64_t dd_perf_igv_transformed(uint64_t a, uint64_t b, unsigned mode) {
    return dd_igv_protected(a, b, mode);
}
static __attribute__((noinline))
uint64_t dd_perf_ibr_native(uint64_t a, uint64_t b, unsigned mode) {
    return dd_ibr_plain(a, b, mode);
}
static __attribute__((noinline))
uint64_t dd_perf_ibr_transformed(uint64_t a, uint64_t b, unsigned mode) {
    return dd_ibr_protected(a, b, mode);
}

static dd_perf_fn const dd_perf_plain_fns[DD_PERF_PAIRS] = {
    dd_perf_vm_native, dd_perf_ce_native, dd_perf_icall_native,
    dd_perf_igv_native, dd_perf_ibr_native
};
static dd_perf_fn const dd_perf_protected_fns[DD_PERF_PAIRS] = {
    dd_perf_vm_transformed, dd_perf_ce_transformed, dd_perf_icall_transformed,
    dd_perf_igv_transformed, dd_perf_ibr_transformed
};

static int dd_now(uint64_t *ns) {
    struct timespec time;
    if (!ns || clock_gettime(CLOCK_MONOTONIC, &time) != 0 ||
        time.tv_sec < 0 || time.tv_nsec < 0 || time.tv_nsec >= 1000000000L)
        return 0;
    *ns = (uint64_t)time.tv_sec * UINT64_C(1000000000) +
          (uint64_t)time.tv_nsec;
    return 1;
}

/* A tiny warm-up and 20,000 sampled calls. One volatile write occurs after
 * the timed interval, so the optimizer cannot silently discard all calls.
 */
static int dd_measure(dd_perf_fn fn, uint64_t *elapsed) {
    uint64_t x = UINT64_C(0x8273beafe1235679);
    uint64_t checksum = 0;
    for (unsigned i = 0; i < 256; ++i) {
        x ^= x << 13; x ^= x >> 7; x ^= x << 17;
        checksum ^= fn(x, x ^ UINT64_C(0x123456789abcdef0), i);
    }
    uint64_t start, end;
    if (!dd_now(&start)) return 0;
    for (unsigned i = 0; i < DD_PERF_ITERATIONS; ++i) {
        x ^= x << 13; x ^= x >> 7; x ^= x << 17;
        checksum ^= fn(x, (x ^ UINT64_C(0x123456789abcdef0)) + i, i);
    }
    if (!dd_now(&end) || end <= start) return 0;
    dd_perf_sink ^= checksum;
    *elapsed = end - start;
    return *elapsed > 0;
}

static uint64_t dd_median(uint64_t values[DD_PERF_REPEATS]) {
    for (unsigned i = 1; i < DD_PERF_REPEATS; ++i) {
        uint64_t key = values[i];
        unsigned j = i;
        while (j > 0 && values[j - 1] > key) {
            values[j] = values[j - 1];
            --j;
        }
        values[j] = key;
    }
    return values[DD_PERF_REPEATS / 2];
}

int dd_perf_run(dd_perf_results *out) {
    if (!out) return 0;
    dd_perf_results measured = {{0}, {0}};
    for (unsigned index = 0; index < DD_PERF_PAIRS; ++index) {
        uint64_t plain[DD_PERF_REPEATS] = {0};
        uint64_t candidate[DD_PERF_REPEATS] = {0};
        for (unsigned rep = 0; rep < DD_PERF_REPEATS; ++rep) {
            /* Alternating order limits systematic warm-cache bias, but does
             * not make these measurements comparable to iPhone production. */
            if (rep & 1U) {
                if (!dd_measure(dd_perf_protected_fns[index], &candidate[rep]) ||
                    !dd_measure(dd_perf_plain_fns[index], &plain[rep]))
                    return 0;
            } else {
                if (!dd_measure(dd_perf_plain_fns[index], &plain[rep]) ||
                    !dd_measure(dd_perf_protected_fns[index], &candidate[rep]))
                    return 0;
            }
        }
        measured.native_ns[index] = dd_median(plain);
        measured.transformed_ns[index] = dd_median(candidate);
        if (!measured.native_ns[index] || !measured.transformed_ns[index])
            return 0;
    }
    *out = measured;
    return 1;
}
