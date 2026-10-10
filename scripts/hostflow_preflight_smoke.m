#import <Foundation/Foundation.h>
#include <stdlib.h>
#import "DuoDashShared.h"

// These are link-only stubs for HostFlowAdapter's unrelated recovery seam.
// The preflight self-test must not call them.
void DDRecoveryRoutingStart(void) {
    abort();
}

NSUInteger DDRecoveryRoutingCapabilities(void) {
    abort();
}

int main(void) {
    @autoreleasepool {
        if (!DDHostSwitchPreflightSelfTest()) {
            NSLog(@"FAIL: DDHostSwitchPreflightSelfTest");
            return 1;
        }
        NSLog(@"PASS: DDHostSwitchPreflightSelfTest");
    }
    return 0;
}
