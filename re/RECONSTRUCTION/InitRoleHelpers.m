#import "DuoDashShared.h"
#include <string.h>

// Exact AC7A4 role-code -> role-name decision promoted session-249.
// Exact AC738 null-safe C-string suffix predicate promoted session-250.
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

BOOL DDRoleCStringHasSuffix(const char *value, const char *suffix) {
    if (!value || !suffix)
        return NO;

    size_t valueLength = strlen(value);
    size_t suffixLength = strlen(suffix);
    return valueLength >= suffixLength
        && strcmp(value + valueLength - suffixLength, suffix) == 0;
}
