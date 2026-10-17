#ifndef DD_PROTECTION_LAB_PERF_REPORT_H
#define DD_PROTECTION_LAB_PERF_REPORT_H
#include "perf_pilot.h"
#include <stddef.h>

/* Lossless, deterministic, machine-readable observation-only text. */
int dd_perf_render(char *output, size_t capacity, const dd_perf_results *data,
                   const char *context, const char *abi);
#endif
