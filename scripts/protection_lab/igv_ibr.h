#ifndef DD_IGV_IBR_PILOT_H
#define DD_IGV_IBR_PILOT_H

#include <stdint.h>

/* Separate source-level pilot, never linked into Crane or its daemons. */
#define DD_IGV_IBR_API __attribute__((visibility("default"), noinline))
typedef uint64_t (*dd_ibr_handler)(uint64_t, uint64_t);

DD_IGV_IBR_API uint64_t dd_igv_plain(uint64_t a, uint64_t b, unsigned index);
DD_IGV_IBR_API uint64_t dd_igv_protected(uint64_t a, uint64_t b, unsigned index);
DD_IGV_IBR_API uint64_t dd_ibr_plain(uint64_t a, uint64_t b, unsigned mode);
DD_IGV_IBR_API uint64_t dd_ibr_protected(uint64_t a, uint64_t b, unsigned mode);

#endif
