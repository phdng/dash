/* Readable baseline, no pass plugin; visible switch paths and inline keys. */
#include "igv_ibr.h"

DD_IGV_IBR_API
uint64_t dd_igv_plain(uint64_t a, uint64_t b, unsigned index) {
    uint64_t key;
    switch (index & 3U) {
        case 0: key = UINT64_C(0x9e3779b97f4a7c15); break;
        case 1: key = UINT64_C(0xd1b54a32d192ed03); break;
        case 2: key = UINT64_C(0xa0761d6478bd642f); break;
        default: key = UINT64_C(0xe7037ed1a0b428db); break;
    }
    return (a ^ key) + b * ((key >> 1) | UINT64_C(1));
}

DD_IGV_IBR_API
uint64_t dd_ibr_plain(uint64_t a, uint64_t b, unsigned mode) {
    uint64_t x = a;
    for (unsigned round = 0; round < 7; ++round) {
        unsigned choice = (unsigned)((x ^ (b >> ((round & 3U) * 8U))) +
                                     (uint64_t)mode + round) & 3U;
        switch (choice) {
            case 0:
                x = (x ^ (b + UINT64_C(0x9e3779b97f4a7c15))) +
                    ((b << 7) | (b >> 57));
                break;
            case 1:
                x = (x + (b ^ UINT64_C(0xd1b54a32d192ed03))) ^ (x >> 11);
                break;
            case 2:
                x = x * UINT64_C(0xa0761d6478bd642f) + (b >> 3);
                break;
            default:
                x = ((x << 9) | (x >> 55)) ^
                    (b + UINT64_C(0xe7037ed1a0b428db));
                break;
        }
    }
    return x;
}
