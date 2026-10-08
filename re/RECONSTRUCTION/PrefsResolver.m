// RECONSTRUCTION/PrefsResolver.m — executable clearpanes slice + synthesis notes
// Original synthesis: session-024. Exact Foundation/CoreFoundation clearpanes phase promoted session-187.
// Remaining republish phases retain unresolved private/helper contracts and are compile-excluded below.

#import "DuoDashShared.h"
#import "ReconstructionRuntime.h"
#import <notify.h>
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

static BOOL DDUnsignedDecimalString(NSString *value) {
    if (!value.length)
        return NO;
    for (NSUInteger index = 0; index < value.length; index++) {
        unichar ch = [value characterAtIndex:index];
        if (ch < '0' || ch > '9')
            return NO;
    }
    return YES;
}

NSUInteger DDResolveBridgedFontFloor(void) {
    NSString *raw = [NSString stringWithContentsOfFile:@"/var/tmp/duodash_ab_fontfloor_force"
                                               encoding:NSUTF8StringEncoding
                                                  error:nil];
    if (raw) {
        NSString *trimmed = [raw stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        NSUInteger length = trimmed.length;
        if (length && DDUnsignedDecimalString(trimmed)) {
            NSInteger value = trimmed.integerValue;
            return (value >= 8 && value <= 96) ? (NSUInteger)value : 0;
        }
        if (!length)
            return 0;
        // Exact 7EA4 behavior: non-empty non-decimal force content falls back to prefs.
    }

    CFPropertyListRef pref = CFPreferencesCopyAppValue(CFSTR("bridged_font_floor"),
                                                       (__bridge CFStringRef)DD_SETTINGS_DOMAIN);
    if (!pref)
        return 0;
    NSUInteger result = 0;
    if (CFGetTypeID(pref) == CFNumberGetTypeID()) {
        NSInteger value = [(__bridge NSNumber *)pref integerValue];
        if (value >= 8 && value <= 96)
            result = (NSUInteger)value;
    }
    CFRelease(pref);
    return result;
}

BOOL DDResolveKeyPaneEnabled(void) {
    CFPreferencesAppSynchronize((__bridge CFStringRef)DD_SETTINGS_DOMAIN);
    Boolean exists = false;
    Boolean value = CFPreferencesGetAppBooleanValue(CFSTR("keypane_enabled"),
                                                     (__bridge CFStringRef)DD_SETTINGS_DOMAIN,
                                                     &exists);
    return value || !exists;
}

BOOL DDBooleanPreferenceDefaultTrue(CFTypeRef value) {
    if (!value)
        return YES;
    return CFGetTypeID(value) == CFBooleanGetTypeID() && CFBooleanGetValue((CFBooleanRef)value);
}

BOOL DDAppBridgeIdentifierIsExcluded(id identifier) {
    if (![identifier isKindOfClass:[NSString class]] || ![(NSString *)identifier length])
        return NO;

    static NSSet<NSString *> *excluded;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        excluded = [NSSet setWithArray:@[
            @"com.apple.springboard",
            @"com.apple.CarPlayApp",
            @"com.apple.InCallService",
            @"com.sensetechlab.duodash",
            @"com.sensetechlab.duodashkey",
        ]];
    });
    return [excluded containsObject:identifier];
}

NSArray<NSString *> *DDNormalizeCarPlayUIAdditional(id candidate, NSString *mainBundleIdentifier) {
    // Exact 7E730: non-array -> empty; keep ordered, unique, non-empty NSString values != main.
    if (![candidate isKindOfClass:[NSArray class]])
        return @[];

    NSMutableArray<NSString *> *result = [NSMutableArray array];
    for (id item in (NSArray *)candidate) {
        if (![item isKindOfClass:[NSString class]])
            continue;
        NSString *bundleIdentifier = item;
        if (!bundleIdentifier.length)
            continue;
        if (mainBundleIdentifier.length && [bundleIdentifier isEqualToString:mainBundleIdentifier])
            continue;
        if ([result containsObject:bundleIdentifier])
            continue;
        [result addObject:[bundleIdentifier copy]];
    }
    return result;
}

NSInteger DDNormalizeAppBridgeIntegerSetting(NSDictionary *source,
                                             NSString *key,
                                             NSInteger minimum,
                                             NSInteger maximum,
                                             NSInteger fallback,
                                             NSString *fixName,
                                             NSMutableDictionary *writes,
                                             NSMutableArray *fixes) {
    // 7EEDC is already reconstructed exactly in ReconstructionRuntime; this executable
    // PrefsResolver seam consumes that verified contract instead of duplicating it.
    return DDNormalizeIntegerSetting(source, key, minimum, maximum, fallback,
                                     fixName, writes, fixes);
}

