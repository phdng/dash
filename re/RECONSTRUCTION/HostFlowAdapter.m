// RECONSTRUCTION/HostFlowAdapter.m — executable post-present host-flow adapter (session-177)
// Exact source site: sub_3257C -> LSDA 0x113860, action-5
// 0x32A94..0x32AB4 -> 0x33A3C.
//
// This adapter is intentionally decision-only. It is compiled into the tweak and consumes
// RecoveryRouting capability state, but does not call DDz4/private selectors itself.

#import "DuoDashShared.h"
#include <math.h>
#import <objc/message.h>

// Exact full-host vs reshow selection at 218D8:307-313 (evidence/hosting_engine.md).
// Does not acquire any gate, call DDz controllers, or mutate host state.
BOOL DDHostRequiresFullHost(BOOL deactivateDismissPresent,
                            BOOL active,
                            BOOL splitHosting,
                            BOOL visible,
                            BOOL geometryMismatch,
                            BOOL dirty,
                            BOOL canPresent) {
    return deactivateDismissPresent || !active || !splitHosting || visible ||
           geometryMismatch || dirty || !canPresent;
}

// 218D8:315-327: empty usable display and failed prepareShell -> no-display refusal.
// Neither display acquisition nor refusal notification is executed here.
BOOL DDHostShouldRefuseNoDisplay(BOOL usableBoundsEmpty,
                                 BOOL prepareShellSucceeded) {
    return usableBoundsEmpty && !prepareShellSucceeded;
}

// 218D8:338-352: calculated content geometry below one point on either axis
// produces the degenerate-content refusal. This does not publish host.state.
BOOL DDHostHasDegenerateContent(double width, double height) {
    return width < 1.0 || height < 1.0;
}

// 27AE4:11-13: the delayed onHosted callback proceeds only for its captured generation.
// Does not schedule work or invoke the downstream reap/kill path.
BOOL DDHostDelayedGenerationIsCurrent(uint64_t capturedGeneration,
                                      uint64_t currentGeneration) {
    return capturedGeneration == currentGeneration;
}

// 208F4:170-206: one early guard requires hosted slot count in [1,3].
// This predicate alone does not authorize an in-place CarPlay UI switch.
BOOL DDHostSwitchSlotCountIsValid(NSInteger hostedSlotCount) {
    return hostedSlotCount >= 1 && hostedSlotCount <= 3;
}

// 208F4:170-206: three required in-place switch mode guards.
// Values are supplied by the caller; this is not sufficient to authorize switching.
BOOL DDHostSwitchModeFlagsAllow(NSUInteger hostMode,
                                NSUInteger hostPhase,
                                NSUInteger stateFlags) {
    return hostMode == 0x0100 && hostPhase == 2 && (stateFlags & 0x101) == 0;
}

// 208F4:170-206: the switch requires consistent hosted, layout and runtime
// slot counts, with enough prepared slot capacity. This is one gate only.
BOOL DDHostSwitchSlotCountsMatch(NSInteger hostedSlotCount,
                                 NSInteger runtimeSlotCount,
                                 NSInteger layoutSlotCount,
                                 NSInteger preparedSlotCapacity) {
    return DDHostSwitchSlotCountIsValid(hostedSlotCount) &&
           hostedSlotCount == runtimeSlotCount &&
           hostedSlotCount == layoutSlotCount &&
           preparedSlotCapacity >= hostedSlotCount;
}

// 208F4:170-206: required host visibility / interaction state for in-place switch.
// This is only one early guard, not sufficient to authorize switching.
BOOL DDHostSwitchInteractionStateAllows(BOOL active,
                                        BOOL splitHosting,
                                        BOOL visible,
                                        BOOL swapInFlight,
                                        NSInteger maximizedPosition,
                                        BOOL maximizeInFlight) {
    return active && splitHosting && visible && !swapInFlight &&
           maximizedPosition >= 0 && !maximizeInFlight;
}

// 208F4:170-206: generation, geometry, and preference-layout consistency.
// These supplied-state checks are necessary but not sufficient for switching.
BOOL DDHostSwitchConsistencyAllows(uint64_t pendingGeneration,
                                   NSInteger requestedGeometryVersion,
                                   NSInteger appliedGeometryVersion,
                                   NSInteger activeLayout,
                                   NSInteger preferredLayout) {
    return pendingGeneration == 0 &&
           requestedGeometryVersion == appliedGeometryVersion &&
           activeLayout == preferredLayout;
}

// 26FE4:81-260: post-switch continuation requires a live, visible split host
// and an active CarPlay connection. Remaining private checks are excluded.
BOOL DDHostSwitchContinuationStateAllows(BOOL active,
                                         BOOL splitHosting,
                                         BOOL visible,
                                         BOOL carPlayConnected) {
    return active && splitHosting && visible && carPlayConnected;
}

// 208F4:238-242: reject in-place switch when 22D64 reports shell-bounds mismatch.
// The bounds check itself remains private and is not called here.
BOOL DDHostSwitchShellBoundsAllow(BOOL shellBoundsMismatch) {
    return !shellBoundsMismatch;
}

// 208F4:574-584: nonempty pending BID set uses the delayed continuation path;
// an empty set calls the continuation directly. Does not schedule either path.
BOOL DDHostSwitchNeedsDelayedContinuation(NSUInteger pendingBidCount) {
    return pendingBidCount != 0;
}

// 217EC:26-37: two-pane wrapper coalesces absent L/R bundle IDs to empty strings.
// Does not construct the host request or invoke hostSlots:skipEvict:onHosted:.
NSString *DDHostSplitBidOrEmpty(NSString * _Nullable bid) {
    return bid ?: @"";
}

