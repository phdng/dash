#pragma once

#import "DuoDashShared.h"
#include <stdint.h>

NS_ASSUME_NONNULL_BEGIN

typedef NS_ENUM(NSInteger, DDIntegerValidationStatus) {
    DDIntegerValidationMissing = 0,
    DDIntegerValidationNumber = 1,
    DDIntegerValidationString = 2,
    DDIntegerValidationError = 3,
};

typedef struct {
    double width;
    double height;
} DDHostSlotSize;

typedef struct {
    BOOL valid;
    DDHostSlotSize nativeSize;
    NSInteger orientation;
} DDAuxScenePreparation;

typedef struct {
    BOOL valid;
    DDHostSlotSize frameSize;
    NSInteger orientation;
} DDAuxSceneSettingsPlan;

typedef struct {
    BOOL shouldDispatch;
    uint64_t generation;
    NSInteger attemptNumber;
    DDAuxSceneSettingsPlan settingsPlan;
} DDAuxSceneSettingsAttempt;

typedef NS_ENUM(NSInteger, DDAuxSettingsMutationExceptionSite) {
    DDAuxSettingsMutationExceptionSiteNone = 0,
    DDAuxSettingsMutationExceptionSiteFramePath = 1,
    DDAuxSettingsMutationExceptionSiteOrientationPath = 2,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldSkipRemainingMutation;
    BOOL shouldContinueCleanupAfterCatch;
    BOOL frameAppliedWriteCouldHaveOccurredBeforeException;
    BOOL orientationAppliedWriteWouldBeSkipped;
} DDAuxSettingsMutationExceptionOutcome;

typedef struct {
    BOOL shouldSwallowException;
    BOOL settingsAppliedWriteWouldBeSkipped;
    BOOL shouldDecrementFailureCounter;
    NSInteger nextFailureCounter;
    BOOL shouldClearReentrantState;
    BOOL shouldDisposeByrefCaptures;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
    BOOL nonmatchingCatchTypeWouldClearReentrantState;
    BOOL nonmatchingCatchTypeWouldDecrementFailureCounter;
    BOOL nonmatchingCatchTypeWouldDisposeByrefCaptures;
} DDAuxSettingsExecutorExceptionOutcome;

