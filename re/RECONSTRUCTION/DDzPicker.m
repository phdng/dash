// RECONSTRUCTION/DDzPicker.m — executable picker-admission seam + DDz3 map
// Original synthesis: session-049. Compile-safe admission promoted session-178.
// Exact admission source: sub_3257C around 0x32AC4..0x32B00 and decompile lines 372+.
// Private DDz3 construction remains documented-only; only Foundation file gates execute here.

#import "DuoDashShared.h"

static NSString * const DDPickerNoPickerPath = @"/var/tmp/duodash_ab_nopicker";
static NSString * const DDPickerNoWakePath = @"/var/tmp/duodash_ab_picker_nowake";
static NSString * const DDPickerNoSpinPath = @"/var/tmp/duodash_ab_picker_nospin";
static NSString * const DDPickerPaneSizedPath = @"/var/tmp/duodash_ab_picker_panesized";

static BOOL gDDPickerAdapterReady;

void DDPickerAdapterStart(void) {
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        DDHostFlowAdapterStart();
        gDDPickerAdapterReady = DDHostFlowAdapterReady();
    });
}

BOOL DDPickerAdapterReady(void) {
    DDPickerAdapterStart();
    return gDDPickerAdapterReady;
}

DDPickerAdmissionDecision DDResolvePickerAdmission(BOOL hostPresent) {
    DDPickerAdmissionDecision decision = {0};
    decision.adapterEnabled = DDPickerAdapterReady();
    decision.hostPresent = hostPresent;
    decision.initialPickerBudget = 6;
    if (!decision.adapterEnabled || !hostPresent)
        return decision;

    NSFileManager *fm = [NSFileManager defaultManager];
    decision.pickerSuppressedByNoPickerFile = [fm fileExistsAtPath:DDPickerNoPickerPath];
    if (decision.pickerSuppressedByNoPickerFile)
        return decision;

    decision.pickerAllowed = YES;
    decision.noWake = [fm fileExistsAtPath:DDPickerNoWakePath];
    decision.noSpin = [fm fileExistsAtPath:DDPickerNoSpinPath];
    decision.paneSized = [fm fileExistsAtPath:DDPickerPaneSizedPath];
    return decision;
}
// Commit chain bodies: DDzCommit.m (5F044/5F224/5F538/5F74C/5F8A4 + why + parallel).
// Shell/hosting classes: DDzCore.m (DDz1 63 + DDz2 35 + division + cross-links).

// ---- DDz3 = app-picker/overlay UI controller (153 methods, 0x524d4–0x69c4c, instance-only, không +shared) ----
    // Cụm (addr-range + vai trò; thân HYPOTHESIS):
    //   init host/slotBids (2) → handles/pills/gutter + drag (17: 52A18–5794C) →
    //   open/close/dismiss picker (57B28–59ABC) → scroll/grid/tile (59C54–5B950) →
    //   arrange drag-drop (5B9AC–5ECD0) → commit pick/slotBids + resolvePair
    //   (5EDC4–5F8A4 — BODIES Ở DDzCommit.m) → resize chrome/ghosts (5FD10–60F6C) →
    //   settings/env/swap/font chips (62194–62D88) → pane chips/kit rows/levels
    //   (63084–63BD8) → buildKitLevel:pane: 0x63CE4 (asm-only, dưới) →
    //   layout tiles/settings/kit present/close/applyRatio (67C30–69C4C).
    // DDz3→DDz1/DDz2 hàng trăm call-sites (startLivePresent/stopLivePresent/dropOverdue/
    //   dropSplash/teardownWindow/present/layoutGutterStripMatInHost/replacePaneAtSlot/
    //   swap/maximize/buildShellIfNeeded/installContent/resetHostingState/hostBundleId/
    //   spikeCreateSlot/spikeHostSlots...) — tầng UI trên cùng điều phối shell+hosting
    //   (HYPOTHESIS kiến trúc, data CONFIRMED).

// ---- buildKitLevel:pane: 0x63CE4 (asm-only, không decompile) ----
    // Head 40 dòng đầu asm: callers none, ~100 callees (63CE4.asm:1-7),
    //   prologue stack 0xB90 + objc_initWeak +
    //   bubblePaneSelectableForOpenSlot/bubblePaneIdForOpenSlot (63D3C-63D5C).
    // Nội dung đầy đủ UNKNOWN — không suy thân, không placeholder semantics.