// 217EC:26-37: nil-coalesce each ordered pane ID, then construct the
// exact two-element host input array. No hostSlots: invocation is performed.
NSArray<NSString *> *DDHostSplitBids(NSString * _Nullable leftBid,
                                     NSString * _Nullable rightBid) {
    return @[DDHostSplitBidOrEmpty(leftBid), DDHostSplitBidOrEmpty(rightBid)];
}

// 208F4:207-237: hosted slot size must reach 1.0 for BID comparison.
// Caller supplies the size; no private slot inspection is performed here.
BOOL DDHostSwitchHostedSlotSizeValid(double hostedSlotSize) {
    return isfinite(hostedSlotSize) && hostedSlotSize >= 1.0;
}

BOOL DDHostSwitchAllSlotSizesValid(NSArray<NSNumber *> * _Nullable sizes,
                                   NSInteger expectedSlotCount) {
    if (!DDHostSwitchSlotCountIsValid(expectedSlotCount) ||
        ![sizes isKindOfClass:[NSArray class]] ||
        sizes.count != (NSUInteger)expectedSlotCount)
        return NO;
    for (id size in sizes) {
        if (![size isKindOfClass:[NSNumber class]] ||
            !DDHostSwitchHostedSlotSizeValid([size doubleValue]))
            return NO;
    }
    return YES;
}

// The decompiled 208F4 loop rejects a slot if either adjacent dimension
// is below 1.0 (v14[-1] or v14[0]). Validate both, for every active slot.
BOOL DDHostSwitchSlotDimensionsValid(NSArray<NSArray<NSNumber *> *> * _Nullable dimensions,
                                     NSInteger expectedSlotCount) {
    if (!DDHostSwitchSlotCountIsValid(expectedSlotCount) ||
        ![dimensions isKindOfClass:[NSArray class]] ||
        dimensions.count < (NSUInteger)expectedSlotCount)
        return NO;
    for (NSUInteger slot = 0; slot < (NSUInteger)expectedSlotCount; ++slot) {
        id pair = dimensions[slot];
        if (![pair isKindOfClass:[NSArray class]] || [pair count] != 2)
            return NO;
        for (id coordinate in pair) {
            if (![coordinate isKindOfClass:[NSNumber class]] ||
                !DDHostSwitchHostedSlotSizeValid([coordinate doubleValue]))
                return NO;
        }
    }
    return YES;
}

// 208F4:207-237: caller must supply the already-normalized BID arrays.
// Preserve strict slot-index order; normalization via private 3DD4C is excluded.
BOOL DDHostSwitchBidsMatch(NSArray<NSString *> * _Nullable requestedBids,
                           NSArray<NSString *> * _Nullable hostedBids,
                           NSInteger expectedSlotCount) {
    if (!DDHostSwitchSlotCountIsValid(expectedSlotCount) ||
        (requestedBids != nil && ![requestedBids isKindOfClass:[NSArray class]]) ||
        ![hostedBids isKindOfClass:[NSArray class]] ||
        hostedBids.count < (NSUInteger)expectedSlotCount)
        return NO;

    for (NSUInteger index = 0; index < (NSUInteger)expectedSlotCount; ++index) {
        // 208F4:214-226: missing requested indexes and nil slot BIDs
        // are compared as empty strings, while excess BIDs are ignored.
        id requested = index < requestedBids.count ? requestedBids[index] : @"";
        id hosted = hostedBids[index];
        if (requested == [NSNull null] || hosted == [NSNull null] ||
            ![requested isKindOfClass:[NSString class]] ||
            ![hosted isKindOfClass:[NSString class]] ||
            ![requested isEqualToString:hosted])
            return NO;
    }
    return YES;
}

// 3DD4C: when a3=0, skip SBApplicationController lookup entirely.
// Preserve ordered slots, non-string/absent to empty and first nonempty BID.
NSArray<NSString *> *DDHostNormalizeBidsWithoutLookup(NSArray * _Nullable requestedBids,
                                                       NSInteger slotCount) {
    if (slotCount < 0 ||
        (requestedBids && ![requestedBids isKindOfClass:[NSArray class]]))
        return @[];
    NSMutableArray<NSString *> *normalized = [NSMutableArray arrayWithCapacity:(NSUInteger)slotCount];
    for (NSUInteger slot = 0; slot < (NSUInteger)slotCount; ++slot) {
        id bid = slot < requestedBids.count ? requestedBids[slot] : nil;
        NSString *value = [bid isKindOfClass:[NSString class]] ? bid : @"";
        if (value.length && [normalized containsObject:value])
            value = @"";
        [normalized addObject:value];
    }
    return normalized;
}

// 3DD4C (a3=1): caller resolves application availability externally.
// A nil set models unavailable SBApplicationController/respondsToSelector;
// CarPlay UI slots bypass application existence checking.
NSArray<NSString *> *DDHostNormalizeBidsWithAvailability(
    NSArray * _Nullable requestedBids, NSInteger slotCount,
    NSArray * _Nullable carPlayUIFlags, NSSet<NSString *> * _Nullable availableBids) {
    if (slotCount < 0 ||
        (requestedBids && ![requestedBids isKindOfClass:[NSArray class]]) ||
        (carPlayUIFlags && ![carPlayUIFlags isKindOfClass:[NSArray class]]) ||
        (availableBids && ![availableBids isKindOfClass:[NSSet class]]))
        return @[];
    NSMutableArray<NSString *> *normalized = [NSMutableArray arrayWithCapacity:(NSUInteger)slotCount];
    for (NSUInteger slot = 0; slot < (NSUInteger)slotCount; ++slot) {
        id input = slot < requestedBids.count ? requestedBids[slot] : nil;
        NSString *bid = [input isKindOfClass:[NSString class]] ? input : @"";
        if (bid.length && [normalized containsObject:bid])
            bid = @"";
        id flag = slot < carPlayUIFlags.count ? carPlayUIFlags[slot] : nil;
        BOOL isCarPlayUI = [flag respondsToSelector:@selector(boolValue)] && [flag boolValue];
        if (bid.length && availableBids != nil && !isCarPlayUI &&
            ![availableBids containsObject:bid])
            bid = @"";
        [normalized addObject:bid];
    }
    return normalized;
}

