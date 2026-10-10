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
