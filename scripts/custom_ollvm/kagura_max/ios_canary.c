/* iPhone-only Kagura LLVM19 baseline vs transformed entry point.
 * Both symbols are compiled from the SAME critical.c; only the protected
 * bitcode is transformed by Kagura's seven real LLVM IR passes.
 * Never uses JIT, PAC stripping, jailbreak APIs, UDID or network.
 */
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <stddef.h>
#include <time.h>

extern uint64_t dd_kagura_plain(uint64_t x, uint64_t salt);
extern uint64_t dd_kagura_protected(uint64_t x, uint64_t salt);

typedef uint64_t (*dd_kagura_function)(uint64_t, uint64_t);
enum { DD_KAGURA_VECTORS = 8192, DD_KAGURA_BENCH_CALLS = 4096,
       DD_KAGURA_BENCH_PAIRS = 5 };
static volatile uint64_t dd_kagura_sink;

static uint64_t dd_rotate(uint64_t value) {
    return (value << 9) | (value >> 55);
}

int dd_kagura_ios_parity(char *report, size_t capacity, const char *app_uuid) {
    if (!report || capacity < 256 || !app_uuid)
        return 0;
    uint64_t seed = UINT64_C(0x123456789abcdef0);
    uint64_t digest = 0;
    for (unsigned i = 0; i < DD_KAGURA_VECTORS; ++i) {
        seed ^= seed << 13;
        seed ^= seed >> 7;
        seed ^= seed << 17;
        const uint64_t x = i < 16 ? (uint64_t)i : seed;
        const uint64_t salt = (seed >> 1) ^
            ((uint64_t)i * UINT64_C(0x9e3779b97f4a7c15));
        const uint64_t plain = dd_kagura_plain(x, salt);
        const uint64_t candidate = dd_kagura_protected(x, salt);
        if (plain != candidate) {
            (void)snprintf(report, capacity,
                           "DD_KAGURA_CONTEXT=IOS_DEVICE\n"
                           "DD_KAGURA_ERROR=MISMATCH_AT_%u\n", i);
            return 0;
        }
        digest = dd_rotate(digest ^ plain) + (uint64_t)i;
    }
    dd_kagura_sink = digest;
    const int count = snprintf(report, capacity,
        "DD_KAGURA_SCHEMA=2\n"
        "DD_KAGURA_CONTEXT=IOS_DEVICE\n"
        "DD_KAGURA_ARCH=arm64:0x00000000\n"
        "DD_KAGURA_APP_UUID=%s\n"
        "DD_KAGURA_PIPELINE=STR_FLA_BCF_SUB_CO_BBR_BBS\n"
        "DD_KAGURA_VECTORS_PASS=8192\n"
        "DD_KAGURA_CHECKSUM=%016" PRIx64 "\n"
        "DD_KAGURA_COMPLETE=PASS\n", app_uuid, digest);
    return count > 0 && (size_t)count < capacity;
}

static int dd_nanotime(uint64_t *out) {
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0)
        return 0;
    *out = (uint64_t)ts.tv_sec * UINT64_C(1000000000) + ts.tv_nsec;
    return 1;
}

static uint64_t dd_batch(dd_kagura_function function) {
    uint64_t digest = 0;
    for (unsigned i = 0; i < DD_KAGURA_BENCH_CALLS; ++i) {
        uint64_t x = (uint64_t)i * UINT64_C(0x9e3779b97f4a7c15);
        uint64_t salt = (x >> 3) ^ UINT64_C(0xc0ffee123456789a);
        digest ^= function(x, salt);
    }
    dd_kagura_sink = digest;
    return digest;
}

static int dd_measure(dd_kagura_function function, uint64_t *nanos,
                      uint64_t *checksum) {
    uint64_t start = 0, end = 0;
    if (!dd_nanotime(&start))
        return 0;
    *checksum = dd_batch(function);
    if (!dd_nanotime(&end) || end <= start)
        return 0;
    *nanos = (end - start) / DD_KAGURA_BENCH_CALLS;
    return *nanos > 0;
}

static uint64_t dd_median5(uint64_t samples[DD_KAGURA_BENCH_PAIRS]) {
    for (unsigned i = 1; i < DD_KAGURA_BENCH_PAIRS; ++i) {
        const uint64_t value = samples[i];
        unsigned j = i;
        while (j > 0 && samples[j - 1] > value) {
            samples[j] = samples[j - 1];
            --j;
        }
        samples[j] = value;
    }
    return samples[DD_KAGURA_BENCH_PAIRS / 2];
}

int dd_kagura_ios_benchmark(char *report, size_t capacity, const char *app_uuid) {
    if (!report || capacity < 256 || !app_uuid)
        return 0;
    uint64_t plain[DD_KAGURA_BENCH_PAIRS];
    uint64_t protected[DD_KAGURA_BENCH_PAIRS];
    uint64_t checksum = 0, check = 0;
    /* Bounded warmups, no startup hooks or background workers. */
    for (unsigned i = 0; i < 2; ++i) {
        if (dd_batch(dd_kagura_plain) != dd_batch(dd_kagura_protected))
            goto mismatch;
    }
    for (unsigned i = 0; i < DD_KAGURA_BENCH_PAIRS; ++i) {
        int ok = 0;
        if (i & 1U) {
            ok = dd_measure(dd_kagura_protected, &protected[i], &check) &&
                 dd_measure(dd_kagura_plain, &plain[i], &checksum);
        } else {
            ok = dd_measure(dd_kagura_plain, &plain[i], &checksum) &&
                 dd_measure(dd_kagura_protected, &protected[i], &check);
        }
        if (!ok || checksum != check)
            goto mismatch;
    }
    const uint64_t median_plain = dd_median5(plain);
    const uint64_t median_protected = dd_median5(protected);
    const int count = snprintf(report, capacity,
        "DD_KAGURA_PERF_SCHEMA=2\n"
        "DD_KAGURA_PERF_CONTEXT=IOS_DEVICE\n"
        "DD_KAGURA_PERF_ARCH=arm64:0x00000000\n"
        "DD_KAGURA_PERF_APP_UUID=%s\n"
        "DD_KAGURA_PERF_PAIRS=5\n"
        "DD_KAGURA_PERF_CALLS_PER_SAMPLE=4096\n"
        "DD_KAGURA_PERF_PLAIN_MEDIAN_NS=%" PRIu64 "\n"
        "DD_KAGURA_PERF_PROTECTED_MEDIAN_NS=%" PRIu64 "\n"
        "DD_KAGURA_PERF_CHECKSUM=%016" PRIx64 "\n"
        "DD_KAGURA_PERF_NOTE=OBSERVATIONAL_NOT_SECURITY_ATTESTATION\n"
        "DD_KAGURA_PERF_COMPLETE=PASS\n",
        app_uuid, median_plain, median_protected, checksum);
    return count > 0 && (size_t)count < capacity;
mismatch:
    (void)snprintf(report, capacity,
                   "DD_KAGURA_PERF_CONTEXT=IOS_DEVICE\n"
                   "DD_KAGURA_PERF_ERROR=TIMING_OR_PARITY\n");
    return 0;
}