// 3DD4C (a3=1): exact class and selectors from decoded source.
// Fail open to lookup-free normalization when private APIs are unavailable,
// matching the original v10=nil branch. No SpringBoard class dependency.
NSArray<NSString *> *DDHostNormalizeBidsUsingSpringBoard(
    NSArray * _Nullable requestedBids, NSInteger slotCount,
    NSArray * _Nullable carPlayUIFlags) {
    if (slotCount < 0 ||
        (requestedBids && ![requestedBids isKindOfClass:[NSArray class]]) ||
        (carPlayUIFlags && ![carPlayUIFlags isKindOfClass:[NSArray class]]))
        return @[];
    Class controllerClass = NSClassFromString(@"SBApplicationController");
    SEL sharedSelector = NSSelectorFromString(@"sharedInstance");
    SEL applicationSelector = NSSelectorFromString(@"applicationWithBundleIdentifier:");
    id controller = nil;
    if (controllerClass && [controllerClass respondsToSelector:sharedSelector]) {
        id (*getShared)(id, SEL) = (id (*)(id, SEL))objc_msgSend;
        controller = getShared(controllerClass, sharedSelector);
        if (![controller respondsToSelector:applicationSelector])
            controller = nil;
    }
    NSMutableArray<NSString *> *normalized = [NSMutableArray arrayWithCapacity:(NSUInteger)slotCount];
    for (NSUInteger slot = 0; slot < (NSUInteger)slotCount; ++slot) {
        id input = slot < requestedBids.count ? requestedBids[slot] : nil;
        NSString *bid = [input isKindOfClass:[NSString class]] ? input : @"";
        if (bid.length && [normalized containsObject:bid])
            bid = @"";
        id flag = slot < carPlayUIFlags.count ? carPlayUIFlags[slot] : nil;
        BOOL isCarPlayUI = [flag respondsToSelector:@selector(boolValue)] && [flag boolValue];
        if (bid.length && controller && !isCarPlayUI) {
            id (*findApplication)(id, SEL, id) = (id (*)(id, SEL, id))objc_msgSend;
            if (!findApplication(controller, applicationSelector, bid))
                bid = @"";
        }
        [normalized addObject:bid];
    }
    return normalized;
}

// 218D8:213-235 contrasts with 208F4: it permits missing hosted entries,
// comparing both absent requested and hosted slots as empty strings. Inputs
// are supplied after private 3DD4C normalization by an external caller.
BOOL DDHostPreparedBidsMatch(NSArray<NSString *> * _Nullable normalizedBids,
                             NSArray<NSString *> * _Nullable hostedBids,
                             NSInteger expectedSlotCount) {
    if (!DDHostSwitchSlotCountIsValid(expectedSlotCount) ||
        (normalizedBids && ![normalizedBids isKindOfClass:[NSArray class]]) ||
        (hostedBids && ![hostedBids isKindOfClass:[NSArray class]]))
        return NO;
    for (NSUInteger slot = 0; slot < (NSUInteger)expectedSlotCount; ++slot) {
        id requested = slot < normalizedBids.count ? normalizedBids[slot] : @"";
        id hosted = slot < hostedBids.count ? hostedBids[slot] : @"";
        if (![requested isKindOfClass:[NSString class]] ||
            ![hosted isKindOfClass:[NSString class]] ||
            ![requested isEqualToString:hosted])
            return NO;
    }
    return YES;
}

// 218D8:213-236 compares normalized and hosted BIDs, and one scalar
// dimension per slot (v20 += 2). This is deliberately distinct from the
// two-dimension switch gate of 208F4. Never accesses private geometry.
BOOL DDHostPreparedSlotsReady(NSArray<NSString *> * _Nullable normalizedBids,
                              NSArray<NSString *> * _Nullable hostedBids,
                              NSArray<NSNumber *> * _Nullable firstDimensions,
                              NSInteger expectedSlotCount) {
    if (!DDHostPreparedBidsMatch(normalizedBids, hostedBids, expectedSlotCount) ||
        ![firstDimensions isKindOfClass:[NSArray class]] ||
        firstDimensions.count < (NSUInteger)expectedSlotCount)
        return NO;
    // 218D8:229-236 reads exactly expectedSlotCount dimensions; trailing
    // measurements are not visited by its loop.
    for (NSUInteger slot = 0; slot < (NSUInteger)expectedSlotCount; ++slot) {
        id value = firstDimensions[slot];
        if (![value isKindOfClass:[NSNumber class]] ||
            !DDHostSwitchHostedSlotSizeValid([value doubleValue]))
            return NO;
    }
    return YES;
}

// 218D8:264-295: sub_22E40 supplies prepared flags; both arrays are read
// within the active count, with missing entries interpreted as false.
BOOL DDHostPreparedCarPlayFlagsMatch(NSArray * _Nullable preparedFlags,
                                    NSArray * _Nullable hostedFlags,
                                    NSInteger expectedSlotCount) {
    if (!DDHostSwitchSlotCountIsValid(expectedSlotCount) ||
        (preparedFlags && ![preparedFlags isKindOfClass:[NSArray class]]) ||
        (hostedFlags && ![hostedFlags isKindOfClass:[NSArray class]]))
        return NO;
    for (NSUInteger slot = 0; slot < (NSUInteger)expectedSlotCount; ++slot) {
        id prepared = slot < preparedFlags.count ? preparedFlags[slot] : nil;
        id hosted = slot < hostedFlags.count ? hostedFlags[slot] : nil;
        BOOL preparedValue = [prepared respondsToSelector:@selector(boolValue)] && [prepared boolValue];
        BOOL hostedValue = [hosted respondsToSelector:@selector(boolValue)] && [hosted boolValue];
        if (preparedValue != hostedValue)
            return NO;
    }
    return YES;
}

