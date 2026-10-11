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

// macOS-only mock of the private class observed in decoded 3DD4C.c.
// Exercises the guarded runtime selector path without SpringBoard installed.
static BOOL DDMockControllerUnavailable = NO;
static BOOL DDMockApplicationSelectorUnavailable = NO;
static NSUInteger DDMockApplicationLookupCount = 0;

@interface SBApplicationController : NSObject
+ (instancetype)sharedInstance;
- (id)applicationWithBundleIdentifier:(NSString *)bundleIdentifier;
@end

@implementation SBApplicationController
+ (instancetype)sharedInstance {
    static SBApplicationController *instance = nil;
    if (!instance) instance = [SBApplicationController new];
    if (DDMockControllerUnavailable) return nil;
    // Return an object without applicationWithBundleIdentifier: to exercise
    // the decoded respondsToSelector: fallback independently of nil controller.
    if (DDMockApplicationSelectorUnavailable) return (id)[NSObject new];
    return instance;
}
- (id)applicationWithBundleIdentifier:(NSString *)bundleIdentifier {
    ++DDMockApplicationLookupCount;
    return [bundleIdentifier isEqualToString:@"com.example.exists"] ? self : nil;
}
@end

int main(void) {
    @autoreleasepool {
        if (!DDHostSwitchPreflightSelfTest()) {
            NSLog(@"FAIL: DDHostSwitchPreflightSelfTest");
            return 1;
        }
        // Mock availability: first missing app rejected, later duplicate
        // accepted as CarPlay UI; ordinary duplicates still cleared.
        DDMockApplicationLookupCount = 0;
        NSArray<NSString *> *normalized = DDHostNormalizeBidsUsingSpringBoard(
            @[@"com.example.missing", @"com.example.missing",
              @"com.example.exists", @"com.example.exists"], 4,
            @[@NO, @YES, @NO, @NO]);
        if (DDMockApplicationLookupCount != 2 ||
            ![normalized isEqualToArray:@[@"", @"com.example.missing",
                                          @"com.example.exists", @""]]) {
            NSLog(@"FAIL: guarded SBApplicationController mock normalization: %@", normalized);
            return 1;
        }
        // The caller-fed pure-data 3DD4C model must agree with the private
        // selector adapter for the same availability and CarPlay slot flags.
        NSArray<NSString *> *modeled = DDHostNormalizeBidsWithAvailability(
            @[@"com.example.missing", @"com.example.missing",
              @"com.example.exists", @"com.example.exists"], 4,
            @[@NO, @YES, @NO, @NO],
            [NSSet setWithObject:@"com.example.exists"]);
        if (![normalized isEqualToArray:modeled]) {
            NSLog(@"FAIL: private vs caller-fed 3DD4C mismatch: %@ / %@",
                  normalized, modeled);
            return 1;
        }
        // Reject malformed caller input before any private controller lookup.
        DDMockApplicationLookupCount = 0;
        if (DDHostPreparedRequestReadyUsingSpringBoard(
                (id)@"not-an-array", 2, nil,
                @[@"", @""], @[@1.0, @1.0]) ||
            DDHostPreparedRequestReadyUsingSpringBoard(
                @[@"com.example.exists"], 2, (id)@"not-an-array",
                @[@"com.example.exists", @""], @[@1.0, @1.0]) ||
            DDHostPreparedRequestReadyUsingSpringBoard(
                @[@"com.example.exists"], 0, nil, nil, nil) ||
            DDMockApplicationLookupCount != 0) {
            NSLog(@"FAIL: malformed prepared-host input reached private API");
            return 1;
        }
        // All CarPlay UI slots and empty/duplicate BIDs must avoid the
        // application selector even when the controller is available.
        DDMockApplicationLookupCount = 0;
        NSArray<NSString *> *carPlayOnly = DDHostNormalizeBidsUsingSpringBoard(
            @[@"com.example.missing", @"com.example.missing", @""], 3,
            @[@YES, @YES, @NO]);
        if (DDMockApplicationLookupCount != 0 ||
            ![carPlayOnly isEqualToArray:@[@"com.example.missing", @"", @""]] ||
            ![carPlayOnly isEqualToArray:DDHostNormalizeBidsWithAvailability(
                @[@"com.example.missing", @"com.example.missing", @""], 3,
                @[@YES, @YES, @NO], [NSSet set])]) {
            NSLog(@"FAIL: CarPlay UI-only BIDs performed private lookup: %@", carPlayOnly);
            return 1;
        }
        // Integrated private resolution + 218D8 prepared comparison.
        if (!DDHostPreparedRequestReadyUsingSpringBoard(
                @[@"com.example.exists", @"com.example.missing"], 2,
                @[@NO, @NO], @[@"com.example.exists", @""], @[@1.0, @1.0]) ||
            DDHostPreparedRequestReadyUsingSpringBoard(
                @[@"com.example.exists", @"com.example.missing"], 2,
                @[@NO, @YES], @[@"com.example.exists", @""], @[@1.0, @1.0]) ||
            DDHostPreparedRequestReadyUsingSpringBoard(
                @[@"com.example.exists", @"com.example.missing"], 2,
                @[@NO, @NO], @[@"com.example.exists", @""], @[@1.0, @0.5])) {
            NSLog(@"FAIL: integrated SpringBoard prepared-host check");
            return 1;
        }
        // Decompiler 3DD4C: unavailable shared controller must skip lookup,
        // but still normalize and deduplicate BIDs in their original order.
        DDMockControllerUnavailable = YES;
        DDMockApplicationLookupCount = 0;
        NSArray<NSString *> *fallback = DDHostNormalizeBidsUsingSpringBoard(
            @[@"com.example.missing", @"com.example.missing", [NSNull null]],
            3, @[@NO, @NO, @NO]);
        if (DDMockApplicationLookupCount != 0 ||
            ![fallback isEqualToArray:@[@"com.example.missing", @"", @""]] ||
            ![fallback isEqualToArray:DDHostNormalizeBidsWithAvailability(
                @[@"com.example.missing", @"com.example.missing", [NSNull null]],
                3, @[@NO, @NO, @NO], nil)]) {
            NSLog(@"FAIL: nil-controller fallback normalization: %@", fallback);
            return 1;
        }
        if (!DDHostPreparedRequestReadyUsingSpringBoard(
                @[@"com.example.missing"], 2, nil,
                @[@"com.example.missing", @""], @[@1.0, @1.0])) {
            NSLog(@"FAIL: nil-controller integrated prepared-host fallback");
            return 1;
        }
        if (DDMockApplicationLookupCount != 0) {
            NSLog(@"FAIL: nil-controller unexpectedly performed private lookup");
            return 1;
        }
        DDMockControllerUnavailable = NO;
        DDMockApplicationSelectorUnavailable = YES;
        DDMockApplicationLookupCount = 0;
        NSArray<NSString *> *selectorFallback = DDHostNormalizeBidsUsingSpringBoard(
            @[@"com.example.missing", @"com.example.missing"], 2,
            @[@NO, @NO]);
        if (DDMockApplicationLookupCount != 0 ||
            ![selectorFallback isEqualToArray:@[@"com.example.missing", @""]] ||
            ![selectorFallback isEqualToArray:DDHostNormalizeBidsWithoutLookup(
                @[@"com.example.missing", @"com.example.missing"], 2)] ||
            !DDHostPreparedRequestReadyUsingSpringBoard(
                @[@"com.example.missing"], 2, nil,
                @[@"com.example.missing", @""], @[@1.0, @1.0])) {
            NSLog(@"FAIL: missing private selector fallback: %@", selectorFallback);
            return 1;
        }
        DDMockApplicationSelectorUnavailable = NO;
        NSLog(@"PASS: DDHostSwitchPreflightSelfTest + mock private lookup/fallback");
    }
    return 0;
}
