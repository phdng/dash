/* Isolated Kagura VM device experiment; arm64 iOS15+ only. No hooks/network. */
#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>
#import <TargetConditionals.h>
#import <mach-o/dyld.h>
#import <mach-o/loader.h>
#import <mach/machine.h>
#include <stdint.h>

#if !TARGET_OS_IPHONE || TARGET_OS_SIMULATOR || defined(__arm64e__)
#error "KaguraVMLab supports physical iOS arm64 only"
#endif

extern int dd_vm_ios_parity(char *, size_t, const char *);
extern int dd_vm_ios_benchmark(char *, size_t, const char *);

static BOOL DDVMArm64(void) {
    const struct mach_header *h = _dyld_get_image_header(0);
    return h && h->magic == MH_MAGIC_64 && h->cputype == CPU_TYPE_ARM64 &&
        (((uint32_t)h->cpusubtype & UINT32_C(0x00ffffff)) == 0);
}

/* Build correlation only; UUID is NOT proof of device execution. */
static NSString *DDVMExecutableUUID(void) {
    if (!DDVMArm64()) return nil;
    const struct mach_header_64 *h =
        (const struct mach_header_64 *)_dyld_get_image_header(0);
    if (h->ncmds == 0 || h->ncmds > 4096 ||
        h->sizeofcmds < 24 || h->sizeofcmds > (1U << 20)) return nil;
    const uint8_t *cursor = (const uint8_t *)(h + 1);
    uint32_t remaining = h->sizeofcmds;
    NSString *found = nil;
    for (uint32_t i = 0; i < h->ncmds; ++i) {
        if (remaining < sizeof(struct load_command)) return nil;
        const struct load_command *cmd = (const struct load_command *)cursor;
        if (cmd->cmdsize < sizeof(*cmd) || cmd->cmdsize > remaining ||
            (cmd->cmdsize & 3U)) return nil;
        if (cmd->cmd == LC_UUID) {
            if (cmd->cmdsize != sizeof(struct uuid_command) || found) return nil;
            const struct uuid_command *u = (const struct uuid_command *)cmd;
            NSUUID *uuid = [[NSUUID alloc] initWithUUIDBytes:u->uuid];
            found = [uuid.UUIDString lowercaseString];
        }
        cursor += cmd->cmdsize;
        remaining -= cmd->cmdsize;
    }
    return remaining == 0 ? found : nil;
}

@interface DDKaguraVMController : UIViewController
@property(nonatomic, strong) UITextView *output;
@property(nonatomic, strong) UILabel *status;
@property(nonatomic, strong) UIButton *runButton;
@property(nonatomic, strong) UIButton *benchButton;
@property(nonatomic, strong) UIButton *shareButton;
@property(nonatomic, copy) NSString *parity;
@property(nonatomic, copy) NSString *bench;
@property(nonatomic, assign) BOOL busy;
@end