// 22D64: reject if saved shell dimensions are >=40 and current shell
// differs by >1 point on either axis; otherwise, reject if the CarPlay
// display differs by >1 point from the layout calculated by sub_23D94.
// Private geometry acquisition and sub_23D94 invocation remain external.
BOOL DDHostDisplayGeometryMismatch(
    double shellWidth, double shellHeight,
    double savedShellWidth, double savedShellHeight,
    double displayWidth, double displayHeight,
    double calculatedWidth, double calculatedHeight) {
    BOOL shellNeedsDisplayCheck = savedShellWidth < 40.0 ||
        savedShellHeight < 40.0 ||
        (fabs(shellWidth - savedShellWidth) <= 1.0 &&
         fabs(shellHeight - savedShellHeight) <= 1.0);
    if (!shellNeedsDisplayCheck)
        return YES;
    return !(fabs(displayWidth - calculatedWidth) <= 1.0 &&
             fabs(displayHeight - calculatedHeight) <= 1.0);
}

// 218D8:213-295: the prepared path requires both normalized BID/size
// agreement and CarPlay UI flag agreement; other private guards are external.
BOOL DDHostPreparedSlotsAndFlagsMatch(
    NSArray<NSString *> * _Nullable normalizedBids,
    NSArray<NSString *> * _Nullable hostedBids,
    NSArray<NSNumber *> * _Nullable firstDimensions,
    NSArray * _Nullable preparedFlags, NSArray * _Nullable hostedFlags,
    NSInteger expectedSlotCount) {
    return DDHostPreparedSlotsReady(normalizedBids, hostedBids,
                                    firstDimensions, expectedSlotCount) &&
           DDHostPreparedCarPlayFlagsMatch(preparedFlags, hostedFlags,
                                           expectedSlotCount);
}

// Compose the two recovered 3DD4C -> 218D8 pure-data stages.
// The caller must supply SBApplication availability and measured geometry.
BOOL DDHostPreparedRequestReady(
    NSArray * _Nullable requestedBids, NSInteger expectedSlotCount,
    NSArray * _Nullable carPlayUIFlags, NSSet<NSString *> * _Nullable availableBids,
    NSArray<NSString *> * _Nullable hostedBids,
    NSArray<NSNumber *> * _Nullable firstDimensions) {
    if (!DDHostSwitchSlotCountIsValid(expectedSlotCount) ||
        (requestedBids && ![requestedBids isKindOfClass:[NSArray class]]) ||
        (carPlayUIFlags && ![carPlayUIFlags isKindOfClass:[NSArray class]]) ||
        (availableBids && ![availableBids isKindOfClass:[NSSet class]]))
        return NO;
    NSArray<NSString *> *normalized = DDHostNormalizeBidsWithAvailability(
        requestedBids, expectedSlotCount, carPlayUIFlags, availableBids);
    return DDHostPreparedSlotsReady(normalized, hostedBids,
                                    firstDimensions, expectedSlotCount);
}

// Live opt-in counterpart to DDHostPreparedRequestReady; the decoded
// SpringBoard resolver is invoked only here, then 218D8's prepared gates run.
BOOL DDHostPreparedRequestReadyUsingSpringBoard(
    NSArray * _Nullable requestedBids, NSInteger expectedSlotCount,
    NSArray * _Nullable carPlayUIFlags,
    NSArray<NSString *> * _Nullable hostedBids,
    NSArray<NSNumber *> * _Nullable firstDimensions) {
    if (!DDHostSwitchSlotCountIsValid(expectedSlotCount) ||
        (requestedBids && ![requestedBids isKindOfClass:[NSArray class]]) ||
        (carPlayUIFlags && ![carPlayUIFlags isKindOfClass:[NSArray class]]))
        return NO;
    NSArray<NSString *> *normalized = DDHostNormalizeBidsUsingSpringBoard(
        requestedBids, expectedSlotCount, carPlayUIFlags);
    return DDHostPreparedSlotsReady(normalized, hostedBids,
                                    firstDimensions, expectedSlotCount);
}

// Composes only the independently evidenced 208F4:170-206 early guards.
// All private state acquisition, BID comparison, geometry and UI mutations
// remain the responsibility of a separately evidenced caller.
NSUInteger DDHostSwitchEarlyGuardFailures(DDHostSwitchEarlyGuardSnapshot snapshot) {
    NSUInteger failures = 0;
    if (!DDHostSwitchInteractionStateAllows(snapshot.active,
                                             snapshot.splitHosting,
                                             snapshot.visible,
                                             snapshot.swapInFlight,
                                             snapshot.maximizedPosition,
                                             snapshot.maximizeInFlight))
        failures |= DDHostSwitchEarlyGuardFailureInteraction;
    if (!DDHostSwitchConsistencyAllows(snapshot.pendingGeneration,
                                        snapshot.requestedGeometryVersion,
                                        snapshot.appliedGeometryVersion,
                                        snapshot.activeLayout,
                                        snapshot.preferredLayout))
        failures |= DDHostSwitchEarlyGuardFailureConsistency;
    if (!DDHostSwitchSlotCountsMatch(snapshot.hostedSlotCount,
                                      snapshot.runtimeSlotCount,
                                      snapshot.layoutSlotCount,
                                      snapshot.preparedSlotCapacity))
        failures |= DDHostSwitchEarlyGuardFailureSlotCounts;
    if (!DDHostSwitchModeFlagsAllow(snapshot.hostMode,
                                     snapshot.hostPhase,
                                     snapshot.stateFlags))
        failures |= DDHostSwitchEarlyGuardFailureModeFlags;
    return failures;
}

