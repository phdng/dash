// RECONSTRUCTION/PrefsResolver.m — executable clearpanes slice + synthesis notes
// Original synthesis: session-024. Exact Foundation/CoreFoundation clearpanes phase promoted session-187.
// Remaining republish phases retain unresolved private/helper contracts and are compile-excluded below.

#import "DuoDashShared.h"
// Record: functions/74C8.md. Helpers (bodies ở EVIDENCE/prefs_split_autostart.md): 7EA4/8058/85CDC/7E568/7E908.

// ---- Phase 0: clearpanes one-shot (B01-B03; 9 keys wipe — F-041) ----
static BOOL DDClearPanesIfNeeded(NSFileManager *fm) {
    NSDictionary *attrs = [fm attributesOfItemAtPath:@"/var/tmp/duodash_ab_clearpanes" error:nil];
    NSDate *mtime = [attrs fileModificationDate];            // B01: nil → skip
    if (!mtime) return NO;
    NSString *done = [NSString stringWithContentsOfFile:@"/var/tmp/duodash_ab_clearpanes.done"
                                              encoding:NSUTF8StringEncoding error:nil];
    double threshold = done.length ? [done doubleValue] + 0.5 : 0.5; // B02
    if ([mtime timeIntervalSince1970] <= threshold) return NO; // B03 false → giữ nguyên
    [[NSString stringWithFormat:@"%.3f", [mtime timeIntervalSince1970]]
        writeToFile:@"/var/tmp/duodash_ab_clearpanes.done" atomically:YES
           encoding:NSUTF8StringEncoding error:nil];
    for (NSString *k in @[@"appbridge_split_left", @"appbridge_split_right",
                          @"appbridge_split_third", @"appbridge_layout",
                          @"appbridge_split_frac_a", @"appbridge_split_frac_b",
                          @"appbridge_split_frac_layout",
                          @"appbridge_split_carplay_ui",
                          @"appbridge_split_carplay_ui_more"])       // ĐÚNG 9 keys (F-041, not 8)
        CFPreferencesSetValue((__bridge CFStringRef)k, NULL,
                              CFSTR("com.sensetechlab.duodash.settings"),
                              kCFPreferencesCurrentUser, kCFPreferencesAnyHost);
    CFPreferencesSynchronize(CFSTR("com.sensetechlab.duodash.settings"),
                             kCFPreferencesCurrentUser, kCFPreferencesAnyHost);
    [fm removeItemAtPath:@"/var/tmp/duodash_ab_clearpanes" error:nil];
    return YES;
}

BOOL DDClearAppBridgePanesIfRequested(void) {
    return DDClearPanesIfNeeded([NSFileManager defaultManager]);
}

