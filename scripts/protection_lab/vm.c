/* Experimental static-bytecode interpreter: NO JIT, NO RWX, NO secrets. */
#include "canary.h"
#include "vm_program.h"
#include <stddef.h>
#include <stdint.h>

enum { DD_VM_REGS = 4, DD_VM_BUDGET = 64 };

static int dd_vm_read_u64(const unsigned char *p, size_t n,
                          size_t *pc, uint64_t *out) {
    if (*pc > n || n - *pc < 8) return 0;
    uint64_t value = 0;
    for (unsigned i = 0; i < 8; ++i) {
        value |= (uint64_t)p[*pc + i] << (8U * i);
    }
    *pc += 8;
    *out = value;
    return 1;
}

/* Fail closed for an invalid bytecode program. Never expose VM pointers. */
static int dd_vm_run(const unsigned char *p, size_t n,
                     uint64_t a, uint64_t b, uint64_t *out) {
    uint64_t r[DD_VM_REGS] = {0, 0, 0, 0};
    size_t pc = 0;
    for (unsigned steps = 0; steps < DD_VM_BUDGET; ++steps) {
        if (pc >= n) return 0;
        unsigned op = p[pc++];
        if (op == 255) {
            if (pc >= n) return 0;
            unsigned source = p[pc++];
            if (source >= DD_VM_REGS || pc != n) return 0;
            *out = r[source];
            return 1;
        }
        if (n - pc < 2) return 0;
        unsigned dst = p[pc++];
        if (dst >= DD_VM_REGS) return 0;
        if (op == 1 || op == 2) {
            /* Two-byte load opcodes carry no third register. */
            r[dst] = op == 1 ? a : b;
            continue;
        }
        if (op == 3) {
            if (!dd_vm_read_u64(p, n, &pc, &r[dst])) return 0;
            continue;
        }
        if (n - pc < 2) return 0;
        unsigned lhs = p[pc++];
        unsigned rhs = p[pc++];
        if (lhs >= DD_VM_REGS) return 0;
        if (op >= 4 && op <= 6) {
            if (rhs >= DD_VM_REGS) return 0;
            if (op == 4) r[dst] = r[lhs] ^ r[rhs];
            if (op == 5) r[dst] = r[lhs] + r[rhs];
            if (op == 6) r[dst] = r[lhs] * r[rhs];
        } else if (op == 7 && rhs < 64) {
            unsigned shift = rhs;
            r[dst] = shift ? (r[lhs] << shift) | (r[lhs] >> (64 - shift))
                           : r[lhs];
        } else if (op == 8 && rhs < 64) {
            r[dst] = r[lhs] >> rhs;
        } else {
            return 0;
        }
    }
    return 0;
}

__attribute__((noinline))
uint64_t dd_canary_vm(uint64_t a, uint64_t b) {
    uint64_t out = 0;
    return dd_vm_run(dd_vm_program, DD_VM_PROGRAM_SIZE, a, b, &out) ? out : 0;
}