NSDictionary<NSString *, NSNumber *> *DDNormalizeAppBridgeNumericConfig(NSDictionary *source,
                                                                        NSMutableDictionary *writes,
                                                                        NSMutableArray *fixes) {
    // Exact raw ARM64 call setup inside 7E908:
    // layout      -> 7EEDC(source,key,1,8,2,"layout",writes,fixes)
    // ratio       -> 7EEDC(source,key,1,99,50,"ratio",writes,fixes)
    // frac_a/b    -> 7EEDC(source,key,0,99,0,"frac_a"/"frac_b",writes,fixes)
    // frac_layout -> 7EEDC(source,key,0,8,0,"frac_tag",writes,fixes)
    NSInteger layout = DDNormalizeIntegerSetting(source, @"appbridge_layout", 1, 8, 2,
                                                 @"layout", writes, fixes);
    NSInteger ratio = DDNormalizeIntegerSetting(source, @"appbridge_split_ratio", 1, 99, 50,
                                                @"ratio", writes, fixes);
    NSInteger fracA = DDNormalizeIntegerSetting(source, @"appbridge_split_frac_a", 0, 99, 0,
                                                @"frac_a", writes, fixes);
    NSInteger fracB = DDNormalizeIntegerSetting(source, @"appbridge_split_frac_b", 0, 99, 0,
                                                @"frac_b", writes, fixes);
    NSInteger fracLayout = DDNormalizeIntegerSetting(source, @"appbridge_split_frac_layout", 0, 8, 0,
                                                     @"frac_tag", writes, fixes);
    return @{
        @"appbridge_layout": @(layout),
        @"appbridge_split_ratio": @(ratio),
        @"appbridge_split_frac_a": @(fracA),
        @"appbridge_split_frac_b": @(fracB),
        @"appbridge_split_frac_layout": @(fracLayout),
    };
}

NSDictionary<NSString *, id> *DDNormalizeAppBridgeConfig(NSDictionary *source) {
    NSMutableDictionary<NSString *, id> *writes = [NSMutableDictionary dictionary];
    NSMutableArray<NSString *> *fixes = [NSMutableArray array];
    NSArray<NSString *> *paneKeys = @[@"appbridge_split_left", @"appbridge_split_right", @"appbridge_split_third"];
    NSMutableArray<NSString *> *panes = [NSMutableArray arrayWithCapacity:3];

    for (NSUInteger index = 0; index < paneKeys.count; index++) {
        NSString *key = paneKeys[index];
        id raw = source[key];
        NSString *resolved = @"";
        NSString *reason = nil;

        if (raw) {
            if (![raw isKindOfClass:[NSString class]]) {
                reason = @"type";
            } else if (DDAppBridgeIdentifierIsExcluded(raw)) {
                reason = @"excluded";
            } else if ([(NSString *)raw length] && [panes containsObject:raw]) {
                reason = @"dup";
            } else {
                resolved = [raw copy];
            }
        }

        if (reason) {
            writes[key] = @"";
            [fixes addObject:[NSString stringWithFormat:@"%@:%ld", reason, (long)index]];
        }
        [panes addObject:resolved];
    }

    NSDictionary<NSString *, NSNumber *> *numeric = DDNormalizeAppBridgeNumericConfig(source, writes, fixes);

    id cpuiRaw = source[@"appbridge_split_carplay_ui"];
    NSString *cpuiMain = @"";
    BOOL cpuiMainNeedsRepair = NO;
    if (cpuiRaw) {
        if (![cpuiRaw isKindOfClass:[NSString class]]) {
            cpuiMainNeedsRepair = YES;
        } else if ([(NSString *)cpuiRaw length]) {
            if (!DDAppBridgeIdentifierIsExcluded(cpuiRaw) && [panes containsObject:cpuiRaw]) {
                cpuiMain = [cpuiRaw copy];
            } else {
                cpuiMainNeedsRepair = YES;
            }
        }
    }
    if (cpuiMainNeedsRepair) {
        writes[@"appbridge_split_carplay_ui"] = @"";
        [fixes addObject:@"cpui_main"];
    }

    id cpuiMoreRaw = source[@"appbridge_split_carplay_ui_more"];
    NSArray<NSString *> *deduped = DDNormalizeCarPlayUIAdditional(cpuiMoreRaw, cpuiMain);
    NSMutableArray<NSString *> *cpuiMore = [NSMutableArray array];
    for (NSString *bundleIdentifier in deduped) {
        if (!DDAppBridgeIdentifierIsExcluded(bundleIdentifier) && [panes containsObject:bundleIdentifier])
            [cpuiMore addObject:bundleIdentifier];
    }
    if (cpuiMoreRaw &&
        (![cpuiMoreRaw isKindOfClass:[NSArray class]] || ![(NSArray *)cpuiMoreRaw isEqualToArray:cpuiMore])) {
        writes[@"appbridge_split_carplay_ui_more"] = [cpuiMore copy];
        [fixes addObject:@"cpui_more"];
    }

    return @{
        @"panes": [panes copy],
        @"layout": numeric[@"appbridge_layout"],
        @"ratio": numeric[@"appbridge_split_ratio"],
        @"fracA": numeric[@"appbridge_split_frac_a"],
        @"fracB": numeric[@"appbridge_split_frac_b"],
        @"fracLayout": numeric[@"appbridge_split_frac_layout"],
        @"cpuiMain": cpuiMain,
        @"cpuiMore": [cpuiMore copy],
        @"writes": [writes copy],
        @"fixes": [fixes copy],
    };
}

