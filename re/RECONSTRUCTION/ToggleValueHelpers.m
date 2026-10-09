#import "DuoDashShared.h"
#include <stdlib.h>

// Exact pure string-value branch from 7EA4 promoted session-255.
// Exact pure reapdelay string parser from 202D0 promoted session-256.
// Exact pure holdsec parser from 163EC promoted session-257.
// Exact pure discoclose-seconds parser from 7B9EC promoted session-258.
// Exact pure splash-seconds parser from 358F0 promoted session-259.
// Exact pure dash-settle parser from 1A18C promoted session-260.
// Exact pure dash-launch-seconds parser from 19A08 promoted session-261.
// Exact pure keypane-hidegap parser from 38E14 promoted session-262.
// Exact pure simulated-speed parser from 71780 promoted session-263.
// Exact pure force-IO string decision from 42124 promoted session-264.
// Exact pure mat-alpha parser from 33DB4 promoted session-265.
// Exact pure orientation parser from 3DFC8 promoted session-266.
// Exact pure render-scale parser from 3B2D8 promoted session-267.
// Exact pure live-present alpha parser from 2A610 promoted session-268.
// Exact pure live-present target canonicalizer from 2A610 promoted session-269.
// Exact pure live-present animation alpha-token validator from 2A610 promoted session-270.
// Exact pure live-present animation easing classifier from 2A610 promoted session-271.
// File reads, CFPreferences fallback, scheduling/UI state, and cache/global mutation remain excluded.

NSUInteger DDFontFloorOverrideValue(NSString *value) {
    NSCharacterSet *whitespace = [NSCharacterSet whitespaceAndNewlineCharacterSet];
    NSString *trimmed = [value stringByTrimmingCharactersInSet:whitespace];
    if (trimmed.length == 0)
        return 0;

    for (NSUInteger i = 0; i < trimmed.length; i++) {
        unichar c = [trimmed characterAtIndex:i];
        if (c < '0' || c > '9')
            return 0;
    }

    NSInteger parsed = trimmed.integerValue;
    if (parsed < 8 || parsed > 96)
        return 0;
    return (NSUInteger)parsed;
}

double DDReapDelayOverrideValue(NSString *value) {
    NSCharacterSet *whitespace = [NSCharacterSet whitespaceAndNewlineCharacterSet];
    NSString *trimmed = [value stringByTrimmingCharactersInSet:whitespace];
    if (trimmed.length == 0)
        return 0.0;

    double parsed = trimmed.doubleValue;
    if (parsed > 60.0 || parsed <= 0.0)
        return 0.0;
    return parsed;
}

double DDHoldSecondsOverrideValue(NSString *value) {
    double parsed = value ? value.doubleValue : 0.0;
    if (parsed > 3600.0 || parsed < 10.0)
        return 900.0;
    return parsed;
}

double DDDisconnectCloseSecondsOverrideValue(NSString *value) {
    double result = 12.0;
    if (value.length == 0)
        return result;

    NSCharacterSet *whitespace = [NSCharacterSet whitespaceAndNewlineCharacterSet];
    NSString *trimmed = [value stringByTrimmingCharactersInSet:whitespace];
    if (trimmed.length == 0)
        return result;

    double parsed = trimmed.doubleValue;
    if (parsed >= 0.0 && parsed <= 120.0)
        result = parsed;
    return result;
}

double DDSplashSecondsOverrideValue(NSString *value) {
    NSCharacterSet *whitespace = [NSCharacterSet whitespaceAndNewlineCharacterSet];
    NSString *trimmed = [value stringByTrimmingCharactersInSet:whitespace];
    double parsed = trimmed.length ? trimmed.doubleValue : 0.0;
    if (parsed > 15.0 || parsed < 0.5)
        return 3.0;
    return parsed;
}

double DDDashSettleSecondsOverrideValue(NSString *value) {
    if (value.length == 0)
        return 0.45;
    double parsed = value.doubleValue;
    if (parsed > 5.0 || parsed < 0.2)
        return 0.45;
    return parsed;
}

double DDDashLaunchSecondsOverrideValue(NSString *value) {
    double result = 1.5;
    if (value.length == 0)
        return result;
    double parsed = value.doubleValue;
    if (parsed >= 0.5 && parsed <= 30.0)
        result = parsed;
    return result;
}

double DDKeypaneHideGapOverrideValue(NSString *value) {
    if (value.length == 0)
        return 71.0;

    const char *start = value.UTF8String;
    if (!start)
        return 71.0;

    char *end = NULL;
    double parsed = strtod(start, &end);
    if (parsed > 200.0 || parsed < 0.0 || end == start)
        return 71.0;
    return parsed;
}

BOOL DDSimulatedSpeedOverrideValue(NSString *value, uint8_t *outValue) {
    NSCharacterSet *whitespace = [NSCharacterSet whitespaceAndNewlineCharacterSet];
    NSString *trimmed = [value stringByTrimmingCharactersInSet:whitespace];
    if (trimmed.length == 0)
        return NO;

    for (NSUInteger i = 0; i < trimmed.length; i++) {
        unichar c = [trimmed characterAtIndex:i];
        if (c < '0' || c > '9')
            return NO;
    }

    NSUInteger parsed = (NSUInteger)trimmed.integerValue;
    if (parsed > 255)
        return NO;
    if (outValue)
        *outValue = (uint8_t)parsed;
    return YES;
}

BOOL DDForceIOOverrideEnabled(NSString *value) {
    NSCharacterSet *whitespace = [NSCharacterSet whitespaceAndNewlineCharacterSet];
    NSString *trimmed = [value stringByTrimmingCharactersInSet:whitespace];
    return [trimmed isEqualToString:@"1"];
}

double DDMatAlphaOverrideValue(NSString *value) {
    if (value.length == 0)
        return 0.996078431;
    double parsed = value.doubleValue;
    if (parsed > 1.0 || parsed <= 0.0)
        return 0.996078431;
    return parsed;
}

NSInteger DDOrientationOverrideValue(NSString *value) {
    NSInteger parsed = value ? value.integerValue : 0;
    if (parsed < 1 || parsed > 4)
        return 1;
    return parsed;
}

double DDRenderScaleOverrideValue(NSString *value) {
    double parsed = value ? value.doubleValue : 0.0;
    if (parsed > 3.0 || parsed < 1.0)
        return 2.0;
    return parsed;
}

float DDLivePresentAlphaOverrideValue(NSString *value) {
    if (value.length == 0)
        return 0.995f;
    float parsed = value.floatValue;
    if (parsed > 0.99999f || parsed < 0.9f)
        return 0.995f;
    return parsed;
}

NSString *DDLivePresentTargetOverrideValue(NSString *value) {
    NSCharacterSet *whitespace = [NSCharacterSet whitespaceAndNewlineCharacterSet];
    NSString *trimmed = [value stringByTrimmingCharactersInSet:whitespace];
    if ([trimmed isEqualToString:@"host"] || [trimmed isEqualToString:@"panes"])
        return trimmed;
    return @"root";
}

BOOL DDLivePresentAnimationAlphaTokenValue(NSString *value, float *outValue) {
    if (value.length == 0)
        return NO;
    float parsed = value.floatValue;
    if (parsed < 0.5f || parsed > 1.0f)
        return NO;
    if (outValue)
        *outValue = parsed;
    return YES;
}

BOOL DDLivePresentAnimationUsesLinearEasing(NSString *value) {
    NSString *lower = value.lowercaseString;
    return [lower hasPrefix:@"lin"];
}
