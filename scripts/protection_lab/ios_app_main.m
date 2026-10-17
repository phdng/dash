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
#include "perf_pilot.h"
#include "perf_report.h"
#include <mach-o/dyld.h>
#include <mach-o/loader.h>
#include <mach/machine.h>
#include <stdint.h>
#include <string.h>
#include <sys/utsname.h>

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

/* Mach-O UUID is an artifact correlation key, never an attestation.
 * Parse bounded load commands from the loader's actual main executable.
 */
static NSString *DDLoadedMachOUUID(void) {
    const struct mach_header *header = _dyld_get_image_header(0);
    if (!header || header->magic != MH_MAGIC_64)
        return nil;
    const struct mach_header_64 *m = (const struct mach_header_64 *)header;
    if (!m->ncmds || m->ncmds > 4096 ||
        m->sizeofcmds < sizeof(struct uuid_command) ||
        m->sizeofcmds > 1024U * 1024U)
        return nil;
    const uint8_t *commands = (const uint8_t *)(m + 1);
    size_t offset = 0;
    NSString *found = nil;
    for (uint32_t index = 0; index < m->ncmds; ++index) {
        if (m->sizeofcmds - offset < sizeof(struct load_command))
            return nil;
        struct load_command command;
        memcpy(&command, commands + offset, sizeof(command));
        if (command.cmdsize < sizeof(command) ||
            (command.cmdsize & 3U) ||
            command.cmdsize > m->sizeofcmds - offset)
            return nil;
        if (command.cmd == LC_UUID) {
            if (found || command.cmdsize != sizeof(struct uuid_command))
                return nil;
            struct uuid_command uuidCommand;
            memcpy(&uuidCommand, commands + offset, sizeof(uuidCommand));
            NSMutableString *hex = [NSMutableString stringWithCapacity:36];
            for (unsigned i = 0; i < 16; ++i) {
                if (i == 4 || i == 6 || i == 8 || i == 10)
                    [hex appendString:@"-"];
                [hex appendFormat:@"%02x", uuidCommand.uuid[i]];
            }
            found = hex;
        }
        offset += command.cmdsize;
    }
    return offset == m->sizeofcmds ? found : nil;
}

