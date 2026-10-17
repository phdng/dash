#ifndef DD_PROTECTION_LAB_PERF_PILOT_H
#define DD_PROTECTION_LAB_PERF_PILOT_H

#include <stdint.h>

/* Only the independent lab may use this observation-only benchmark. */
enum { DD_PERF_ITERATIONS = 20000, DD_PERF_REPEATS = 5, DD_PERF_PAIRS = 5 };
enum {
    DD_PERF_VM = 0,
    DD_PERF_CE = 1,
    DD_PERF_ICALL = 2,
    DD_PERF_IGV = 3,
    DD_PERF_IBR = 4
};
typedef struct {
    /* Median monotonic elapsed nanoseconds for 20,000 calls per variant. */
    uint64_t native_ns[DD_PERF_PAIRS];
    uint64_t transformed_ns[DD_PERF_PAIRS];
} dd_perf_results;

/* Returns 1 only if all sample clocks and counters are usable. No latency
 * guarantees and no comparison threshold: cross-device clocks are noisy. */
int dd_perf_run(dd_perf_results *out);

#endif
