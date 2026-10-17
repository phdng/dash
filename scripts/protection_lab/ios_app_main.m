/* Standalone UIKit canary app. Never loads Crane or requests jailbreak privileges.
 * The Run button exercises the exact existing C functions on the actual
 * device, and exports a seven-line log compatible with device_audit.py.
 *
 * No user data, network, persistence, private API, JIT or background agents.
 */
#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>
#import <TargetConditionals.h>
#include "device_suites.h"
#include "objc_ce.h"
#include <mach-o/dyld.h>
#include <mach-o/loader.h>
#include <mach/machine.h>
#include <stdint.h>
#include <string.h>

#if !TARGET_OS_IPHONE || TARGET_OS_SIMULATOR
#error "This UIKit validation app must be compiled for a physical iOS device."
#endif

static NSString *DDRuntimeABI(void) {
    const struct mach_header *h = _dyld_get_image_header(0);
    if (!h || h->magic != MH_MAGIC_64 || h->cputype != CPU_TYPE_ARM64)
        return nil;
    const uint32_t raw = (uint32_t)h->cpusubtype;
#if defined(__arm64e__)
    if ((raw & UINT32_C(0x00ffffff)) != 2 ||
        !(raw & UINT32_C(0x80000000)) ||
        (raw & UINT32_C(0x40000000)))
        return nil;
    return [NSString stringWithFormat:@"arm64e:0x%08x", raw];
#else
    if ((raw & UINT32_C(0x00ffffff)) != 0)
        return nil;
    return [NSString stringWithFormat:@"arm64:0x%08x", raw];
#endif
}

static BOOL DDNSStringParity(void) {
    for (unsigned i = 0; i < DD_DEVICE_VECTORS; ++i) {
        @autoreleasepool {
            NSString *plain = DDObjCPlainValue(i);
            NSString *candidate = DDObjCProtectedValue(i);
            if (!plain || !candidate ||
                ![plain isEqualToString:candidate] ||
                plain.length != candidate.length ||
                [plain lengthOfBytesUsingEncoding:NSUTF8StringEncoding] !=
                    [candidate lengthOfBytesUsingEncoding:NSUTF8StringEncoding] ||
                strcmp([plain UTF8String], [candidate UTF8String]) != 0)
                return NO;
        }
    }
    return YES;
}

static NSString *DDRunValidation(void) {
    NSMutableArray<NSString *> *lines = [NSMutableArray array];
    [lines addObject:@"DD_RUNTIME_CONTEXT=IOS_DEVICE"];
    NSString *abi = DDRuntimeABI();
    if (!abi) {
        [lines addObject:@"DD_RUNTIME_ERROR=ARCH_OR_PAC_ABI_MISMATCH"];
        return [lines componentsJoinedByString:@"\n"];
    }
    [lines addObject:[@"DD_RUNTIME_ABI=" stringByAppendingString:abi]];

    /* The existing suites print to stdout/stderr as well; only this
     * structured UI report is exported through the system share sheet. */
    if (!dd_device_test_vm()) {
        [lines addObject:@"DD_RUNTIME_ERROR=VM"];
        return [lines componentsJoinedByString:@"\n"];
    }
    [lines addObject:@"DD_RUNTIME_VM_PASS=8192"];
    if (!dd_device_test_ce_icall()) {
        [lines addObject:@"DD_RUNTIME_ERROR=CE_ICALL"];
        return [lines componentsJoinedByString:@"\n"];
    }
    [lines addObject:@"DD_RUNTIME_CE_ICALL_PASS=8192"];
    if (!dd_device_test_igv_ibr()) {
        [lines addObject:@"DD_RUNTIME_ERROR=IGV_IBR"];
        return [lines componentsJoinedByString:@"\n"];
    }
    [lines addObject:@"DD_RUNTIME_IGV_IBR_PASS=8192"];
    if (!DDNSStringParity()) {
        [lines addObject:@"DD_RUNTIME_ERROR=OBJC_CE"];
        return [lines componentsJoinedByString:@"\n"];
    }
    [lines addObject:@"DD_RUNTIME_OBJC_CE_PASS=8192"];
    [lines addObject:@"DD_RUNTIME_COMPLETE=PASS"];
    return [[lines componentsJoinedByString:@"\n"] stringByAppendingString:@"\n"];
}

@interface DDProtectionLabViewController : UIViewController
@property(nonatomic, strong) UITextView *reportView;
@property(nonatomic, strong) UIButton *runButton;
@property(nonatomic, strong) UIButton *shareButton;
@property(nonatomic, copy) NSString *report;
@property(nonatomic, assign) BOOL running;
@end

