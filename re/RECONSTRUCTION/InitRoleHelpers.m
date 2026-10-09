#import "DuoDashShared.h"
#include <string.h>

// Exact AC7A4 role-code -> role-name decision promoted session-249.
// Exact AC738 null-safe C-string suffix predicate promoted session-250.
// Exact AC5FC supplied-path role classifier (F-012 suffixes) promoted session-251.
// _NSGetExecutablePath acquisition/cache and AC7A4 latch/filesystem/notify/arming state remain excluded.

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

DDRole DDRoleForExecutablePathCString(const char *path) {
    if (DDRoleCStringHasSuffix(path, "/SpringBoard.app/SpringBoard"))
        return DDRoleSpringBoard;
    if (DDRoleCStringHasSuffix(path, "/Preferences.app/Preferences"))
        return DDRolePreferences;
    if (DDRoleCStringHasSuffix(path, "/CarPlay.app/CarPlay"))
        return DDRoleCarPlayApp;
    if (DDRoleCStringHasSuffix(path, "/mediaserverd"))
        return DDRoleMediaServerd;
    if (DDRoleCStringHasSuffix(path, "/TextInput/kbd"))
        return DDRoleKbd;
    return DDRoleUIApp;
}
