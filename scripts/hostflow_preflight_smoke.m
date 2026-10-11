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
        // 218D8:264-295 also compares prepared vs hosted CarPlay UI flags.
        if (!DDHostPreparedCarPlayFlagsMatch(@[@YES, @NO], @[@YES, @NO], 2) ||
            !DDHostPreparedCarPlayFlagsMatch(@[@NO], @[], 2) ||
            !DDHostPreparedCarPlayFlagsMatch(@[@NO, @YES, @YES], @[@NO, @YES, @NO], 2) ||
            DDHostPreparedCarPlayFlagsMatch(@[@YES, @NO], @[@YES, @YES], 2) ||
            DDHostPreparedCarPlayFlagsMatch((id)@"invalid", @[], 2) ||
            DDHostPreparedCarPlayFlagsMatch(@[], @[], 0)) {
            NSLog(@"FAIL: 218D8 prepared CarPlay UI flag comparison");
            return 1;
        }
        // 23D94 subrect threshold follows containment within usable bounds
        // expanded one point, and an axis smaller by more than one point.
        if (!DDHostGeometryIsCarPlaySubrect(100, 80, 120, 80, YES) ||
            !DDHostGeometryIsCarPlaySubrect(120, 60, 120, 80, YES) ||
            DDHostGeometryIsCarPlaySubrect(119, 79, 120, 80, YES) ||
            DDHostGeometryIsCarPlaySubrect(100, 80, 120, 80, NO) ||
            DDHostGeometryIsCarPlaySubrect(39, 80, 120, 80, YES)) {
            NSLog(@"FAIL: recovered 23D94 carplay-subrect threshold");
            return 1;
        }
        // 26654: clipped dock intersection classifies four edge strips,
        // rejects centered/empty/outside strips, and guards 40pt remainder.
        CGRect area = CGRectMake(10, 20, 200, 120);
        if (![DDHostDockEdgeLabel(area, CGRectMake(10, 20, 30, 120)) isEqualToString:@"left"] ||
            ![DDHostDockEdgeLabel(area, CGRectMake(180, 20, 30, 120)) isEqualToString:@"right"] ||
            ![DDHostDockEdgeLabel(area, CGRectMake(10, 20, 200, 20)) isEqualToString:@"top"] ||
            ![DDHostDockEdgeLabel(area, CGRectMake(10, 120, 200, 20)) isEqualToString:@"bottom"] ||
            ![DDHostDockEdgeLabel(area, CGRectMake(250, 20, 30, 120)) isEqualToString:@"strip-outside-area"] ||
            ![DDHostDockEdgeLabel(area, CGRectMake(90, 20, 30, 120)) isEqualToString:@"not-an-edge-strip"] ||
            ![DDHostDockEdgeLabel(area, CGRectMake(10, 20, 170, 120)) isEqualToString:@"degenerate"] ||
            ![DDHostDockEdgeLabel(area, CGRectZero) isEqualToString:@"not-an-edge-strip"]) {
            NSLog(@"FAIL: recovered 26654 dock edge classification");
            return 1;
        }
        // 26654: reconstruct surviving area for each accepted edge strip.
        CGRect trimmed = CGRectZero;
        if (!DDHostTrimUsableBoundsForDock(area, CGRectMake(10, 20, 30, 120), &trimmed) ||
            !CGRectEqualToRect(trimmed, CGRectMake(40, 20, 170, 120)) ||
            !DDHostTrimUsableBoundsForDock(area, CGRectMake(180, 20, 30, 120), &trimmed) ||
            !CGRectEqualToRect(trimmed, CGRectMake(10, 20, 170, 120)) ||
            !DDHostTrimUsableBoundsForDock(area, CGRectMake(10, 20, 200, 20), &trimmed) ||
            !CGRectEqualToRect(trimmed, CGRectMake(10, 40, 200, 100)) ||
            !DDHostTrimUsableBoundsForDock(area, CGRectMake(10, 120, 200, 20), &trimmed) ||
            !CGRectEqualToRect(trimmed, CGRectMake(10, 20, 200, 100)) ||
            DDHostTrimUsableBoundsForDock(area, CGRectMake(90, 20, 30, 120), &trimmed) ||
            DDHostTrimUsableBoundsForDock(area, CGRectMake(10, 20, 170, 120), &trimmed) ||
            !CGRectEqualToRect(trimmed, CGRectMake(10, 20, 200, 100))) {
            NSLog(@"FAIL: recovered 26654 trimmed usable bounds");
            return 1;
        }
        // 83FC: 64-bit notify dock state: x,y,width,height are four
        // unsigned 16-bit fields, each in tenths of a point.
        CGRect dock = CGRectZero;
        uint64_t dockState = (UINT64_C(123) << 48) |
                             (UINT64_C(456) << 32) |
                             (UINT64_C(800) << 16) | UINT64_C(400);
        if (!DDHostDecodeDockRectState(dockState, &dock) ||
            !CGRectEqualToRect(dock, CGRectMake(12.3, 45.6, 80.0, 40.0)) ||
            !DDHostDecodeDockRectState(dockState, NULL) ||
            DDHostDecodeDockRectState(0, &dock) ||
            DDHostDecodeDockRectState(UINT64_C(500) << 48, &dock) ||
            !CGRectEqualToRect(dock, CGRectMake(12.3, 45.6, 80.0, 40.0))) {
            NSLog(@"FAIL: recovered 83FC packed dock rectangle");
            return 1;
        }
        // 23D94 also checks shell origin within usable bounds inset -1pt.
        CGRect usable = CGRectMake(10, 20, 120, 100);
        if (!DDHostGeometryIsCarPlaySubrectForRects(
                CGRectMake(11, 21, 100, 80), usable) ||
            DDHostGeometryIsCarPlaySubrectForRects(
                CGRectMake(9 - 0.1, 21, 100, 80), usable) ||
            !DDHostGeometryIsCarPlaySubrectForRects(
                CGRectMake(9, 21, 100, 80), usable) ||
            DDHostGeometryIsCarPlaySubrectForRects(
                CGRectMake(11, 21, 39, 80), usable)) {
            NSLog(@"FAIL: recovered 23D94 CGRect containment");
            return 1;
        }
        // 22D64 rejects shell mismatch first, except when saved shell is
        // undersized (<40); it then compares calculated CarPlay display size.
        if (DDHostDisplayGeometryMismatch(100, 80, 100, 80, 200, 150, 200, 150) ||
            DDHostDisplayGeometryMismatch(101, 79, 100, 80, 201, 149, 200, 150) ||
            !DDHostDisplayGeometryMismatch(102, 80, 100, 80, 200, 150, 200, 150) ||
            !DDHostDisplayGeometryMismatch(100, 80, 100, 80, 202, 150, 200, 150) ||
            DDHostDisplayGeometryMismatch(999, 80, 39, 80, 200, 150, 200, 150) ||
            !DDHostDisplayGeometryMismatch(999, 80, 39, 80, 200, 152, 200, 150)) {
            NSLog(@"FAIL: recovered 22D64 display geometry mismatch gate");
            return 1;
        }
        // Combined 218D8 prepared path: valid BIDs and first-dimensions
        // must not override a prepared-vs-hosted CarPlay UI flag mismatch.
        if (!DDHostPreparedSlotsAndFlagsMatch(
                @[@"com.example.exists", @""], @[@"com.example.exists", @""],
                @[@1.0, @1.0], @[@NO, @YES], @[@NO, @YES], 2) ||
            DDHostPreparedSlotsAndFlagsMatch(
                @[@"com.example.exists", @""], @[@"com.example.exists", @""],
                @[@1.0, @1.0], @[@NO, @YES], @[@NO, @NO], 2) ||
            DDHostPreparedSlotsAndFlagsMatch(
                @[@"com.example.exists", @""], @[@"wrong", @""],
                @[@1.0, @1.0], @[@NO, @YES], @[@NO, @YES], 2) ||
            DDHostPreparedSlotsAndFlagsMatch(
                @[@"com.example.exists", @""], @[@"com.example.exists", @""],
                @[@1.0, @0.5], @[@NO, @YES], @[@NO, @YES], 2)) {
            NSLog(@"FAIL: combined 218D8 prepared BID/size/flag gate");
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
