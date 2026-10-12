#import <Foundation/Foundation.h>
#include <stdlib.h>
#include <math.h>
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
        // 26654 boundary cases: clipped overhang, inclusive 2pt edge
        // tolerance, minimum remaining size (40pt inclusive), and NaN.
        if (![DDHostDockEdgeLabel(area, CGRectMake(0, 20, 40, 120)) isEqualToString:@"left"] ||
            ![DDHostDockEdgeLabel(area, CGRectMake(12, 20, 28, 120)) isEqualToString:@"left"] ||
            ![DDHostDockEdgeLabel(area, CGRectMake(10, 20, 160, 120)) isEqualToString:@"left"] ||
            ![DDHostDockEdgeLabel(area, CGRectMake(10, 20, 160.1, 120)) isEqualToString:@"degenerate"] ||
            ![DDHostDockEdgeLabel(area, CGRectMake(NAN, 20, 30, 120)) isEqualToString:@"not-an-edge-strip"] ||
            ![DDHostDockEdgeLabel(area, CGRectMake(10, 20, INFINITY, 120)) isEqualToString:@"not-an-edge-strip"]) {
            NSLog(@"FAIL: recovered 26654 dock edge boundary behavior");
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
        // 26654 clipping with overhang must use the intersection, not the
        // raw dock rectangle; 2pt near-edge tolerance is inclusive.
        CGRect clipped = CGRectZero;
        if (!DDHostTrimUsableBoundsForDock(
                area, CGRectMake(0, 20, 40, 120), &clipped) ||
            !CGRectEqualToRect(clipped, CGRectMake(40, 20, 170, 120)) ||
            !DDHostTrimUsableBoundsForDock(
                area, CGRectMake(12, 20, 28, 120), &clipped) ||
            !CGRectEqualToRect(clipped, CGRectMake(40, 20, 170, 120)) ||
            !DDHostTrimUsableBoundsForDock(
                area, CGRectMake(10, 20, 160, 120), &clipped) ||
            !CGRectEqualToRect(clipped, CGRectMake(170, 20, 40, 120)) ||
            DDHostTrimUsableBoundsForDock(
                area, CGRectMake(10, 20, 160.1, 120), &clipped) ||
            !CGRectEqualToRect(clipped, CGRectMake(170, 20, 40, 120))) {
            NSLog(@"FAIL: 26654 clipped dock overhang and residual threshold");
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
        // 83FC -> 26654: packed edge dock must decode and trim atomically.
        uint64_t leftDockState = (UINT64_C(100) << 48) |
                                 (UINT64_C(200) << 32) |
                                 (UINT64_C(300) << 16) | UINT64_C(1200);
        CGRect stateTrimmed = CGRectZero;
        if (!DDHostTrimUsableBoundsForDockState(area, leftDockState, &stateTrimmed) ||
            !CGRectEqualToRect(stateTrimmed, CGRectMake(40, 20, 170, 120)) ||
            DDHostTrimUsableBoundsForDockState(area, 0, &stateTrimmed) ||
            DDHostTrimUsableBoundsForDockState(area, UINT64_C(500) << 48, &stateTrimmed) ||
            !CGRectEqualToRect(stateTrimmed, CGRectMake(40, 20, 170, 120))) {
            NSLog(@"FAIL: recovered packed dock state to trimmed area");
            return 1;
        }
        // Packed state parity for the other three edges and rejected dock:
        // the state-driven path must match direct CGRect trimming exactly.
        CGRect edgeDocks[] = {
            CGRectMake(180, 20, 30, 120),
            CGRectMake(10, 20, 200, 20),
            CGRectMake(10, 120, 200, 20)};
        uint64_t edgeStates[] = {
            (UINT64_C(1800) << 48) | (UINT64_C(200) << 32) |
                (UINT64_C(300) << 16) | UINT64_C(1200),
            (UINT64_C(100) << 48) | (UINT64_C(200) << 32) |
                (UINT64_C(2000) << 16) | UINT64_C(200),
            (UINT64_C(100) << 48) | (UINT64_C(1200) << 32) |
                (UINT64_C(2000) << 16) | UINT64_C(200)};
        for (NSUInteger edgeIndex = 0; edgeIndex < 3; ++edgeIndex) {
            CGRect direct = CGRectZero;
            CGRect packed = CGRectZero;
            if (!DDHostTrimUsableBoundsForDock(area,
                    edgeDocks[edgeIndex], &direct) ||
                !DDHostTrimUsableBoundsForDockState(area,
                    edgeStates[edgeIndex], &packed) ||
                !CGRectEqualToRect(direct, packed)) {
                NSLog(@"FAIL: packed dock state parity for edge %lu",
                      (unsigned long)edgeIndex);
                return 1;
            }
        }
        CGRect rejectedOutput = CGRectMake(1, 2, 3, 4);
        uint64_t centerState = (UINT64_C(900) << 48) |
                               (UINT64_C(200) << 32) |
                               (UINT64_C(300) << 16) | UINT64_C(1200);
        if (DDHostTrimUsableBoundsForDockState(area, centerState,
                                               &rejectedOutput) ||
            !CGRectEqualToRect(rejectedOutput, CGRectMake(1, 2, 3, 4))) {
            NSLog(@"FAIL: packed nonedge dock changed output");
            return 1;
        }
        // 269FC: dock extends an adjacent candidate on one edge within 2pt.
        CGRect window = CGRectMake(40, 40, 100, 80);
        if (![DDHostDockAdjacentEdge(window, CGRectMake(20, 40, 20, 80)) isEqualToString:@"left"] ||
            ![DDHostDockAdjacentEdge(window, CGRectMake(140, 40, 20, 80)) isEqualToString:@"right"] ||
            ![DDHostDockAdjacentEdge(window, CGRectMake(40, 20, 100, 20)) isEqualToString:@"top"] ||
            ![DDHostDockAdjacentEdge(window, CGRectMake(40, 120, 100, 20)) isEqualToString:@"bottom"] ||
            DDHostDockAdjacentEdge(window, CGRectMake(145, 40, 20, 80)) != nil ||
            DDHostDockAdjacentEdge(window, CGRectMake(140, 60, 20, 20)) != nil ||
            DDHostDockAdjacentEdge(window, CGRectMake(60, 60, 20, 20)) != nil) {
            NSLog(@"FAIL: recovered 269FC adjacent dock edges");
            return 1;
        }
        // 269FC final covered gate checks the expanded candidate against
        // carPlayUsableBounds expanded by one point, preserving output on NO.
        CGRect covered = CGRectZero;
        CGRect coveredUsable = CGRectMake(10, 10, 180, 180);
        if (!DDHostDockCoveredExpandedBounds(coveredUsable, window,
                CGRectMake(20, 40, 20, 80), &covered) ||
            !CGRectEqualToRect(covered, CGRectMake(20, 40, 120, 80)) ||
            !DDHostDockCoveredExpandedBounds(coveredUsable, window,
                CGRectMake(140, 40, 20, 80), &covered) ||
            !CGRectEqualToRect(covered, CGRectMake(40, 40, 120, 80)) ||
            !DDHostDockCoveredExpandedBounds(coveredUsable, window,
                CGRectMake(40, 20, 100, 20), &covered) ||
            !CGRectEqualToRect(covered, CGRectMake(40, 20, 100, 100)) ||
            !DDHostDockCoveredExpandedBounds(coveredUsable, window,
                CGRectMake(40, 120, 100, 20), &covered) ||
            !CGRectEqualToRect(covered, CGRectMake(40, 40, 100, 100)) ||
            DDHostDockCoveredExpandedBounds(CGRectMake(40, 40, 100, 80),
                window, CGRectMake(140, 40, 20, 80), &covered) ||
            !CGRectEqualToRect(covered, CGRectMake(40, 40, 100, 100))) {
            NSLog(@"FAIL: 269FC covered expanded geometry containment");
            return 1;
        }
        // 269FC: inclusive 2pt adjacency and inclusive 1pt usable-bounds
        // containment; out-of-range geometry must preserve caller output.
        CGRect edgeCandidate = CGRectMake(40, 40, 100, 80);
        CGRect atTwoPointGap = CGRectMake(142, 40, 20, 80);
        CGRect justBeyondTwo = CGRectMake(142.1, 40, 20, 80);
        CGRect onePointUsable = CGRectMake(39, 39, 122, 82);
        CGRect edgeResult = CGRectMake(1, 2, 3, 4);
        if (!DDHostDockCoveredExpandedBounds(
                CGRectMake(21, 39, 140, 82), edgeCandidate,
                CGRectMake(20, 40, 20, 80), &edgeResult) ||
            !CGRectEqualToRect(edgeResult, CGRectMake(20, 40, 120, 80)) ||
            !DDHostDockCoveredExpandedBounds(
                CGRectMake(40, 40, 121, 80), edgeCandidate,
                CGRectMake(140, 40, 20, 80), &edgeResult) ||
            !CGRectEqualToRect(edgeResult, CGRectMake(40, 40, 120, 80)) ||
            !DDHostDockCoveredExpandedBounds(onePointUsable, edgeCandidate,
                atTwoPointGap, &edgeResult) ||
            !CGRectEqualToRect(edgeResult, CGRectMake(40, 40, 122, 80)) ||
            DDHostDockCoveredExpandedBounds(coveredUsable, edgeCandidate,
                justBeyondTwo, &edgeResult) ||
            !CGRectEqualToRect(edgeResult, CGRectMake(40, 40, 122, 80)) ||
            DDHostDockCoveredExpandedBounds(
                CGRectMake(21.1, 39, 139.9, 82), edgeCandidate,
                CGRectMake(20, 40, 20, 80), &edgeResult) ||
            !CGRectEqualToRect(edgeResult, CGRectMake(40, 40, 122, 80))) {
            NSLog(@"FAIL: 269FC expanded geometry tolerance limits");
            return 1;
        }
        // 269FC integrated classifier covers the complete source-derived
        // reason ordering, with output written only for covered geometry.
        CGRect coverageResult = CGRectMake(1, 2, 3, 4);
        CGRect adjacentRight = CGRectMake(140, 40, 20, 80);
        if (![DDHostDockCoverageReason(NO, NO, CGRectZero, window,
                adjacentRight, &coverageResult) isEqualToString:@"no-exit"] ||
            ![DDHostDockCoverageReason(YES, NO, coveredUsable, window,
                adjacentRight, &coverageResult) isEqualToString:@"no-strip-published"] ||
            ![DDHostDockCoverageReason(YES, YES, CGRectZero, window,
                adjacentRight, &coverageResult) isEqualToString:@"no-window"] ||
            ![DDHostDockCoverageReason(YES, YES, coveredUsable, window,
                CGRectMake(60, 60, 20, 20), &coverageResult) isEqualToString:@"already-inside"] ||
            ![DDHostDockCoverageReason(YES, YES, coveredUsable, window,
                CGRectMake(170, 40, 20, 80), &coverageResult) isEqualToString:@"strip-not-adjacent"] ||
            ![DDHostDockCoverageReason(YES, YES, window, window,
                adjacentRight, &coverageResult) isEqualToString:@"outside-usable"] ||
            !CGRectEqualToRect(coverageResult, CGRectMake(1, 2, 3, 4)) ||
            ![DDHostDockCoverageReason(YES, YES, coveredUsable, window,
                adjacentRight, &coverageResult) isEqualToString:@"covered"] ||
            !CGRectEqualToRect(coverageResult, CGRectMake(40, 40, 120, 80))) {
            NSLog(@"FAIL: integrated 269FC coverage reason order");
            return 1;
        }
        // 269FC early exits have strict precedence before coverage checks.
        CGRect candidate = CGRectMake(10, 20, 200, 120);
        CGRect insideDock = CGRectMake(20, 30, 20, 20);
        if (![DDHostDockCoverageEarlyReason(NO, NO, CGRectZero,
                CGRectZero, CGRectZero) isEqualToString:@"no-exit"] ||
            ![DDHostDockCoverageEarlyReason(YES, NO, CGRectZero,
                CGRectZero, CGRectZero) isEqualToString:@"no-strip-published"] ||
            ![DDHostDockCoverageEarlyReason(YES, YES, area,
                CGRectZero, insideDock) isEqualToString:@"no-window"] ||
            ![DDHostDockCoverageEarlyReason(YES, YES, area,
                candidate, insideDock) isEqualToString:@"already-inside"] ||
            DDHostDockCoverageEarlyReason(YES, YES, area,
                candidate, CGRectMake(220, 30, 20, 20)) != nil) {
            NSLog(@"FAIL: recovered 269FC early coverage guards");
            return 1;
        }
        // 23D94 initial branch precedence: subrect wins over a measured
        // dock; invalid/outside shell falls back to display or dock.
        if (![DDHostInitialGeometryReason(CGRectZero, area, NO)
                isEqualToString:@"display-unmeasured-dock"] ||
            ![DDHostInitialGeometryReason(CGRectZero, area, YES)
                isEqualToString:@"measured-dock-nofrome"] ||
            ![DDHostInitialGeometryReason(CGRectMake(11, 21, 100, 80), area, YES)
                isEqualToString:@"carplay-subrect"] ||
            ![DDHostInitialGeometryReason(area, area, NO)
                isEqualToString:@"carplay-fullscreen"] ||
            ![DDHostInitialGeometryReason(area, area, YES)
                isEqualToString:@"measured-dock"] ||
            ![DDHostInitialGeometryReason(CGRectMake(500, 20, 100, 80), area, YES)
                isEqualToString:@"measured-dock-nofrome"] ||
            ![DDHostInitialGeometryReason(CGRectMake(10, 20, 39, 80), area, NO)
                isEqualToString:@"display-unmeasured-dock"]) {
            NSLog(@"FAIL: 23D94 initial geometry branch selection");
            return 1;
        }
        // 23D94: initial CGRect output, before 269FC covered-dock handling.
        CGRect initialBounds = CGRectMake(1, 2, 3, 4);
        if (!DDHostInitialGeometryBounds(CGRectZero, area, NO,
                CGRectZero, &initialBounds) ||
            !CGRectEqualToRect(initialBounds, area) ||
            !DDHostInitialGeometryBounds(CGRectZero, area, YES,
                CGRectMake(10, 20, 30, 120), &initialBounds) ||
            !CGRectEqualToRect(initialBounds, CGRectMake(40, 20, 170, 120)) ||
            !DDHostInitialGeometryBounds(CGRectMake(11, 21, 100, 80), area, YES,
                CGRectMake(10, 20, 30, 120), &initialBounds) ||
            !CGRectEqualToRect(initialBounds, CGRectMake(11, 21, 100, 80)) ||
            !DDHostInitialGeometryBounds(area, area, YES,
                CGRectMake(10, 20, 30, 120), &initialBounds) ||
            !CGRectEqualToRect(initialBounds, CGRectMake(40, 20, 170, 120)) ||
            !DDHostInitialGeometryBounds(area, area, YES,
                CGRectMake(100, 40, 20, 20), &initialBounds) ||
            !CGRectEqualToRect(initialBounds, area) ||
            DDHostInitialGeometryBounds(CGRectZero, CGRectZero, NO,
                CGRectZero, &initialBounds) ||
            !CGRectEqualToRect(initialBounds, area)) {
            NSLog(@"FAIL: 23D94 initial geometry bounds composition");
            return 1;
        }
        // 23D94 writes the initial result before 269FC's covered expansion.
        CGRect combinedInitial = CGRectMake(1, 2, 3, 4);
        CGRect combinedResolved = CGRectMake(5, 6, 7, 8);
        CGRect combinedShell = CGRectMake(40, 40, 100, 80);
        CGRect combinedUsable = CGRectMake(10, 10, 180, 180);
        if (![DDHostResolvedGeometryForDock(combinedShell, combinedUsable,
                YES, CGRectMake(20, 40, 20, 80), YES, YES,
                &combinedInitial, &combinedResolved) isEqualToString:@"covered"] ||
            !CGRectEqualToRect(combinedInitial, combinedShell) ||
            !CGRectEqualToRect(combinedResolved, CGRectMake(20, 40, 120, 80)) ||
            ![DDHostResolvedGeometryForDock(combinedShell, combinedUsable,
                NO, CGRectZero, YES, NO, &combinedInitial,
                &combinedResolved) isEqualToString:@"no-strip-published"] ||
            !CGRectEqualToRect(combinedInitial, combinedShell) ||
            !CGRectEqualToRect(combinedResolved, combinedShell) ||
            ![DDHostResolvedGeometryForDock(combinedShell, combinedUsable,
                YES, CGRectMake(170, 40, 20, 80), YES, YES,
                &combinedInitial, &combinedResolved) isEqualToString:@"strip-not-adjacent"] ||
            !CGRectEqualToRect(combinedResolved, combinedShell) ||
            ![DDHostResolvedGeometryForDock(combinedShell, CGRectZero,
                NO, CGRectZero, YES, NO, &combinedInitial,
                &combinedResolved) isEqualToString:@"invalid-geometry"] ||
            !CGRectEqualToRect(combinedInitial, combinedShell) ||
            !CGRectEqualToRect(combinedResolved, combinedShell)) {
            NSLog(@"FAIL: 23D94/269FC combined geometry output order");
            return 1;
        }
        // 23D94 final reason, intermediate coverage and both CGRect outputs.
        NSString *finalCoverage = @"untouched";
        CGRect finalInitial = CGRectMake(1, 2, 3, 4);
        CGRect finalResolved = CGRectMake(5, 6, 7, 8);
        if (![DDHostResolvedGeometryFinalReason(combinedShell, combinedUsable,
                YES, CGRectMake(20, 40, 20, 80), YES, YES,
                &finalInitial, &finalResolved, &finalCoverage)
                isEqualToString:@"carplay-subrect+dock"] ||
            ![finalCoverage isEqualToString:@"covered"] ||
            !CGRectEqualToRect(finalInitial, combinedShell) ||
            !CGRectEqualToRect(finalResolved, CGRectMake(20, 40, 120, 80)) ||
            ![DDHostResolvedGeometryFinalReason(combinedShell, combinedUsable,
                NO, CGRectZero, YES, NO, &finalInitial, &finalResolved,
                &finalCoverage) isEqualToString:@"carplay-subrect"] ||
            ![finalCoverage isEqualToString:@"no-strip-published"] ||
            !CGRectEqualToRect(finalResolved, combinedShell) ||
            ![DDHostResolvedGeometryFinalReason(combinedShell, CGRectZero,
                NO, CGRectZero, YES, NO, &finalInitial, &finalResolved,
                &finalCoverage) isEqualToString:@"invalid-geometry"] ||
            ![finalCoverage isEqualToString:@"no-strip-published"] ||
            !CGRectEqualToRect(finalInitial, combinedShell) ||
            !CGRectEqualToRect(finalResolved, combinedShell)) {
            NSLog(@"FAIL: 23D94 combined final diagnostic geometry");
            return 1;
        }
        // Full 83FC -> 23D94 -> 26654 -> 269FC packed-state path.
        CGRect stateInitial = CGRectMake(1, 2, 3, 4);
        CGRect stateResolved = CGRectMake(5, 6, 7, 8);
        NSString *stateCoverage = @"untouched";
        if (![DDHostResolvedGeometryForDockState(CGRectZero, area,
                leftDockState, NO, &stateInitial, &stateResolved,
                &stateCoverage) isEqualToString:@"measured-dock-nofrome"] ||
            ![stateCoverage isEqualToString:@"no-exit"] ||
            !CGRectEqualToRect(stateInitial, CGRectMake(40, 20, 170, 120)) ||
            !CGRectEqualToRect(stateResolved, stateInitial) ||
            ![DDHostResolvedGeometryForDockState(CGRectZero, area,
                0, YES, &stateInitial, &stateResolved,
                &stateCoverage) isEqualToString:@"display-unmeasured-dock"] ||
            ![stateCoverage isEqualToString:@"no-strip-published"] ||
            !CGRectEqualToRect(stateInitial, area) ||
            !CGRectEqualToRect(stateResolved, area) ||
            ![DDHostResolvedGeometryForDockState(CGRectZero, area,
                UINT64_C(100) << 48, YES, &stateInitial,
                &stateResolved, &stateCoverage)
                isEqualToString:@"display-unmeasured-dock"] ||
            !CGRectEqualToRect(stateInitial, area) ||
            ![DDHostResolvedGeometryForDockState(CGRectZero, CGRectZero,
                leftDockState, YES, &stateInitial, &stateResolved,
                &stateCoverage) isEqualToString:@"invalid-geometry"] ||
            !CGRectEqualToRect(stateInitial, area) ||
            !CGRectEqualToRect(stateResolved, area) ||
            ![stateCoverage isEqualToString:@"no-strip-published"]) {
            NSLog(@"FAIL: 83FC-to-269FC packed dock-state geometry flow");
            return 1;
        }
        // Repeated packed-state updates: right/top/bottom dock must trim
        // distinct axes; disappearance must restore the original usable bounds.
        uint64_t rightState = (UINT64_C(1900) << 48) |
            (UINT64_C(200) << 32) | (UINT64_C(200) << 16) | UINT64_C(1200);
        uint64_t topState = (UINT64_C(100) << 48) |
            (UINT64_C(200) << 32) | (UINT64_C(2000) << 16) | UINT64_C(200);
        uint64_t bottomState = (UINT64_C(100) << 48) |
            (UINT64_C(1200) << 32) | (UINT64_C(2000) << 16) | UINT64_C(200);
        if (![DDHostResolvedGeometryForDockState(CGRectZero, area,
                rightState, NO, &stateInitial, &stateResolved,
                &stateCoverage) isEqualToString:@"measured-dock-nofrome"] ||
            !CGRectEqualToRect(stateInitial, CGRectMake(10, 20, 180, 120)) ||
            !CGRectEqualToRect(stateResolved, stateInitial) ||
            ![DDHostResolvedGeometryForDockState(CGRectZero, area,
                topState, NO, &stateInitial, &stateResolved,
                &stateCoverage) isEqualToString:@"measured-dock-nofrome"] ||
            !CGRectEqualToRect(stateInitial, CGRectMake(10, 40, 200, 100)) ||
            ![DDHostResolvedGeometryForDockState(CGRectZero, area,
                bottomState, NO, &stateInitial, &stateResolved,
                &stateCoverage) isEqualToString:@"measured-dock-nofrome"] ||
            !CGRectEqualToRect(stateInitial, CGRectMake(10, 20, 200, 100)) ||
            ![DDHostResolvedGeometryForDockState(CGRectZero, area,
                0, NO, &stateInitial, &stateResolved,
                &stateCoverage) isEqualToString:@"display-unmeasured-dock"] ||
            !CGRectEqualToRect(stateInitial, area) ||
            !CGRectEqualToRect(stateResolved, area) ||
            ![DDHostResolvedGeometryForDockState(CGRectZero, area,
                leftDockState, NO, &stateInitial, &stateResolved,
                &stateCoverage) isEqualToString:@"measured-dock-nofrome"] ||
            !CGRectEqualToRect(stateInitial, CGRectMake(40, 20, 170, 120))) {
            NSLog(@"FAIL: packed dock-state directional and recovery transitions");
            return 1;
        }
        // Complete packed-state covered branch: measured dock beside a
        // subrect must expand resolved geometry while preserving initial.
        uint64_t adjacentLeftState = (UINT64_C(200) << 48) |
            (UINT64_C(400) << 32) | (UINT64_C(200) << 16) | UINT64_C(800);
        CGRect packedInitial = CGRectZero;
        CGRect packedResolved = CGRectZero;
        NSString *packedCoverage = nil;
        if (![DDHostResolvedGeometryForDockState(combinedShell,
                combinedUsable, adjacentLeftState, YES, &packedInitial,
                &packedResolved, &packedCoverage)
                isEqualToString:@"carplay-subrect+dock"] ||
            ![packedCoverage isEqualToString:@"covered"] ||
            !CGRectEqualToRect(packedInitial, combinedShell) ||
            !CGRectEqualToRect(packedResolved, CGRectMake(20, 40, 120, 80)) ||
            ![DDHostResolvedGeometryForDockState(combinedShell,
                combinedUsable, adjacentLeftState, NO, &packedInitial,
                &packedResolved, &packedCoverage)
                isEqualToString:@"carplay-subrect"] ||
            ![packedCoverage isEqualToString:@"no-exit"] ||
            !CGRectEqualToRect(packedResolved, combinedShell) ||
            ![DDHostResolvedGeometryForDockState(combinedShell,
                combinedUsable, 0, YES, &packedInitial,
                &packedResolved, &packedCoverage)
                isEqualToString:@"carplay-subrect"] ||
            ![packedCoverage isEqualToString:@"no-strip-published"] ||
            !CGRectEqualToRect(packedResolved, combinedShell) ||
            ![DDHostResolvedGeometryForDockState(combinedShell,
                combinedUsable, adjacentLeftState, YES, &packedInitial,
                &packedResolved, &packedCoverage)
                isEqualToString:@"carplay-subrect+dock"] ||
            !CGRectEqualToRect(packedResolved, CGRectMake(20, 40, 120, 80))) {
            NSLog(@"FAIL: packed dock covered, exit-toggle and restore transitions");
            return 1;
        }
        // Malformed CarPlay snapshots must not leak NaN/Inf into layout;
        // finite shell fallback remains deterministic for measured dock.
        CGRect invalidOutputInitial = CGRectMake(1, 2, 3, 4);
        CGRect invalidOutputResolved = CGRectMake(5, 6, 7, 8);
        NSString *invalidOutputCoverage = @"untouched";
        if (![DDHostResolvedGeometryForDockState(
                combinedShell, CGRectMake(NAN, 10, 180, 180),
                adjacentLeftState, YES, &invalidOutputInitial,
                &invalidOutputResolved, &invalidOutputCoverage)
                isEqualToString:@"invalid-geometry"] ||
            !CGRectEqualToRect(invalidOutputInitial, CGRectMake(1, 2, 3, 4)) ||
            !CGRectEqualToRect(invalidOutputResolved, CGRectMake(5, 6, 7, 8)) ||
            ![invalidOutputCoverage isEqualToString:@"untouched"] ||
            ![DDHostResolvedGeometryForDockState(
                CGRectMake(NAN, 40, 100, 80), combinedUsable,
                adjacentLeftState, NO, &invalidOutputInitial,
                &invalidOutputResolved, &invalidOutputCoverage)
                isEqualToString:@"measured-dock-nofrome"] ||
            !CGRectEqualToRect(invalidOutputInitial, combinedUsable) ||
            !CGRectEqualToRect(invalidOutputResolved, combinedUsable)) {
            NSLog(@"FAIL: nonfinite CarPlay geometry recovery");
            return 1;
        }
        // Match portable invalid-usable matrix across NaN, Inf, negative
        // width and zero height; no rejected call may mutate any output.
        CGRect rejectedUsable[] = {
            CGRectMake(NAN, 10, 180, 180),
            CGRectMake(10, INFINITY, 180, 180),
            CGRectMake(10, 10, -1, 180),
            CGRectMake(10, 10, 180, -1),
            CGRectMake(10, 10, 180, 0),
        };
        for (NSUInteger index = 0;
             index < sizeof(rejectedUsable) / sizeof(rejectedUsable[0]);
             ++index) {
            invalidOutputInitial = CGRectMake(1, 2, 3, 4);
            invalidOutputResolved = CGRectMake(5, 6, 7, 8);
            invalidOutputCoverage = @"untouched";
            NSString *invalidLabel = DDHostResolvedGeometryForDockState(
                combinedShell, rejectedUsable[index], adjacentLeftState,
                YES, &invalidOutputInitial, &invalidOutputResolved,
                &invalidOutputCoverage);
            CGRect rejectedInitial = CGRectMake(1, 2, 3, 4);
            CGRect rejectedTrim = CGRectMake(5, 6, 7, 8);
            BOOL initialAccepted = DDHostInitialGeometryBounds(
                combinedShell, rejectedUsable[index], YES,
                CGRectMake(20, 40, 20, 80), &rejectedInitial);
            BOOL trimAccepted = DDHostTrimUsableBoundsForDock(
                rejectedUsable[index], CGRectMake(20, 40, 20, 80),
                &rejectedTrim);
            NSString *edgeLabel = DDHostDockEdgeLabel(
                rejectedUsable[index], CGRectMake(20, 40, 20, 80));
            CGRect rejectedCovered = CGRectMake(9, 10, 11, 12);
            NSString *coverageLabel = DDHostDockCoverageReason(
                YES, YES, rejectedUsable[index], combinedShell,
                CGRectMake(20, 40, 20, 80), &rejectedCovered);
            if (![invalidLabel isEqualToString:@"invalid-geometry"] ||
                !CGRectEqualToRect(invalidOutputInitial, CGRectMake(1, 2, 3, 4)) ||
                !CGRectEqualToRect(invalidOutputResolved, CGRectMake(5, 6, 7, 8)) ||
                ![invalidOutputCoverage isEqualToString:@"untouched"] ||
                initialAccepted || trimAccepted ||
                !CGRectEqualToRect(rejectedInitial, CGRectMake(1, 2, 3, 4)) ||
                !CGRectEqualToRect(rejectedTrim, CGRectMake(5, 6, 7, 8)) ||
                !CGRectEqualToRect(rejectedCovered, CGRectMake(9, 10, 11, 12)) ||
                ![coverageLabel isEqualToString:@"no-window"] ||
                ![edgeLabel isEqualToString:@"not-an-edge-strip"]) {
                NSLog(@"FAIL: invalid usable geometry vector %lu (size=%g,%g reason=%@ initialAccepted=%d trimAccepted=%d edge=%@)",
                    (unsigned long)index, (double)rejectedUsable[index].size.width,
                    (double)rejectedUsable[index].size.height, invalidLabel,
                    (int)initialAccepted, (int)trimAccepted, edgeLabel);
                NSLog(@"Coverage reason for rejected bounds: %@", coverageLabel);
                return 1;
            }
        }
        // Absent state and invalid zero-width/height packed states all
        // select the same measured-dock fallback and publication guards.
        uint64_t rejectedStates[] = {
            0, UINT64_C(100) << 48,
            (UINT64_C(100) << 48) | (UINT64_C(200) << 32) |
                (UINT64_C(300) << 16),
        };
        for (NSUInteger index = 0; index < 3; ++index) {
            NSString *missingCoverage = @"untouched";
            CGRect missingInitial = CGRectZero;
            CGRect missingResolved = CGRectZero;
            NSString *missingLabel = DDHostResolvedGeometryForDockState(
                CGRectZero, area, rejectedStates[index], YES,
                &missingInitial, &missingResolved, &missingCoverage);
            if (![missingLabel isEqualToString:@"display-unmeasured-dock"] ||
                ![missingCoverage isEqualToString:@"no-strip-published"] ||
                !CGRectEqualToRect(missingInitial, area) ||
                !CGRectEqualToRect(missingResolved, area)) {
                NSLog(@"FAIL: invalid packed dock state vector %lu", (unsigned long)index);
                return 1;
            }
        }
        // Full hosting transition gate: no-op, relayout, restoration,
        // reason-only update, and atomic rejection of invalid geometry.
        CGRect transitionBefore = CGRectMake(1, 2, 3, 4);
        CGRect transitionAfter = CGRectMake(5, 6, 7, 8);
        NSString *transitionBeforeReason = @"before-sentinel";
        NSString *transitionAfterReason = @"after-sentinel";
        if (![DDHostDockLayoutTransition(CGRectZero, area,
                leftDockState, NO, leftDockState, NO,
                &transitionBefore, &transitionAfter,
                &transitionBeforeReason, &transitionAfterReason)
                isEqualToString:@"unchanged"] ||
            !CGRectEqualToRect(transitionBefore, CGRectMake(40, 20, 170, 120)) ||
            !CGRectEqualToRect(transitionAfter, transitionBefore) ||
            ![transitionBeforeReason isEqualToString:@"measured-dock-nofrome"] ||
            ![transitionAfterReason isEqualToString:transitionBeforeReason] ||
            ![DDHostDockLayoutTransition(CGRectZero, area,
                leftDockState, NO, 0, NO,
                &transitionBefore, &transitionAfter,
                &transitionBeforeReason, &transitionAfterReason)
                isEqualToString:@"restored"] ||
            !CGRectEqualToRect(transitionBefore, CGRectMake(40, 20, 170, 120)) ||
            !CGRectEqualToRect(transitionAfter, area) ||
            ![DDHostDockLayoutTransition(CGRectZero, area,
                0, NO, leftDockState, NO,
                &transitionBefore, &transitionAfter,
                &transitionBeforeReason, &transitionAfterReason)
                isEqualToString:@"updated"] ||
            !CGRectEqualToRect(transitionBefore, area) ||
            !CGRectEqualToRect(transitionAfter, CGRectMake(40, 20, 170, 120)) ||
            ![DDHostDockLayoutTransition(combinedShell, combinedUsable,
                adjacentLeftState, NO, adjacentLeftState, YES,
                &transitionBefore, &transitionAfter,
                &transitionBeforeReason, &transitionAfterReason)
                isEqualToString:@"updated"] ||
            !CGRectEqualToRect(transitionBefore, combinedShell) ||
            !CGRectEqualToRect(transitionAfter, CGRectMake(20, 40, 120, 80)) ||
            ![transitionAfterReason isEqualToString:@"carplay-subrect+dock"] ||
            ![DDHostDockLayoutTransition(CGRectZero, combinedUsable,
                0, YES, adjacentLeftState, YES,
                &transitionBefore, &transitionAfter,
                &transitionBeforeReason, &transitionAfterReason)
                isEqualToString:@"reason-only"] ||
            !CGRectEqualToRect(transitionBefore, combinedUsable) ||
            !CGRectEqualToRect(transitionAfter, combinedUsable) ||
            ![transitionBeforeReason isEqualToString:@"display-unmeasured-dock"] ||
            ![transitionAfterReason isEqualToString:@"measured-dock-nofrome"]) {
            NSLog(@"FAIL: dock layout transition decision matrix");
            return 1;
        }
        transitionBefore = CGRectMake(1, 2, 3, 4);
        transitionAfter = CGRectMake(5, 6, 7, 8);
        transitionBeforeReason = @"before-sentinel";
        transitionAfterReason = @"after-sentinel";
        if (![DDHostDockLayoutTransition(combinedShell, CGRectZero,
                leftDockState, NO, 0, YES,
                &transitionBefore, &transitionAfter,
                &transitionBeforeReason, &transitionAfterReason)
                isEqualToString:@"invalid-geometry"] ||
            !CGRectEqualToRect(transitionBefore, CGRectMake(1, 2, 3, 4)) ||
            !CGRectEqualToRect(transitionAfter, CGRectMake(5, 6, 7, 8)) ||
            ![transitionBeforeReason isEqualToString:@"before-sentinel"] ||
            ![transitionAfterReason isEqualToString:@"after-sentinel"]) {
            NSLog(@"FAIL: dock transition must preserve rejected outputs");
            return 1;
        }
        // Independent snapshots: shell movement, usable-area growth and
        // loss of dock must be evaluated, not only packed-state changes.
        {
            CGRect beforeSnapshotRect = CGRectMake(1, 2, 3, 4);
            CGRect afterSnapshotRect = CGRectMake(5, 6, 7, 8);
            NSString *beforeSnapshotLabel = @"before";
            NSString *afterSnapshotLabel = @"after";
            if (![DDHostDockLayoutTransitionForSnapshots(
                    CGRectZero, area, leftDockState, NO,
                    CGRectZero, CGRectMake(10, 20, 240, 120),
                    leftDockState, NO, &beforeSnapshotRect,
                    &afterSnapshotRect, &beforeSnapshotLabel,
                    &afterSnapshotLabel) isEqualToString:@"updated"] ||
                !CGRectEqualToRect(beforeSnapshotRect,
                    CGRectMake(40, 20, 170, 120)) ||
                !CGRectEqualToRect(afterSnapshotRect,
                    CGRectMake(40, 20, 210, 120)) ||
                ![beforeSnapshotLabel isEqualToString:@"measured-dock-nofrome"] ||
                ![afterSnapshotLabel isEqualToString:beforeSnapshotLabel] ||
                ![DDHostDockLayoutTransitionForSnapshots(
                    combinedShell, combinedUsable, 0, YES,
                    CGRectMake(50, 40, 100, 80), combinedUsable, 0, YES,
                    &beforeSnapshotRect, &afterSnapshotRect,
                    &beforeSnapshotLabel, &afterSnapshotLabel)
                    isEqualToString:@"updated"] ||
                !CGRectEqualToRect(beforeSnapshotRect, combinedShell) ||
                !CGRectEqualToRect(afterSnapshotRect,
                    CGRectMake(50, 40, 100, 80)) ||
                ![DDHostDockLayoutTransitionForSnapshots(
                    combinedShell, combinedUsable, 0, YES,
                    combinedShell, CGRectMake(10, 10, 220, 180), 0, YES,
                    &beforeSnapshotRect, &afterSnapshotRect,
                    &beforeSnapshotLabel, &afterSnapshotLabel)
                    isEqualToString:@"unchanged"] ||
                !CGRectEqualToRect(beforeSnapshotRect, combinedShell) ||
                !CGRectEqualToRect(afterSnapshotRect, combinedShell) ||
                ![DDHostDockLayoutTransitionForSnapshots(
                    CGRectZero, area, leftDockState, NO,
                    CGRectZero, CGRectMake(10, 20, 240, 120), 0, NO,
                    &beforeSnapshotRect, &afterSnapshotRect,
                    &beforeSnapshotLabel, &afterSnapshotLabel)
                    isEqualToString:@"restored"] ||
                !CGRectEqualToRect(beforeSnapshotRect,
                    CGRectMake(40, 20, 170, 120)) ||
                !CGRectEqualToRect(afterSnapshotRect,
                    CGRectMake(10, 20, 240, 120)) ||
                ![DDHostDockLayoutTransitionForSnapshots(
                    CGRectZero, area, 0, YES,
                    area, area, 0, YES,
                    &beforeSnapshotRect, &afterSnapshotRect,
                    &beforeSnapshotLabel, &afterSnapshotLabel)
                    isEqualToString:@"reason-only"] ||
                !CGRectEqualToRect(beforeSnapshotRect, area) ||
                !CGRectEqualToRect(afterSnapshotRect, area) ||
                ![beforeSnapshotLabel isEqualToString:@"display-unmeasured-dock"] ||
                ![afterSnapshotLabel isEqualToString:@"carplay-fullscreen"]) {
                NSLog(@"FAIL: independent CarPlay snapshot transition geometry");
                return 1;
            }
            beforeSnapshotRect = CGRectMake(1, 2, 3, 4);
            afterSnapshotRect = CGRectMake(5, 6, 7, 8);
            beforeSnapshotLabel = @"before";
            afterSnapshotLabel = @"after";
            if (![DDHostDockLayoutTransitionForSnapshots(
                    combinedShell, combinedUsable, 0, YES,
                    combinedShell, CGRectMake(NAN, 10, 180, 180),
                    leftDockState, YES, &beforeSnapshotRect,
                    &afterSnapshotRect, &beforeSnapshotLabel,
                    &afterSnapshotLabel) isEqualToString:@"invalid-geometry"] ||
                ![DDHostDockLayoutTransitionForSnapshots(
                    combinedShell, CGRectZero, 0, YES,
                    combinedShell, combinedUsable, leftDockState, YES,
                    &beforeSnapshotRect, &afterSnapshotRect,
                    &beforeSnapshotLabel, &afterSnapshotLabel)
                    isEqualToString:@"invalid-geometry"] ||
                !CGRectEqualToRect(beforeSnapshotRect,
                    CGRectMake(1, 2, 3, 4)) ||
                !CGRectEqualToRect(afterSnapshotRect,
                    CGRectMake(5, 6, 7, 8)) ||
                ![beforeSnapshotLabel isEqualToString:@"before"] ||
                ![afterSnapshotLabel isEqualToString:@"after"]) {
                NSLog(@"FAIL: invalid second CarPlay snapshot must not publish");
                return 1;
            }
        }
        // Planning layer: combine geometry transitions with the existing
        // full-host lifecycle guard. These labels never execute hosting.
        {
            DDHostCarPlayLayoutSnapshot planBefore =
                { CGRectZero, area, leftDockState, NO };
            DDHostCarPlayLayoutSnapshot planNext =
                { CGRectZero, area, 0, NO };
            DDHostHostingLifecycleSnapshot planLifecycle =
                { NO, YES, YES, NO, NO, NO, YES };
            CGRect planPreviousRect = CGRectMake(1, 2, 3, 4);
            CGRect planNextRect = CGRectMake(5, 6, 7, 8);
            NSString *planPreviousReason = @"previous-sentinel";
            NSString *planNextReason = @"next-sentinel";
            if (![DDHostDockHostingPlanForSnapshots(
                    planBefore, planBefore, planLifecycle,
                    &planPreviousRect, &planNextRect, &planPreviousReason,
                    &planNextReason) isEqualToString:@"no-change"] ||
                !CGRectEqualToRect(planPreviousRect,
                    CGRectMake(40, 20, 170, 120)) ||
                !CGRectEqualToRect(planNextRect, planPreviousRect) ||
                ![DDHostDockHostingPlanForSnapshots(
                    planBefore, planNext, planLifecycle,
                    &planPreviousRect, &planNextRect, &planPreviousReason,
                    &planNextReason) isEqualToString:@"restore-layout"] ||
                !CGRectEqualToRect(planPreviousRect,
                    CGRectMake(40, 20, 170, 120)) ||
                !CGRectEqualToRect(planNextRect, area) ||
                ![planPreviousReason isEqualToString:@"measured-dock-nofrome"] ||
                ![planNextReason isEqualToString:@"display-unmeasured-dock"] ||
                ![DDHostDockHostingPlanForSnapshots(
                    planNext, planBefore, planLifecycle,
                    &planPreviousRect, &planNextRect, &planPreviousReason,
                    &planNextReason) isEqualToString:@"update-layout"] ||
                !CGRectEqualToRect(planPreviousRect, area) ||
                !CGRectEqualToRect(planNextRect,
                    CGRectMake(40, 20, 170, 120))) {
                NSLog(@"FAIL: host plan no-op, dock restore and update");
                return 1;
            }
            // An unchanged CGRect never relayouts, even if diagnostics
            // or unrelated lifecycle flags have changed.
            planBefore.dockState = 0;
            planNext.dockState = adjacentLeftState;
            planBefore.usableBounds = combinedUsable;
            planNext.usableBounds = combinedUsable;
            planLifecycle.dirty = YES;
            if (![DDHostDockHostingPlanForSnapshots(
                    planBefore, planNext, planLifecycle,
                    &planPreviousRect, &planNextRect, &planPreviousReason,
                    &planNextReason) isEqualToString:@"diagnostic-only"] ||
                !CGRectEqualToRect(planPreviousRect, combinedUsable) ||
                !CGRectEqualToRect(planNextRect, combinedUsable) ||
                ![planNextReason isEqualToString:@"measured-dock-nofrome"]) {
                NSLog(@"FAIL: host plan diagnostic-only must avoid relayout");
                return 1;
            }
            // Only geometry-changing transitions consult the existing
            // full-host guard, and a flag can force conservative fallback.
            planBefore.usableBounds = area;
            planNext.usableBounds = area;
            planBefore.dockState = 0;
            planNext.dockState = leftDockState;
            if (![DDHostDockHostingPlanForSnapshots(
                    planBefore, planNext, planLifecycle,
                    &planPreviousRect, &planNextRect, NULL, NULL)
                    isEqualToString:@"full-host-required"]) {
                NSLog(@"FAIL: dirty lifecycle must require full-host fallback");
                return 1;
            }
            planLifecycle.dirty = NO;
            planLifecycle.active = NO;
            if (![DDHostDockHostingPlanForSnapshots(
                    planBefore, planNext, planLifecycle,
                    NULL, NULL, NULL, NULL)
                    isEqualToString:@"full-host-required"]) {
                NSLog(@"FAIL: inactive lifecycle must require full-host fallback");
                return 1;
            }
            planLifecycle.active = YES;
            // Shell movement requires an update even with identical dock.
            // A caller-reported geometry mismatch upgrades it to full host.
            DDHostCarPlayLayoutSnapshot movingBefore =
                { combinedShell, combinedUsable, 0, YES };
            DDHostCarPlayLayoutSnapshot movingAfter =
                { CGRectMake(50, 40, 100, 80), combinedUsable, 0, YES };
            if (![DDHostDockHostingPlanForSnapshots(
                    movingBefore, movingAfter, planLifecycle,
                    &planPreviousRect, &planNextRect, NULL, NULL)
                    isEqualToString:@"update-layout"] ||
                !CGRectEqualToRect(planPreviousRect, combinedShell) ||
                !CGRectEqualToRect(planNextRect,
                    CGRectMake(50, 40, 100, 80))) {
                NSLog(@"FAIL: shell movement should update hosting layout");
                return 1;
            }
            planLifecycle.geometryMismatch = YES;
            if (![DDHostDockHostingPlanForSnapshots(
                    movingBefore, movingAfter, planLifecycle,
                    NULL, NULL, NULL, NULL)
                    isEqualToString:@"full-host-required"]) {
                NSLog(@"FAIL: shell mismatch should demand full host");
                return 1;
            }
            planLifecycle.geometryMismatch = NO;
            planNext.usableBounds = CGRectZero;
            planPreviousRect = CGRectMake(1, 2, 3, 4);
            planNextRect = CGRectMake(5, 6, 7, 8);
            planPreviousReason = @"previous-sentinel";
            planNextReason = @"next-sentinel";
            if (![DDHostDockHostingPlanForSnapshots(
                    planBefore, planNext, planLifecycle,
                    &planPreviousRect, &planNextRect, &planPreviousReason,
                    &planNextReason) isEqualToString:@"invalid-geometry"] ||
                !CGRectEqualToRect(planPreviousRect, CGRectMake(1, 2, 3, 4)) ||
                !CGRectEqualToRect(planNextRect, CGRectMake(5, 6, 7, 8)) ||
                ![planPreviousReason isEqualToString:@"previous-sentinel"] ||
                ![planNextReason isEqualToString:@"next-sentinel"]) {
                NSLog(@"FAIL: host plan rejected geometry modified outputs");
                return 1;
            }
        }
        // 23D94: source-derived diagnostic label is suffixed only for covered.
        if (![DDHostFinalGeometryReason(@"carplay-subrect", @"covered")
                isEqualToString:@"carplay-subrect+dock"] ||
            ![DDHostFinalGeometryReason(@"measured-dock", @"covered")
                isEqualToString:@"measured-dock+dock"] ||
            ![DDHostFinalGeometryReason(@"measured-dock-nofrome", @"covered")
                isEqualToString:@"measured-dock-nofrome+dock"] ||
            ![DDHostFinalGeometryReason(@"single-app", @"covered")
                isEqualToString:@"single-app+dock"] ||
            ![DDHostFinalGeometryReason(@"carplay-fullscreen", @"covered")
                isEqualToString:@"covered+dock"] ||
            ![DDHostFinalGeometryReason(nil, @"covered")
                isEqualToString:@"covered+dock"] ||
            ![DDHostFinalGeometryReason(@"measured-dock", @"outside-usable")
                isEqualToString:@"measured-dock"] ||
            ![DDHostFinalGeometryReason(@"carplay-subrect", nil)
                isEqualToString:@"carplay-subrect"]) {
            NSLog(@"FAIL: 23D94 final covered dock diagnostic labels");
            return 1;
        }
        // 23D94: missing/undersized/outside shell falls back to the usable
        // CarPlay rectangle before clipping a measured edge dock.
        CGRect fallbackBounds = CGRectMake(1, 2, 3, 4);
        if (!DDHostTrimFallbackCarPlayBoundsForDockState(
                CGRectZero, area, leftDockState, &fallbackBounds) ||
            !CGRectEqualToRect(fallbackBounds, CGRectMake(40, 20, 170, 120)) ||
            !DDHostTrimFallbackCarPlayBoundsForDockState(
                CGRectMake(10, 20, 39, 100), area, leftDockState, &fallbackBounds) ||
            !DDHostTrimFallbackCarPlayBoundsForDockState(
                CGRectMake(500, 20, 100, 100), area, leftDockState, &fallbackBounds) ||
            DDHostTrimFallbackCarPlayBoundsForDockState(
                CGRectMake(50, 40, 100, 80), area, leftDockState, &fallbackBounds) ||
            DDHostTrimFallbackCarPlayBoundsForDockState(
                CGRectZero, area, 0, &fallbackBounds) ||
            !CGRectEqualToRect(fallbackBounds, CGRectMake(40, 20, 170, 120))) {
            NSLog(@"FAIL: 23D94 fallback measured-dock clipping");
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
