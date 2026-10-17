/* Standalone Kagura real-LLVM-pass arm64 iPhone validation UI.
 * No Crane tweak loaded. Manual buttons only, no persistence/UDID/network.
 */
#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>
#import <TargetConditionals.h>
#import <mach-o/dyld.h>
#import <mach-o/loader.h>
#import <mach/machine.h>
#include <stdint.h>

#if !TARGET_OS_IPHONE || TARGET_OS_SIMULATOR || defined(__arm64e__)
#error "KaguraLab device pilot only supports physical arm64 iPhone, not arm64e"
#endif

extern int dd_kagura_ios_parity(char *report, size_t capacity);
extern int dd_kagura_ios_benchmark(char *report, size_t capacity);

static BOOL DDIsPhysicalArm64(void) {
    const struct mach_header *h = _dyld_get_image_header(0);
    return h != NULL && h->magic == MH_MAGIC_64 &&
        h->cputype == CPU_TYPE_ARM64 &&
        (((uint32_t)h->cpusubtype & UINT32_C(0x00ffffff)) == 0);
}

@interface DDKaguraViewController : UIViewController
@property(nonatomic, strong) UILabel *statusLabel;
@property(nonatomic, strong) UITextView *outputView;
@property(nonatomic, strong) UIButton *runButton;
@property(nonatomic, strong) UIButton *perfButton;
@property(nonatomic, strong) UIButton *shareButton;
@property(nonatomic, copy) NSString *parityLog;
@property(nonatomic, copy) NSString *perfLog;
@property(nonatomic, assign) BOOL busy;
@end

@implementation DDKaguraViewController
- (void)viewDidLoad {
    [super viewDidLoad];
    self.title = @"Kagura LLVM Lab";
    self.view.backgroundColor = [UIColor systemBackgroundColor];

    UILabel *heading = [UILabel new];
    heading.text = @"Kagura MAX · arm64 Test";
    heading.font = [UIFont preferredFontForTextStyle:UIFontTextStyleTitle2];

    UILabel *note = [UILabel new];
    note.numberOfLines = 0;
    note.font = [UIFont preferredFontForTextStyle:UIFontTextStyleFootnote];
    note.text = @"Real LLVM19 Kagura STR/FLA/BCF/SUB/CO/BBR/BBS vs plain C. "
                @"Isolated research IPA: no Crane, no signing, no PAC test.";

    self.statusLabel = [UILabel new];
    self.statusLabel.numberOfLines = 0;
    self.statusLabel.text = @"Not tested on this device";
    self.statusLabel.font = [UIFont preferredFontForTextStyle:UIFontTextStyleSubheadline];

    self.runButton = [UIButton buttonWithType:UIButtonTypeSystem];
    [self.runButton setTitle:@"Run 8192 Kagura vectors" forState:UIControlStateNormal];
    [self.runButton addTarget:self action:@selector(runParity)
             forControlEvents:UIControlEventTouchUpInside];

    self.perfButton = [UIButton buttonWithType:UIButtonTypeSystem];
    [self.perfButton setTitle:@"Measure Kagura overhead (optional)"
                    forState:UIControlStateNormal];
    [self.perfButton addTarget:self action:@selector(runPerformance)
             forControlEvents:UIControlEventTouchUpInside];
    self.perfButton.enabled = NO;

    self.shareButton = [UIButton buttonWithType:UIButtonTypeSystem];
    [self.shareButton setTitle:@"Share Kagura test logs" forState:UIControlStateNormal];
    [self.shareButton addTarget:self action:@selector(shareReport)
             forControlEvents:UIControlEventTouchUpInside];
    self.shareButton.enabled = NO;

    self.outputView = [UITextView new];
    self.outputView.editable = NO;
    self.outputView.selectable = YES;
    self.outputView.backgroundColor = [UIColor secondarySystemBackgroundColor];
    self.outputView.font = [UIFont monospacedSystemFontOfSize:12
                                                        weight:UIFontWeightRegular];
    self.outputView.layer.cornerRadius = 10;
    self.outputView.text = @"NOT TESTED\nTap Run to test actual Kagura code on this iPhone.";

    UIScrollView *scroll = [UIScrollView new];
    scroll.translatesAutoresizingMaskIntoConstraints = NO;
    [self.view addSubview:scroll];
    UIStackView *stack = [[UIStackView alloc] initWithArrangedSubviews:@[
        heading, note, self.statusLabel, self.runButton, self.perfButton,
        self.shareButton, self.outputView
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
        [self.outputView.heightAnchor constraintEqualToConstant:260]
    ]];
}