@implementation DDKaguraVMController
- (void)viewDidLoad {
    [super viewDidLoad];
    self.title = @"Kagura VM Lab";
    self.view.backgroundColor = [UIColor systemBackgroundColor];
    UILabel *head = [UILabel new];
    head.text = @"Kagura VM · iPhone arm64";
    head.font = [UIFont preferredFontForTextStyle:UIFontTextStyleTitle2];
    UILabel *note = [UILabel new];
    note.numberOfLines = 0;
    note.font = [UIFont preferredFontForTextStyle:UIFontTextStyleFootnote];
    note.text = @"Standalone native vs real Kagura LLVM19 bytecode VM. "
                @"No Crane, no hooks, no arm64e PAC or security attestation.";
    self.status = [UILabel new];
    self.status.numberOfLines = 0;
    self.status.text = @"NOT TESTED on this iPhone";
    self.runButton = [UIButton buttonWithType:UIButtonTypeSystem];
    [self.runButton setTitle:@"Run 4096 VM vectors" forState:UIControlStateNormal];
    [self.runButton addTarget:self action:@selector(runParity)
             forControlEvents:UIControlEventTouchUpInside];
    self.benchButton = [UIButton buttonWithType:UIButtonTypeSystem];
    [self.benchButton setTitle:@"Measure VM overhead (optional)"
                     forState:UIControlStateNormal];
    [self.benchButton addTarget:self action:@selector(runBenchmark)
              forControlEvents:UIControlEventTouchUpInside];
    self.benchButton.enabled = NO;
    self.shareButton = [UIButton buttonWithType:UIButtonTypeSystem];
    [self.shareButton setTitle:@"Share K7 VM test log" forState:UIControlStateNormal];
    [self.shareButton addTarget:self action:@selector(shareLog)
               forControlEvents:UIControlEventTouchUpInside];
    self.shareButton.enabled = NO;
    self.output = [UITextView new];
    self.output.editable = NO;
    self.output.selectable = YES;
    self.output.font = [UIFont monospacedSystemFontOfSize:12
                                                     weight:UIFontWeightRegular];
    self.output.backgroundColor = [UIColor secondarySystemBackgroundColor];
    self.output.text = @"Run parity before optional benchmark.";
    UIScrollView *scroll = [UIScrollView new];
    scroll.translatesAutoresizingMaskIntoConstraints = NO;
    [self.view addSubview:scroll];
    UIStackView *stack = [[UIStackView alloc] initWithArrangedSubviews:@[
        head, note, self.status, self.runButton, self.benchButton,
        self.shareButton, self.output
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
        [self.output.heightAnchor constraintEqualToConstant:320]
    ]];
}
- (void)runParity {
    if (self.busy) return;
    self.busy = YES;
    self.parity = nil;
    self.bench = nil;
    self.runButton.enabled = NO;
    self.benchButton.enabled = NO;
    self.shareButton.enabled = NO;
    self.status.text = @"Running 4096 actual VM vectors...";
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
        char buffer[1024] = {0};
        NSString *uuid = DDVMExecutableUUID();
        BOOL passed = uuid != nil &&
            dd_vm_ios_parity(buffer, sizeof(buffer), uuid.UTF8String);
        NSString *log = uuid ? [NSString stringWithUTF8String:buffer] :
            @"DD_VM_IOS_ERROR=INVALID_MACHO_ARM64_UUID\n";
        if (!log) {
            passed = NO;
            log = @"DD_VM_IOS_ERROR=INVALID_UTF8\n";
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            self.busy = NO;
            self.parity = log;
            self.runButton.enabled = YES;
            self.benchButton.enabled = passed;
            self.shareButton.enabled = YES;
            self.status.text = passed ? @"K7 VM parity: PASS (4096/4096)" :
                                        @"K7 VM parity: FAIL (see log)";
            self.status.textColor = passed ? [UIColor labelColor] :
                                             [UIColor systemRedColor];
            self.output.text = log;
        });
    });
}
- (void)runBenchmark {
    if (self.busy || !self.benchButton.enabled ||
        ![self.parity hasSuffix:@"DD_VM_IOS_COMPLETE=PASS\n"]) return;
    self.busy = YES;
    self.runButton.enabled = NO;
    self.benchButton.enabled = NO;
    self.shareButton.enabled = NO;
    self.status.text = @"Measuring native vs VM on iPhone...";
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
        char buffer[1024] = {0};
        NSString *uuid = DDVMExecutableUUID();
        BOOL passed = uuid != nil &&
            dd_vm_ios_benchmark(buffer, sizeof(buffer), uuid.UTF8String);
        NSString *log = uuid ? [NSString stringWithUTF8String:buffer] :
            @"DD_VM_IOS_PERF_ERROR=INVALID_MACHO_ARM64_UUID\n";
        if (!log) {
            passed = NO;
            log = @"DD_VM_IOS_PERF_ERROR=INVALID_UTF8\n";
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            self.busy = NO;
            self.bench = log;
            self.runButton.enabled = YES;
            self.benchButton.enabled = YES;
            self.shareButton.enabled = YES;
            self.status.text = passed ? @"K7 VM benchmark: PASS" :
                                        @"K7 VM benchmark: FAIL";
            self.status.textColor = passed ? [UIColor labelColor] :
                                             [UIColor systemRedColor];
            self.output.text = log;
        });
    });
}
- (void)shareLog {
    if (self.busy || !self.parity.length) return;
    NSString *combined = self.bench.length ?
        [NSString stringWithFormat:@"%@\n%@", self.parity, self.bench] :
        self.parity;
    UIActivityViewController *share =
        [[UIActivityViewController alloc] initWithActivityItems:@[combined]
                                         applicationActivities:nil];
    share.popoverPresentationController.sourceView = self.shareButton;
    [self presentViewController:share animated:YES completion:nil];
}
@end

@interface DDKaguraVMAppDelegate : UIResponder <UIApplicationDelegate>
@property(nonatomic, strong) UIWindow *window;
@end
@implementation DDKaguraVMAppDelegate
- (BOOL)application:(UIApplication *)app
    didFinishLaunchingWithOptions:(NSDictionary *)opts {
    (void)app; (void)opts;
    self.window = [[UIWindow alloc] initWithFrame:[UIScreen mainScreen].bounds];
    DDKaguraVMController *root = [DDKaguraVMController new];
    self.window.rootViewController =
        [[UINavigationController alloc] initWithRootViewController:root];
    [self.window makeKeyAndVisible];
    return YES;
}
@end

int main(int argc, char *argv[]) {
    @autoreleasepool {
        return UIApplicationMain(argc, argv, nil,
                                 NSStringFromClass([DDKaguraVMAppDelegate class]));
    }
}
