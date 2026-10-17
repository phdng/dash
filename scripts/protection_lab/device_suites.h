#ifndef DD_PROTECTION_LAB_DEVICE_SUITES_H
#define DD_PROTECTION_LAB_DEVICE_SUITES_H

#include <stdint.h>

enum { DD_DEVICE_VECTORS = 8192 };

int dd_device_test_vm(void);
int dd_device_test_ce_icall(void);
int dd_device_test_igv_ibr(void);

#endif
