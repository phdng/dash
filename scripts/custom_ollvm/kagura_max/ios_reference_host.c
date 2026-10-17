/* macOS CI-only C source-of-truth parity/benchmark checksum check.
 * Both functions link from baseline critical.c; this does NOT test Kagura
 * obfuscation or iPhone execution. Output is HOST_REFERENCE only.
 */
#include <ctype.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

extern int dd_kagura_ios_parity(char *, size_t, const char *);
extern int dd_kagura_ios_benchmark(char *, size_t, const char *);

static int emit(const char *report, const char *field, const char *label) {
    const char *start = strstr(report, field);
    if (!start)
        return 0;
    start += strlen(field);
    for (unsigned i = 0; i < 16; ++i) {
        if (!((start[i] >= '0' && start[i] <= '9') ||
              (start[i] >= 'a' && start[i] <= 'f')))
            return 0;
    }
    if (start[16] != '\n')
        return 0;
    printf("%s=%.*s\n", label, 16, start);
    return 1;
}

int main(void) {
    char report[1024] = {0};
    const char *uuid = "179f30eb-1629-3658-86fc-cd7da188a483";
    if (!dd_kagura_ios_parity(report, sizeof(report), uuid) ||
        !emit(report, "DD_KAGURA_CHECKSUM=",
              "DD_KAGURA_HOST_PARITY_CHECKSUM"))
        return 1;
    memset(report, 0, sizeof(report));
    if (!dd_kagura_ios_benchmark(report, sizeof(report), uuid) ||
        !emit(report, "DD_KAGURA_PERF_CHECKSUM=",
              "DD_KAGURA_HOST_BENCHMARK_CHECKSUM"))
        return 1;
    return 0;
}
