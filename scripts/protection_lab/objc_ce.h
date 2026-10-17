#ifndef DD_OBJC_CE_PILOT_H
#define DD_OBJC_CE_PILOT_H
#import <Foundation/Foundation.h>
#include <stdint.h>

/* An isolated Foundation canary; never injected into Crane. */
#define DD_OBJC_CE_EXPORT __attribute__((visibility("default"), noinline))

DD_OBJC_CE_EXPORT NSString *DDObjCPlainValue(uint32_t choice);
DD_OBJC_CE_EXPORT NSString *DDObjCProtectedValue(uint32_t choice);

#endif
