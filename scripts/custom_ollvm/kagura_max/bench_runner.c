/* Native host-only timing microbenchmark. No device claims or secrets.
 * Compiled separately with Apple Clang, linked with each LLVM19 candidate.
 * Fixed inputs, warmups, multiple samples, observable volatile checksum.
 */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <time.h>

extern uint64_t dd_kagura_critical(uint64_t x, uint64_t salt);
static volatile uint64_t dd_bench_sink;

enum { DD_BENCH_WARMUPS = 2, DD_BENCH_SAMPLES = 11,
       DD_BENCH_CALLS = 32768 };

static int dd_now(uint64_t *value) {
    struct timespec when;
    if (clock_gettime(CLOCK_MONOTONIC, &when) != 0)
        return 0;
    *value = (uint64_t)when.tv_sec * UINT64_C(1000000000) +
             (uint64_t)when.tv_nsec;
    return 1;
}

static uint64_t dd_batch(uint64_t initial) {
    uint64_t acc = initial;
    for (unsigned i = 0; i < DD_BENCH_CALLS; ++i) {
        uint64_t x = (uint64_t)i * UINT64_C(0x9e3779b97f4a7c15);
        uint64_t salt = (x >> 3) ^ UINT64_C(0xc0ffee123456789a);
        acc ^= dd_kagura_critical(x, salt);
    }
    dd_bench_sink = acc;
    return acc;
}

int main(void) {
    uint64_t t0 = 0, t1 = 0, result = 0;
    for (unsigned w = 0; w < DD_BENCH_WARMUPS; ++w)
        result = dd_batch(UINT64_C(0x123456789abcdef0));

    if (puts("DD_KAGURA_BENCH_SCHEMA=1") < 0 ||
        puts("DD_KAGURA_BENCH_CONTEXT=MACOS_HOST") < 0 ||
        puts("DD_KAGURA_BENCH_SAMPLES=11") < 0 ||
        puts("DD_KAGURA_BENCH_CALLS_PER_SAMPLE=32768") < 0)
        return 2;
    for (unsigned i = 1; i <= DD_BENCH_SAMPLES; ++i) {
        if (!dd_now(&t0))
            return 3;
        result = dd_batch(UINT64_C(0x123456789abcdef0));
        if (!dd_now(&t1) || t1 <= t0)
            return 4;
        uint64_t nanos_per_call = (t1 - t0) / DD_BENCH_CALLS;
        if (nanos_per_call == 0)
            nanos_per_call = 1;
        if (printf("DD_KAGURA_BENCH_SAMPLE_%02u_NS_PER_CALL=%" PRIu64 "\n",
                   i, nanos_per_call) < 0)
            return 5;
    }
    if (printf("DD_KAGURA_BENCH_CHECKSUM=%016" PRIx64 "\n", result) < 0 ||
        puts("DD_KAGURA_BENCH_COMPLETE=PASS") < 0)
        return 6;
    return 0;
}
