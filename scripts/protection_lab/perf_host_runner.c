/* macOS-host sample, never confused with A12+ iOS benchmark evidence. */
#include "perf_pilot.h"
#include "perf_report.h"
#include <stdio.h>

int main(void) {
    dd_perf_results results;
    char buffer[2048];
    if (!dd_perf_run(&results) ||
        !dd_perf_render(buffer, sizeof(buffer), &results,
                        "MACOS_HOST", "NOT_APPLICABLE")) {
        fputs("DD_PERF_ERROR=HOST_MEASUREMENT_FAILED\n", stderr);
        return 1;
    }
    fputs(buffer, stdout);
    return 0;
}