- (void)runParity {
    if (self.busy) return;
    self.busy = YES;
    self.parityLog = nil;
    self.perfLog = nil;
    self.runButton.enabled = NO;
    self.perfButton.enabled = NO;
    self.shareButton.enabled = NO;
    self.statusLabel.text = @"Running on real arm64 device...";
    self.statusLabel.textColor = [UIColor secondaryLabelColor];
    self.outputView.text = @"RUNNING: 8192 native baseline / Kagura comparisons";
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
        char buffer[1024] = {0};
        BOOL passed = DDIsPhysicalArm64() &&
                      dd_kagura_ios_parity(buffer, sizeof(buffer));
        NSString *report = DDIsPhysicalArm64() ?
            [NSString stringWithUTF8String:buffer] :
            @"DD_KAGURA_ERROR=INVALID_MACHO_ARM64_ABI\n";
        if (!report) {
            passed = NO;
            report = @"DD_KAGURA_ERROR=INVALID_UTF8\n";
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            self.busy = NO;
            self.parityLog = report;
            self.runButton.enabled = YES;
            self.perfButton.enabled = passed;
            self.shareButton.enabled = YES;
            self.statusLabel.text = passed ? @"Kagura parity: PASS (8192/8192)" :
                                             @"Kagura parity: FAIL — see report";
            self.statusLabel.textColor = passed ?
                [UIColor labelColor] : [UIColor systemRedColor];
            self.outputView.text = report;
        });
    });
}

- (void)runPerformance {
    if (self.busy || !self.perfButton.enabled ||
        ![self.parityLog hasSuffix:@"DD_KAGURA_COMPLETE=PASS\n"]) return;
    self.busy = YES;
    self.runButton.enabled = NO;
    self.perfButton.enabled = NO;
    self.shareButton.enabled = NO;
    self.statusLabel.text = @"Measuring Kagura on iPhone...";
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
        char buffer[1024] = {0};
        BOOL passed = DDIsPhysicalArm64() &&
                      dd_kagura_ios_benchmark(buffer, sizeof(buffer));
        NSString *report = DDIsPhysicalArm64() ?
            [NSString stringWithUTF8String:buffer] :
            @"DD_KAGURA_PERF_ERROR=INVALID_MACHO_ARM64_ABI\n";
        if (!report) {
            passed = NO;
            report = @"DD_KAGURA_PERF_ERROR=INVALID_UTF8\n";
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            self.busy = NO;
            self.perfLog = report;
            self.runButton.enabled = YES;
            self.perfButton.enabled = YES;
            self.shareButton.enabled = YES;
            self.outputView.text = report;
            self.statusLabel.text = passed ? @"Kagura benchmark: PASS" :
                                             @"Kagura benchmark: FAIL — see report";
            self.statusLabel.textColor = passed ?
                [UIColor labelColor] : [UIColor systemRedColor];
        });
    });
}

- (void)shareReport {
    if (self.busy || !self.parityLog.length) return;
    NSString *combined = self.perfLog.length ?
        [NSString stringWithFormat:@"%@\n%@", self.parityLog, self.perfLog] :
        self.parityLog;
    UIActivityViewController *sheet =
        [[UIActivityViewController alloc] initWithActivityItems:@[combined]
                                         applicationActivities:nil];
    sheet.popoverPresentationController.sourceView = self.shareButton;
    [self presentViewController:sheet animated:YES completion:nil];
}
@end

@interface DDKaguraAppDelegate : UIResponder <UIApplicationDelegate>
@property(nonatomic, strong) UIWindow *window;
@end
@implementation DDKaguraAppDelegate
- (BOOL)application:(UIApplication *)application
    didFinishLaunchingWithOptions:(NSDictionary *)options {
    (void)application;
    (void)options;
    self.window = [[UIWindow alloc] initWithFrame:[UIScreen mainScreen].bounds];
    DDKaguraViewController *root = [DDKaguraViewController new];
    self.window.rootViewController =
        [[UINavigationController alloc] initWithRootViewController:root];
    [self.window makeKeyAndVisible];
    return YES;
}
@end

int main(int argc, char *argv[]) {
    @autoreleasepool {
        return UIApplicationMain(argc, argv, nil,
                                 NSStringFromClass([DDKaguraAppDelegate class]));
    }
}