NSDictionary<NSString *, id> *DDCopyAppBridgeConfigPreferences(void) {
    static NSArray<NSString *> *keys;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        keys = @[
            @"appbridge_split_left",
            @"appbridge_split_right",
            @"appbridge_split_third",
            @"appbridge_layout",
            @"appbridge_split_ratio",
            @"appbridge_split_frac_a",
            @"appbridge_split_frac_b",
            @"appbridge_split_frac_layout",
            @"appbridge_split_carplay_ui",
            @"appbridge_split_carplay_ui_more",
        ];
    });

    NSMutableDictionary<NSString *, id> *snapshot = [NSMutableDictionary dictionaryWithCapacity:keys.count];
    for (NSString *key in keys) {
        CFPropertyListRef raw = CFPreferencesCopyAppValue((__bridge CFStringRef)key,
                                                          (__bridge CFStringRef)DD_SETTINGS_DOMAIN);
        if (raw) {
            snapshot[key] = CFBridgingRelease(raw);
        }
    }
    return [snapshot copy];
}

BOOL DDRepairAppBridgeConfigIfNeeded(void) {
    if ([[NSFileManager defaultManager] fileExistsAtPath:@"/var/tmp/duodash_ab_noconfigrepair"])
        return NO;

    static NSArray<NSString *> *keys;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        keys = @[
            @"appbridge_split_left",
            @"appbridge_split_right",
            @"appbridge_split_third",
            @"appbridge_layout",
            @"appbridge_split_ratio",
            @"appbridge_split_frac_a",
            @"appbridge_split_frac_b",
            @"appbridge_split_frac_layout",
            @"appbridge_split_carplay_ui",
            @"appbridge_split_carplay_ui_more",
        ];
    });

    CFPreferencesSynchronize((__bridge CFStringRef)DD_SETTINGS_DOMAIN,
                             kCFPreferencesCurrentUser,
                             kCFPreferencesAnyHost);

    NSMutableDictionary<NSString *, id> *source = [NSMutableDictionary dictionaryWithCapacity:keys.count];
    for (NSString *key in keys) {
        CFPropertyListRef raw = CFPreferencesCopyValue((__bridge CFStringRef)key,
                                                       (__bridge CFStringRef)DD_SETTINGS_DOMAIN,
                                                       kCFPreferencesCurrentUser,
                                                       kCFPreferencesAnyHost);
        if (raw)
            source[key] = CFBridgingRelease(raw);
    }

    NSDictionary<NSString *, id> *normalized = DDNormalizeAppBridgeConfig(source);
    NSDictionary<NSString *, id> *writes = normalized[@"writes"];
    if (!writes.count)
        return NO;

    for (NSString *key in keys) {
        id value = writes[key];
        if (value) {
            CFPreferencesSetValue((__bridge CFStringRef)key,
                                  (__bridge CFPropertyListRef)value,
                                  (__bridge CFStringRef)DD_SETTINGS_DOMAIN,
                                  kCFPreferencesCurrentUser,
                                  kCFPreferencesAnyHost);
        }
    }
    return CFPreferencesSynchronize((__bridge CFStringRef)DD_SETTINGS_DOMAIN,
                                    kCFPreferencesCurrentUser,
                                    kCFPreferencesAnyHost);
}

BOOL DDRepairAndRepublishAppBridge(void) {
    // Exact 27E20 tail ordering: repair attempt (including knob/clean paths) is followed
    // unconditionally by 74C8 republish. The subsequent private springboard.bringup call
    // remains outside this bounded executable seam.
    (void)DDRepairAppBridgeConfigIfNeeded();
    return DDRepublishAppBridgeResolvedSnapshot();
}

