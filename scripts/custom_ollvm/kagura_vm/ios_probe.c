/* K7 separate device canary; no Crane/ProtectionLab/K5 code or identifiers. */
#include <inttypes.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <time.h>
#include <string.h>

extern uint64_t dd_vm_plain(uint64_t, uint64_t);
extern uint64_t dd_vm_protected(uint64_t, uint64_t);
extern uint64_t dd_vm_guard_plain(uint64_t, uint64_t);
extern uint64_t dd_vm_guard_protected(uint64_t, uint64_t);

enum { DD_VM_VECTORS = 4096, DD_VM_BENCH_CALLS = 1024, DD_VM_BENCH_PAIRS = 3 };
typedef uint64_t (*vm_fun)(uint64_t, uint64_t);
static volatile uint64_t vm_sink;

static uint64_t rotate(uint64_t x) { return (x << 9) | (x >> 55); }
static void vector(unsigned i, uint64_t *x, uint64_t *salt) {
    uint64_t t = UINT64_C(0x123456789abcdef0) ^
                 ((uint64_t)i * UINT64_C(0x9e3779b97f4a7c15));
    t ^= t >> 17;
    t ^= t << 23;
    t ^= t >> 11;
    *x = i < 16 ? (uint64_t)i : t;
    *salt = (t >> 3) ^ ((uint64_t)i * UINT64_C(0xbf58476d1ce4e5b9));
}
static uint64_t ns(void) {
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC, &t) != 0) return 0;
    return (uint64_t)t.tv_sec * UINT64_C(1000000000) + (uint64_t)t.tv_nsec;
}
static uint64_t batch(vm_fun f) {
    uint64_t digest = 0;
    for (unsigned i = 0; i < DD_VM_BENCH_CALLS; ++i) {
        uint64_t x, salt;
        vector(i, &x, &salt);
        digest = rotate(digest ^ f(x, salt)) + i;
    }
    vm_sink = digest;
    return digest;
}
static int identifier_ok(const char *uuid) {
    if (!uuid || strlen(uuid) != 36) return 0;
    for (unsigned i = 0; i < 36; ++i) {
        if (i == 8 || i == 13 || i == 18 || i == 23) {
            if (uuid[i] != '-') return 0;
        } else if (!((uuid[i] >= '0' && uuid[i] <= '9') ||
                     (uuid[i] >= 'a' && uuid[i] <= 'f'))) return 0;
    }
    return 1;
}
static int written(int len, size_t size) { return len > 0 && (size_t)len < size; }

int dd_vm_ios_parity(char *out, size_t size, const char *uuid) {
    if (!out || size < 512 || !identifier_ok(uuid)) return 0;
    uint64_t parity = 0, guard = 0;
    for (unsigned i = 0; i < DD_VM_VECTORS; ++i) {
        uint64_t x, salt;
        vector(i, &x, &salt);
        uint64_t plain = dd_vm_plain(x, salt);
        uint64_t vm = dd_vm_protected(x, salt);
        uint64_t gp = dd_vm_guard_plain(x, salt);
        uint64_t gv = dd_vm_guard_protected(x, salt);
        if (plain != vm || gp != gv) {
            (void)snprintf(out, size, "DD_VM_IOS_ERROR=MISMATCH_AT_%u\n", i);
            return 0;
        }
        parity = rotate(parity ^ plain) + i;
        guard = rotate(guard ^ gp) + i;
    }
    vm_sink = parity ^ guard;
    if (parity != UINT64_C(0x9625f13d712f59c3) ||
        guard != UINT64_C(0x09d9d53ddf189ce7)) {
        (void)snprintf(out, size, "DD_VM_IOS_ERROR=REFERENCE_CHECKSUM_MISMATCH\n");
        return 0;
    }
    const int count = snprintf(out, size,
        "DD_VM_IOS_SCHEMA=1\n"
        "DD_VM_IOS_CONTEXT=IOS_DEVICE\n"
        "DD_VM_IOS_ARCH=arm64:0x00000000\n"
        "DD_VM_IOS_APP_UUID=%s\n"
        "DD_VM_IOS_PIPELINE=KAGURA_VM_SELECTIVE\n"
        "DD_VM_IOS_VECTORS_PASS=4096\n"
        "DD_VM_IOS_PARITY_CHECKSUM=%016" PRIx64 "\n"
        "DD_VM_IOS_GUARD_CHECKSUM=%016" PRIx64 "\n"
        "DD_VM_IOS_COMPLETE=PASS\n", uuid, parity, guard);
    return written(count, size);
}

int dd_vm_ios_benchmark(char *out, size_t size, const char *uuid) {
    if (!out || size < 512 || !identifier_ok(uuid)) return 0;
    if (batch(dd_vm_plain) != batch(dd_vm_protected)) {
        (void)snprintf(out, size, "DD_VM_IOS_PERF_ERROR=MISMATCH\n");
        return 0;
    }
    uint64_t plain[DD_VM_BENCH_PAIRS], protected[DD_VM_BENCH_PAIRS];
    for (unsigned i = 0; i < DD_VM_BENCH_PAIRS; ++i) {
        vm_fun first = (i & 1U) ? dd_vm_protected : dd_vm_plain;
        vm_fun second = (i & 1U) ? dd_vm_plain : dd_vm_protected;
        const uint64_t a = ns();
        const uint64_t da = batch(first);
        const uint64_t b = ns();
        const uint64_t db = batch(second);
        const uint64_t c = ns();
        if (a == 0 || b <= a || c <= b || da != db) {
            (void)snprintf(out, size, "DD_VM_IOS_PERF_ERROR=TIMING_OR_RESULT\n");
            return 0;
        }
        const uint64_t first_ns = (b - a) / DD_VM_BENCH_CALLS;
        const uint64_t second_ns = (c - b) / DD_VM_BENCH_CALLS;
        plain[i] = (i & 1U) ? second_ns : first_ns;
        protected[i] = (i & 1U) ? first_ns : second_ns;
        if (plain[i] == 0 || protected[i] == 0) {
            (void)snprintf(out, size, "DD_VM_IOS_PERF_ERROR=ZERO_SAMPLE\n");
            return 0;
        }
    }
    const int count = snprintf(out, size,
        "DD_VM_IOS_PERF_SCHEMA=1\n"
        "DD_VM_IOS_PERF_CONTEXT=IOS_DEVICE\n"
        "DD_VM_IOS_PERF_ARCH=arm64:0x00000000\n"
        "DD_VM_IOS_PERF_APP_UUID=%s\n"
        "DD_VM_IOS_PERF_PAIRS=3\n"
        "DD_VM_IOS_PERF_CALLS_PER_SAMPLE=1024\n"
        "DD_VM_IOS_PERF_PLAIN_NS_0=%" PRIu64 "\n"
        "DD_VM_IOS_PERF_PROTECTED_NS_0=%" PRIu64 "\n"
        "DD_VM_IOS_PERF_PLAIN_NS_1=%" PRIu64 "\n"
        "DD_VM_IOS_PERF_PROTECTED_NS_1=%" PRIu64 "\n"
        "DD_VM_IOS_PERF_PLAIN_NS_2=%" PRIu64 "\n"
        "DD_VM_IOS_PERF_PROTECTED_NS_2=%" PRIu64 "\n"
        "DD_VM_IOS_PERF_NOTE=OBSERVATIONAL_NOT_SECURITY_ATTESTATION\n"
        "DD_VM_IOS_PERF_COMPLETE=PASS\n",
        uuid, plain[0], protected[0], plain[1], protected[1],
        plain[2], protected[2]);
    return written(count, size);
}
