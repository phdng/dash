#import "DuoDashShared.h"
#import <objc/message.h>

BOOL DDKeyinputFieldMayRelay(id field) {
    if (!field)
        return NO;
    SEL secureSelector = NSSelectorFromString(@"isSecureTextEntry");
    if (![field respondsToSelector:secureSelector])
        return YES;
    BOOL secure = ((BOOL (*)(id, SEL))objc_msgSend)(field, secureSelector);
    return !secure;
}
