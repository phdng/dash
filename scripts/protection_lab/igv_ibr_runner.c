/* Independent differential runner: runs on macOS host, never on an iOS device. */
#include "igv_ibr.h"
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <time.h>

typedef uint64_t (*dd_pilot_eval)(uint64_t, uint64_t, unsigned);
static volatile uint64_t dd_bench_sink;

static double measure_us(dd_pilot_eval fn) {
    clock_t start = clock();
    uint64_t sink = 0;
    for (unsigned i = 0; i < 100000; ++i) {
        uint64_t a = (uint64_t)i * UINT64_C(0x9e3779b97f4a7c15);
        uint64_t b = a ^ UINT64_C(0xd1b54a32d192ed03);
        sink ^= fn(a, b, i);
    }
    clock_t elapsed = clock() - start;
    dd_bench_sink = sink;
    return elapsed >= 0 ? (double)elapsed * 1000000.0 / CLOCKS_PER_SEC : 0.0;
}

int main(void) {
    uint64_t state = UINT64_C(0x8273beafe1235679);
    for (unsigned i = 0; i < 8192; ++i) {
        state ^= state << 13;
        state ^= state >> 7;
        state ^= state << 17;
        uint64_t a = state;
        uint64_t b = (state ^ UINT64_C(0x123456789abcdef0)) + i;
        unsigned mode = (unsigned)(state >> 23) ^ i;
        if (i == 0) { a = 0; b = 0; mode = 0; }
        if (i == 1) { a = UINT64_MAX; b = UINT64_MAX; mode = UINT32_MAX; }
        if (i == 2) { a = UINT64_MAX; b = 0; mode = 2; }
        if (i == 3) { a = 0; b = UINT64_MAX; mode = 3; }
        uint64_t igv_plain = dd_igv_plain(a, b, mode);
        uint64_t igv_protected = dd_igv_protected(a, b, mode);
        uint64_t ibr_plain = dd_ibr_plain(a, b, mode);
        uint64_t ibr_protected = dd_ibr_protected(a, b, mode);
        if (igv_plain != igv_protected || ibr_plain != ibr_protected) {
            fprintf(stderr,
                    "IGV_IBR_MISMATCH i=%u igv=%016" PRIx64 "/%016" PRIx64
                    " ibr=%016" PRIx64 "/%016" PRIx64 "\n",
                    i, igv_plain, igv_protected, ibr_plain, ibr_protected);
            return 1;
        }
    }
    puts("IGV_IBR_HOST_PASS: 8192 dual-function parity vectors");
    double igv_plain = measure_us(dd_igv_plain);
    double igv_protected = measure_us(dd_igv_protected);
    double ibr_plain = measure_us(dd_ibr_plain);
    double ibr_protected = measure_us(dd_ibr_protected);
    printf("IGV_IBR_BENCH: igv_plain_us=%.3f igv_protected_us=%.3f "
           "ibr_plain_us=%.3f ibr_protected_us=%.3f\n",
           igv_plain, igv_protected, ibr_plain, ibr_protected);
    return 0;
}