BOOL DDRepublishAppBridgeResolvedSnapshot(void) {
    // Bounded executable reconstruction of the publish-facing 74C8 path.
    // Repair writes produced by 7E908 are intentionally NOT applied here: original 74C8 only reads fixes.count.
    DDClearPanesIfNeeded([NSFileManager defaultManager]);
    CFPreferencesAppSynchronize((__bridge CFStringRef)DD_SETTINGS_DOMAIN);

    // Preserve the original refresh/read ordering. These reconstruction helpers expose the resolved values;
    // the original private/global cache destinations remain outside this bounded publisher surface.
    (void)DDResolveBridgedFontFloor();
    (void)DDResolveKeyPaneEnabled();

    Boolean enabledExists = false;
    Boolean enabledRaw = CFPreferencesGetAppBooleanValue(CFSTR("appbridge_enabled"),
                                                          (__bridge CFStringRef)DD_SETTINGS_DOMAIN,
                                                          &enabledExists);

    CFPropertyListRef bridgedRawRef = CFPreferencesCopyAppValue(CFSTR("bridgedApps"),
                                                                (__bridge CFStringRef)DD_SETTINGS_DOMAIN);
    id bridgedRaw = CFBridgingRelease(bridgedRawRef);
    NSArray *bridged = [bridgedRaw isKindOfClass:[NSArray class]] ? bridgedRaw : @[];
    NSArray *filteredBridged = bridged;
    if (bridged.count) {
        NSMutableArray *filtered = [NSMutableArray arrayWithCapacity:bridged.count];
        for (id item in bridged) {
            if (![item isKindOfClass:[NSString class]] || !DDAppBridgeIdentifierIsExcluded(item))
                [filtered addObject:item];
        }
        if (filtered.count != bridged.count)
            filteredBridged = [filtered copy];
    }

    CFPropertyListRef autostartRaw = CFPreferencesCopyValue(CFSTR("appbridge_autostart"),
                                                            (__bridge CFStringRef)DD_SETTINGS_DOMAIN,
                                                            kCFPreferencesCurrentUser,
                                                            kCFPreferencesAnyHost);
    BOOL autostart = DDBooleanPreferenceDefaultTrue(autostartRaw);
    if (autostartRaw)
        CFRelease(autostartRaw);

    NSDictionary<NSString *, id> *configRaw = DDCopyAppBridgeConfigPreferences();
    NSDictionary<NSString *, id> *config = DDNormalizeAppBridgeConfig(configRaw);
    NSArray<NSString *> *panes = config[@"panes"];

    NSMutableDictionary<NSString *, id> *plist = [@{
        @"appbridge_enabled": @((enabledRaw && enabledExists) ? 1 : 0),
        @"bridgedApps": filteredBridged,
        @"appbridge_split_enabled": @YES,
        @"appbridge_split_left": panes[0],
        @"appbridge_split_right": panes[1],
        @"appbridge_split_third": panes[2],
        @"appbridge_split_ratio": config[@"ratio"],
        @"appbridge_layout": config[@"layout"],
        @"appbridge_split_frac_a": config[@"fracA"],
        @"appbridge_split_frac_b": config[@"fracB"],
        @"appbridge_split_frac_layout": config[@"fracLayout"],
        @"appbridge_autostart": @(autostart),
        @"appbridge_split_carplay_ui": config[@"cpuiMain"],
        @"appbridge_split_carplay_ui_more": config[@"cpuiMore"],
    } mutableCopy];

    CFPropertyListRef navRaw = CFPreferencesCopyAppValue(CFSTR("navprovider_selected"),
                                                         (__bridge CFStringRef)DD_SETTINGS_DOMAIN);
    NSString *navSelected = @"";
    if (navRaw && CFGetTypeID(navRaw) == CFStringGetTypeID())
        navSelected = [(__bridge NSString *)navRaw copy];
    if (navRaw)
        CFRelease(navRaw);
    plist[@"navprovider_selected"] = navSelected;

    Boolean navExists = false;
    Boolean navRawBool = CFPreferencesGetAppBooleanValue(CFSTR("navprovider_autostart"),
                                                         (__bridge CFStringRef)DD_SETTINGS_DOMAIN,
                                                         &navExists);
    plist[@"navprovider_autostart"] = @((navRawBool && navExists) ? 1 : 0);

    BOOL wrote = [plist writeToFile:DD_APPBRIDGE_CACHE atomically:YES];
    notify_post([DD_N_APPBRIDGE_RESOLVED UTF8String]);
    return wrote;
}

// ---- Historical synthesis reference for phase ordering; compile-excluded because the executable
// publisher above replaces the old placeholder body without private helper/class calls. ----
#if 0
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