BOOL DDHostSwitchEarlyGuardsAllow(DDHostSwitchEarlyGuardSnapshot snapshot) {
    return DDHostSwitchEarlyGuardFailures(snapshot) == 0;
}

// 208F4:207-242: preserve later rejection gates independently of the
// 170-206 snapshot. The caller must first check BID identity and obtain the
// observed shell-bounds comparison; this function performs neither operation.
NSUInteger DDHostSwitchPostEarlyFailures(double hostedSlotSize,
                                         BOOL shellBoundsMismatch) {
    NSUInteger failures = 0;
    if (!DDHostSwitchHostedSlotSizeValid(hostedSlotSize))
        failures |= DDHostSwitchPostEarlyFailureHostedSlotSize;
    if (!DDHostSwitchShellBoundsAllow(shellBoundsMismatch))
        failures |= DDHostSwitchPostEarlyFailureShellBounds;
    return failures;
}

// Combine the independently established 208F4 refusal stages without
// fetching private state or attempting any UI mutation. The caller must
// provide normalized BIDs and an already-observed shell bounds comparison.
DDHostSwitchPreflightResult DDHostSwitchPreflight(
    DDHostSwitchEarlyGuardSnapshot snapshot,
    NSArray<NSString *> * _Nullable requestedBids,
    NSArray<NSString *> * _Nullable hostedBids,
    double hostedSlotSize,
    BOOL shellBoundsMismatch) {
    DDHostSwitchPreflightResult result = {0};
    result.earlyFailures = DDHostSwitchEarlyGuardFailures(snapshot);
    if (result.earlyFailures != 0)
        return result;

    result.bidsMatch = DDHostSwitchBidsMatch(requestedBids,
                                             hostedBids,
                                             snapshot.hostedSlotCount);
    if (!result.bidsMatch)
        return result;

    result.postEarlyFailures = DDHostSwitchPostEarlyFailures(hostedSlotSize,
                                                              shellBoundsMismatch);
    result.canProceedToPrivateSwitchChecks = result.postEarlyFailures == 0;
    return result;
}

// Staged per-slot version: the private caller supplies all measured slot sizes.
DDHostSwitchPreflightResult DDHostSwitchPreflightForSlots(
    DDHostSwitchEarlyGuardSnapshot snapshot,
    NSArray<NSString *> * _Nullable requestedBids,
    NSArray<NSString *> * _Nullable hostedBids,
    NSArray<NSNumber *> * _Nullable hostedSlotSizes,
    BOOL shellBoundsMismatch) {
    DDHostSwitchPreflightResult result = {0};
    result.earlyFailures = DDHostSwitchEarlyGuardFailures(snapshot);
    if (result.earlyFailures != 0)
        return result;

    result.bidsMatch = DDHostSwitchBidsMatch(requestedBids, hostedBids,
                                             snapshot.hostedSlotCount);
    if (!result.bidsMatch)
        return result;

    if (!DDHostSwitchAllSlotSizesValid(hostedSlotSizes, snapshot.hostedSlotCount))
        result.postEarlyFailures |= DDHostSwitchPostEarlyFailureHostedSlotSize;
    if (!DDHostSwitchShellBoundsAllow(shellBoundsMismatch))
        result.postEarlyFailures |= DDHostSwitchPostEarlyFailureShellBounds;
    result.canProceedToPrivateSwitchChecks = result.postEarlyFailures == 0;
    return result;
}

DDHostSwitchPreflightResult DDHostSwitchPreflightForDimensions(
    DDHostSwitchEarlyGuardSnapshot snapshot,
    NSArray<NSString *> * _Nullable requestedBids,
    NSArray<NSString *> * _Nullable hostedBids,
    NSArray<NSArray<NSNumber *> *> * _Nullable hostedSlotDimensions,
    BOOL shellBoundsMismatch) {
    DDHostSwitchPreflightResult result = {0};
    result.earlyFailures = DDHostSwitchEarlyGuardFailures(snapshot);
    if (result.earlyFailures != 0)
        return result;
    result.bidsMatch = DDHostSwitchBidsMatch(requestedBids, hostedBids,
                                             snapshot.hostedSlotCount);
    if (!result.bidsMatch)
        return result;
    if (!DDHostSwitchSlotDimensionsValid(hostedSlotDimensions, snapshot.hostedSlotCount))
        result.postEarlyFailures |= DDHostSwitchPostEarlyFailureHostedSlotSize;
    if (!DDHostSwitchShellBoundsAllow(shellBoundsMismatch))
        result.postEarlyFailures |= DDHostSwitchPostEarlyFailureShellBounds;
    result.canProceedToPrivateSwitchChecks = result.postEarlyFailures == 0;
    return result;
}

