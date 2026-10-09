#import "DuoDashShared.h"

// Exact decision-only core shared by AZ CarPlay hooks 49870..49990 (F-017), promoted session-252.
// Hook installation, per-hook counters, byte_163ED8 acquisition, and original-function invocation remain excluded.

NSInteger DDAZCarPlaySpoofedResult(BOOL forceDisconnected, NSInteger originalResult) {
    return forceDisconnected ? 0 : originalResult;
}