static NSString *DDRunEvidence(NSString *abi) {
    if (!abi) return nil;
    NSString *uuid = DDLoadedMachOUUID();
    struct utsname device;
    if (!uuid || uname(&device) != 0)
        return nil;
    NSString *model = [NSString stringWithUTF8String:device.machine];
    NSOperatingSystemVersion version = [NSProcessInfo processInfo].operatingSystemVersion;
    if (!model || version.majorVersion <= 0 || version.minorVersion < 0 ||
        version.patchVersion < 0)
        return nil;
    /* Hardware model and iOS version only: no serial, UDID, hostname,
     * advertising identifier, account, or other device-personal metadata.
     */
    return [NSString stringWithFormat:
        @"DD_EVIDENCE_SCHEMA=1\n"
         @"DD_EVIDENCE_CONTEXT=IOS_DEVICE\n"
         @"DD_EVIDENCE_ABI=%@\n"
         @"DD_EVIDENCE_MACHO_UUID=%@\n"
         @"DD_EVIDENCE_DEVICE_MODEL=%@\n"
         @"DD_EVIDENCE_IOS_VERSION=%ld.%ld.%ld\n"
         @"DD_EVIDENCE_NOTE=USER_SHARED_NOT_ATTESTED\n",
         abi, uuid, model, (long)version.majorVersion,
         (long)version.minorVersion, (long)version.patchVersion];
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

/* A launchable app is not a completed parity run. Emit only UI progress;
 * the strict seven-line machine report remains unchanged.
 */
static BOOL DDValidationPassed(NSString *result) {
    return [result hasSuffix:@"DD_RUNTIME_COMPLETE=PASS\n"];
}

static NSString *DDRunValidation(void (^progress)(NSString *)) {
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
    if (progress) progress(@"Testing VM (1/4)");
    if (!dd_device_test_vm()) {
        [lines addObject:@"DD_RUNTIME_ERROR=VM"];
        return [lines componentsJoinedByString:@"\n"];
    }
    [lines addObject:@"DD_RUNTIME_VM_PASS=8192"];
    if (progress) progress(@"Testing CE/ICALL (2/4)");
    if (!dd_device_test_ce_icall()) {
        [lines addObject:@"DD_RUNTIME_ERROR=CE_ICALL"];
        return [lines componentsJoinedByString:@"\n"];
    }
    [lines addObject:@"DD_RUNTIME_CE_ICALL_PASS=8192"];
    if (progress) progress(@"Testing IGV/IBR (3/4)");
    if (!dd_device_test_igv_ibr()) {
        [lines addObject:@"DD_RUNTIME_ERROR=IGV_IBR"];
        return [lines componentsJoinedByString:@"\n"];
    }
    [lines addObject:@"DD_RUNTIME_IGV_IBR_PASS=8192"];
    if (progress) progress(@"Testing Objective-C/ARC (4/4)");
    if (!DDNSStringParity()) {
        [lines addObject:@"DD_RUNTIME_ERROR=OBJC_CE"];
        return [lines componentsJoinedByString:@"\n"];
    }
    [lines addObject:@"DD_RUNTIME_OBJC_CE_PASS=8192"];
    [lines addObject:@"DD_RUNTIME_COMPLETE=PASS"];
    return [[lines componentsJoinedByString:@"\n"] stringByAppendingString:@"\n"];
}

static NSString *DDRunPerformance(NSString *abi) {
    if (!abi) return nil;
    dd_perf_results times;
    char encoded[2048];
    if (!dd_perf_run(&times) ||
        !dd_perf_render(encoded, sizeof(encoded), &times,
                        "IOS_DEVICE", abi.UTF8String))
        return nil;
    return [NSString stringWithUTF8String:encoded];
}

@interface DDProtectionLabViewController : UIViewController
@property(nonatomic, strong) UILabel *runtimeStatusLabel;
@property(nonatomic, strong) UITextView *reportView;
@property(nonatomic, strong) UIButton *runButton;
@property(nonatomic, strong) UIButton *benchmarkButton;
@property(nonatomic, strong) UIButton *shareButton;
@property(nonatomic, copy) NSString *report;
@property(nonatomic, copy) NSString *performanceReport;
@property(nonatomic, copy) NSString *evidenceReport;
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

    self.runtimeStatusLabel = [[UILabel alloc] init];
    self.runtimeStatusLabel.text = @"App launched · Runtime: NOT TESTED";
    self.runtimeStatusLabel.font = [UIFont preferredFontForTextStyle:UIFontTextStyleSubheadline];
    self.runtimeStatusLabel.numberOfLines = 0;
    self.runtimeStatusLabel.textColor = [UIColor secondaryLabelColor];

    self.runButton = [UIButton buttonWithType:UIButtonTypeSystem];
    [self.runButton setTitle:@"Run 4 suites × 8192" forState:UIControlStateNormal];
    [self.runButton addTarget:self action:@selector(startValidation)
             forControlEvents:UIControlEventTouchUpInside];

    self.benchmarkButton = [UIButton buttonWithType:UIButtonTypeSystem];
    [self.benchmarkButton setTitle:@"Measure overhead (optional)"
                              forState:UIControlStateNormal];
    [self.benchmarkButton addTarget:self action:@selector(startBenchmark)
                    forControlEvents:UIControlEventTouchUpInside];
    self.benchmarkButton.enabled = NO;

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

    /* Keep every control reachable on small iPhone displays. */
    UIScrollView *scroll = [[UIScrollView alloc] init];
    scroll.translatesAutoresizingMaskIntoConstraints = NO;
    [self.view addSubview:scroll];
    UIStackView *stack = [[UIStackView alloc] initWithArrangedSubviews:@[
        heading, note, self.runtimeStatusLabel, self.runButton, self.benchmarkButton,
        self.shareButton, self.reportView
    ]];
    stack.axis = UILayoutConstraintAxisVertical;
    stack.spacing = 14;
    stack.translatesAutoresizingMaskIntoConstraints = NO;
    [scroll addSubview:stack];
    UILayoutGuide *safe = self.view.safeAreaLayoutGuide;
    [NSLayoutConstraint activateConstraints:@[
        [scroll.leadingAnchor constraintEqualToAnchor:safe.leadingAnchor],
        [scroll.trailingAnchor constraintEqualToAnchor:safe.trailingAnchor],
        [scroll.topAnchor constraintEqualToAnchor:safe.topAnchor],
        [scroll.bottomAnchor constraintEqualToAnchor:safe.bottomAnchor],
        [stack.leadingAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.leadingAnchor constant:20],
        [stack.trailingAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.trailingAnchor constant:-20],
        [stack.topAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.topAnchor constant:22],
        [stack.bottomAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.bottomAnchor constant:-20],
        [stack.widthAnchor constraintEqualToAnchor:scroll.frameLayoutGuide.widthAnchor constant:-40],
        [self.reportView.heightAnchor constraintEqualToConstant:270]
    ]];
}