// Can be invoked explicitly in a device test to exercise the compiled
// implementation; never run implicitly during SpringBoard/CarPlay startup.
BOOL DDHostSwitchPreflightSelfTest(void) {
    DDHostSwitchEarlyGuardSnapshot snapshot = {0};
    snapshot.active = YES;
    snapshot.splitHosting = YES;
    snapshot.visible = YES;
    snapshot.maximizedPosition = 0;
    snapshot.requestedGeometryVersion = 7;
    snapshot.appliedGeometryVersion = 7;
    snapshot.activeLayout = 2;
    snapshot.preferredLayout = 2;
    snapshot.hostedSlotCount = 2;
    snapshot.runtimeSlotCount = 2;
    snapshot.layoutSlotCount = 2;
    snapshot.preparedSlotCapacity = 2;
    snapshot.hostMode = 0x0100;
    snapshot.hostPhase = 2;

    NSArray<NSString *> *bids = @[@"com.example.left", @"com.example.right"];
    // Verify the wrapper preserves both pane positions, including nil input.
    if (![DDHostSplitBids(nil, @"com.example.right")
          isEqualToArray:@[@"", @"com.example.right"]] ||
        ![DDHostSplitBids(@"com.example.left", nil)
          isEqualToArray:@[@"com.example.left", @""]] ||
        ![DDHostSplitBids(nil, nil) isEqualToArray:@[@"", @""]])
        return NO;

    // Decompiled 208F4:215: nil requested array has count 0, so each
    // position compares against an empty BID. Wrong-type input still fails.
    if (!DDHostSwitchBidsMatch(nil, @[@"", @""], 2) ||
        DDHostSwitchBidsMatch(nil, bids, 2) ||
        DDHostSwitchBidsMatch((id)@"invalid-array", @[@"", @""], 2))
        return NO;

    // Decompiled 208F4:207-237: missing requested slots coalesce to @"";
    // hosted arrays may contain more slots than the current layout.
    if (!DDHostSwitchBidsMatch(@[@"com.example.left"],
                               @[@"com.example.left", @""], 2) ||
        !DDHostSwitchBidsMatch(@[@"com.example.left"],
                               @[@"com.example.left", @"", @"extra"], 2) ||
        !DDHostSwitchBidsMatch(bids, @[@"com.example.left", @"com.example.right", @"extra"], 2) ||
        DDHostSwitchBidsMatch(@[@"com.example.left"], bids, 2) ||
        DDHostSwitchBidsMatch(bids, @[@"com.example.left"], 2))
        return NO;

    // 3DD4C is count-driven independently of 208F4's 1..3 switch limit.
    if (![DDHostNormalizeBidsWithoutLookup(@[@"a", @"b", @"c", @"d"], 4)
          isEqualToArray:@[@"a", @"b", @"c", @"d"]] ||
        ![DDHostNormalizeBidsWithAvailability(@[@"a", @"b", @"c", @"d"], 4,
                                               nil, nil)
          isEqualToArray:@[@"a", @"b", @"c", @"d"]])
        return NO;

    // 3DD4C: application rejection precedes insertion into the output,
    // so a later duplicate can survive when the first occurrence was erased.
    if (![DDHostNormalizeBidsWithAvailability(@[@"a", @"a"], 2,
                                               @[@NO, @YES],
                                               [NSSet set])
          isEqualToArray:@[@"", @"a"]] ||
        ![DDHostNormalizeBidsWithAvailability(@[@"a", @"a"], 2,
                                               @[@YES, @YES],
                                               [NSSet set])
          isEqualToArray:@[@"a", @""]] ||
        ![DDHostNormalizeBidsWithAvailability(@[@"a", @"a"], 2,
                                               @[@NO, @NO],
                                               [NSSet set])
          isEqualToArray:@[@"", @""]])
        return NO;

    // 3DD4C without SBApplication lookup: normalize strings and dedupe
    // nonempty repeated IDs, preserving exact position with empty entries.
    if (![DDHostNormalizeBidsWithoutLookup(@[@"a", @"a", @"b"], 3)
          isEqualToArray:@[@"a", @"", @"b"]] ||
        ![DDHostNormalizeBidsWithoutLookup((id)@[@"a", [NSNull null]], 3)
          isEqualToArray:@[@"a", @"", @""]] ||
        ![DDHostNormalizeBidsWithoutLookup(nil, 2) isEqualToArray:@[@"", @""]] ||
        ![DDHostNormalizeBidsWithoutLookup(@[@"a", @"b", @"c"], 2)
          isEqualToArray:@[@"a", @"b"]])
        return NO;

    // 3DD4C (a3=1) application lookup is caller-resolved: UI slots
    // bypass lookup, unavailable apps empty out, duplicates remain empty.
    if (![DDHostNormalizeBidsWithAvailability(@[@"a", @"b", @"a"], 3,
                                               @[@NO, @YES, @NO],
                                               [NSSet setWithObject:@"a"])
          isEqualToArray:@[@"a", @"b", @""]] ||
        ![DDHostNormalizeBidsWithAvailability(@[@"missing", @"a"], 2,
                                               @[@NO, @NO],
                                               [NSSet setWithObject:@"a"])
          isEqualToArray:@[@"", @"a"]] ||
        ![DDHostNormalizeBidsWithAvailability(@[@"missing"], 1, nil, nil)
          isEqualToArray:@[@"missing"]])
        return NO;

    // Integration contract from decompiled 3DD4C -> 218D8. Availability
    // filtering occurs before prepared BID/geometry comparison.
    if (!DDHostPreparedRequestReady(@[@"a", @"unknown"], 2,
                                     @[@NO, @NO], [NSSet setWithObject:@"a"],
                                     @[@"a", @""], @[@1.0, @2.0]) ||
        DDHostPreparedRequestReady(@[@"a", @"unknown"], 2,
                                    @[@NO, @YES], [NSSet setWithObject:@"a"],
                                    @[@"a", @""], @[@1.0, @2.0]) ||
        DDHostPreparedRequestReady(@[@"a"], 2,
                                    nil, [NSSet setWithObject:@"a"],
                                    @[@"a", @""], @[@1.0, @0.5]) ||
        DDHostPreparedRequestReady((id)@"invalid-array", 2,
                                    nil, nil, @[@"", @""], @[@1.0, @2.0]))
        return NO;

    // Decompiled 218D8:213-235 permits missing hosted BIDs, unlike 208F4.
    if (!DDHostPreparedBidsMatch(@[@"com.example.left"],
                                  @[@"com.example.left"], 2) ||
        !DDHostPreparedBidsMatch(nil, nil, 2) ||
        DDHostPreparedBidsMatch(@[@"com.example.left"], nil, 2) ||
        DDHostPreparedBidsMatch((id)@"bad", nil, 2) ||
        DDHostPreparedBidsMatch(@[@"com.example.left"],
                                @[@"com.example.right"], 2))
        return NO;

    // 218D8 validates one measured dimension per prepared hosted slot.
    if (!DDHostPreparedSlotsReady(@[@"com.example.left"],
                                   @[@"com.example.left"], @[@1.0, @2.0], 2) ||
        !DDHostPreparedSlotsReady(nil, nil, @[@1.0, @2.0, @0.0], 2) ||
        DDHostPreparedSlotsReady(@[@"com.example.left"],
                                 @[@"com.example.left"], @[@1.0, @0.5], 2) ||
        DDHostPreparedSlotsReady(nil, nil, @[@1.0], 2) ||
        DDHostPreparedSlotsReady(@[@"com.example.left"], nil, @[@1.0, @2.0], 2))
        return NO;

    // Independently exercise all four diagnostic failure categories.
    snapshot.swapInFlight = YES;
    if (DDHostSwitchEarlyGuardFailures(snapshot) != DDHostSwitchEarlyGuardFailureInteraction)
        return NO;
    snapshot.swapInFlight = NO;
    snapshot.requestedGeometryVersion = 8;
    if (DDHostSwitchEarlyGuardFailures(snapshot) != DDHostSwitchEarlyGuardFailureConsistency)
        return NO;
    snapshot.requestedGeometryVersion = 7;
    snapshot.preparedSlotCapacity = 1;
    if (DDHostSwitchEarlyGuardFailures(snapshot) != DDHostSwitchEarlyGuardFailureSlotCounts)
        return NO;
    snapshot.preparedSlotCapacity = 2;
    snapshot.hostPhase = 1;
    if (DDHostSwitchEarlyGuardFailures(snapshot) != DDHostSwitchEarlyGuardFailureModeFlags)
        return NO;
    snapshot.hostPhase = 2;

    // Direct 208F4:228 evidence: both width AND height must reach 1.0.
    NSArray<NSArray<NSNumber *> *> *validDimensions = @[@[@1.0, @2.0], @[@3.0, @4.0]];
    if (!DDHostSwitchSlotDimensionsValid(validDimensions, 2) ||
        DDHostSwitchSlotDimensionsValid(@[@[@1.0, @2.0], @[@3.0, @0.5]], 2) ||
        DDHostSwitchSlotDimensionsValid(@[@[@1.0, @2.0], @[@0.5, @3.0]], 2) ||
        DDHostSwitchSlotDimensionsValid(@[@[@1.0, @2.0]], 2) ||
        DDHostSwitchSlotDimensionsValid((id)@[@[@1.0, @2.0], @"wrong"], 2))
        return NO;
    DDHostSwitchPreflightResult dimensionResult = DDHostSwitchPreflightForDimensions(
        snapshot, bids, bids, validDimensions, NO);
    if (!dimensionResult.canProceedToPrivateSwitchChecks || !dimensionResult.bidsMatch)
        return NO;
    dimensionResult = DDHostSwitchPreflightForDimensions(
        snapshot, bids, bids, @[@[@1.0, @2.0], @[@3.0, @0.5]], NO);
    if (dimensionResult.postEarlyFailures != DDHostSwitchPostEarlyFailureHostedSlotSize ||
        dimensionResult.canProceedToPrivateSwitchChecks)
        return NO;

    DDHostSwitchPreflightResult result = DDHostSwitchPreflight(snapshot, bids, bids, 1.0, NO);
    if (result.earlyFailures != 0 || !result.bidsMatch ||
        result.postEarlyFailures != 0 || !result.canProceedToPrivateSwitchChecks)
        return NO;

    result = DDHostSwitchPreflight(snapshot, bids,
                                   @[@"com.example.right", @"com.example.left"], 1.0, NO);
    if (result.earlyFailures != 0 || result.bidsMatch ||
        result.canProceedToPrivateSwitchChecks)
        return NO;

    snapshot.pendingGeneration = 1;
    result = DDHostSwitchPreflight(snapshot, bids, bids, 1.0, NO);
    if ((result.earlyFailures & DDHostSwitchEarlyGuardFailureConsistency) == 0 ||
        result.bidsMatch || result.canProceedToPrivateSwitchChecks)
        return NO;
    snapshot.pendingGeneration = 0;

    result = DDHostSwitchPreflight(snapshot, bids, bids, 0.5, NO);
    if (!result.bidsMatch ||
        result.postEarlyFailures != DDHostSwitchPostEarlyFailureHostedSlotSize ||
        result.canProceedToPrivateSwitchChecks)
        return NO;

    result = DDHostSwitchPreflight(snapshot, bids, bids, 1.0, YES);
    if (!result.bidsMatch ||
        result.postEarlyFailures != DDHostSwitchPostEarlyFailureShellBounds ||
        result.canProceedToPrivateSwitchChecks)
        return NO;

    // Fail closed on non-finite slot sizes without changing the documented
    // 218D8 finite-geometry comparison semantics.
    if (DDHostSwitchHostedSlotSizeValid(INFINITY) ||
        DDHostSwitchHostedSlotSizeValid(NAN) ||
        DDHostSwitchAllSlotSizesValid(@[@1.0, @(INFINITY)], 2) ||
        DDHostSwitchAllSlotSizesValid(@[@1.0, @(NAN)], 2))
        return NO;

    // Per-slot 208F4:207-237 check must reject a bad second pane even
    // when the first pane's measured size is valid.
    if (!DDHostSwitchAllSlotSizesValid(@[@1.0, @2.0], 2) ||
        DDHostSwitchAllSlotSizesValid(@[@1.0, @0.5], 2) ||
        DDHostSwitchAllSlotSizesValid(@[@1.0], 2) ||
        DDHostSwitchAllSlotSizesValid(nil, 2) ||
        DDHostSwitchAllSlotSizesValid(@[@1.0, @2.0], 3))
        return NO;

    // Malformed caller input must fail closed before indexed access.
    if (DDHostSwitchBidsMatch((id)@"not-an-array", bids, 2) ||
        DDHostSwitchBidsMatch(bids, (id)@"not-an-array", 2) ||
        DDHostSwitchBidsMatch((id)@[@"com.example.left", [NSNull null]], bids, 2) ||
        DDHostSwitchAllSlotSizesValid((id)@[@1.0, [NSNull null]], 2))
        return NO;

    DDHostSwitchPreflightResult slotsResult = DDHostSwitchPreflightForSlots(
        snapshot, bids, bids, @[@1.0, @2.0], NO);
    if (!slotsResult.canProceedToPrivateSwitchChecks || !slotsResult.bidsMatch ||
        slotsResult.postEarlyFailures != 0)
        return NO;
    slotsResult = DDHostSwitchPreflightForSlots(snapshot, bids, bids,
                                                 @[@1.0, @0.5], NO);
    if (!slotsResult.bidsMatch ||
        slotsResult.postEarlyFailures != DDHostSwitchPostEarlyFailureHostedSlotSize ||
        slotsResult.canProceedToPrivateSwitchChecks)
        return NO;
    slotsResult = DDHostSwitchPreflightForSlots(snapshot, bids, bids,
                                                 @[@1.0, @0.5], YES);
    if (slotsResult.postEarlyFailures != (DDHostSwitchPostEarlyFailureHostedSlotSize |
                                           DDHostSwitchPostEarlyFailureShellBounds) ||
        slotsResult.canProceedToPrivateSwitchChecks)
        return NO;

    // Reject malformed slot measurements and preserve the stage ordering:
    // an early refusal must not report a later BID/geometry acceptance.
    slotsResult = DDHostSwitchPreflightForSlots(snapshot, bids, bids,
                                                 (id)@"invalid-array", NO);
    if (!slotsResult.bidsMatch ||
        slotsResult.postEarlyFailures != DDHostSwitchPostEarlyFailureHostedSlotSize ||
        slotsResult.canProceedToPrivateSwitchChecks)
        return NO;
    snapshot.swapInFlight = YES;
    slotsResult = DDHostSwitchPreflightForSlots(snapshot, bids, bids,
                                                 @[@1.0, @2.0], NO);
    if ((slotsResult.earlyFailures & DDHostSwitchEarlyGuardFailureInteraction) == 0 ||
        slotsResult.bidsMatch || slotsResult.postEarlyFailures != 0 ||
        slotsResult.canProceedToPrivateSwitchChecks)
        return NO;
    snapshot.swapInFlight = NO;

    result = DDHostSwitchPreflight(snapshot, bids, bids, 0.5, YES);
    return result.bidsMatch &&
           result.postEarlyFailures == (DDHostSwitchPostEarlyFailureHostedSlotSize |
                                        DDHostSwitchPostEarlyFailureShellBounds) &&
           !result.canProceedToPrivateSwitchChecks;
}

