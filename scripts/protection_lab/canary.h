#ifndef DD_PROTECTION_LAB_CANARY_H
#define DD_PROTECTION_LAB_CANARY_H
#include <stdint.h>

/* This API is a standalone C canary, not loaded by any jailbreak tweak. */
typedef uint64_t (*dd_eval_fn)(uint64_t, uint64_t);
#define DD_LAB_API __attribute__((visibility("default")))
DD_LAB_API uint64_t dd_canary_native(uint64_t a, uint64_t b);
DD_LAB_API uint64_t dd_canary_vm(uint64_t a, uint64_t b);
DD_LAB_API uint64_t dd_canary_indirect(dd_eval_fn fn, uint64_t a, uint64_t b);

#endif