- (void)startValidation {
    if (self.running) return;
    self.running = YES;
    self.report = nil;
    self.performanceReport = nil;
    self.evidenceReport = nil;
    self.runButton.enabled = NO;
    self.benchmarkButton.enabled = NO;
    self.shareButton.enabled = NO;
    self.runtimeStatusLabel.text = @"Runtime: RUNNING (0/4)";
    self.runtimeStatusLabel.textColor = [UIColor secondaryLabelColor];
    self.reportView.text = @"RUNNING — checking ABI, C/VM, CE/ICALL, IGV/IBR, NSString/ARC...";
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
        NSString *result = DDRunValidation(^(NSString *stage) {
            dispatch_async(dispatch_get_main_queue(), ^{
                self.runtimeStatusLabel.text = stage;
            });
        });
        BOOL passed = DDValidationPassed(result);
        NSString *identity = passed ? DDRunEvidence(DDRuntimeABI()) : nil;
        dispatch_async(dispatch_get_main_queue(), ^{
            self.evidenceReport = identity;
            self.report = result;
            self.reportView.text = result;
            self.running = NO;
            self.runButton.enabled = YES;
            self.shareButton.enabled = YES;
            self.benchmarkButton.enabled = passed;
            self.runtimeStatusLabel.text = passed ?
                @"Runtime: PASS (4/4)" : @"Runtime: FAILED / INCOMPLETE — see report";
            self.runtimeStatusLabel.textColor = passed ?
                [UIColor labelColor] : [UIColor systemRedColor];
            self.reportView.textColor = passed ?
                [UIColor labelColor] : [UIColor systemRedColor];
        });
    });
}

- (void)startBenchmark {
    if (self.running || !self.benchmarkButton.enabled ||
        !DDValidationPassed(self.report)) return;
    self.running = YES;
    self.runButton.enabled = NO;
    self.benchmarkButton.enabled = NO;
    self.shareButton.enabled = NO;
    self.runtimeStatusLabel.text = @"Runtime: PASS (4/4) · Benchmark: RUNNING";
    self.reportView.text = @"MEASURING — five pairs, 20,000 calls x 5 repeats.\n"
                            @"Observational only; results vary with thermal state.";
    NSString *abi = DDRuntimeABI();
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
        NSString *result = DDRunPerformance(abi);
        dispatch_async(dispatch_get_main_queue(), ^{
            self.running = NO;
            self.runButton.enabled = YES;
            self.shareButton.enabled = YES;
            self.benchmarkButton.enabled = YES;
            self.performanceReport = result;
            self.runtimeStatusLabel.text = result ?
                @"Runtime: PASS (4/4) · Benchmark: RECORDED" :
                @"Runtime: PASS (4/4) · Benchmark: FAILED";
            self.reportView.text = result ?
                [NSString stringWithFormat:@"%@\n--- BENCHMARK (observation only) ---\n%@",
                                           self.report, result] :
                @"DD_PERF_ERROR=MEASUREMENT_FAILED\nYou may retry. Previous functional PASS is still stored.";
            self.reportView.textColor = result ?
                [UIColor labelColor] : [UIColor systemRedColor];
        });
    });
}

- (void)presentShareWithText:(NSString *)text {
    UIActivityViewController *share = [[UIActivityViewController alloc]
        initWithActivityItems:@[text] applicationActivities:nil];
    UIPopoverPresentationController *pop = share.popoverPresentationController;
    if (pop) {
        pop.sourceView = self.shareButton;
        pop.sourceRect = self.shareButton.bounds;
    }
    [self presentViewController:share animated:YES completion:nil];
}

- (void)shareReport {
    if (self.running || self.report.length == 0) return;
    /* Never merge 7-line parity, 17-line perf or 7-line identity proof. */
    if (!self.performanceReport.length && !self.evidenceReport.length) {
        [self presentShareWithText:self.report];
        return;
    }
    UIAlertController *options = [UIAlertController
        alertControllerWithTitle:@"Choose evidence"
                        message:@"Parity, binary identity and timing reports are separate."
                 preferredStyle:UIAlertControllerStyleActionSheet];
    [options addAction:[UIAlertAction
        actionWithTitle:@"Share functional PASS/failure"
                  style:UIAlertActionStyleDefault
                handler:^(UIAlertAction *action) {
                    (void)action;
                    [self presentShareWithText:self.report];
                }]];
    if (self.evidenceReport.length) {
        [options addAction:[UIAlertAction
            actionWithTitle:@"Share binary identity / OS model"
                      style:UIAlertActionStyleDefault
                    handler:^(UIAlertAction *action) {
                        (void)action;
                        [self presentShareWithText:self.evidenceReport];
                    }]];
    }
    if (self.performanceReport.length) {
        [options addAction:[UIAlertAction
            actionWithTitle:@"Share observational benchmark"
                      style:UIAlertActionStyleDefault
                    handler:^(UIAlertAction *action) {
                        (void)action;
                        [self presentShareWithText:self.performanceReport];
                    }]];
    }
    [options addAction:[UIAlertAction actionWithTitle:@"Cancel"
                      style:UIAlertActionStyleCancel handler:nil]];
    UIPopoverPresentationController *pop = options.popoverPresentationController;
    if (pop) {
        pop.sourceView = self.shareButton;
        pop.sourceRect = self.shareButton.bounds;
    }
    [self presentViewController:options animated:YES completion:nil];
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