static BOOL gDDHostFlowAdapterReady;

void DDHostFlowAdapterStart(void) {
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        DDRecoveryRoutingStart();
        NSUInteger capabilities = DDRecoveryRoutingCapabilities();
        gDDHostFlowAdapterReady =
            (capabilities & DDRecoveryRoutingCapabilityPresentOverlayCleanup) != 0 &&
            (capabilities & DDRecoveryRoutingCapabilityReapplyMaximize) != 0;
    });
}

BOOL DDHostFlowAdapterReady(void) {
    DDHostFlowAdapterStart();
    return gDDHostFlowAdapterReady;
}

DDPostPresentHostFlowDecision DDPostPresentHostFlowDecisionForSite(DDPostPresentHostFlowExceptionSite site) {
    DDPostPresentHostFlowDecision decision = {0};
    decision.adapterEnabled = DDHostFlowAdapterReady();
    if (!decision.adapterEnabled || site == DDPostPresentHostFlowExceptionSiteNone)
        return decision;

    // Matching type at 0x33A3C begin/end-catches then branches to 0x32ABC.
    // 0x32ABC releases the retained host input and resumes the caller's post-block flow.
    // Nonmatching type routes through 0x33CF0 -> 0x33D00 -> 0x33D1C.
    decision.shouldSwallowExpectedException = YES;
    decision.shouldContinueAfterHostBlock = YES;
    decision.nonmatchingTypeWouldResumeUnwind = YES;
    decision.remainingHostBlockDefinitelySkipped = YES;
    decision.retainedHostDefinitelyReleasedOnContinuation = YES;

    switch (site) {
        case DDPostPresentHostFlowExceptionSiteSharedAcquisition:
            // 0x32A94 +[DDz4 shared], retainAutoreleasedReturnValue at 0x32A9C.
            // teardown/buildInHost are not reached. Because the catch jumps to 0x32ABC,
            // the normal x22 release at 0x32AB4 is also skipped if acquisition got far
            // enough to retain the shared controller.
            decision.sharedControllerNormalReleaseDefinitelySkipped = YES;
            break;

        case DDPostPresentHostFlowExceptionSiteTeardown:
            // x22 is already the retained DDz4 shared controller.
            // teardown at 0x32AA4 may have applied side effects before throwing.
            decision.sharedControllerDefinitelyAcquiredBeforeSite = YES;
            decision.teardownCouldHaveAppliedBeforeException = YES;
            decision.sharedControllerNormalReleaseDefinitelySkipped = YES;
            break;

        case DDPostPresentHostFlowExceptionSiteBuildInHost:
            // teardown has returned normally; buildInHost: at 0x32AB0 may have partially
            // attached/rebuilt against the retained host before throwing.
            decision.sharedControllerDefinitelyAcquiredBeforeSite = YES;
            decision.teardownDefinitelyCompletedBeforeSite = YES;
            decision.buildInHostCouldHaveAppliedBeforeException = YES;
            decision.sharedControllerNormalReleaseDefinitelySkipped = YES;
            break;

        case DDPostPresentHostFlowExceptionSiteNone:
            break;
    }

    return decision;
}
