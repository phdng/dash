// RECONSTRUCTION/HostFlowAdapter.m — executable post-present host-flow adapter (session-177)
// Exact source site: sub_3257C -> LSDA 0x113860, action-5
// 0x32A94..0x32AB4 -> 0x33A3C.
//
// This adapter is intentionally decision-only. It is compiled into the tweak and consumes
// RecoveryRouting capability state, but does not call DDz4/private selectors itself.

#import "DuoDashShared.h"

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

// 208F4:207-237: hosted slot size must reach 1.0 for BID comparison.
// Caller supplies the size; no private slot inspection is performed here.
BOOL DDHostSwitchHostedSlotSizeValid(double hostedSlotSize) {
    return hostedSlotSize >= 1.0;
}

// Composes only the independently evidenced 208F4:170-206 early guards.
// All private state acquisition, BID comparison, geometry and UI mutations
// remain the responsibility of a separately evidenced caller.
BOOL DDHostSwitchEarlyGuardsAllow(DDHostSwitchEarlyGuardSnapshot snapshot) {
    return DDHostSwitchInteractionStateAllows(snapshot.active,
                                              snapshot.splitHosting,
                                              snapshot.visible,
                                              snapshot.swapInFlight,
                                              snapshot.maximizedPosition,
                                              snapshot.maximizeInFlight) &&
           DDHostSwitchConsistencyAllows(snapshot.pendingGeneration,
                                         snapshot.requestedGeometryVersion,
                                         snapshot.appliedGeometryVersion,
                                         snapshot.activeLayout,
                                         snapshot.preferredLayout) &&
           DDHostSwitchSlotCountsMatch(snapshot.hostedSlotCount,
                                       snapshot.runtimeSlotCount,
                                       snapshot.layoutSlotCount,
                                       snapshot.preparedSlotCapacity) &&
           DDHostSwitchModeFlagsAllow(snapshot.hostMode,
                                      snapshot.hostPhase,
                                      snapshot.stateFlags);
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
