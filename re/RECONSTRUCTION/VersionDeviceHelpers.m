#import "DuoDashShared.h"

// Exact decision-only comparator from A4008 fallback promoted session-245.
// Weak-import availability checks, global initialization, and SystemVersion.plist parsing remain excluded.

BOOL DDVersionTupleAtLeast(NSInteger installedMajor,
                           NSInteger installedMinor,
                           NSInteger installedPatch,
                           NSInteger requiredMajor,
                           NSInteger requiredMinor,
                           NSInteger requiredPatch) {
    if (installedMajor > requiredMajor)
        return YES;
    if (installedMajor < requiredMajor)
        return NO;
    if (installedMinor > requiredMinor)
        return YES;
    if (installedMinor < requiredMinor)
        return NO;
    return installedPatch >= requiredPatch;
}