typedef NS_ENUM(NSInteger, DDAuxSettingsPreparationExceptionSite) {
    DDAuxSettingsPreparationExceptionSiteNone = 0,
    DDAuxSettingsPreparationExceptionSiteInitialAuxGate = 1,
    DDAuxSettingsPreparationExceptionSiteCurrentFrameRead = 2,
    DDAuxSettingsPreparationExceptionSiteCurrentOrientationRead = 3,
    DDAuxSettingsPreparationExceptionSiteLateUpdatePreparation = 4,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldSkipRemainingPreparation;
    BOOL shouldContinueFinalOuterCleanup;
    BOOL retainedWorkingObjectReleaseWouldBeBypassed;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDAuxSettingsPreparationExceptionOutcome;

typedef NS_ENUM(NSInteger, DDSceneIdentityRouteKind) {
    DDSceneIdentityRouteNone = 0,
    DDSceneIdentityRouteHostSlot = 1,
    DDSceneIdentityRouteAux = 2,
};

typedef struct {
    DDSceneIdentityRouteKind kind;
    NSInteger slotIndex;
} DDSceneIdentityRoute;

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldReturnNilIdentity;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDSceneIdentityResolutionExceptionOutcome;

typedef NS_ENUM(NSInteger, DDSceneResolverExceptionSite) {
    DDSceneResolverExceptionSiteNone = 0,
    DDSceneResolverExceptionSitePrimarySceneIfExistsPath = 1,
    DDSceneResolverExceptionSiteFallbackScenePath = 2,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldReturnNilScene;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDSceneResolverExceptionOutcome;

typedef NS_ENUM(NSInteger, DDSceneDiagnosticSummaryExceptionSite) {
    DDSceneDiagnosticSummaryExceptionSiteNone = 0,
    DDSceneDiagnosticSummaryExceptionSiteSceneHandleResolution = 1,
    DDSceneDiagnosticSummaryExceptionSiteSceneResolution = 2,
    DDSceneDiagnosticSummaryExceptionSiteSettingsResolution = 3,
    DDSceneDiagnosticSummaryExceptionSiteSelectorConstruction = 4,
    DDSceneDiagnosticSummaryExceptionSiteForegroundProbe = 5,
    DDSceneDiagnosticSummaryExceptionSiteDiagnosticFormatting = 6,
};

typedef NS_ENUM(NSInteger, DDSceneDiagnosticSummaryFallbackKind) {
    DDSceneDiagnosticSummaryFallbackNone = 0,
    DDSceneDiagnosticSummaryFallbackThrew = 1,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldReturnFallbackSummary;
    DDSceneDiagnosticSummaryFallbackKind fallbackKind;
    BOOL shouldContinueFinalOuterCleanup;
    NSUInteger guaranteedRetainedIntermediateReleaseBypassCount;
    BOOL additionalFormattedIntermediateReleaseCouldBeBypassed;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDSceneDiagnosticSummaryExceptionOutcome;

typedef NS_ENUM(NSInteger, DDBundleNormalizationExceptionSite) {
    DDBundleNormalizationExceptionSiteNone = 0,
    DDBundleNormalizationExceptionSiteApplicationControllerLookup = 1,
    DDBundleNormalizationExceptionSitePerItemApplicationLookup = 2,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldContinueCanonicalization;
    BOOL shouldForceApplicationControllerNil;
    BOOL shouldPreserveSanitizedCandidate;
    BOOL shouldAddCandidateAndContinueLoop;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDBundleNormalizationExceptionOutcome;

typedef NS_ENUM(NSInteger, DDDismissExceptionSite) {
    DDDismissExceptionSiteNone = 0,
    DDDismissExceptionSitePrimaryPrivateTeardown = 1,
    DDDismissExceptionSiteSecondaryPrivateTeardown = 2,
    DDDismissExceptionSitePrivateCleanupRelease = 3,
    DDDismissExceptionSiteSlotZeroBridgeOffPublish = 4,
    DDDismissExceptionSiteLaterSlotBridgeOffPublish = 5,
    DDDismissExceptionSiteResetHostingState = 6,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldSkipRemainingPrivateTeardown;
    BOOL shouldContinueBridgeOffPhase;
    BOOL shouldContinueLaterSlotPublications;
    BOOL shouldContinueSlotLoop;
    BOOL primaryControllerIvarWasAlreadyCleared;
    BOOL secondaryControllerIvarsWereAlreadyCleared;
    BOOL normalPrivateTeardownCleanupWouldBeBypassed;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDDismissExceptionOutcome;

typedef NS_ENUM(NSInteger, DDConvertSlotToCarPlayExceptionSite) {
    DDConvertSlotToCarPlayExceptionSiteNone = 0,
    DDConvertSlotToCarPlayExceptionSitePrivateHostedViewTeardown = 1,
    DDConvertSlotToCarPlayExceptionSiteBridgeOffPublish = 2,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldContinueControllerIvarClear;
    BOOL shouldContinueBridgeOffPhase;
    BOOL shouldCommitHostedBundleState;
    BOOL shouldSetCarPlayFlag;
    BOOL controllerIvarWasAlreadyClearedBeforeCatch;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDConvertSlotToCarPlayExceptionOutcome;

typedef NS_ENUM(NSInteger, DDSpikeHostSlotsLandscapeExceptionSite) {
    DDSpikeHostSlotsLandscapeExceptionSiteNone = 0,
    DDSpikeHostSlotsLandscapeExceptionSiteTypedBeforeAuxStateCommit = 1,
    DDSpikeHostSlotsLandscapeExceptionSiteTypedAfterAuxStateCommit = 2,
    DDSpikeHostSlotsLandscapeExceptionSiteActionZeroCleanup = 3,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldClearParsedLandscapeOrientation;
    BOOL shouldResolveFallbackOrientation;
    BOOL shouldContinueHosting;
    BOOL swapStateWouldRemainCommitted;
    BOOL crossSwapStateWouldRemainCommitted;
    BOOL rotationStateWouldRemainCommitted;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDSpikeHostSlotsLandscapeExceptionOutcome;

typedef NS_ENUM(NSInteger, DDAuxSceneTeardownExceptionSite) {
    DDAuxSceneTeardownExceptionSiteNone = 0,
    DDAuxSceneTeardownExceptionSitePrivateViewTeardown = 1,
    DDAuxSceneTeardownExceptionSiteUnprotectedRange = 2,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL auxControllerIvarWasAlreadyClearedBeforeCatch;
    BOOL shouldSkipRemainingPrivateTeardown;
    BOOL shouldContinueAuxStateReset;
    BOOL shouldRefreshAuxGenerationState;
    BOOL retainedViewReleaseCouldBeBypassed;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDAuxSceneTeardownExceptionOutcome;

typedef NS_ENUM(NSInteger, DDAuxSceneCreationExceptionSite) {
    DDAuxSceneCreationExceptionSiteNone = 0,
    DDAuxSceneCreationExceptionSiteProtectedCreationWork = 1,
    DDAuxSceneCreationExceptionSiteProtectedFailureTeardown = 2,
    DDAuxSceneCreationExceptionSiteCatchTeardown = 3,
    DDAuxSceneCreationExceptionSiteUnprotectedRange = 4,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldInvokeTeardownFromCatch;
    BOOL shouldRetryTeardownFromCatch;
    BOOL shouldSkipRemainingCreation;
    BOOL shouldReturnNilScene;
    BOOL shouldEndActiveCatchBeforeResumeUnwind;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDAuxSceneCreationExceptionOutcome;

typedef NS_ENUM(NSInteger, DDDegradeSlotExceptionSite) {
    DDDegradeSlotExceptionSiteNone = 0,
    DDDegradeSlotExceptionSitePrivateControllerTeardown = 1,
    DDDegradeSlotExceptionSiteUnprotectedRange = 2,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldSkipRemainingPrivateTeardown;
    BOOL controllerIvarClearStillPendingAtCatch;
    BOOL shouldContinueControllerIvarClear;
    BOOL shouldContinueHostedBidReset;
    BOOL shouldContinuePlaceholderCreation;
    BOOL retainedViewReleaseCouldBeBypassed;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDDegradeSlotExceptionOutcome;

typedef NS_ENUM(NSInteger, DDSpikeCreateSlotExceptionSite) {
    DDSpikeCreateSlotExceptionSiteNone = 0,
    DDSpikeCreateSlotExceptionSitePreControllerPrivateWork = 1,
    DDSpikeCreateSlotExceptionSitePostControllerPrivateWork = 2,
    DDSpikeCreateSlotExceptionSitePrivateDeviceDecoration = 3,
    DDSpikeCreateSlotExceptionSitePlaceholderCreationAfterApplicationMiss = 4,
    DDSpikeCreateSlotExceptionSiteFailureDegradeBeforeControllerStore = 5,
    DDSpikeCreateSlotExceptionSiteFailureDegradeAfterControllerStore = 6,
    DDSpikeCreateSlotExceptionSiteCatchDegrade = 7,
    DDSpikeCreateSlotExceptionSiteUnprotectedRange = 8,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL spikeInProgressFlagWasAlreadySet;
    BOOL hostedBidAndNativeStateWereCommittedBeforeProtectedRange;
    BOOL controllerIvarHadBeenStoredBeforeProtectedCall;
    BOOL shouldRouteThroughDegradeFromCatch;
    BOOL shouldRetryDegradeFromCatch;
    BOOL shouldSkipRemainingPrivateDecoration;
    BOOL shouldContinueReturningMainView;
    BOOL shouldReturnDegradedResult;
    BOOL shouldEndActiveCatchBeforeResumeUnwind;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDSpikeCreateSlotExceptionOutcome;

typedef NS_ENUM(NSInteger, DDCNABBuildSceneHostExceptionSite) {
    DDCNABBuildSceneHostExceptionSiteNone = 0,
    DDCNABBuildSceneHostExceptionSitePreControllerPrivateWork = 1,
    DDCNABBuildSceneHostExceptionSitePostControllerPrivateWork = 2,
    DDCNABBuildSceneHostExceptionSitePrivateDeviceDecoration = 3,
    DDCNABBuildSceneHostExceptionSiteFailureReset = 4,
    DDCNABBuildSceneHostExceptionSiteCatchReset = 5,
    DDCNABBuildSceneHostExceptionSiteUnprotectedRange = 6,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL controllerIvarHadBeenStoredBeforeProtectedCall;
    BOOL shouldInvokeResetHostingStateFromCatch;
    BOOL shouldRetryResetHostingStateFromCatch;
    BOOL shouldForceNilReturn;
    BOOL retainedIntermediateReleasesCouldBeBypassed;
    BOOL shouldSkipRemainingPrivateDecoration;
    BOOL mainViewHadBeenAcquiredBeforeProtectedCall;
    BOOL shouldContinueReturningMainView;
    BOOL retainedDeviceControllerReleaseCouldBeBypassed;
    BOOL shouldEndActiveCatchBeforeResumeUnwind;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDCNABBuildSceneHostExceptionOutcome;

typedef NS_ENUM(NSInteger, DDEvictFromPhoneExceptionSite) {
    DDEvictFromPhoneExceptionSiteNone = 0,
    DDEvictFromPhoneExceptionSiteWorkspaceClassLookup = 1,
    DDEvictFromPhoneExceptionSiteWorkspacePreparation = 2,
    DDEvictFromPhoneExceptionSiteTransitionRequestCreation = 3,
    DDEvictFromPhoneExceptionSiteApplicationContextPreparation = 4,
    DDEvictFromPhoneExceptionSiteApplicationContextMutation = 5,
    DDEvictFromPhoneExceptionSiteProtectedFallbackInvocation = 6,
    DDEvictFromPhoneExceptionSiteCompletionSelectorProbe = 7,
    DDEvictFromPhoneExceptionSiteCompletionHandlerInstall = 8,
    DDEvictFromPhoneExceptionSiteExecuteTransitionOrFallback = 9,
    DDEvictFromPhoneExceptionSiteEarlyProbeOrBypassCleanup = 10,
    DDEvictFromPhoneExceptionSiteCatchFallback = 11,
    DDEvictFromPhoneExceptionSiteUnprotectedRange = 12,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldInvokeFallbackWrapperFromCatch;
    BOOL shouldSkipRemainingEvictionWork;
    BOOL shouldContinueFinalCleanup;
    BOOL protectedFallbackThrowOccursAfterOneShotGateSet;
    BOOL catchFallbackMayBeSuppressedByOneShotGate;
    BOOL completionHandlerMayAlreadyBeInstalled;
    BOOL timeoutFallbackMayAlreadyBeScheduled;
    BOOL transitionExecutionMayHaveStarted;
    BOOL retainedTransitionIntermediatesReleaseCouldBeBypassed;
    BOOL resumeUnwindRunsByrefCleanup;
    BOOL shouldEndActiveCatchBeforeResumeUnwind;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDEvictFromPhoneExceptionOutcome;

typedef NS_ENUM(NSInteger, DDSplitHostGeometryExceptionSite) {
    DDSplitHostGeometryExceptionSiteNone = 0,
    DDSplitHostGeometryExceptionSiteHostFrameSetter = 1,
    DDSplitHostGeometryExceptionSiteSplitCenterSetter = 2,
    DDSplitHostGeometryExceptionSiteGapRead = 3,
    DDSplitHostGeometryExceptionSiteFinalGeometrySync = 4,
    DDSplitHostGeometryExceptionSiteUnprotectedRange = 5,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldSkipRemainingGeometryWork;
    BOOL shouldContinueRetainedViewCleanup;
    BOOL hostFrameDefinitelyAppliedBeforeProtectedCall;
    BOOL hostFrameCouldHaveAppliedBeforeException;
    BOOL splitCenterDefinitelyAppliedBeforeProtectedCall;
    BOOL splitCenterCouldHaveAppliedBeforeException;
    BOOL finalGeometrySyncCouldHaveStartedBeforeException;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDSplitHostGeometryExceptionOutcome;

typedef NS_ENUM(NSInteger, DDSceneLayerHostPredicateExceptionSite) {
    DDSceneLayerHostPredicateExceptionSiteNone = 0,
    DDSceneLayerHostPredicateExceptionSiteClassAndTraversalArraySetup = 1,
    DDSceneLayerHostPredicateExceptionSiteTraversalStep = 2,
    DDSceneLayerHostPredicateExceptionSiteTraversalCountRefresh = 3,
    DDSceneLayerHostPredicateExceptionSiteCandidateGeometryRead = 4,
    DDSceneLayerHostPredicateExceptionSiteUnprotectedRange = 5,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldForcePredicateFalse;
    BOOL shouldAttemptPostScanCounterDecrement;
    BOOL shouldSkipRotationRebuildEvaluation;
    BOOL shouldContinueInputCleanup;
    BOOL shouldReturnFalse;
    BOOL retainedRootViewReleaseCouldBeBypassed;
    BOOL retainedTraversalArrayReleaseCouldBeBypassed;
    BOOL retainedCurrentCandidateReleaseCouldBeBypassed;
    BOOL retainedSubviewsReleaseCouldBeBypassed;
    BOOL candidateGeometryReadCouldHaveStartedBeforeException;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDSceneLayerHostPredicateExceptionOutcome;

typedef NS_ENUM(NSInteger, DDSlideAnimationExceptionSite) {
    DDSlideAnimationExceptionSiteNone = 0,
    DDSlideAnimationExceptionSiteUIViewAnimationCall = 1,
    DDSlideAnimationExceptionSiteCatchFallbackCenterSetter = 2,
    DDSlideAnimationExceptionSiteUnprotectedRange = 3,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL slideFlagWasAlreadySet;
    BOOL oneSecondFollowupWasAlreadyScheduled;
    BOOL targetCenterWasAlreadyComputed;
    BOOL animationCouldHaveStartedBeforeException;
    BOOL shouldInvokeDirectCenterFallback;
    BOOL retainedAnimationCaptureReleaseCouldBeBypassed;
    BOOL shouldContinuePrimaryViewAndInputCleanup;
    BOOL directCenterFallbackCouldHaveAppliedBeforeException;
    BOOL shouldEndActiveCatchBeforeResumeUnwind;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDSlideAnimationExceptionOutcome;

typedef NS_ENUM(NSInteger, DDRecursiveTransparencyExceptionSite) {
    DDRecursiveTransparencyExceptionSiteNone = 0,
    DDRecursiveTransparencyExceptionSiteBackgroundColorSetup = 1,
    DDRecursiveTransparencyExceptionSiteOpaqueSetter = 2,
    DDRecursiveTransparencyExceptionSiteInitialSubviewsEnumeration = 3,
    DDRecursiveTransparencyExceptionSiteRecursiveChildStep = 4,
    DDRecursiveTransparencyExceptionSiteNextEnumerationBatch = 5,
    DDRecursiveTransparencyExceptionSiteCleanupUnwind = 6,
    DDRecursiveTransparencyExceptionSiteUnprotectedRange = 7,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldAbortRemainingTraversal;
    BOOL shouldContinueInputCleanup;
    BOOL backgroundColorDefinitelyAppliedBeforeProtectedCall;
    BOOL backgroundColorCouldHaveAppliedBeforeException;
    BOOL opaqueDefinitelyAppliedBeforeProtectedCall;
    BOOL opaqueCouldHaveAppliedBeforeException;
    BOOL retainedClearColorReleaseCouldBeBypassed;
    BOOL retainedSubviewsArrayReleaseCouldBeBypassed;
    BOOL recursiveChildExceptionCouldBeSwallowedByParent;
    BOOL recursiveChildMayHavePartiallyMutatedDescendantsBeforeException;
    BOOL priorEnumerationBatchDefinitelyCompletedBeforeProtectedCall;
    BOOL shouldResumeUnwindFromCleanup;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDRecursiveTransparencyExceptionOutcome;

typedef NS_ENUM(NSInteger, DDTopLevelTransparencyExceptionSite) {
    DDTopLevelTransparencyExceptionSiteNone = 0,
    DDTopLevelTransparencyExceptionSiteHostBackgroundColor = 1,
    DDTopLevelTransparencyExceptionSiteHostOpaqueSetter = 2,
    DDTopLevelTransparencyExceptionSiteSplitBackgroundColor = 3,
    DDTopLevelTransparencyExceptionSiteSplitOpaqueSetter = 4,
    DDTopLevelTransparencyExceptionSiteRecursiveRoot = 5,
    DDTopLevelTransparencyExceptionSiteUnprotectedRange = 6,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldReturnImmediately;
    BOOL hostBackgroundDefinitelyAppliedBeforeProtectedCall;
    BOOL hostBackgroundCouldHaveAppliedBeforeException;
    BOOL hostOpaqueDefinitelyAppliedBeforeProtectedCall;
    BOOL hostOpaqueCouldHaveAppliedBeforeException;
    BOOL splitBackgroundDefinitelyAppliedBeforeProtectedCall;
    BOOL splitBackgroundCouldHaveAppliedBeforeException;
    BOOL splitOpaqueDefinitelyAppliedBeforeProtectedCall;
    BOOL splitOpaqueCouldHaveAppliedBeforeException;
    BOOL retainedClearColorReleaseCouldBeBypassed;
    BOOL recursiveRootExceptionCouldBeSwallowedByWrapper;
    BOOL recursiveRootMayHavePartiallyMutatedSubtreeBeforeException;
    BOOL exceptionWouldPropagate;
} DDTopLevelTransparencyExceptionOutcome;

typedef NS_ENUM(NSInteger, DDCNABKeyPaneHideSymbolExceptionSite) {
    DDCNABKeyPaneHideSymbolExceptionSiteNone = 0,
    DDCNABKeyPaneHideSymbolExceptionSiteSymbolConfiguration = 1,
    DDCNABKeyPaneHideSymbolExceptionSiteSymbolImageLookup = 2,
    DDCNABKeyPaneHideSymbolExceptionSiteSymbolImageViewInit = 3,
    DDCNABKeyPaneHideSymbolExceptionSiteManualFallbackUnprotected = 4,
    DDCNABKeyPaneHideSymbolExceptionSiteOtherUnprotectedRange = 5,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldSkipRemainingSymbolPath;
    BOOL shouldContinueManualChevronFallback;
    BOOL symbolConfigurationDefinitelyRetainedBeforeProtectedCall;
    BOOL symbolImageDefinitelyRetainedBeforeProtectedCall;
    BOOL retainedSymbolConfigurationReleaseCouldBeBypassed;
    BOOL retainedSymbolImageReleaseCouldBeBypassed;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDCNABKeyPaneHideSymbolExceptionOutcome;

typedef NS_ENUM(NSInteger, DDKeyPaneHideGapExceptionSite) {
    DDKeyPaneHideGapExceptionSiteNone = 0,
    DDKeyPaneHideGapExceptionSiteFileRead = 1,
    DDKeyPaneHideGapExceptionSiteLengthRead = 2,
    DDKeyPaneHideGapExceptionSiteUTF8StringRead = 3,
    DDKeyPaneHideGapExceptionSiteNumericParse = 4,
    DDKeyPaneHideGapExceptionSiteRetainAutoreleaseGap = 5,
    DDKeyPaneHideGapExceptionSiteOtherUnprotectedRange = 6,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldReturnDefaultGap;
    double defaultGap;
    BOOL retainedStringDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedStringReleaseCouldBeBypassed;
    BOOL retainAutoreleaseCouldHaveStartedBeforeException;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDKeyPaneHideGapExceptionOutcome;

typedef NS_ENUM(NSInteger, DDDisplayScaleCapExceptionSite) {
    DDDisplayScaleCapExceptionSiteNone = 0,
    DDDisplayScaleCapExceptionSiteDisplayAcquisition = 1,
    DDDisplayScaleCapExceptionSiteDisplayClassLookup = 2,
    DDDisplayScaleCapExceptionSiteConfigurationConstruction = 3,
    DDDisplayScaleCapExceptionSiteScaleCapabilityProbe = 4,
    DDDisplayScaleCapExceptionSiteScaleGetter = 5,
    DDDisplayScaleCapExceptionSiteWindowBoundsRead = 6,
    DDDisplayScaleCapExceptionSitePixelSizeCapabilityProbe = 7,
    DDDisplayScaleCapExceptionSitePixelSizeGetter = 8,
    DDDisplayScaleCapExceptionSiteUnprotectedRange = 9,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldReturnOriginalBoundsDimension;
    BOOL shouldSkipDisplayScaleCap;
    BOOL shouldContinueInputCleanup;
    BOOL retainedDisplayDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedDisplayReleaseCouldBeBypassed;
    BOOL retainedConfigurationDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedConfigurationReleaseCouldBeBypassed;
    BOOL temporaryConfigurationConstructionCouldHaveStartedBeforeException;
    BOOL temporaryConfigurationReleaseCouldBeBypassed;
    BOOL retainedWindowDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedWindowReleaseCouldBeBypassed;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDDisplayScaleCapExceptionOutcome;

typedef NS_ENUM(NSInteger, DDPropertyListWriterExceptionSite) {
    DDPropertyListWriterExceptionSiteNone = 0,
    DDPropertyListWriterExceptionSiteSerialization = 1,
    DDPropertyListWriterExceptionSiteDataWrite = 2,
    DDPropertyListWriterExceptionSiteFileManagerAcquisition = 3,
    DDPropertyListWriterExceptionSitePermissionsDictionaryConstruction = 4,
    DDPropertyListWriterExceptionSiteSetAttributes = 5,
    DDPropertyListWriterExceptionSiteIntermediateCleanupUnwind = 6,
    DDPropertyListWriterExceptionSiteFinalArgumentCleanupUnwind = 7,
    DDPropertyListWriterExceptionSiteUnprotectedRange = 8,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldReturnFalse;
    BOOL shouldReturnTrueAfterSuccessfulWrite;
    BOOL dataWriteDefinitelySucceededBeforeProtectedCall;
    BOOL retainedDataDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedDataReleaseCouldBeBypassed;
    BOOL shouldContinueRetainedDataCleanup;
    BOOL temporaryFileManagerAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryFileManagerReleaseCouldBeBypassed;
    BOOL retainedFileManagerDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedFileManagerReleaseCouldBeBypassed;
    BOOL temporaryPermissionsDictionaryConstructionCouldHaveStartedBeforeException;
    BOOL temporaryPermissionsDictionaryReleaseCouldBeBypassed;
    BOOL retainedPermissionsDictionaryDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedPermissionsDictionaryReleaseCouldBeBypassed;
    BOOL fileAttributesCouldHaveAppliedBeforeException;
    BOOL shouldContinueFinalArgumentCleanup;
    BOOL shouldResumeUnwindFromCleanup;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDPropertyListWriterExceptionOutcome;

typedef NS_ENUM(NSInteger, DDKeyPaneHostConstructionExceptionSite) {
    DDKeyPaneHostConstructionExceptionSiteNone = 0,
    DDKeyPaneHostConstructionExceptionSiteOuterViewBackgroundSetup = 1,
    DDKeyPaneHostConstructionExceptionSiteOuterViewOpaqueSetter = 2,
    DDKeyPaneHostConstructionExceptionSiteInnerViewAndSceneEmbedding = 3,
    DDKeyPaneHostConstructionExceptionSiteInnerOpaqueAndHierarchyInsertion = 4,
    DDKeyPaneHostConstructionExceptionSiteHideGapRead = 5,
    DDKeyPaneHostConstructionExceptionSiteLeftHideKeyCreation = 6,
    DDKeyPaneHostConstructionExceptionSiteRightHideKeyCreationAndInsertion = 7,
    DDKeyPaneHostConstructionExceptionSiteGeometryAndStateCommit = 8,
    DDKeyPaneHostConstructionExceptionSiteTransparencyWrapper = 9,
    DDKeyPaneHostConstructionExceptionSiteFrontingAndActivation = 10,
    DDKeyPaneHostConstructionExceptionSiteUnprotectedRange = 11,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldReturnFalse;
    BOOL shouldClearLeftKeyGlobal;
    BOOL shouldClearRightKeyGlobal;
    BOOL shouldInvokeAuxSceneTeardown;
    BOOL shouldClearOuterHostGlobal;
    BOOL shouldContinueAuxSceneAndControllerCleanup;
    BOOL shouldContinueSplitHostAndInputCleanup;
    BOOL outerViewReleaseCouldBeBypassed;
    BOOL innerViewReleaseCouldBeBypassed;
    BOOL leftKeyReleaseCouldBeBypassed;
    BOOL rightKeyReleaseCouldBeBypassed;
    BOOL temporaryColorReleaseCouldBeBypassed;
    BOOL hostHierarchyCouldHaveBeenMutatedBeforeException;
    BOOL hostHierarchyDefinitelyInsertedBeforeProtectedCall;
    BOOL keySubviewsCouldHaveBeenInsertedBeforeException;
    BOOL keySubviewsDefinitelyInsertedBeforeProtectedCall;
    BOOL allFiveViewGlobalsDefinitelyStoredBeforeProtectedCall;
    BOOL innerViewGlobalNotExplicitlyClearedByCatch;
    BOOL auxSceneGlobalNotExplicitlyClearedByCatch;
    BOOL geometrySyncCouldHaveStartedBeforeException;
    BOOL sizeAndFlagsCouldBePartiallyCommittedBeforeException;
    BOOL geometrySizeAndFlagsDefinitelyCommittedBeforeProtectedCall;
    BOOL mediaTimeAndGenerationDefinitelyCommittedBeforeProtectedCall;
    BOOL initialDelayedDispatchesDefinitelyScheduledBeforeProtectedCall;
    BOOL transparencyCouldHaveStartedBeforeException;
    BOOL transparencyWrapperDefinitelyCompletedBeforeProtectedCall;
    BOOL fourStaggeredDispatchesDefinitelyScheduledBeforeProtectedCall;
    BOOL frontingCouldHaveAppliedBeforeException;
    BOOL activationCouldHaveStartedBeforeException;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDKeyPaneHostConstructionExceptionOutcome;

typedef NS_ENUM(NSInteger, DDPropertyListReaderExceptionSite) {
    DDPropertyListReaderExceptionSiteNone = 0,
    DDPropertyListReaderExceptionSiteDataRead = 1,
    DDPropertyListReaderExceptionSitePropertyListDecode = 2,
    DDPropertyListReaderExceptionSiteDictionaryTypeCheck = 3,
    DDPropertyListReaderExceptionSiteUnprotectedRange = 4,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldReturnNil;
    BOOL shouldContinueInputCleanup;
    BOOL retainedDataDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedDataReleaseCouldBeBypassed;
    BOOL propertyListDecodeCouldHaveStartedBeforeException;
    BOOL retainedPropertyListDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedPropertyListReleaseCouldBeBypassed;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDPropertyListReaderExceptionOutcome;

typedef NS_ENUM(NSInteger, DDKeyboardLostRecoveryExceptionSite) {
    DDKeyboardLostRecoveryExceptionSiteNone = 0,
    DDKeyboardLostRecoveryExceptionSiteSharedControllerAcquisition = 1,
    DDKeyboardLostRecoveryExceptionSiteSceneSummaryAcquisition = 2,
    DDKeyboardLostRecoveryExceptionSiteUnprotectedRange = 3,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldUseFallbackSceneSummary;
    BOOL shouldContinueMarkerAndRebuildFlow;
    BOOL temporaryControllerAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryControllerReleaseCouldBeBypassed;
    BOOL retainedControllerDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedControllerReleaseCouldBeBypassed;
    BOOL temporarySceneSummaryAcquisitionCouldHaveStartedBeforeException;
    BOOL temporarySceneSummaryReleaseCouldBeBypassed;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDKeyboardLostRecoveryExceptionOutcome;

typedef NS_ENUM(NSInteger, DDCarPlayUIStatusCallbackExceptionSite) {
    DDCarPlayUIStatusCallbackExceptionSiteNone = 0,
    DDCarPlayUIStatusCallbackExceptionSiteSharedControllerAcquisition = 1,
    DDCarPlayUIStatusCallbackExceptionSiteStatusCallbackSend = 2,
    DDCarPlayUIStatusCallbackExceptionSiteUnprotectedRange = 3,
};

typedef struct {
    BOOL shouldSwallowAnyException;
    BOOL shouldReturnImmediately;
    BOOL temporaryControllerAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryControllerReleaseCouldBeBypassed;
    BOOL retainedControllerDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedControllerReleaseCouldBeBypassed;
    BOOL callbackCouldHaveAppliedSideEffectsBeforeException;
    BOOL exceptionWouldPropagate;
} DDCarPlayUIStatusCallbackExceptionOutcome;

typedef NS_ENUM(NSInteger, DDDropSplashIfOverdueExceptionSite) {
    DDDropSplashIfOverdueExceptionSiteNone = 0,
    DDDropSplashIfOverdueExceptionSiteSharedControllerAcquisition = 1,
    DDDropSplashIfOverdueExceptionSiteDropSelectorSend = 2,
    DDDropSplashIfOverdueExceptionSiteUnprotectedRange = 3,
};

typedef struct {
    BOOL shouldSwallowAnyException;
    BOOL shouldReturnImmediately;
    BOOL temporaryControllerAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryControllerReleaseCouldBeBypassed;
    BOOL retainedControllerDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedControllerReleaseCouldBeBypassed;
    BOOL dropSelectorCouldHaveAppliedSideEffectsBeforeException;
    BOOL exceptionWouldPropagate;
} DDDropSplashIfOverdueExceptionOutcome;

typedef NS_ENUM(NSInteger, DDDropServerNoticeNowExceptionSite) {
    DDDropServerNoticeNowExceptionSiteNone = 0,
    DDDropServerNoticeNowExceptionSiteSharedControllerAcquisition = 1,
    DDDropServerNoticeNowExceptionSiteDropSelectorSend = 2,
    DDDropServerNoticeNowExceptionSiteUnprotectedRange = 3,
};

typedef struct {
    BOOL shouldSwallowAnyException;
    BOOL shouldReturnImmediately;
    BOOL temporaryControllerAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryControllerReleaseCouldBeBypassed;
    BOOL retainedControllerDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedControllerReleaseCouldBeBypassed;
    BOOL dropSelectorCouldHaveAppliedSideEffectsBeforeException;
    BOOL exceptionWouldPropagate;
} DDDropServerNoticeNowExceptionOutcome;

typedef NS_ENUM(NSInteger, DDDropOverdueNoticeExceptionSite) {
    DDDropOverdueNoticeExceptionSiteNone = 0,
    DDDropOverdueNoticeExceptionSiteSharedControllerAcquisition = 1,
    DDDropOverdueNoticeExceptionSiteDropSelectorSend = 2,
    DDDropOverdueNoticeExceptionSiteUnprotectedRange = 3,
};

typedef struct {
    BOOL shouldSwallowAnyException;
    BOOL shouldReturnImmediately;
    BOOL temporaryControllerAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryControllerReleaseCouldBeBypassed;
    BOOL retainedControllerDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedControllerReleaseCouldBeBypassed;
    BOOL dropSelectorCouldHaveAppliedSideEffectsBeforeException;
    BOOL exceptionWouldPropagate;
} DDDropOverdueNoticeExceptionOutcome;

typedef NS_ENUM(NSInteger, DDNudgePresentGateExceptionSite) {
    DDNudgePresentGateExceptionSiteNone = 0,
    DDNudgePresentGateExceptionSiteSharedControllerAcquisition = 1,
    DDNudgePresentGateExceptionSiteVisibleCheck = 2,
    DDNudgePresentGateExceptionSiteLivePresentRunningCheck = 3,
    DDNudgePresentGateExceptionSiteFileManagerAcquisition = 4,
    DDNudgePresentGateExceptionSiteMarkerFileCheck = 5,
    DDNudgePresentGateExceptionSiteNudgePresentSend = 6,
    DDNudgePresentGateExceptionSiteUnprotectedRange = 7,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldReturnImmediately;
    BOOL temporaryControllerAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryControllerReleaseCouldBeBypassed;
    BOOL retainedControllerDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedControllerReleaseCouldBeBypassed;
    BOOL visibleCheckDefinitelyPassedBeforeProtectedCall;
    BOOL livePresentCheckDefinitelyReturnedFalseBeforeProtectedCall;
    BOOL temporaryFileManagerAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryFileManagerReleaseCouldBeBypassed;
    BOOL retainedFileManagerDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedFileManagerReleaseCouldBeBypassed;
    BOOL markerCheckDefinitelyCompletedBeforeProtectedCall;
    BOOL markerDefinitelyAbsentBeforeProtectedCall;
    BOOL fileManagerReleaseDefinitelyCompletedBeforeProtectedCall;
    BOOL nudgeCouldHaveAppliedSideEffectsBeforeException;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDNudgePresentGateExceptionOutcome;

typedef NS_ENUM(NSInteger, DDDisplayBoundsFallbackExceptionSite) {
    DDDisplayBoundsFallbackExceptionSiteNone = 0,
    DDDisplayBoundsFallbackExceptionSiteMainScreenAcquisition = 1,
    DDDisplayBoundsFallbackExceptionSiteBoundsRead = 2,
    DDDisplayBoundsFallbackExceptionSiteUnprotectedRange = 3,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldReturnZero;
    BOOL shouldIgnoreBoundsResult;
    BOOL boundsDimensionsDefinitelyUncommittedBeforeCatch;
    BOOL temporaryScreenAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryScreenReleaseCouldBeBypassed;
    BOOL retainedScreenDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedScreenReleaseCouldBeBypassed;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDDisplayBoundsFallbackExceptionOutcome;

typedef NS_ENUM(NSInteger, DDLayoutAreaPublishExceptionSite) {
    DDLayoutAreaPublishExceptionSiteNone = 0,
    DDLayoutAreaPublishExceptionSiteInitialRectEmptyCheck = 1,
    DDLayoutAreaPublishExceptionSiteDockSuffixLabelAppend = 2,
    DDLayoutAreaPublishExceptionSiteStatusStringFormatting = 3,
    DDLayoutAreaPublishExceptionSiteStatusDedupEquality = 4,
    DDLayoutAreaPublishExceptionSiteGlobalStatusStoreUnwind = 5,
    DDLayoutAreaPublishExceptionSitePreferencesSetValue = 6,
    DDLayoutAreaPublishExceptionSitePreferencesSynchronize = 7,
    DDLayoutAreaPublishExceptionSiteDarwinCenterAcquisition = 8,
    DDLayoutAreaPublishExceptionSiteNotificationNameConstruction = 9,
    DDLayoutAreaPublishExceptionSiteDarwinNotificationPost = 10,
    DDLayoutAreaPublishExceptionSiteFinalStatusCleanupUnwind = 11,
    DDLayoutAreaPublishExceptionSiteFinalLabelCleanupUnwind = 12,
    DDLayoutAreaPublishExceptionSiteUnprotectedRange = 13,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldReturnImmediately;
    BOOL temporaryLabelConstructionCouldHaveStartedBeforeException;
    BOOL temporaryLabelReleaseCouldBeBypassed;
    BOOL retainedLabelCouldBeCommittedBeforeProtectedCall;
    BOOL retainedLabelReleaseCouldBeBypassed;
    BOOL temporaryStatusStringConstructionCouldHaveStartedBeforeException;
    BOOL temporaryStatusStringReleaseCouldBeBypassed;
    BOOL retainedStatusStringDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedStatusStringReleaseCouldBeBypassed;
    BOOL globalStatusDefinitelyStoredBeforeProtectedCall;
    BOOL globalStatusCouldHaveAppliedBeforeException;
    BOOL preferencesValueDefinitelySetBeforeProtectedCall;
    BOOL preferencesValueCouldHaveAppliedBeforeException;
    BOOL preferencesSynchronizeDefinitelyCompletedBeforeProtectedCall;
    BOOL preferencesSynchronizeCouldHaveAppliedBeforeException;
    BOOL darwinCenterDefinitelyAcquiredBeforeProtectedCall;
    BOOL notificationNameDefinitelyConstructedBeforeProtectedCall;
    BOOL notificationCouldHavePostedBeforeException;
    BOOL statusStringReleaseDefinitelyCompletedBeforeProtectedCall;
    BOOL shouldResumeUnwindFromActionZero;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDLayoutAreaPublishExceptionOutcome;

typedef NS_ENUM(NSInteger, DDDisplayConfigurationPublishExceptionSite) {
    DDDisplayConfigurationPublishExceptionSiteNone = 0,
    DDDisplayConfigurationPublishExceptionSiteDisplayAcquisition = 1,
    DDDisplayConfigurationPublishExceptionSiteConfigurationClassLookup = 2,
    DDDisplayConfigurationPublishExceptionSiteConfigurationConstruction = 3,
    DDDisplayConfigurationPublishExceptionSitePixelSizeCapabilityCheck = 4,
    DDDisplayConfigurationPublishExceptionSitePixelSizeRead = 5,
    DDDisplayConfigurationPublishExceptionSiteScaleCapabilityCheck = 6,
    DDDisplayConfigurationPublishExceptionSiteScaleRead = 7,
    DDDisplayConfigurationPublishExceptionSiteBoundsCapabilityCheck = 8,
    DDDisplayConfigurationPublishExceptionSiteBoundsRead = 9,
    DDDisplayConfigurationPublishExceptionSiteFrameCapabilityCheck = 10,
    DDDisplayConfigurationPublishExceptionSiteFrameRead = 11,
    DDDisplayConfigurationPublishExceptionSiteResolutionStringFormatting = 12,
    DDDisplayConfigurationPublishExceptionSiteResolutionDedupEquality = 13,
    DDDisplayConfigurationPublishExceptionSiteQualityDedupEquality = 14,
    DDDisplayConfigurationPublishExceptionSiteResolutionPreferenceSet = 15,
    DDDisplayConfigurationPublishExceptionSiteQualityPreferenceSet = 16,
    DDDisplayConfigurationPublishExceptionSitePreferencesSynchronize = 17,
    DDDisplayConfigurationPublishExceptionSiteDarwinCenterAcquisition = 18,
    DDDisplayConfigurationPublishExceptionSiteNotificationNameConstruction = 19,
    DDDisplayConfigurationPublishExceptionSiteDarwinNotificationPost = 20,
    DDDisplayConfigurationPublishExceptionSiteUnprotectedRange = 21,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldForceFalseResult;
    BOOL shouldContinueAtDisplayBoundsFallback;
    BOOL shouldContinueAtGeometryValidityGate;
    BOOL shouldRestorePixelWidthFallbackBeforeContinuation;
    BOOL shouldKeepScaleAtZeroFallbackBeforeContinuation;
    BOOL shouldSkipScaleDerivationBeforeValidityGate;
    BOOL retainedInputDefinitelyCommittedBeforeProtectedCall;
    BOOL shouldContinueFinalInputCleanup;
    BOOL temporaryDisplayAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryDisplayReleaseCouldBeBypassed;
    BOOL retainedDisplayDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedDisplayReleaseCouldBeBypassed;
    BOOL temporaryConfigurationAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryConfigurationReleaseCouldBeBypassed;
    BOOL retainedConfigurationDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedConfigurationReleaseCouldBeBypassed;
    BOOL pixelSizeCapabilityDefinitelyPassedBeforeProtectedCall;
    BOOL scaleCapabilityDefinitelyPassedBeforeProtectedCall;
    BOOL boundsCapabilityDefinitelyPassedBeforeProtectedCall;
    BOOL boundsProbeDefinitelyCompletedBeforeProtectedCall;
    BOOL frameCapabilityDefinitelyPassedBeforeProtectedCall;
    BOOL frameDimensionsDefinitelyUncommittedBeforeCatch;
    BOOL geometryGlobalsDefinitelyCommittedBeforeProtectedCall;
    BOOL temporaryResolutionStringConstructionCouldHaveStartedBeforeException;
    BOOL temporaryResolutionStringReleaseCouldBeBypassed;
    BOOL retainedResolutionStringDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedResolutionStringReleaseCouldBeBypassed;
    BOOL retainedQualityLabelDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedQualityLabelReleaseCouldBeBypassed;
    BOOL resolutionDedupDefinitelyMatchedBeforeProtectedCall;
    BOOL resolutionGlobalDefinitelyStoredBeforeProtectedCall;
    BOOL qualityGlobalDefinitelyStoredBeforeProtectedCall;
    BOOL resolutionPreferenceDefinitelySetBeforeProtectedCall;
    BOOL resolutionPreferenceCouldHaveAppliedBeforeException;
    BOOL qualityPreferenceDefinitelySetBeforeProtectedCall;
    BOOL qualityPreferenceCouldHaveAppliedBeforeException;
    BOOL preferencesSynchronizeDefinitelyCompletedBeforeProtectedCall;
    BOOL preferencesSynchronizeCouldHaveAppliedBeforeException;
    BOOL darwinCenterDefinitelyAcquiredBeforeProtectedCall;
    BOOL notificationNameDefinitelyConstructedBeforeProtectedCall;
    BOOL notificationCouldHavePostedBeforeException;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDDisplayConfigurationPublishExceptionOutcome;

typedef NS_ENUM(NSInteger, DDDisplayChangedWrapperExceptionSite) {
    DDDisplayChangedWrapperExceptionSiteNone = 0,
    DDDisplayChangedWrapperExceptionSiteInnerDisplayConfigurationCall = 1,
    DDDisplayChangedWrapperExceptionSiteUnprotectedRange = 2,
};

typedef struct {
    BOOL shouldSwallowAnyException;
    BOOL shouldReturnImmediately;
    BOOL innerDisplayConfigurationCouldHaveAppliedSideEffectsBeforeException;
    BOOL exceptionWouldPropagate;
} DDDisplayChangedWrapperExceptionOutcome;

typedef NS_ENUM(NSInteger, DDCarPlayConnectedExceptionSite) {
    DDCarPlayConnectedExceptionSiteNone = 0,
    DDCarPlayConnectedExceptionSiteExternalDeviceClassLookup = 1,
    DDCarPlayConnectedExceptionSiteCurrentDeviceAcquisition = 2,
    DDCarPlayConnectedExceptionSiteUnprotectedRange = 3,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldReturnFalse;
    BOOL booleanResultDefinitelyUncommittedBeforeCatch;
    BOOL temporaryDeviceAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryDeviceReleaseCouldBeBypassed;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDCarPlayConnectedExceptionOutcome;

typedef NS_ENUM(NSInteger, DDShellRebuildBlockExceptionSite) {
    DDShellRebuildBlockExceptionSiteNone = 0,
    DDShellRebuildBlockExceptionSiteTeardownWindowSend = 1,
    DDShellRebuildBlockExceptionSiteBuildShellIfNeededSend = 2,
    DDShellRebuildBlockExceptionSiteUnprotectedRange = 3,
};

typedef struct {
    BOOL shouldSwallowAnyException;
    BOOL shouldReturnImmediately;
    BOOL capturedResultByteStoreWouldBeSkipped;
    BOOL teardownWindowCouldHaveAppliedSideEffectsBeforeException;
    BOOL teardownWindowDefinitelyCompletedBeforeProtectedCall;
    BOOL buildShellCouldHaveAppliedSideEffectsBeforeException;
    BOOL exceptionWouldPropagate;
} DDShellRebuildBlockExceptionOutcome;

typedef NS_ENUM(NSInteger, DDSplashFadeCompletionExceptionSite) {
    DDSplashFadeCompletionExceptionSiteNone = 0,
    DDSplashFadeCompletionExceptionSiteRemoveFromSuperview = 1,
    DDSplashFadeCompletionExceptionSiteUnprotectedRange = 2,
};

typedef struct {
    BOOL shouldSwallowAnyException;
    BOOL shouldContinueWeakOwnerAcquisition;
    BOOL ownerSlotClearCouldStillOccurAfterCatch;
    BOOL shouldContinueNudgePresent;
    BOOL shouldContinueWeakRetainedOwnerRelease;
    BOOL removeFromSuperviewCouldHaveAppliedSideEffectsBeforeException;
    BOOL exceptionWouldPropagate;
} DDSplashFadeCompletionExceptionOutcome;

typedef NS_ENUM(NSInteger, DDSplashFadeAnimationExceptionSite) {
    DDSplashFadeAnimationExceptionSiteNone = 0,
    DDSplashFadeAnimationExceptionSiteUIViewAnimationInvocation = 1,
    DDSplashFadeAnimationExceptionSiteUnprotectedRange = 2,
};

typedef struct {
    BOOL shouldResumeUnwindFromActionZero;
    BOOL exceptionWouldPropagate;
    BOOL copiedWeakCaptureDefinitelyInitializedBeforeProtectedCall;
    BOOL copiedWeakCaptureDefinitelyDestroyedBeforeResumeUnwind;
    BOOL retainedAnimationCaptureDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedAnimationCaptureReleaseCouldBeBypassed;
    BOOL retainedCompletionCaptureDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedCompletionCaptureReleaseCouldBeBypassed;
    BOOL animationCouldHaveAppliedSideEffectsBeforeException;
} DDSplashFadeAnimationExceptionOutcome;

typedef NS_ENUM(NSInteger, DDSplashPresentationExceptionSite) {
    DDSplashPresentationExceptionSiteNone = 0,
    DDSplashPresentationExceptionSiteNoSplashMarkerProbe = 1,
    DDSplashPresentationExceptionSiteContentViewSelection = 2,
    DDSplashPresentationExceptionSiteBoundsRead = 3,
    DDSplashPresentationExceptionSitePreferenceLoadAndParse = 4,
    DDSplashPresentationExceptionSiteImagePathSelectionAndProbe = 5,
    DDSplashPresentationExceptionSiteRemoveExistingSplashBeforeBuild = 6,
    DDSplashPresentationExceptionSiteSplashViewBuildAndHierarchy = 7,
    DDSplashPresentationExceptionSiteDurationReadAndParse = 8,
    DDSplashPresentationExceptionSiteRemoveExistingSplashForDisabledSelection = 9,
    DDSplashPresentationExceptionSitePostDurationDispatchPipelineUnprotected = 10,
    DDSplashPresentationExceptionSiteUnprotectedRange = 11,
};

typedef struct {
    BOOL shouldSwallowExpectedException;
    BOOL shouldReturnImmediately;
    BOOL nonmatchingTypeWouldResumeUnwind;
    BOOL nonmatchingTypeWouldUseLocalCleanupLandingBeforeResume;
    BOOL temporaryFileManagerAcquisitionCouldHaveStartedBeforeException;
    BOOL fileManagerReleaseCouldBeBypassed;
    BOOL selectedViewCouldBeCommittedBeforeException;
    BOOL selectedViewDefinitelyCommittedBeforeProtectedCall;
    BOOL selectedViewReleaseCouldBeBypassed;
    BOOL preferencesSynchronizeCouldHaveAppliedBeforeException;
    BOOL preferenceValueCouldBeCommittedBeforeException;
    BOOL preferenceValueReleaseCouldBeBypassed;
    BOOL imagePathCouldBeCommittedBeforeException;
    BOOL imagePathReleaseCouldBeBypassed;
    BOOL removeSplashCouldHaveAppliedSideEffectsBeforeException;
    BOOL splashViewCouldBeCommittedBeforeException;
    BOOL splashHierarchyCouldHaveChangedBeforeException;
    BOOL splashViewPropertiesCouldHaveAppliedBeforeException;
    BOOL globalSplashDefinitelyStoredBeforeProtectedCall;
    BOOL durationStringCouldBeCommittedBeforeException;
    BOOL deadlineDefinitelyUncommittedBeforeCatch;
    BOOL deadlineDefinitelyCommittedBeforeProtectedCall;
    BOOL weakOwnerCaptureCouldHaveBeenInitializedBeforeException;
    BOOL firstDispatchCouldHaveBeenScheduledBeforeException;
    BOOL secondDispatchCouldHaveBeenScheduledBeforeException;
    BOOL exceptionWouldPropagate;
} DDSplashPresentationExceptionOutcome;

typedef NS_ENUM(NSInteger, DDSplashOpacityTransactionExceptionSite) {
    DDSplashOpacityTransactionExceptionSiteNone = 0,
    DDSplashOpacityTransactionExceptionSiteOpacityRead = 1,
    DDSplashOpacityTransactionExceptionSiteTransactionBegin = 2,
    DDSplashOpacityTransactionExceptionSiteDisableActions = 3,
    DDSplashOpacityTransactionExceptionSiteOpacityMutation = 4,
    DDSplashOpacityTransactionExceptionSiteTransactionCommit = 5,
    DDSplashOpacityTransactionExceptionSiteUnprotectedRange = 6,
};

typedef struct {
    BOOL shouldSwallowAnyException;
    BOOL shouldReturnImmediately;
    BOOL opacityMatchDefinitelyPassedBeforeProtectedCall;
    BOOL transactionBeginCouldHaveAppliedBeforeException;
    BOOL transactionBeginDefinitelyCompletedBeforeProtectedCall;
    BOOL disableActionsCouldHaveAppliedBeforeException;
    BOOL disableActionsDefinitelyCompletedBeforeProtectedCall;
    BOOL opacityMutationCouldHaveAppliedBeforeException;
    BOOL opacityMutationDefinitelyCompletedBeforeProtectedCall;
    BOOL transactionCommitCouldHaveAppliedBeforeException;
    BOOL localTransactionCompletionWouldBeSkippedAfterCatch;
    BOOL exceptionWouldPropagate;
} DDSplashOpacityTransactionExceptionOutcome;

typedef NS_ENUM(NSInteger, DDSplashNudgePreparationExceptionSite) {
    DDSplashNudgePreparationExceptionSiteNone = 0,
    DDSplashNudgePreparationExceptionSiteTargetHiddenCheck = 1,
    DDSplashNudgePreparationExceptionSiteLivePresentRunningCheck = 2,
    DDSplashNudgePreparationExceptionSiteLayerAcquisition = 3,
    DDSplashNudgePreparationExceptionSiteLayerOpacityRead = 4,
    DDSplashNudgePreparationExceptionSiteOpacityAnimationLookup = 5,
    DDSplashNudgePreparationExceptionSiteTransactionBegin = 6,
    DDSplashNudgePreparationExceptionSiteDisableActions = 7,
    DDSplashNudgePreparationExceptionSiteOpacityMutation = 8,
    DDSplashNudgePreparationExceptionSiteTransactionCommit = 9,
    DDSplashNudgePreparationExceptionSitePostTransactionCounterAndDispatchUnprotected = 10,
    DDSplashNudgePreparationExceptionSiteUnprotectedRange = 11,
};

typedef struct {
    BOOL shouldSwallowExpectedException;
    BOOL shouldReturnImmediately;
    BOOL retainedOwnerDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedOwnerReleaseCouldBeBypassed;
    BOOL retainedTargetDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedTargetReleaseCouldBeBypassed;
    BOOL targetHiddenCheckDefinitelyReturnedFalseBeforeProtectedCall;
    BOOL ownerPresentationGateDefinitelyEnabledBeforeProtectedCall;
    BOOL livePresentRunningDefinitelyReturnedFalseBeforeProtectedCall;
    BOOL temporaryLayerAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryLayerReleaseCouldBeBypassed;
    BOOL retainedLayerDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedLayerReleaseCouldBeBypassed;
    BOOL opacityThresholdDefinitelyPassedBeforeProtectedCall;
    BOOL temporaryOpacityAnimationAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryOpacityAnimationReleaseCouldBeBypassed;
    BOOL opacityAnimationDefinitelyAbsentBeforeProtectedCall;
    BOOL transactionBeginCouldHaveAppliedBeforeException;
    BOOL transactionBeginDefinitelyCompletedBeforeProtectedCall;
    BOOL disableActionsCouldHaveAppliedBeforeException;
    BOOL disableActionsDefinitelyCompletedBeforeProtectedCall;
    BOOL opacityMutationCouldHaveAppliedBeforeException;
    BOOL opacityMutationDefinitelyCompletedBeforeProtectedCall;
    BOOL transactionCommitCouldHaveAppliedBeforeException;
    BOOL transactionCommitDefinitelyCompletedBeforeTail;
    BOOL counterCouldHaveDecrementedBeforeException;
    BOOL delayedLayerCaptureCouldHaveBeenRetainedBeforeException;
    BOOL delayedDispatchCouldHaveBeenScheduledBeforeException;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
    BOOL nonmatchingCatchTypeCouldUseCleanupLandingBeforeResume;
} DDSplashNudgePreparationExceptionOutcome;

typedef NS_ENUM(NSInteger, DDRestoreTargetsExceptionSite) {
    DDRestoreTargetsExceptionSiteNone = 0,
    DDRestoreTargetsExceptionSiteInitialTargetsProbe = 1,
    DDRestoreTargetsExceptionSiteTransactionBegin = 2,
    DDRestoreTargetsExceptionSiteDisableActions = 3,
    DDRestoreTargetsExceptionSiteEnumerationSourceAcquisition = 4,
    DDRestoreTargetsExceptionSiteEnumerationCollectionAcquisition = 5,
    DDRestoreTargetsExceptionSiteInitialEnumerationRead = 6,
    DDRestoreTargetsExceptionSiteEnumerationMutationOrTypeFilter = 7,
    DDRestoreTargetsExceptionSiteFirstOpacityRead = 8,
    DDRestoreTargetsExceptionSiteSecondOpacityRead = 9,
    DDRestoreTargetsExceptionSiteOpacityAnimationLookup = 10,
    DDRestoreTargetsExceptionSiteOpacityMutation = 11,
    DDRestoreTargetsExceptionSiteEnumerationAdvance = 12,
    DDRestoreTargetsExceptionSiteTransactionCommit = 13,
    DDRestoreTargetsExceptionSiteAnimationResultReleaseActionZero = 14,
    DDRestoreTargetsExceptionSiteRetainedLayerReleaseActionZero = 15,
    DDRestoreTargetsExceptionSiteCollectionReleaseActionZero = 16,
    DDRestoreTargetsExceptionSiteUnprotectedRange = 17,
};

typedef struct {
    BOOL shouldSwallowExpectedException;
    BOOL shouldReturnViaEpilogue;
    BOOL shouldResumeUnwind;
    BOOL transactionBeginCouldHaveAppliedBeforeException;
    BOOL transactionBeginDefinitelyCompletedBeforeProtectedCall;
    BOOL disableActionsCouldHaveAppliedBeforeException;
    BOOL disableActionsDefinitelyCompletedBeforeProtectedCall;
    BOOL finalTransactionCommitWouldBeSkippedAfterCatch;
    BOOL noFurtherTransactionCommitAttemptAfterCatch;
    BOOL temporaryTargetsAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryTargetsReleaseCouldBeBypassed;
    BOOL retainedEnumerationSourceDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedEnumerationSourceReleaseCouldBeBypassed;
    BOOL temporaryCollectionAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryCollectionReleaseCouldBeBypassed;
    BOOL retainedCollectionDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedCollectionReleaseCouldBeBypassed;
    BOOL enumerationDefinitelyStartedBeforeProtectedCall;
    BOOL retainedLayerDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedLayerReleaseCouldBeBypassed;
    BOOL firstOpacityReadDefinitelyCompletedBeforeProtectedCall;
    BOOL secondOpacityReadDefinitelyCompletedBeforeProtectedCall;
    BOOL temporaryOpacityAnimationAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryOpacityAnimationReleaseCouldBeBypassed;
    BOOL opacityAnimationDefinitelyAbsentBeforeProtectedCall;
    BOOL opacityMutationCouldHaveAppliedBeforeException;
    BOOL opacityMutationDefinitelyCompletedBeforeProtectedCall;
    BOOL transactionCommitCouldHaveAppliedBeforeException;
    BOOL actionZeroCurrentReleaseCouldHaveStartedBeforeException;
    BOOL remainingLayerReleaseCouldBeBypassed;
    BOOL remainingCollectionReleaseCouldBeBypassed;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDRestoreTargetsExceptionOutcome;

typedef NS_ENUM(NSInteger, DDTickPresenterExceptionSite) {
    DDTickPresenterExceptionSiteNone = 0,
    DDTickPresenterExceptionSiteWindowAcquisition = 1,
    DDTickPresenterExceptionSiteMissingWindowInvalidate = 2,
    DDTickPresenterExceptionSiteNoopCheck = 3,
    DDTickPresenterExceptionSiteNoopTickMaintenance = 4,
    DDTickPresenterExceptionSiteWindowLayerAcquisition = 5,
    DDTickPresenterExceptionSiteWindowHiddenCheck = 6,
    DDTickPresenterExceptionSiteWindowOpacityAnimationLookup = 7,
    DDTickPresenterExceptionSiteTargetsPresenceProbe = 8,
    DDTickPresenterExceptionSiteTargetsProviderAcquisition = 9,
    DDTickPresenterExceptionSiteTargetsCollectionAcquisition = 10,
    DDTickPresenterExceptionSiteFallbackOpacityAltGate = 11,
    DDTickPresenterExceptionSiteFallbackCollectionAcquisition = 12,
    DDTickPresenterExceptionSiteSelectedCollectionCount = 13,
    DDTickPresenterExceptionSitePhaseReadAndMutation = 14,
    DDTickPresenterExceptionSitePhaseOpacityPreparation = 15,
    DDTickPresenterExceptionSiteTransactionBegin = 16,
    DDTickPresenterExceptionSiteDisableActions = 17,
    DDTickPresenterExceptionSiteInitialEnumerationRead = 18,
    DDTickPresenterExceptionSiteEnumerationMutationOrTypeFilter = 19,
    DDTickPresenterExceptionSitePerLayerAnimationLookup = 20,
    DDTickPresenterExceptionSitePerLayerOpacityAltGate = 21,
    DDTickPresenterExceptionSiteGroupTargetsAcquisition = 22,
    DDTickPresenterExceptionSiteGroupOpacityComparison = 23,
    DDTickPresenterExceptionSiteGroupOpacityMutation = 24,
    DDTickPresenterExceptionSiteOpacityMutation = 25,
    DDTickPresenterExceptionSiteEnumerationAdvance = 26,
    DDTickPresenterExceptionSiteTransactionCommit = 27,
    DDTickPresenterExceptionSitePostCommitTicksRead = 28,
    DDTickPresenterExceptionSitePostCommitTicksMutation = 29,
    DDTickPresenterExceptionSiteAnimationResultReleaseActionZero = 30,
    DDTickPresenterExceptionSiteGroupTargetsReleaseActionZero = 31,
    DDTickPresenterExceptionSiteRetainedLayerReleaseActionZero = 32,
    DDTickPresenterExceptionSiteEnumerationCollectionReleaseActionZero = 33,
    DDTickPresenterExceptionSiteFinalSelectedCollectionReleaseActionZero = 34,
    DDTickPresenterExceptionSiteFinalWindowLayerReleaseActionZero = 35,
    DDTickPresenterExceptionSiteFinalWindowReleaseActionZero = 36,
    DDTickPresenterExceptionSiteFinalTimerReleaseActionZero = 37,
    DDTickPresenterExceptionSiteUnprotectedRange = 38,
};

typedef struct {
    BOOL shouldSwallowExpectedException;
    BOOL shouldContinueFinalTimerCleanup;
    BOOL shouldResumeUnwind;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
    BOOL exceptionWouldPropagate;
    BOOL retainedTimerDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedTimerReleaseCouldBeBypassed;
    BOOL timerInvalidateCouldHaveAppliedBeforeException;
    BOOL ticksMutationCouldHaveAppliedBeforeException;
    BOOL temporaryWindowAcquisitionCouldHaveStartedBeforeException;
    BOOL retainedWindowDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedWindowReleaseCouldBeBypassed;
    BOOL temporaryWindowLayerAcquisitionCouldHaveStartedBeforeException;
    BOOL retainedWindowLayerDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedWindowLayerReleaseCouldBeBypassed;
    BOOL temporaryGateAnimationAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryGateAnimationReleaseCouldBeBypassed;
    BOOL temporaryTargetsAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryTargetsReleaseCouldBeBypassed;
    BOOL temporaryTargetsProviderAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryTargetsProviderReleaseCouldBeBypassed;
    BOOL retainedTargetsProviderDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedTargetsProviderReleaseCouldBeBypassed;
    BOOL temporarySelectedCollectionAcquisitionCouldHaveStartedBeforeException;
    BOOL temporarySelectedCollectionReleaseCouldBeBypassed;
    BOOL selectedCollectionDefinitelyCommittedBeforeProtectedCall;
    BOOL selectedCollectionReleaseCouldBeBypassed;
    BOOL phaseMutationCouldHaveAppliedBeforeException;
    BOOL phaseMutationDefinitelyCompletedBeforeProtectedCall;
    BOOL transactionBeginCouldHaveAppliedBeforeException;
    BOOL transactionBeginDefinitelyCompletedBeforeProtectedCall;
    BOOL disableActionsCouldHaveAppliedBeforeException;
    BOOL disableActionsDefinitelyCompletedBeforeProtectedCall;
    BOOL enumerationCollectionRetainDefinitelyCommittedBeforeProtectedCall;
    BOOL enumerationCollectionReleaseCouldBeBypassed;
    BOOL retainedLayerDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedLayerReleaseCouldBeBypassed;
    BOOL temporaryOpacityAnimationAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryOpacityAnimationReleaseCouldBeBypassed;
    BOOL opacityAnimationDefinitelyAbsentBeforeProtectedCall;
    BOOL temporaryGroupTargetsAcquisitionCouldHaveStartedBeforeException;
    BOOL temporaryGroupTargetsReleaseCouldBeBypassed;
    BOOL retainedGroupTargetsDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedGroupTargetsReleaseCouldBeBypassed;
    BOOL groupOpacityMutationCouldHaveAppliedBeforeException;
    BOOL opacityMutationCouldHaveAppliedBeforeException;
    BOOL transactionCommitCouldHaveAppliedBeforeException;
    BOOL transactionCommitDefinitelyCompletedBeforeProtectedCall;
    BOOL actionZeroCurrentReleaseCouldHaveStartedBeforeException;
} DDTickPresenterExceptionOutcome;

typedef NS_ENUM(NSInteger, DDKeyPaneCenterAdjustmentExceptionSite) {
    DDKeyPaneCenterAdjustmentExceptionSiteNone = 0,
    DDKeyPaneCenterAdjustmentExceptionSiteGeometryHelpers = 1,
    DDKeyPaneCenterAdjustmentExceptionSiteCenterGetter = 2,
    DDKeyPaneCenterAdjustmentExceptionSiteCenterSetter = 3,
    DDKeyPaneCenterAdjustmentExceptionSiteUnprotectedRange = 4,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldSkipRemainingGeometryWork;
    BOOL shouldContinueFinalRetainedViewCleanup;
    BOOL preGeometryCallbackDefinitelyCompletedBeforeProtectedCall;
    BOOL retainedViewDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedViewReleaseCouldBeBypassed;
    BOOL centerGetterDefinitelyCompletedBeforeProtectedCall;
    BOOL centerCouldHaveAppliedBeforeException;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDKeyPaneCenterAdjustmentExceptionOutcome;

typedef NS_ENUM(NSInteger, DDKeyPaneRectangleForwardExceptionSite) {
    DDKeyPaneRectangleForwardExceptionSiteNone = 0,
    DDKeyPaneRectangleForwardExceptionSiteCandidateGeometryHelper = 1,
    DDKeyPaneRectangleForwardExceptionSiteCandidateNullCheck = 2,
    DDKeyPaneRectangleForwardExceptionSiteUnprotectedRange = 3,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldForwardOriginalCallerRectangle;
    BOOL shouldSkipCandidateRectangleAdoption;
    BOOL shouldSkipGeometryCounterDecrement;
    BOOL shouldInvokeForwardCallback;
    BOOL shouldContinueFinalInputCleanup;
    BOOL retainedInputDefinitelyCommittedBeforeProtectedCall;
    BOOL candidateRectangleDefinitelyAcquiredBeforeProtectedCall;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDKeyPaneRectangleForwardExceptionOutcome;

typedef NS_ENUM(NSInteger, DDKeyPaneCenterForwardExceptionSite) {
    DDKeyPaneCenterForwardExceptionSiteNone = 0,
    DDKeyPaneCenterForwardExceptionSitePreGeometryHelper = 1,
    DDKeyPaneCenterForwardExceptionSiteCandidateGeometryHelper = 2,
    DDKeyPaneCenterForwardExceptionSiteCandidateNullCheck = 3,
    DDKeyPaneCenterForwardExceptionSiteCandidateMidX = 4,
    DDKeyPaneCenterForwardExceptionSiteCandidateMidY = 5,
    DDKeyPaneCenterForwardExceptionSiteUnprotectedRange = 6,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldForwardOriginalCallerCenter;
    BOOL shouldSkipCandidateCenterAdoption;
    BOOL shouldSkipGeometryCounterDecrement;
    BOOL shouldInvokeCenterForwardCallback;
    BOOL shouldContinueFinalRetainedInputCleanup;
    BOOL retainedInputDefinitelyCommittedBeforeProtectedCall;
    BOOL retainedInputReleaseCouldBeBypassed;
    BOOL candidateRectangleDefinitelyAcquiredBeforeProtectedCall;
    BOOL candidateNullCheckDefinitelyCompletedBeforeProtectedCall;
    BOOL candidateMidXDefinitelyComputedBeforeProtectedCall;
    BOOL exceptionWouldPropagate;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDKeyPaneCenterForwardExceptionOutcome;

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldReturnNilValue;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDStringSelectorExceptionOutcome;

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldReturnFalse;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDFrontmostPhoneIdentityExceptionOutcome;

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldContinueCleanupAfterCatch;
} DDActivatingEntitySetterExceptionOutcome;

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldContinueCleanupAfterCatch;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDHostUIAppRequestExceptionOutcome;

typedef NS_ENUM(NSInteger, DDAVCSceneHandleUpdateKind) {
    DDAVCSceneHandleUpdateNone = 0,
    DDAVCSceneHandleUpdateHostSlot = 1,
    DDAVCSceneHandleUpdateAux = 2,
};

typedef struct {
    DDAVCSceneHandleUpdateKind kind;
    NSInteger slotIndex;
    DDHostSlotSize targetSize;
    BOOL shouldAttemptGeneralCounterDecrement;
    BOOL shouldReadSceneSettingsForAux;
} DDAVCSceneHandleUpdateDecision;

typedef struct {
    BOOL shouldCallOriginal;
    BOOL shouldSuppressOriginal;
    BOOL shouldIncrementSuppressionCount;
    uint64_t nextSuppressionCount;
} DDAVCSceneHandleCallbackDecision;

typedef struct {
    BOOL shouldResetAttemptCount;
    NSInteger nextAttemptCount;
    BOOL shouldRaiseGeneralCounterFloor;
    NSInteger nextGeneralCounter;
    BOOL shouldProbePrivateScene;
    BOOL shouldRequestPrivateSceneUpdate;
    NSInteger slotIndex;
    DDHostSlotSize targetSize;
} DDHostSlotResizePrivateFollowup;

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldContinuePostPublishFollowup;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDHostSlotResizePublishExceptionOutcome;

typedef struct {
    NSInteger orientation;
    DDHostSlotSize frameSize;
    BOOL foreground;
} DDSceneSettingsSnapshot;

typedef struct {
    DDHostSlotSize size;
    BOOL substituted;
    BOOL shouldAttemptSuccessCounterDecrement;
    NSInteger nextSuccessCounter;
} DDSceneCallbackSizeRewrite;

typedef NS_ENUM(NSInteger, DDSceneCallbackExceptionSite) {
    DDSceneCallbackExceptionSiteNone = 0,
    DDSceneCallbackExceptionSiteRouteEligibility = 1,
    DDSceneCallbackExceptionSiteNativeSizeResolution = 2,
    DDSceneCallbackExceptionSiteOriginalCallback = 3,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldCallOriginalAfterCatch;
    BOOL shouldIncrementDiagnosticCount;
    uint64_t nextDiagnosticCount;
} DDSceneCallbackExceptionOutcome;

typedef NS_ENUM(NSInteger, DDSceneDestroyDecisionKind) {
    DDSceneDestroyDecisionNone = 0,
    DDSceneDestroyDecisionAuxDestroyedNotice = 1,
    DDSceneDestroyDecisionClearHostSlot = 2,
    DDSceneDestroyDecisionDismissHost = 3,
};

typedef struct {
    DDSceneDestroyDecisionKind kind;
    NSInteger slotIndex;
} DDSceneDestroyDecision;

typedef NS_ENUM(NSInteger, DDToAppsYieldDecisionKind) {
    DDToAppsYieldDecisionNone = 0,
    DDToAppsYieldDecisionYieldThenCallOriginal = 1,
    DDToAppsYieldDecisionSwallowOriginal = 2,
};

typedef struct {
    DDToAppsYieldDecisionKind kind;
    NSInteger slotIndex;
} DDToAppsYieldDecision;

typedef NS_ENUM(NSInteger, DDToAppsYieldExceptionSite) {
    DDToAppsYieldExceptionSiteNone = 0,
    DDToAppsYieldExceptionSitePreYieldRouting = 1,
    DDToAppsYieldExceptionSiteDismissSideEffect = 2,
    DDToAppsYieldExceptionSiteDisconnectSideEffect = 3,
    DDToAppsYieldExceptionSiteHideSideEffect = 4,
    DDToAppsYieldExceptionSiteYieldLogSideEffect = 5,
    DDToAppsYieldExceptionSiteOriginalCallback = 6,
    DDToAppsYieldExceptionSiteCleanup = 7,
};

typedef NS_ENUM(NSInteger, DDToAppsYieldExceptionContinuation) {
    DDToAppsYieldExceptionContinuationNone = 0,
    DDToAppsYieldExceptionContinuationCallOriginal = 1,
    DDToAppsYieldExceptionContinuationContinueYieldSideEffects = 2,
    DDToAppsYieldExceptionContinuationContinueYieldCleanup = 3,
    DDToAppsYieldExceptionContinuationCleanupReturn = 4,
    DDToAppsYieldExceptionContinuationResumeUnwind = 5,
};

typedef struct {
    BOOL shouldClear;
    NSInteger flagValue;
    NSInteger settingIndex;
} DDOtherSettingsFlagClearDecision;

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldSkipRemainingFlagClear;
    BOOL shouldContinueCleanup;
} DDOtherSettingsFlagClearExceptionOutcome;

typedef struct {
    BOOL withinBudget;
    BOOL shouldReadReason;
    uint64_t nextProbeCount;
} DDExceptionReasonProbeDecision;

typedef struct {
    BOOL shouldSwallowException;
    DDToAppsYieldExceptionContinuation continuation;
    BOOL yieldInProgressWouldRemainSet;
    BOOL shouldApplyReasonProbeDecision;
    BOOL probeExceptionWouldResumeUnwind;
    DDExceptionReasonProbeDecision reasonProbeDecision;
} DDToAppsYieldExceptionOutcome;

typedef NS_ENUM(NSInteger, DDSceneOrientationExceptionSite) {
    DDSceneOrientationExceptionSiteNone = 0,
    DDSceneOrientationExceptionSiteDecisionPath = 1,
    DDSceneOrientationExceptionSiteOriginalCallback = 2,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldCallOriginalAfterCatch;
    BOOL shouldApplyReasonProbeDecision;
    BOOL probeExceptionWouldResumeUnwind;
    BOOL shouldForceFalseResultAfterProbe;
    DDExceptionReasonProbeDecision reasonProbeDecision;
} DDSceneOrientationExceptionOutcome;

typedef NS_ENUM(NSInteger, DDSceneForegroundExceptionSite) {
    DDSceneForegroundExceptionSiteNone = 0,
    DDSceneForegroundExceptionSiteOriginalCallback = 1,
    DDSceneForegroundExceptionSiteRouteEligibility = 2,
    DDSceneForegroundExceptionSiteMutableSettingsPath = 3,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldApplyReasonProbeDecision;
    BOOL probeExceptionWouldResumeUnwind;
    BOOL shouldContinueForegroundEvaluationAfterCatch;
    BOOL shouldSkipRemainingForegroundForcing;
    DDExceptionReasonProbeDecision reasonProbeDecision;
} DDSceneForegroundExceptionOutcome;

typedef NS_ENUM(NSInteger, DDSceneDestroyExceptionSite) {
    DDSceneDestroyExceptionSiteNone = 0,
    DDSceneDestroyExceptionSitePreOriginalRouting = 1,
    DDSceneDestroyExceptionSiteOriginalCallback = 2,
    DDSceneDestroyExceptionSitePostCallbackDestroyRouting = 3,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldCallOriginalAfterCatch;
    BOOL shouldApplyReasonProbeDecision;
    BOOL probeExceptionWouldResumeUnwind;
    BOOL shouldRestoreSavedIdentityAfterCatch;
    BOOL preservesPreparedDestroyRoutingState;
    BOOL shouldContinuePreparedDestroyRoutingAfterOriginal;
    BOOL exceptionWouldResumeUnwind;
    DDExceptionReasonProbeDecision reasonProbeDecision;
} DDSceneDestroyExceptionOutcome;

typedef NS_ENUM(NSInteger, DDAVCSceneHandleExceptionSite) {
    DDAVCSceneHandleExceptionSiteNone = 0,
    DDAVCSceneHandleExceptionSiteInitialSceneLookup = 1,
    DDAVCSceneHandleExceptionSiteUpdateRouting = 2,
    DDAVCSceneHandleExceptionSiteSuppressionDecision = 3,
    DDAVCSceneHandleExceptionSiteOriginalCallback = 4,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldSkipRemainingUpdateRouting;
    BOOL shouldContinueSuppressionEvaluationAfterCatch;
    BOOL shouldCallOriginalAfterCatch;
    BOOL shouldApplyReasonProbeDecision;
    BOOL probeExceptionWouldResumeUnwind;
    DDExceptionReasonProbeDecision reasonProbeDecision;
} DDAVCSceneHandleExceptionOutcome;

typedef NS_ENUM(NSInteger, DDPrivateIvarWriteWidth) {
    DDPrivateIvarWriteWidthUnsupported = 0,
    DDPrivateIvarWriteWidthByte = 1,
    DDPrivateIvarWriteWidthWord = 2,
    DDPrivateIvarWriteWidthDWord = 4,
    DDPrivateIvarWriteWidthQWord = 8,
};

typedef struct {
    BOOL shouldWrite;
    BOOL shouldRecordUnsupportedType;
    DDPrivateIvarWriteWidth writeWidth;
} DDPrivateIntegerIvarWritePlan;

typedef struct {
    BOOL shouldReadObject;
    BOOL shouldRecordUnsupportedType;
} DDPrivateObjectIvarAccessPlan;

typedef NS_ENUM(NSInteger, DDPrivateSceneIvarAction) {
    DDPrivateSceneIvarActionNone = 0,
    DDPrivateSceneIvarActionWrite = 1,
    DDPrivateSceneIvarActionRecordUnsupported = 2,
};

typedef struct {
    DDPrivateSceneIvarAction frameAction;
    DDPrivateSceneIvarAction foregroundAction;
    DDHostSlotSize frameSize;
    BOOL foregroundValue;
    BOOL shouldAttemptFailureBudgetDecrement;
} DDSceneSettingsPrivateIvarPlan;

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldSkipRemainingPrivateMutation;
    BOOL shouldSkipFailureBudgetDecrement;
    BOOL shouldReturnThroughNormalCleanup;
} DDSceneSettingsPrivateIvarExceptionOutcome;

typedef NS_ENUM(NSInteger, DDFBSUpdateExceptionSite) {
    DDFBSUpdateExceptionSiteNone = 0,
    DDFBSUpdateExceptionSitePreSettingsPreparation = 1,
    DDFBSUpdateExceptionSiteSceneSettingsPath = 2,
    DDFBSUpdateExceptionSiteMutableSettingsPath = 3,
    DDFBSUpdateExceptionSiteRoutingDecisionOrExecution = 4,
    DDFBSUpdateExceptionSiteOriginalCallback = 5,
};

typedef NS_ENUM(NSInteger, DDFBSUpdateExceptionContinuation) {
    DDFBSUpdateExceptionContinuationNone = 0,
    DDFBSUpdateExceptionContinuationContinueMutableSettings = 1,
    DDFBSUpdateExceptionContinuationContinuePostSettingsRouting = 2,
    DDFBSUpdateExceptionContinuationCallOriginal = 3,
    DDFBSUpdateExceptionContinuationCleanupReturn = 4,
};

typedef struct {
    BOOL shouldSwallowException;
    DDFBSUpdateExceptionContinuation continuation;
    BOOL shouldApplyReasonProbeDecision;
    BOOL probeExceptionWouldResumeUnwind;
    DDExceptionReasonProbeDecision reasonProbeDecision;
} DDFBSUpdateExceptionOutcome;

typedef NS_ENUM(NSInteger, DDFBSSettingsCallbackExceptionSite) {
    DDFBSSettingsCallbackExceptionSiteNone = 0,
    DDFBSSettingsCallbackExceptionSiteCustomPath = 1,
    DDFBSSettingsCallbackExceptionSiteOriginalCallback = 2,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldCallOriginalAfterCatch;
    BOOL shouldApplyReasonProbeDecision;
    BOOL probeExceptionWouldResumeUnwind;
    BOOL shouldContinueCleanupAfterProbe;
    DDExceptionReasonProbeDecision reasonProbeDecision;
} DDFBSSettingsCallbackExceptionOutcome;

typedef NS_ENUM(NSInteger, DDFBSPresentationUpdateExceptionSite) {
    DDFBSPresentationUpdateExceptionSiteNone = 0,
    DDFBSPresentationUpdateExceptionSiteOriginalCallback = 1,
    DDFBSPresentationUpdateExceptionSiteNoPresentationUpdateFileProbe = 2,
    DDFBSPresentationUpdateExceptionSiteUpdateFrameAndTransform = 3,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldApplyReasonProbeDecision;
    BOOL probeExceptionWouldResumeUnwind;
    BOOL shouldContinuePostOriginalEvaluationAfterProbe;
    BOOL exceptionWouldResumeUnwind;
    BOOL shouldContinueCleanupAfterCatch;
    DDExceptionReasonProbeDecision reasonProbeDecision;
} DDFBSPresentationUpdateExceptionOutcome;

typedef struct {
    BOOL shouldSwallowException;
    NSInteger fallbackOrientation;
} DDCurrentInterfaceOrientationExceptionOutcome;

typedef NS_ENUM(NSInteger, DDFBSSceneSettingsUpdateReason) {
    DDFBSSceneSettingsUpdateReasonNone = 0,
    DDFBSSceneSettingsUpdateReasonSlotNotMarked = 1,
    DDFBSSceneSettingsUpdateReasonFrameWidthMismatch = 2,
    DDFBSSceneSettingsUpdateReasonOrientationMismatch = 3,
};

typedef struct {
    BOOL shouldRequestUpdate;
    DDFBSSceneSettingsUpdateReason reason;
    DDHostSlotSize targetSize;
} DDFBSSceneSettingsUpdateDecision;

typedef NS_ENUM(NSInteger, DDFBSSceneSettingsExecutorAdmissionKind) {
    DDFBSSceneSettingsExecutorAdmissionNone = 0,
    DDFBSSceneSettingsExecutorAdmissionInvalidInput = 1,
    DDFBSSceneSettingsExecutorAdmissionReentrant = 2,
    DDFBSSceneSettingsExecutorAdmissionAttemptLimit = 3,
    DDFBSSceneSettingsExecutorAdmissionCapabilityUnavailable = 4,
    DDFBSSceneSettingsExecutorAdmissionInvalidMethodSignature = 5,
    DDFBSSceneSettingsExecutorAdmissionDispatch = 6,
};

typedef NS_ENUM(NSInteger, DDFBSSceneSettingsExecutorCounterKind) {
    DDFBSSceneSettingsExecutorCounterNone = 0,
    DDFBSSceneSettingsExecutorCounterGeneralFailure = 1,
    DDFBSSceneSettingsExecutorCounterAttemptLimit = 2,
    DDFBSSceneSettingsExecutorCounterSignatureFailure = 3,
};

typedef struct {
    DDFBSSceneSettingsExecutorAdmissionKind kind;
    DDFBSSceneSettingsExecutorCounterKind counterKind;
    BOOL shouldIncrementAttemptCount;
    DDHostSlotSize targetSize;
} DDFBSSceneSettingsExecutorDecision;

typedef struct {
    BOOL shouldSetFrame;
    DDHostSlotSize frameSize;
    BOOL shouldSetInterfaceOrientation;
    NSInteger targetOrientation;
    NSInteger previousOrientation;
    BOOL shouldRecordOrientationChange;
} DDFBSSceneSettingsMutationPlan;

typedef NS_ENUM(NSInteger, DDFBSSceneSettingsMutationExceptionSite) {
    DDFBSSceneSettingsMutationExceptionSiteNone = 0,
    DDFBSSceneSettingsMutationExceptionSiteFramePath = 1,
    DDFBSSceneSettingsMutationExceptionSiteOrientationPath = 2,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL shouldContinueOrientationAfterCatch;
    BOOL shouldContinueCleanupAfterCatch;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
} DDFBSSceneSettingsMutationExceptionOutcome;

typedef NS_ENUM(NSInteger, DDFBSSceneSettingsExecutionAdmissionKind) {
    DDFBSSceneSettingsExecutionAdmissionGenerationMismatch = 0,
    DDFBSSceneSettingsExecutionAdmissionReentrant = 1,
    DDFBSSceneSettingsExecutionAdmissionInvoke = 2,
};

typedef struct {
    DDFBSSceneSettingsExecutionAdmissionKind kind;
    BOOL shouldEnterReentrantState;
} DDFBSSceneSettingsExecutionAdmission;

typedef NS_ENUM(NSInteger, DDFBSSceneSettingsInvocationCounterKind) {
    DDFBSSceneSettingsInvocationCounterNone = 0,
    DDFBSSceneSettingsInvocationCounterGeneral = 1,
    DDFBSSceneSettingsInvocationCounterOrientationChanged = 2,
    DDFBSSceneSettingsInvocationCounterException = 3,
};

typedef struct {
    BOOL shouldMarkSlot;
    NSInteger slotIndex;
    DDFBSSceneSettingsInvocationCounterKind counterKind;
    BOOL shouldAttemptCounterDecrement;
    BOOL shouldClearReentrantState;
} DDFBSSceneSettingsInvocationOutcome;

typedef NS_ENUM(NSInteger, DDFBSSceneSettingsExecutorExceptionSite) {
    DDFBSSceneSettingsExecutorExceptionSiteNone = 0,
    DDFBSSceneSettingsExecutorExceptionSiteOuterBeforeAttemptIncrement = 1,
    DDFBSSceneSettingsExecutorExceptionSiteOuterAfterAttemptIncrement = 2,
    DDFBSSceneSettingsExecutorExceptionSitePrivateInvocation = 3,
};

typedef struct {
    BOOL shouldSwallowException;
    BOOL exceptionWouldResumeUnwind;
    BOOL attemptCountWouldRemainIncremented;
    BOOL shouldMarkSlot;
    DDFBSSceneSettingsInvocationCounterKind counterKind;
    BOOL shouldDecrementExceptionCounter;
    NSInteger nextExceptionCounter;
    BOOL shouldClearReentrantState;
    BOOL shouldDisposeInvocationCaptures;
    BOOL nonmatchingCatchTypeWouldResumeUnwind;
    BOOL nonmatchingCatchTypeWouldClearReentrantState;
} DDFBSSceneSettingsExecutorExceptionOutcome;

typedef struct {
    BOOL valid;
    double boundsWidth;
    double boundsHeight;
    double scale;
    double rotationRadians;
    double centerX;
    double centerY;
} DDHostLandscapeGeometryPlan;

typedef struct {
    double frameX;
    double frameY;
    double frameWidth;
    double frameHeight;
    double windowX;
    double windowY;
    double windowWidth;
    double windowHeight;
    BOOL windowValid;
    uint8_t reserved[23];
    double carPlayWindowWidth;
    double carPlayWindowHeight;
} DDHostFrameMetrics;

FOUNDATION_EXPORT DDRole DDDetectRole(void);
FOUNDATION_EXPORT NSString *DDRoleName(DDRole role);
FOUNDATION_EXPORT NSDictionary *DDBuildKnownAppBridgeSnapshot(void);
FOUNDATION_EXPORT BOOL DDRepublishKnownAppBridgeSnapshot(NSError * _Nullable * _Nullable error);
FOUNDATION_EXPORT NSString * _Nullable DDCachedStringValue(NSString *key);
FOUNDATION_EXPORT NSArray<NSString *> *DDCachedCarPlayUIMore(void);
FOUNDATION_EXPORT BOOL DDCachedAutostartEnabled(void);
FOUNDATION_EXPORT NSInteger DDCachedFractionValue(NSString *key);
FOUNDATION_EXPORT NSInteger DDCachedFractionLayoutValue(void);
FOUNDATION_EXPORT BOOL DDReadKeyPaneEnabled(void);
FOUNDATION_EXPORT NSInteger DDReadBridgedFontFloor(void);
FOUNDATION_EXPORT NSInteger DDValidateIntegerValue(id _Nullable candidate,
                                                   NSInteger minimum,
                                                   NSInteger maximum,
                                                   NSInteger fallback,
                                                   DDIntegerValidationStatus * _Nullable status);
FOUNDATION_EXPORT NSInteger DDNormalizeIntegerSetting(NSDictionary *source,
                                                       NSString *key,
                                                       NSInteger minimum,
                                                       NSInteger maximum,
                                                       NSInteger fallback,
                                                       NSString *fixName,
                                                       NSMutableDictionary *writes,
                                                       NSMutableArray *fixes);
FOUNDATION_EXPORT BOOL DDSetAppBridgeLayout(NSInteger layout);
FOUNDATION_EXPORT BOOL DDSetCarPlayUI(NSString * _Nullable mainBundleIdentifier,
                                     id _Nullable additionalBundleIdentifiers);
FOUNDATION_EXPORT BOOL DDToggleAppBridgeAutostart(void);
FOUNDATION_EXPORT BOOL DDEvictCarPlayUIBundle(NSString *bundleIdentifier);
FOUNDATION_EXPORT NSInteger DDCountLiveSnapshotEntries(NSArray * _Nullable snapshot,
                                                       NSString * _Nullable bundleIdentifierFilter);
FOUNDATION_EXPORT BOOL DDPostDistributedNotification(NSString *name,
                                                     id _Nullable object,
                                                     NSDictionary * _Nullable userInfo);
FOUNDATION_EXPORT BOOL DDObserveDistributedNotification(NSString *name,
                                                        id observer,
                                                        SEL selector,
                                                        id _Nullable object);
FOUNDATION_EXPORT BOOL DDPostUIAppRequest(NSString * _Nullable bundleIdentifier);
FOUNDATION_EXPORT BOOL DDPostUIAppState(NSString * _Nullable bundleIdentifier,
                                       BOOL shouldBridge,
                                       NSInteger orientation,
                                       BOOL split,
                                       double displayWidth,
                                       double displayHeight);
FOUNDATION_EXPORT BOOL DDPostUIAppFontFloorState(NSString * _Nullable bundleIdentifier);
FOUNDATION_EXPORT BOOL DDPostUIAppKeyPaneState(NSString * _Nullable bundleIdentifier);
FOUNDATION_EXPORT NSDictionary *DDCurrentUIAppBridgeState(void);
FOUNDATION_EXPORT NSInteger DDReadHostOrientation(void);
FOUNDATION_EXPORT DDHostSlotSize DDResolveSingleHostMirrorSize(DDHostSlotSize renderSize,
                                                               DDHostSlotSize screenBoundsSize);
FOUNDATION_EXPORT BOOL DDParseLandscapeOverride(NSString * _Nullable text,
                                                NSInteger * _Nullable orientation,
                                                BOOL * _Nullable swap,
                                                BOOL * _Nullable cSwap,
                                                double * _Nullable rotationDegrees);
FOUNDATION_EXPORT NSInteger DDResolveSplitHostOrientationFromAcceptedOverride(NSString * _Nullable text);
FOUNDATION_EXPORT NSInteger DDResolveCoordinatedSplitHostOrientation(void);
FOUNDATION_EXPORT uint64_t DDPrepareSplitHostMirrorFromEnvironment(NSArray *bundleIdentifiers,
                                                                   const DDHostSlotSize *slotSizes,
                                                                   NSUInteger slotSizeCount,
                                                                   NSArray * _Nullable carPlayUIFlags);
FOUNDATION_EXPORT uint64_t DDPrepareSingleHostMirror(NSString * _Nullable bundleIdentifier,
                                                      DDHostSlotSize renderSize,
                                                      DDHostSlotSize screenBoundsSize);
FOUNDATION_EXPORT uint64_t DDPrepareSplitHostMirror(NSArray *bundleIdentifiers,
                                                     const DDHostSlotSize *slotSizes,
                                                     NSUInteger slotSizeCount,
                                                     NSArray * _Nullable carPlayUIFlags,
                                                     NSInteger resolvedOrientation);
FOUNDATION_EXPORT uint64_t DDUpdateHostSlotMirror(NSArray *bundleIdentifiers,
                                                  const DDHostSlotSize *slotSizes,
                                                  NSUInteger slotSizeCount,
                                                  NSArray * _Nullable carPlayUIFlags,
                                                  NSInteger orientation,
                                                  BOOL split);
FOUNDATION_EXPORT void DDResetHostSlotMirror(void);
FOUNDATION_EXPORT NSDictionary *DDCurrentHostSlotMirror(void);
FOUNDATION_EXPORT DDHostSlotSize DDApplyLandscapeSwapToSize(DDHostSlotSize size);
FOUNDATION_EXPORT DDHostLandscapeGeometryPlan DDComputeHostLandscapeGeometryPlan(NSUInteger slotIndex,
                                                                                  DDHostSlotSize nativeSize,
                                                                                  double slotX,
                                                                                  double slotY,
                                                                                  double slotWidth,
                                                                                  double slotHeight);
FOUNDATION_EXPORT BOOL DDSceneGeometryUpdatesEnabled(void);
FOUNDATION_EXPORT BOOL DDSceneSettingsHasInterfaceOrientationIvar(void);
FOUNDATION_EXPORT BOOL DDAuxSceneOrientationMutationSupported(void);
FOUNDATION_EXPORT DDAuxScenePreparation DDPrepareAuxSceneCandidate(NSString * _Nullable bundleIdentifier,
                                                                   DDHostSlotSize nativeSize,
                                                                   NSInteger requestedOrientation,
                                                                   BOOL auxControllerAlreadyExists);
FOUNDATION_EXPORT BOOL DDCommitAuxSceneMirrorAfterApplicationLookup(NSString * _Nullable bundleIdentifier,
                                                                    DDAuxScenePreparation preparation,
                                                                    BOOL applicationLookupSucceeded);
FOUNDATION_EXPORT void DDClearAuxSceneMirror(void);
FOUNDATION_EXPORT NSDictionary *DDCurrentAuxSceneMirror(void);
FOUNDATION_EXPORT DDAuxSceneSettingsPlan DDCurrentAuxSceneSettingsPlan(void);
FOUNDATION_EXPORT BOOL DDAuxSceneSettingsNeedUpdate(DDAuxSceneSettingsPlan plan,
                                                    BOOL previouslyApplied,
                                                    BOOL hasCurrentSettings,
                                                    DDHostSlotSize currentFrameSize,
                                                    NSInteger currentOrientation);
FOUNDATION_EXPORT NSArray<NSNumber *> *DDAuxCreateKickRetryDelays(void);
FOUNDATION_EXPORT BOOL DDAuxCreateKickRetriesEnabled(void);
FOUNDATION_EXPORT BOOL DDAuxCreateKickShouldRequestPrivateSceneObject(uint64_t capturedGeneration);
FOUNDATION_EXPORT DDAuxSceneSettingsAttempt DDBeginAuxSceneSettingsAttempt(BOOL settingsNeedUpdate,
                                                                          BOOL privateExecutorMethodSupported);
FOUNDATION_EXPORT BOOL DDBeginAuxSceneSettingsApply(uint64_t capturedGeneration);
FOUNDATION_EXPORT BOOL DDCompleteAuxSceneSettingsApply(uint64_t capturedGeneration);
FOUNDATION_EXPORT DDAuxSettingsMutationExceptionOutcome DDResolveAuxSettingsMutationExceptionOutcome(DDAuxSettingsMutationExceptionSite site);
FOUNDATION_EXPORT DDAuxSettingsExecutorExceptionOutcome DDResolveAuxSettingsExecutorExceptionOutcome(NSInteger currentFailureCounter);
FOUNDATION_EXPORT DDAuxSettingsPreparationExceptionOutcome DDResolveAuxSettingsPreparationExceptionOutcome(DDAuxSettingsPreparationExceptionSite site);
FOUNDATION_EXPORT BOOL DDBundleIdentifierMatchesAux(NSString * _Nullable bundleIdentifier);
FOUNDATION_EXPORT DDSceneIdentityResolutionExceptionOutcome DDResolveSceneIdentityResolutionExceptionOutcome(void);
FOUNDATION_EXPORT DDSceneResolverExceptionOutcome DDResolveSceneResolverExceptionOutcome(DDSceneResolverExceptionSite site);
FOUNDATION_EXPORT DDSceneDiagnosticSummaryExceptionOutcome DDResolveSceneDiagnosticSummaryExceptionOutcome(DDSceneDiagnosticSummaryExceptionSite site);
FOUNDATION_EXPORT DDBundleNormalizationExceptionOutcome DDResolveBundleNormalizationExceptionOutcome(DDBundleNormalizationExceptionSite site);
FOUNDATION_EXPORT DDDismissExceptionOutcome DDResolveDismissExceptionOutcome(DDDismissExceptionSite site);
FOUNDATION_EXPORT DDConvertSlotToCarPlayExceptionOutcome DDResolveConvertSlotToCarPlayExceptionOutcome(DDConvertSlotToCarPlayExceptionSite site);
FOUNDATION_EXPORT DDSpikeHostSlotsLandscapeExceptionOutcome DDResolveSpikeHostSlotsLandscapeExceptionOutcome(DDSpikeHostSlotsLandscapeExceptionSite site);
FOUNDATION_EXPORT DDAuxSceneTeardownExceptionOutcome DDResolveAuxSceneTeardownExceptionOutcome(DDAuxSceneTeardownExceptionSite site);
FOUNDATION_EXPORT DDAuxSceneCreationExceptionOutcome DDResolveAuxSceneCreationExceptionOutcome(DDAuxSceneCreationExceptionSite site);
FOUNDATION_EXPORT DDDegradeSlotExceptionOutcome DDResolveDegradeSlotExceptionOutcome(DDDegradeSlotExceptionSite site);
FOUNDATION_EXPORT DDSpikeCreateSlotExceptionOutcome DDResolveSpikeCreateSlotExceptionOutcome(DDSpikeCreateSlotExceptionSite site);
FOUNDATION_EXPORT DDCNABBuildSceneHostExceptionOutcome DDResolveCNABBuildSceneHostExceptionOutcome(DDCNABBuildSceneHostExceptionSite site);
FOUNDATION_EXPORT DDEvictFromPhoneExceptionOutcome DDResolveEvictFromPhoneExceptionOutcome(DDEvictFromPhoneExceptionSite site);
FOUNDATION_EXPORT DDSplitHostGeometryExceptionOutcome DDResolveSplitHostGeometryExceptionOutcome(DDSplitHostGeometryExceptionSite site);
FOUNDATION_EXPORT DDSceneLayerHostPredicateExceptionOutcome DDResolveSceneLayerHostPredicateExceptionOutcome(DDSceneLayerHostPredicateExceptionSite site);
FOUNDATION_EXPORT DDSlideAnimationExceptionOutcome DDResolveSlideAnimationExceptionOutcome(DDSlideAnimationExceptionSite site);
FOUNDATION_EXPORT DDRecursiveTransparencyExceptionOutcome DDResolveRecursiveTransparencyExceptionOutcome(DDRecursiveTransparencyExceptionSite site);
FOUNDATION_EXPORT DDTopLevelTransparencyExceptionOutcome DDResolveTopLevelTransparencyExceptionOutcome(DDTopLevelTransparencyExceptionSite site);
FOUNDATION_EXPORT DDCNABKeyPaneHideSymbolExceptionOutcome DDResolveCNABKeyPaneHideSymbolExceptionOutcome(DDCNABKeyPaneHideSymbolExceptionSite site);
FOUNDATION_EXPORT DDKeyPaneHideGapExceptionOutcome DDResolveKeyPaneHideGapExceptionOutcome(DDKeyPaneHideGapExceptionSite site);
FOUNDATION_EXPORT DDDisplayScaleCapExceptionOutcome DDResolveDisplayScaleCapExceptionOutcome(DDDisplayScaleCapExceptionSite site);
FOUNDATION_EXPORT DDPropertyListWriterExceptionOutcome DDResolvePropertyListWriterExceptionOutcome(DDPropertyListWriterExceptionSite site);
FOUNDATION_EXPORT DDKeyPaneHostConstructionExceptionOutcome DDResolveKeyPaneHostConstructionExceptionOutcome(DDKeyPaneHostConstructionExceptionSite site);
FOUNDATION_EXPORT DDPropertyListReaderExceptionOutcome DDResolvePropertyListReaderExceptionOutcome(DDPropertyListReaderExceptionSite site);
FOUNDATION_EXPORT DDKeyboardLostRecoveryExceptionOutcome DDResolveKeyboardLostRecoveryExceptionOutcome(DDKeyboardLostRecoveryExceptionSite site);
FOUNDATION_EXPORT DDCarPlayUIStatusCallbackExceptionOutcome DDResolveCarPlayUIStatusCallbackExceptionOutcome(DDCarPlayUIStatusCallbackExceptionSite site);
FOUNDATION_EXPORT DDDropSplashIfOverdueExceptionOutcome DDResolveDropSplashIfOverdueExceptionOutcome(DDDropSplashIfOverdueExceptionSite site);
FOUNDATION_EXPORT DDDropServerNoticeNowExceptionOutcome DDResolveDropServerNoticeNowExceptionOutcome(DDDropServerNoticeNowExceptionSite site);
FOUNDATION_EXPORT DDDropOverdueNoticeExceptionOutcome DDResolveDropOverdueNoticeExceptionOutcome(DDDropOverdueNoticeExceptionSite site);
FOUNDATION_EXPORT DDNudgePresentGateExceptionOutcome DDResolveNudgePresentGateExceptionOutcome(DDNudgePresentGateExceptionSite site);
FOUNDATION_EXPORT DDDisplayBoundsFallbackExceptionOutcome DDResolveDisplayBoundsFallbackExceptionOutcome(DDDisplayBoundsFallbackExceptionSite site);
FOUNDATION_EXPORT DDLayoutAreaPublishExceptionOutcome DDResolveLayoutAreaPublishExceptionOutcome(DDLayoutAreaPublishExceptionSite site);
FOUNDATION_EXPORT DDDisplayConfigurationPublishExceptionOutcome DDResolveDisplayConfigurationPublishExceptionOutcome(DDDisplayConfigurationPublishExceptionSite site);
FOUNDATION_EXPORT DDDisplayChangedWrapperExceptionOutcome DDResolveDisplayChangedWrapperExceptionOutcome(DDDisplayChangedWrapperExceptionSite site);
FOUNDATION_EXPORT DDCarPlayConnectedExceptionOutcome DDResolveCarPlayConnectedExceptionOutcome(DDCarPlayConnectedExceptionSite site);
FOUNDATION_EXPORT DDShellRebuildBlockExceptionOutcome DDResolveShellRebuildBlockExceptionOutcome(DDShellRebuildBlockExceptionSite site);
FOUNDATION_EXPORT DDSplashFadeCompletionExceptionOutcome DDResolveSplashFadeCompletionExceptionOutcome(DDSplashFadeCompletionExceptionSite site);
FOUNDATION_EXPORT DDSplashFadeAnimationExceptionOutcome DDResolveSplashFadeAnimationExceptionOutcome(DDSplashFadeAnimationExceptionSite site);
FOUNDATION_EXPORT DDSplashPresentationExceptionOutcome DDResolveSplashPresentationExceptionOutcome(DDSplashPresentationExceptionSite site);
FOUNDATION_EXPORT DDSplashOpacityTransactionExceptionOutcome DDResolveSplashOpacityTransactionExceptionOutcome(DDSplashOpacityTransactionExceptionSite site);
FOUNDATION_EXPORT DDSplashNudgePreparationExceptionOutcome DDResolveSplashNudgePreparationExceptionOutcome(DDSplashNudgePreparationExceptionSite site);
FOUNDATION_EXPORT DDRestoreTargetsExceptionOutcome DDResolveRestoreTargetsExceptionOutcome(DDRestoreTargetsExceptionSite site);
FOUNDATION_EXPORT DDTickPresenterExceptionOutcome DDResolveTickPresenterExceptionOutcome(DDTickPresenterExceptionSite site);
FOUNDATION_EXPORT DDKeyPaneCenterAdjustmentExceptionOutcome DDResolveKeyPaneCenterAdjustmentExceptionOutcome(DDKeyPaneCenterAdjustmentExceptionSite site);
FOUNDATION_EXPORT DDKeyPaneRectangleForwardExceptionOutcome DDResolveKeyPaneRectangleForwardExceptionOutcome(DDKeyPaneRectangleForwardExceptionSite site);
FOUNDATION_EXPORT DDKeyPaneCenterForwardExceptionOutcome DDResolveKeyPaneCenterForwardExceptionOutcome(DDKeyPaneCenterForwardExceptionSite site);
FOUNDATION_EXPORT DDStringSelectorExceptionOutcome DDResolveStringSelectorExceptionOutcome(void);
FOUNDATION_EXPORT DDFrontmostPhoneIdentityExceptionOutcome DDResolveFrontmostPhoneIdentityExceptionOutcome(void);
FOUNDATION_EXPORT DDActivatingEntitySetterExceptionOutcome DDResolveActivatingEntitySetterExceptionOutcome(void);
FOUNDATION_EXPORT DDHostUIAppRequestExceptionOutcome DDResolveHostUIAppRequestExceptionOutcome(void);
FOUNDATION_EXPORT DDSceneIdentityRoute DDResolveFBSUpdateIdentityRoute(NSString * _Nullable bundleIdentifier);
FOUNDATION_EXPORT DDSceneIdentityRoute DDResolveAVCSceneHandleIdentityRoute(NSString * _Nullable bundleIdentifier);
FOUNDATION_EXPORT DDAVCSceneHandleUpdateDecision DDResolveAVCSceneHandleUpdateDecision(NSString * _Nullable bundleIdentifier,
                                                                                      BOOL scenePresent,
                                                                                      BOOL slotSettingsMarked,
                                                                                      BOOL sceneSettingsSelectorSupported);
FOUNDATION_EXPORT DDAVCSceneHandleCallbackDecision DDResolveAVCSceneHandleCallbackDecision(NSString * _Nullable bundleIdentifier,
                                                                                           BOOL scenePresent,
                                                                                           BOOL sceneSettingsSelectorSupported,
                                                                                           BOOL settingsObjectPresent,
                                                                                           BOOL foregroundSelectorSupported,
                                                                                           BOOL isForeground,
                                                                                           uint64_t suppressionCount);
FOUNDATION_EXPORT DDHostSlotResizePrivateFollowup DDResolveHostSlotResizePrivateFollowup(NSInteger slotIndex,
                                                                                        DDHostSlotSize acceptedRawSize,
                                                                                        NSInteger attemptCount,
                                                                                        NSInteger generalCounter,
                                                                                        BOOL privateScenePresent);
FOUNDATION_EXPORT DDHostSlotResizePublishExceptionOutcome DDResolveHostSlotResizePublishExceptionOutcome(void);
FOUNDATION_EXPORT DDHostSlotSize DDResolveIdentityNativeSize(NSString * _Nullable bundleIdentifier);
FOUNDATION_EXPORT DDHostSlotSize DDResolveIdentityAdjustedSize(NSString * _Nullable bundleIdentifier);
FOUNDATION_EXPORT NSInteger DDResolveIdentityRawSettingsOrientation(NSString * _Nullable bundleIdentifier);
FOUNDATION_EXPORT BOOL DDShouldAttemptDirectInterfaceOrientationRepair(NSString * _Nullable bundleIdentifier,
                                                                      BOOL forceInterfaceOrientation);
FOUNDATION_EXPORT BOOL DDSceneSettingsSnapshotsEquivalent(DDSceneSettingsSnapshot before,
                                                          DDSceneSettingsSnapshot after);
FOUNDATION_EXPORT BOOL DDShouldClearAuxSceneSettingsDiff(BOOL settingsDiffPresent,
                                                         BOOL settingsDiffSetterSupported,
                                                         DDSceneSettingsSnapshot before,
                                                         DDSceneSettingsSnapshot after);
FOUNDATION_EXPORT DDSceneCallbackSizeRewrite DDResolveSceneCallbackSizeRewrite(NSString * _Nullable bundleIdentifier,
                                                                               DDHostSlotSize originalSize);
FOUNDATION_EXPORT DDSceneCallbackSizeRewrite DDResolveSceneCallbackSizeRewriteWithSuccessCounter(NSString * _Nullable bundleIdentifier,
                                                                                                 DDHostSlotSize originalSize,
                                                                                                 NSInteger successCounter);
FOUNDATION_EXPORT DDSceneCallbackExceptionOutcome DDResolveSceneCallbackExceptionOutcome(DDSceneCallbackExceptionSite site,
                                                                                         uint64_t diagnosticCount);
FOUNDATION_EXPORT BOOL DDResolveSceneOrientationEqualityResult(NSString * _Nullable bundleIdentifier,
                                                               NSInteger requestedOrientation,
                                                               BOOL originalResult);
FOUNDATION_EXPORT BOOL DDShouldForceMutableSceneForeground(NSString * _Nullable bundleIdentifier,
                                                           BOOL mutableSettingsClassAvailable,
                                                           BOOL settingsIsMutableApplicationSceneSettings,
                                                           BOOL foregroundSetterSupported);
FOUNDATION_EXPORT DDSceneDestroyDecision DDResolveSceneDestroyDecision(NSString * _Nullable primaryBundleIdentifier,
                                                                       NSString * _Nullable secondaryBundleIdentifier);
FOUNDATION_EXPORT DDToAppsYieldDecision DDResolveToAppsYieldDecision(NSArray<NSString *> * _Nullable destinationBundleIdentifiers,
                                                                     BOOL yieldInProgress,
                                                                     BOOL swallowOriginalCallback);
FOUNDATION_EXPORT DDToAppsYieldExceptionOutcome DDResolveToAppsYieldExceptionOutcome(DDToAppsYieldExceptionSite site,
                                                                                     uint64_t currentProbeCount,
                                                                                     BOOL reasonSelectorSupported);
FOUNDATION_EXPORT DDOtherSettingsFlagClearDecision DDResolveOtherSettingsFlagClearDecision(BOOL settingsObjectPresent,
                                                                                           BOOL otherSettingsPresent,
                                                                                           BOOL flagSetterSupported);
FOUNDATION_EXPORT DDOtherSettingsFlagClearExceptionOutcome DDResolveOtherSettingsFlagClearExceptionOutcome(void);
FOUNDATION_EXPORT DDExceptionReasonProbeDecision DDResolveExceptionReasonProbeDecision(uint64_t currentProbeCount,
                                                                                        BOOL reasonSelectorSupported);
FOUNDATION_EXPORT DDSceneOrientationExceptionOutcome DDResolveSceneOrientationExceptionOutcome(DDSceneOrientationExceptionSite site,
                                                                                                uint64_t currentProbeCount,
                                                                                                BOOL reasonSelectorSupported);
FOUNDATION_EXPORT DDSceneForegroundExceptionOutcome DDResolveSceneForegroundExceptionOutcome(DDSceneForegroundExceptionSite site,
                                                                                              uint64_t currentProbeCount,
                                                                                              BOOL reasonSelectorSupported);
FOUNDATION_EXPORT DDSceneDestroyExceptionOutcome DDResolveSceneDestroyExceptionOutcome(DDSceneDestroyExceptionSite site,
                                                                                        BOOL destroyRoutingPrepared,
                                                                                        uint64_t currentProbeCount,
                                                                                        BOOL reasonSelectorSupported);
FOUNDATION_EXPORT DDAVCSceneHandleExceptionOutcome DDResolveAVCSceneHandleExceptionOutcome(DDAVCSceneHandleExceptionSite site,
                                                                                           BOOL scenePresent,
                                                                                           uint64_t currentProbeCount,
                                                                                           BOOL reasonSelectorSupported);
FOUNDATION_EXPORT DDPrivateIntegerIvarWritePlan DDResolvePrivateIntegerIvarWritePlan(BOOL ivarFound,
                                                                                     NSInteger typeEncodingFirstByte);
FOUNDATION_EXPORT DDPrivateObjectIvarAccessPlan DDResolvePrivateObjectIvarAccessPlan(BOOL ivarFound,
                                                                                     NSInteger typeEncodingFirstByte);
FOUNDATION_EXPORT NSString *DDBuildPrivateIvarDiagnosticKey(NSString * _Nullable className,
                                                            NSString * _Nullable ivarName);
FOUNDATION_EXPORT BOOL DDShouldInsertPrivateIvarDiagnostic(BOOL alreadyRecorded);
FOUNDATION_EXPORT DDSceneSettingsPrivateIvarPlan DDResolveSceneSettingsPrivateIvarPlan(double frameWidth,
                                                                                       double frameHeight,
                                                                                       BOOL frameIvarFound,
                                                                                       NSString * _Nullable frameTypeEncoding,
                                                                                       BOOL foregroundIvarFound,
                                                                                       NSString * _Nullable foregroundTypeEncoding);
FOUNDATION_EXPORT DDSceneSettingsPrivateIvarExceptionOutcome DDResolveSceneSettingsPrivateIvarExceptionOutcome(void);
FOUNDATION_EXPORT DDFBSUpdateExceptionOutcome DDResolveFBSUpdateExceptionOutcome(DDFBSUpdateExceptionSite site,
                                                                                uint64_t currentProbeCount,
                                                                                BOOL reasonSelectorSupported);
FOUNDATION_EXPORT DDFBSSettingsCallbackExceptionOutcome DDResolveFBSSettingsCallbackExceptionOutcome(DDFBSSettingsCallbackExceptionSite site,
                                                                                                      uint64_t currentProbeCount,
                                                                                                      BOOL reasonSelectorSupported);
FOUNDATION_EXPORT DDFBSPresentationUpdateExceptionOutcome DDResolveFBSPresentationUpdateExceptionOutcome(DDFBSPresentationUpdateExceptionSite site,
                                                                                                          uint64_t currentProbeCount,
                                                                                                          BOOL reasonSelectorSupported);
FOUNDATION_EXPORT DDCurrentInterfaceOrientationExceptionOutcome DDResolveCurrentInterfaceOrientationExceptionOutcome(void);
FOUNDATION_EXPORT NSInteger DDResolveCurrentInterfaceOrientation(BOOL settingsObjectPresent,
                                                                 BOOL interfaceOrientationSelectorSupported,
                                                                 NSInteger currentOrientation);
FOUNDATION_EXPORT DDFBSSceneSettingsUpdateDecision DDResolveFBSSceneSettingsUpdateDecision(DDHostSlotSize targetSize,
                                                                                           BOOL slotSettingsMarked,
                                                                                           BOOL frameSelectorSupported,
                                                                                           double currentFrameWidth,
                                                                                           NSInteger desiredOrientation,
                                                                                           NSInteger currentOrientation);
FOUNDATION_EXPORT BOOL DDPrivateUpdateSettingsMethodSignatureSupported(BOOL methodFound,
                                                                       NSString * _Nullable methodTypeEncoding);
FOUNDATION_EXPORT BOOL DDPrivateVoidIntegerSetterSignatureSupported(BOOL methodFound,
                                                                    NSUInteger argumentCount,
                                                                    NSInteger returnTypeFirstByte,
                                                                    NSInteger valueArgumentTypeFirstByte);
FOUNDATION_EXPORT DDFBSSceneSettingsExecutorDecision DDResolveFBSSceneSettingsExecutorDecision(BOOL sceneObjectPresent,
                                                                                               DDHostSlotSize targetSize,
                                                                                               BOOL executorReentrant,
                                                                                               NSInteger attemptCount,
                                                                                               BOOL geometryUpdatesEnabled,
                                                                                               BOOL updateSettingsSelectorSupported,
                                                                                               BOOL updateMethodFound,
                                                                                               NSString * _Nullable updateMethodTypeEncoding);
FOUNDATION_EXPORT DDFBSSceneSettingsMutationPlan DDResolveFBSSceneSettingsMutationPlan(BOOL settingsObjectPresent,
                                                                                       DDHostSlotSize targetSize,
                                                                                       BOOL frameSetterSupported,
                                                                                       NSInteger desiredOrientation,
                                                                                       BOOL orientationSetterSignatureSupported,
                                                                                       NSInteger currentOrientation);
FOUNDATION_EXPORT DDFBSSceneSettingsMutationExceptionOutcome DDResolveFBSSceneSettingsMutationExceptionOutcome(DDFBSSceneSettingsMutationExceptionSite site);
FOUNDATION_EXPORT DDFBSSceneSettingsExecutionAdmission DDResolveFBSSceneSettingsExecutionAdmission(uint64_t capturedGeneration,
                                                                                                    uint64_t currentGeneration,
                                                                                                    BOOL executorReentrant);
FOUNDATION_EXPORT DDFBSSceneSettingsInvocationOutcome DDResolveFBSSceneSettingsInvocationOutcome(NSInteger slotIndex,
                                                                                                 BOOL invocationThrewException,
                                                                                                 BOOL orientationChanged);
FOUNDATION_EXPORT DDFBSSceneSettingsExecutorExceptionOutcome DDResolveFBSSceneSettingsExecutorExceptionOutcome(DDFBSSceneSettingsExecutorExceptionSite site,
                                                                                                               NSInteger currentExceptionCounter);
FOUNDATION_EXPORT NSInteger DDResolvePaneSettingsOrientation(BOOL isAuxScene,
                                                              NSInteger auxOrientation);
FOUNDATION_EXPORT BOOL DDUpdateHostSlotRenderSize(NSUInteger slotIndex, DDHostSlotSize size);
FOUNDATION_EXPORT void DDSetHostSlotCarPlayUI(NSUInteger slotIndex, BOOL carPlayUI);
FOUNDATION_EXPORT BOOL DDConvertHostSlotToCarPlayUI(NSUInteger slotIndex);
FOUNDATION_EXPORT void DDDismissHostMirror(void);
FOUNDATION_EXPORT void DDScheduleAppSideHandshake(void);
FOUNDATION_EXPORT void DDScheduleGeometryPushesForSlot(NSUInteger slotIndex);
FOUNDATION_EXPORT void DDAppendHostFrameMetrics(NSMutableDictionary *payload,
                                                const DDHostFrameMetrics *metrics);
FOUNDATION_EXPORT BOOL DDPostHostRequest(NSString * _Nullable bundleIdentifier,
                                         BOOL activate,
                                         const DDHostFrameMetrics *metrics);
FOUNDATION_EXPORT BOOL DDPostSplitHostRequest(NSString * _Nullable leftBundleIdentifier,
                                              NSString * _Nullable rightBundleIdentifier,
                                              NSString * _Nullable centerBundleIdentifier,
                                              NSInteger layout,
                                              BOOL activate,
                                              BOOL skipEvict,
                                              BOOL environmentOnly,
                                              const DDHostFrameMetrics *metrics);
FOUNDATION_EXPORT BOOL DDPostCarPlayUIStatus(uint64_t generation,
                                             NSString * _Nullable bundleIdentifier,
                                             BOOL ok,
                                             NSString * _Nullable reason);
FOUNDATION_EXPORT BOOL DDPostHostRefusedState(NSString * _Nullable reason);
FOUNDATION_EXPORT BOOL DDPostHostState(BOOL activated,
                                       NSString * _Nullable bundleIdentifier,
                                       NSString * _Nullable carPlayUIBundleIdentifier,
                                       NSArray * _Nullable carPlayUIMore,
                                       NSArray * _Nullable killedBundleIdentifiers,
                                       uint64_t carPlayUIGeneration,
                                       double rectX,
                                       double rectY,
                                       double rectWidth,
                                       double rectHeight);
FOUNDATION_EXPORT void DDReconstructionStart(void);

NS_ASSUME_NONNULL_END
