/* A separate protocol from the seven-line runtime PASS proof. */
#include "perf_report.h"
#include <inttypes.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

int dd_perf_render(char *output, size_t capacity, const dd_perf_results *data,
                   const char *context, const char *abi) {
    if (!output || capacity == 0 || !data || !context || !abi)
        return 0;
    if (!((strcmp(context, "MACOS_HOST") == 0 &&
           strcmp(abi, "NOT_APPLICABLE") == 0) ||
          (strcmp(context, "IOS_DEVICE") == 0 &&
           (strcmp(abi, "arm64:0x00000000") == 0 ||
            strcmp(abi, "arm64e:0x80000002") == 0))))
        return 0;
    for (unsigned i = 0; i < DD_PERF_PAIRS; ++i)
        if (!data->native_ns[i] || !data->transformed_ns[i])
            return 0;
    int n = snprintf(
        output, capacity,
        "DD_PERF_SCHEMA=1\n"
        "DD_PERF_CONTEXT=%s\n"
        "DD_PERF_ABI=%s\n"
        "DD_PERF_ITERATIONS=20000\n"
        "DD_PERF_REPEATS=5\n"
        "DD_PERF_ESTIMATOR=MEDIAN_ELAPSED_NS\n"
        "DD_PERF_VM_NATIVE_NS=%" PRIu64 "\n"
        "DD_PERF_VM_PROTECTED_NS=%" PRIu64 "\n"
        "DD_PERF_CE_NATIVE_NS=%" PRIu64 "\n"
        "DD_PERF_CE_PROTECTED_NS=%" PRIu64 "\n"
        "DD_PERF_ICALL_NATIVE_NS=%" PRIu64 "\n"
        "DD_PERF_ICALL_PROTECTED_NS=%" PRIu64 "\n"
        "DD_PERF_IGV_NATIVE_NS=%" PRIu64 "\n"
        "DD_PERF_IGV_PROTECTED_NS=%" PRIu64 "\n"
        "DD_PERF_IBR_NATIVE_NS=%" PRIu64 "\n"
        "DD_PERF_IBR_PROTECTED_NS=%" PRIu64 "\n"
        "DD_PERF_NOTE=OBSERVATIONAL_NOT_SECURITY_PROOF\n",
        context, abi,
        data->native_ns[DD_PERF_VM], data->transformed_ns[DD_PERF_VM],
        data->native_ns[DD_PERF_CE], data->transformed_ns[DD_PERF_CE],
        data->native_ns[DD_PERF_ICALL], data->transformed_ns[DD_PERF_ICALL],
        data->native_ns[DD_PERF_IGV], data->transformed_ns[DD_PERF_IGV],
        data->native_ns[DD_PERF_IBR], data->transformed_ns[DD_PERF_IBR]);
    if (n <= 0 || (size_t)n >= capacity) {
        output[0] = '\0';
        return 0;
    }
    return 1;
}
