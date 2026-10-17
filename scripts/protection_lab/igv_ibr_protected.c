/* IGV/IBR-inspired source pilot, NOT a commercial SLLVM compiler pass.
 * Typed data pointers and typed handler callbacks preserve native Apple ABI
 * under arm64e; no raw pointer casts, JIT, PAC stripping or writable code.
 */
#include "igv_ibr.h"

/* Volatile data and pointer loads keep the two-stage global indirection
 * observable under Apple Clang -O2. Contents are PUBLIC test constants. */
static const volatile uint64_t dd_test_globals[4] = {
    UINT64_C(0xa0761d6478bd642f),
    UINT64_C(0xe7037ed1a0b428db),
    UINT64_C(0x9e3779b97f4a7c15),
    UINT64_C(0xd1b54a32d192ed03)
};
static const volatile uint64_t *volatile dd_test_global_refs[4] = {
    &dd_test_globals[2], &dd_test_globals[3],
    &dd_test_globals[0], &dd_test_globals[1]
};

DD_IGV_IBR_API
uint64_t dd_igv_protected(uint64_t a, uint64_t b, unsigned index) {
    const volatile uint64_t *pointer = dd_test_global_refs[index & 3U];
    uint64_t key = *pointer;
    return (a ^ key) + b * ((key >> 1) | UINT64_C(1));
}

static __attribute__((noinline))
uint64_t dd_ibr_step_zero(uint64_t x, uint64_t b) {
    return (x ^ (b + UINT64_C(0x9e3779b97f4a7c15))) +
           ((b << 7) | (b >> 57));
}
static __attribute__((noinline))
uint64_t dd_ibr_step_one(uint64_t x, uint64_t b) {
    return (x + (b ^ UINT64_C(0xd1b54a32d192ed03))) ^ (x >> 11);
}
static __attribute__((noinline))
uint64_t dd_ibr_step_two(uint64_t x, uint64_t b) {
    return x * UINT64_C(0xa0761d6478bd642f) + (b >> 3);
}
static __attribute__((noinline))
uint64_t dd_ibr_step_three(uint64_t x, uint64_t b) {
    return ((x << 9) | (x >> 55)) ^
           (b + UINT64_C(0xe7037ed1a0b428db));
}

/* State-machine branch selection via a typed handler pointer table.
 * This is an IBR-*inspired* experiment, not general LLVM IR IBR lowering. */
static dd_ibr_handler const dd_ibr_handlers[4] = {
    dd_ibr_step_zero, dd_ibr_step_one, dd_ibr_step_two, dd_ibr_step_three
};

DD_IGV_IBR_API
uint64_t dd_ibr_protected(uint64_t a, uint64_t b, unsigned mode) {
    uint64_t x = a;
    for (unsigned round = 0; round < 7; ++round) {
        unsigned choice = (unsigned)((x ^ (b >> ((round & 3U) * 8U))) +
                                     (uint64_t)mode + round) & 3U;
        dd_ibr_handler handler = dd_ibr_handlers[choice];
        x = handler(x, b);
    }
    return x;
}
