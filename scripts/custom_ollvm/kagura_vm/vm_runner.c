/* Native host only: compare actual LLVM19 baseline vs Kagura VM runtime. */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <time.h>

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

int main(void) {
    uint64_t parity = 0, guard = 0;
    for (unsigned i = 0; i < DD_VM_VECTORS; ++i) {
        uint64_t x, salt;
        vector(i, &x, &salt);
        uint64_t plain = dd_vm_plain(x, salt);
        uint64_t vm = dd_vm_protected(x, salt);
        uint64_t gp = dd_vm_guard_plain(x, salt);
        uint64_t gv = dd_vm_guard_protected(x, salt);
        if (plain != vm || gp != gv) {
            fprintf(stderr, "DD_VM_ERROR=MISMATCH_AT_%u\n", i);
            return 1;
        }
        parity = rotate(parity ^ plain) + i;
        guard = rotate(guard ^ gp) + i;
    }
    uint64_t plain_ns[DD_VM_BENCH_PAIRS], protected_ns[DD_VM_BENCH_PAIRS];
    if (batch(dd_vm_plain) != batch(dd_vm_protected)) return 2;
    for (unsigned i = 0; i < DD_VM_BENCH_PAIRS; ++i) {
        vm_fun first = (i & 1u) ? dd_vm_protected : dd_vm_plain;
        vm_fun second = (i & 1u) ? dd_vm_plain : dd_vm_protected;
        uint64_t a = ns();
        uint64_t check_a = batch(first);
        uint64_t b = ns();
        uint64_t check_b = batch(second);
        uint64_t c = ns();
        if (!a || b <= a || c <= b || check_a != check_b) return 3;
        uint64_t a_ns = (b - a) / DD_VM_BENCH_CALLS;
        uint64_t b_ns = (c - b) / DD_VM_BENCH_CALLS;
        plain_ns[i] = (i & 1u) ? b_ns : a_ns;
        protected_ns[i] = (i & 1u) ? a_ns : b_ns;
    }
    for (unsigned i = 0; i < DD_VM_BENCH_PAIRS; ++i) {
        if (!plain_ns[i] || !protected_ns[i]) return 4;
    }
    vm_sink = parity ^ guard;
    printf("DD_VM_SCHEMA=1\n");
    printf("DD_VM_CONTEXT=MACOS_HOST\n");
    printf("DD_VM_VECTORS_PASS=4096\n");
    printf("DD_VM_PARITY_CHECKSUM=%016" PRIx64 "\n", parity);
    printf("DD_VM_GUARD_CHECKSUM=%016" PRIx64 "\n", guard);
    printf("DD_VM_BENCH_CALLS=1024\n");
    printf("DD_VM_BENCH_PAIRS=3\n");
    for (unsigned i = 0; i < DD_VM_BENCH_PAIRS; ++i) {
        printf("DD_VM_PLAIN_NS_%u=%" PRIu64 "\n", i, plain_ns[i]);
        printf("DD_VM_PROTECTED_NS_%u=%" PRIu64 "\n", i, protected_ns[i]);
    }
    printf("DD_VM_COMPLETE=PASS\n");
    return 0;
}
