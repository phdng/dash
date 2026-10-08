// RECONSTRUCTION/RecoveryRouting.m — compile-safe integration seam (session-176)
// Consumes evidence-safe ReconstructionRuntime contracts and exposes a stable,
// Foundation-only routing surface for later executable subsystem promotion.
// This module deliberately performs no UIKit/private-selector/global-state mutation.

#import "DuoDashShared.h"
#import "ReconstructionRuntime.h"

static NSUInteger gDDRecoveryRoutingCapabilities;

static BOOL DDLayoutInitialContractIsUsable(void) {
    DDLayoutConfirmInitialEnumerationExceptionOutcome o =
        DDResolveLayoutConfirmInitialEnumerationExceptionOutcome();
    return o.shouldSwallowExpectedException &&
           o.shouldClearSplashInFlightFlag &&
           o.shouldContinueOuterCleanupAndReturn &&
           o.nonmatchingCatchTypeWouldResumeUnwind &&
           o.initialEnumerationResultDefinitelyUncommittedBeforeCatch;
}

static BOOL DDLayoutSubsequentContractIsUsable(void) {
    DDLayoutConfirmSubsequentEnumerationExceptionOutcome o =
        DDResolveLayoutConfirmSubsequentEnumerationExceptionOutcome();
    return o.shouldSwallowExpectedException &&
           o.shouldContinueOuterCleanupAndReturn &&
           o.nonmatchingCatchTypeWouldResumeUnwind &&
           o.subsequentEnumerationResultDefinitelyUncommittedBeforeCatch &&
           o.newLayoutConfirmGlobalCommitDefinitelyNotReachedBeforeCatch;
}

static BOOL DDLayoutSetRootContractIsUsable(void) {
    DDLayoutConfirmSetRootExceptionOutcome o =
        DDResolveLayoutConfirmSetRootExceptionOutcome();
    return o.shouldSwallowExpectedException &&
           o.shouldContinueOuterCleanupAndReturn &&
           o.nonmatchingCatchTypeWouldResumeUnwind &&
           o.newLayoutConfirmGlobalCommitDefinitelyNotReachedBeforeCatch &&
           o.rootAttachDefinitelyNotReachedBeforeCatch &&
           o.countdownTickDefinitelyNotReachedBeforeCatch;
}

static BOOL DDLayoutPostCommitContractIsUsable(void) {
    DDLayoutConfirmPostCommitExceptionOutcome attach =
        DDResolveLayoutConfirmPostCommitExceptionOutcome(
            DDLayoutConfirmPostCommitExceptionSiteRootAttachTyped);
    DDLayoutConfirmPostCommitExceptionOutcome tick =
        DDResolveLayoutConfirmPostCommitExceptionOutcome(
            DDLayoutConfirmPostCommitExceptionSiteCountdownTickTyped);
    DDLayoutConfirmPostCommitExceptionOutcome store =
        DDResolveLayoutConfirmPostCommitExceptionOutcome(
            DDLayoutConfirmPostCommitExceptionSiteGlobalStoreStrongCleanupOnly);
    return attach.shouldSwallowExpectedException &&
           attach.newLayoutConfirmGlobalDefinitelyCommittedBeforeSite &&
           attach.cleanupClearsCommittedLayoutConfirmGlobal &&
           tick.shouldSwallowExpectedException &&
           tick.rootAttachDefinitelyCompletedBeforeSite &&
           store.exceptionWouldResumeUnwind;
}

static BOOL DDReapplyMaximizeContractIsUsable(void) {
    DDReapplyMaximizeRecoveryExceptionOutcome top =
        DDResolveReapplyMaximizeRecoveryExceptionOutcome(
            DDReapplyMaximizeRecoveryExceptionSiteTopLevelTyped);
    DDReapplyMaximizeRecoveryExceptionOutcome nested =
        DDResolveReapplyMaximizeRecoveryExceptionOutcome(
            DDReapplyMaximizeRecoveryExceptionSiteRebuildMatTyped);
    return top.shouldSwallowExpectedException &&
           top.shouldResetHostMaximizeState &&
           top.shouldContinuePresentAfterRecovery &&
           nested.shouldSwallowExpectedNestedRebuildException &&
           nested.shouldContinuePresentAfterNestedRebuildFailure;
}

static BOOL DDPresentOverlayContractIsUsable(void) {
    DDPresentAndOverlayCleanupExceptionOutcome present =
        DDResolvePresentAndOverlayCleanupExceptionOutcome(
            DDPresentAndOverlayCleanupExceptionSitePresentCall);
    DDPresentAndOverlayCleanupExceptionOutcome overlay =
        DDResolvePresentAndOverlayCleanupExceptionOutcome(
            DDPresentAndOverlayCleanupExceptionSiteWeakOverlayCleanup);
    return present.shouldSwallowExpectedException &&
           present.presentResultDefinitelyUncommittedBeforeCatch &&
           present.shouldReturnImmediatelyAfterCatch &&
           overlay.shouldSwallowExpectedException &&
           overlay.presentResultDefinitelyCommittedBeforeSite &&
           overlay.laterBuildInHostDefinitelySkipped;
}

void DDRecoveryRoutingStart(void) {
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        NSUInteger capabilities = 0;
        if (DDLayoutInitialContractIsUsable())
            capabilities |= DDRecoveryRoutingCapabilityLayoutInitialEnumeration;
        if (DDLayoutSubsequentContractIsUsable())
            capabilities |= DDRecoveryRoutingCapabilityLayoutSubsequentEnumeration;
        if (DDLayoutSetRootContractIsUsable())
            capabilities |= DDRecoveryRoutingCapabilityLayoutSetRoot;
        if (DDLayoutPostCommitContractIsUsable())
            capabilities |= DDRecoveryRoutingCapabilityLayoutPostCommit;
        if (DDReapplyMaximizeContractIsUsable())
            capabilities |= DDRecoveryRoutingCapabilityReapplyMaximize;
        if (DDPresentOverlayContractIsUsable())
            capabilities |= DDRecoveryRoutingCapabilityPresentOverlayCleanup;
        gDDRecoveryRoutingCapabilities = capabilities;
    });
}

NSUInteger DDRecoveryRoutingCapabilities(void) {
    DDRecoveryRoutingStart();
    return gDDRecoveryRoutingCapabilities;
}