@implementation DDProtectionLabViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    self.title = @"Protection Lab";
    self.view.backgroundColor = [UIColor systemBackgroundColor];

    UILabel *heading = [[UILabel alloc] init];
    heading.text = @"DuoDash · Device Validation";
    heading.font = [UIFont preferredFontForTextStyle:UIFontTextStyleTitle2];
    heading.numberOfLines = 0;

    UILabel *note = [[UILabel alloc] init];
    note.text = @"Independent research canary. No Crane tweaks are loaded. "
                @"Only a real device run can produce a device result.";
    note.textColor = [UIColor secondaryLabelColor];
    note.numberOfLines = 0;
    note.font = [UIFont preferredFontForTextStyle:UIFontTextStyleFootnote];

    self.runButton = [UIButton buttonWithType:UIButtonTypeSystem];
    [self.runButton setTitle:@"Run 4 suites × 8192" forState:UIControlStateNormal];
    [self.runButton addTarget:self action:@selector(startValidation)
             forControlEvents:UIControlEventTouchUpInside];

    self.shareButton = [UIButton buttonWithType:UIButtonTypeSystem];
    [self.shareButton setTitle:@"Share result text" forState:UIControlStateNormal];
    [self.shareButton addTarget:self action:@selector(shareReport)
               forControlEvents:UIControlEventTouchUpInside];
    self.shareButton.enabled = NO;

    self.reportView = [[UITextView alloc] init];
    self.reportView.editable = NO;
    self.reportView.selectable = YES;
    self.reportView.font = [UIFont monospacedSystemFontOfSize:12 weight:UIFontWeightRegular];
    self.reportView.text = @"NOT TESTED\nTap Run to execute the on-device parity checks.";
    self.reportView.backgroundColor = [UIColor secondarySystemBackgroundColor];
    self.reportView.layer.cornerRadius = 10;
    self.reportView.textContainerInset = UIEdgeInsetsMake(12, 8, 12, 8);

    UIStackView *stack = [[UIStackView alloc] initWithArrangedSubviews:@[
        heading, note, self.runButton, self.shareButton, self.reportView
    ]];
    stack.axis = UILayoutConstraintAxisVertical;
    stack.spacing = 14;
    stack.translatesAutoresizingMaskIntoConstraints = NO;
    [self.view addSubview:stack];
    UILayoutGuide *safe = self.view.safeAreaLayoutGuide;
    [NSLayoutConstraint activateConstraints:@[
        [stack.leadingAnchor constraintEqualToAnchor:safe.leadingAnchor constant:20],
        [stack.trailingAnchor constraintEqualToAnchor:safe.trailingAnchor constant:-20],
        [stack.topAnchor constraintEqualToAnchor:safe.topAnchor constant:22],
        [stack.bottomAnchor constraintEqualToAnchor:safe.bottomAnchor constant:-20],
        [self.reportView.heightAnchor constraintGreaterThanOrEqualToConstant:210]
    ]];
}

- (void)startValidation {
    if (self.running) return;
    self.running = YES;
    self.report = nil;
    self.runButton.enabled = NO;
    self.shareButton.enabled = NO;
    self.reportView.text = @"RUNNING — checking ABI, C/VM, CE/ICALL, IGV/IBR, NSString/ARC...";
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
        NSString *result = DDRunValidation();
        dispatch_async(dispatch_get_main_queue(), ^{
            self.report = result;
            self.reportView.text = result;
            self.running = NO;
            self.runButton.enabled = YES;
            self.shareButton.enabled = YES;
            self.reportView.textColor =
                [result hasSuffix:@"DD_RUNTIME_COMPLETE=PASS\n"] ?
                    [UIColor labelColor] : [UIColor systemRedColor];
        });
    });
}

- (void)shareReport {
    if (self.running || self.report.length == 0) return;
    UIActivityViewController *share = [[UIActivityViewController alloc]
        initWithActivityItems:@[self.report] applicationActivities:nil];
    UIPopoverPresentationController *pop = share.popoverPresentationController;
    if (pop) {
        pop.sourceView = self.shareButton;
        pop.sourceRect = self.shareButton.bounds;
    }
    [self presentViewController:share animated:YES completion:nil];
}
@end

@interface DDProtectionLabAppDelegate : UIResponder <UIApplicationDelegate>
@property(nonatomic, strong) UIWindow *window;
@end

@implementation DDProtectionLabAppDelegate
- (BOOL)application:(UIApplication *)application
    didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
    (void)application;
    (void)launchOptions;
    self.window = [[UIWindow alloc] initWithFrame:UIScreen.mainScreen.bounds];
    DDProtectionLabViewController *root = [[DDProtectionLabViewController alloc] init];
    self.window.rootViewController = [[UINavigationController alloc]
        initWithRootViewController:root];
    [self.window makeKeyAndVisible];
    return YES;
}
@end

int main(int argc, char *argv[]) {
    @autoreleasepool {
        return UIApplicationMain(argc, argv, nil,
                                 NSStringFromClass([DDProtectionLabAppDelegate class]));
    }
}
