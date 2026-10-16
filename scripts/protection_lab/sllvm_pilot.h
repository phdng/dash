#ifndef DD_PROTECTION_LAB_SLLVM_PILOT_H
#define DD_PROTECTION_LAB_SLLVM_PILOT_H

#include <stdint.h>

/* Isolated source-level demonstration; no commercial SLLVM plugin used. */
#define DD_PILOT_EXPORT __attribute__((visibility("default"), noinline))
typedef uint64_t (*dd_pilot_calculator)(uint64_t, uint64_t);

DD_PILOT_EXPORT uint32_t dd_pilot_plain_hash(uint32_t seed);
DD_PILOT_EXPORT uint32_t dd_pilot_protected_hash(uint32_t seed);
DD_PILOT_EXPORT uint64_t dd_pilot_plain_dispatch(uint64_t a, uint64_t b, unsigned mode);
DD_PILOT_EXPORT uint64_t dd_pilot_protected_dispatch(uint64_t a, uint64_t b, unsigned mode);

#endif