// ---- Phase 1-4 + publish (B04-B11, TRACE 04-18) ----
#if 0 // Not executable yet: phases below still depend on unresolved 7EA4/8058/7E568/7E908/85CDC contracts.
void DDRepublishAppBridge(void) {                            // void sub_74C8(), 8 callers
    DDClearPanesIfNeeded([NSFileManager defaultManager]);
    CFPreferencesAppSynchronize(CFSTR("com.sensetechlab.duodash.settings"));
    sub_7EA4(/* v8 = sync-return; arg use UNKNOWN U03 */);   // floor refresh (clamp 97)
    sub_8058(/* v9 = floor-return; arg use UNKNOWN U03 */);  // keypane refresh (missing=ON)
    Boolean exists = false;
    BOOL enabledRaw = CFPreferencesGetAppBooleanValue(CFSTR("appbridge_enabled"),
                        CFSTR("com.sensetechlab.duodash.settings"), &exists);
    id bridged = CFPreferencesCopyAppValue(CFSTR("bridgedApps"),
                     CFSTR("com.sensetechlab.duodash.settings"));
    if (![bridged isKindOfClass:[NSArray class]]) bridged = @[]; // B04: non-array → empty
    NSMutableArray *filtered = bridged;                      // count==0 → giữ nguyên
    if ([bridged count]) {
        filtered = [NSMutableArray arrayWithCapacity:[bridged count]];
        for (id bid in bridged)                              // B04 per-element: GIỮ non-string +
            if (![bid isKindOfClass:[NSString class]] || !sub_7E568(bid)) // non-excluded (giữ-lỏng F-041)
                [filtered addObject:bid];                    // LOẠI excluded-strings
        if (filtered.count != [bridged count]) { /* v13 = filtered */ }
    }
    id autostartRaw = CFPreferencesCopyValue(CFSTR("appbridge_autostart"),
                        CFSTR("com.sensetechlab.duodash.settings"),
                        kCFPreferencesCurrentUser, kCFPreferencesAnyHost);
    BOOL autostart = sub_85CDC(/* x0-carryover HYPOTHESIS (=autostartRaw), U02 */); // nil→1 (trap!)
    if (autostartRaw) CFRelease((__bridge CFTypeRef)autostartRaw);
    NSMutableDictionary *bulk = [NSMutableDictionary dictionary];
    for (NSString *k in /* off_154208, 10 keys (content HYPOTHESIS U04) */ @[]) { // B06
        id v = CFPreferencesCopyAppValue((__bridge CFStringRef)k,
                 CFSTR("com.sensetechlab.duodash.settings"));
        if (v) { bulk[k] = v; /* release after set */ }
    }
    id cfg = sub_7E908(bulk);                                // compute (record riêng/cross-ref)
    NSArray *panes = [cfg panes];                            // [0/1/2]
    // B07 derive: published = value&&exists (truth table INFERRED, U05)
    int enabled = (enabledRaw && exists) ? 1 : 0;
    NSDictionary *core = [NSDictionary dictionaryWithObjects:@[
        @(enabled),                                           // appbridge_enabled
        filtered,                                            // bridgedApps
        @YES,                                                // appbridge_split_enabled HẰNG YES
        panes[0], panes[1], panes[2],                        // split_left/right/third
        @([cfg ratio]), @([cfg layout]),                     // ratio/layout (integers)
        @([cfg fracA]), @([cfg fracB]), @([cfg fracLayout]), // fracs (integers)
        @(autostart),                                        // autostart (bool)
        [cfg cpuiMain], [cfg cpuiMore],                      // carplay_ui/_more
    ] forKeys:@[@"appbridge_enabled", @"bridgedApps", @"appbridge_split_enabled",
                @"appbridge_split_left", @"appbridge_split_right", @"appbridge_split_third",
                @"appbridge_split_ratio", @"appbridge_layout",
                @"appbridge_split_frac_a", @"appbridge_split_frac_b",
                @"appbridge_split_frac_layout", @"appbridge_autostart",
                @"appbridge_split_carplay_ui", @"appbridge_split_carplay_ui_more"]
                                                       count:14]; // ĐÚNG 14
    NSMutableDictionary *plist = [core mutableCopy];
    id navSel = CFPreferencesCopyAppValue(CFSTR("navprovider_selected"),
                  CFSTR("com.sensetechlab.duodash.settings"));
    plist[@"navprovider_selected"] = ([navSel isKindOfClass:[NSString class]] // B08 type-gate
                                      ? navSel : @"");       // (+CFRelease nếu non-nil)
    Boolean navExists = false;                               // B09 (cùng pattern B07)
    BOOL navRaw = CFPreferencesGetAppBooleanValue(CFSTR("navprovider_autostart"),
                    CFSTR("com.sensetechlab.duodash.settings"), &navExists);
    plist[@"navprovider_autostart"] = @((navRaw && navExists) ? 1 : 0);
    [plist writeToFile:@"/var/tmp/com.sensetechlab.appbridge.plist" atomically:YES]; // B: luôn
    // B10 cf-check: `if (cf) CFRelease(cf)` — cf INDETERMINATE (U01, cùng lớp U01 2565C)
    notify_post("com.sensetechlab.appbridge.resolved");      // B: luôn cuối (kể cả write-fail INFERRED U06)
}
#endif

// ---- Setters gọi republish (cross-ref records/EVIDENCE, không duplicate bodies) ----
// 746C(layout): 1..8 mới SetAppValue+Sync+republish, else return nguyên (B-15/F-025).
// 84D8(carplay_ui/more): normalize via 7E730 + SetAppValue cả 2 + Sync + republish (F-025 §7).
// 637E8 (autostart toggle UI): đọc 836C + flip + SetAppValue + Sync + republish (F-025 §10).
// Callers republish (8 sites): 746C/84D8/27E20/29198/56B24/5F8A4/637E8/69824 (74C8.c:5).
