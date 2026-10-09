#import "DuoDashShared.h"

// Exact AC7A4 role-code -> role-name decision promoted session-249.
// AC5FC executable-path detection/cache and AC7A4 latch/filesystem/notify/arming state remain excluded.

NSString *DDRoleName(DDRole role) {
    switch (role) {
        case DDRoleSpringBoard:
            return @"bridge";
        case DDRolePreferences:
            return @"prefsrefresh";
        case DDRoleCarPlayApp:
            return @"appbridge_cp";
        case DDRoleMediaServerd:
            return @"carplay";
        case DDRoleUIApp:
            return @"appbridge_uiapp";
        case DDRoleKbd:
            return @"kbdpoc";
        default:
            return nil;
    }
}
