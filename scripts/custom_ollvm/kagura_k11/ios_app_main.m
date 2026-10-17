/* Standalone K11 UIKit lab, not Crane, iOS arm64 only. */
#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>
#import <TargetConditionals.h>
#import <mach-o/dyld.h>
#import <mach-o/loader.h>
#import <mach/machine.h>
#include <stdint.h>
#if !TARGET_OS_IPHONE || TARGET_OS_SIMULATOR || defined(__arm64e__)
#error "K11 only allows physical iOS arm64 ABI (not arm64e)"
#endif

extern int dd_k11_ios_parity(char *, size_t, const char *);

static NSString *DDK11UUID(void) {
    const struct mach_header *base = _dyld_get_image_header(0);
    if (!base || base->magic != MH_MAGIC_64 ||
        base->cputype != CPU_TYPE_ARM64 ||
        (((uint32_t)base->cpusubtype & UINT32_C(0x00ffffff)) != 0))
        return nil;
    const struct mach_header_64 *h = (const struct mach_header_64 *)base;
    if (h->ncmds < 1 || h->ncmds > 4096 ||
        h->sizeofcmds < 24 || h->sizeofcmds > (1U << 20))
        return nil;
    const uint8_t *p = (const uint8_t *)(h + 1);
    uint32_t left = h->sizeofcmds;
    NSString *result = nil;
    for (uint32_t i = 0; i < h->ncmds; ++i) {
        if (left < sizeof(struct load_command)) return nil;
        const struct load_command *cmd = (const struct load_command *)p;
        if (cmd->cmdsize < 8 || cmd->cmdsize > left ||
            (cmd->cmdsize & 3U)) return nil;
        if (cmd->cmd == LC_UUID) {
            if (cmd->cmdsize != sizeof(struct uuid_command) || result)
                return nil;
            const struct uuid_command *u = (const struct uuid_command *)cmd;
            NSUUID *value = [[NSUUID alloc] initWithUUIDBytes:u->uuid];
            result = value.UUIDString.lowercaseString;
        }
        p += cmd->cmdsize;
        left -= cmd->cmdsize;
    }
    return left == 0 ? result : nil;
}

@interface DDK11Controller : UIViewController
@property(nonatomic,strong) UITextView *logView;
@property(nonatomic,strong) UILabel *status;
@property(nonatomic,strong) UIButton *runButton;
@property(nonatomic,strong) UIButton *shareButton;
@property(nonatomic,copy) NSString *lastLog;
@property(nonatomic,assign) BOOL busy;
@end
@implementation DDK11Controller
- (void)viewDidLoad {
    [super viewDidLoad];
    self.title = @"Kagura Five Lab";
    self.view.backgroundColor = UIColor.systemBackgroundColor;
    UILabel *title = [UILabel new];
    title.text = @"K11 · Five Kagura passes · iOS arm64";
    title.font = [UIFont preferredFontForTextStyle:UIFontTextStyleHeadline];
    title.numberOfLines = 0;
    UILabel *note = [UILabel new];
    note.numberOfLines = 0;
    note.font = [UIFont preferredFontForTextStyle:UIFontTextStyleFootnote];
    note.text = @"MVO → GENC → FSPLIT → IBR → CI. Separate lab only. "
                @"No Crane, no hooks, no arm64e PAC or device attestation.";
    self.status = [UILabel new];
    self.status.numberOfLines = 0;
    self.status.text = @"Device test not run";
    self.runButton = [UIButton buttonWithType:UIButtonTypeSystem];
    [self.runButton setTitle:@"Run 4096 vectors per function"
                   forState:UIControlStateNormal];
    [self.runButton addTarget:self action:@selector(runParity)
             forControlEvents:UIControlEventTouchUpInside];
    self.shareButton = [UIButton buttonWithType:UIButtonTypeSystem];
    [self.shareButton setTitle:@"Share K11 result"
                    forState:UIControlStateNormal];
    [self.shareButton addTarget:self action:@selector(shareLog)
               forControlEvents:UIControlEventTouchUpInside];
    self.shareButton.enabled = NO;
    self.logView = [UITextView new];
    self.logView.editable = NO;
    self.logView.selectable = YES;
    self.logView.font = [UIFont monospacedSystemFontOfSize:12
                                                  weight:UIFontWeightRegular];
    self.logView.text = @"Run and share the full unedited 9-line result.";
    self.logView.backgroundColor = UIColor.secondarySystemBackgroundColor;
    UIScrollView *scroll = [UIScrollView new];
    scroll.translatesAutoresizingMaskIntoConstraints = NO;
    [self.view addSubview:scroll];
    UIStackView *stack = [[UIStackView alloc] initWithArrangedSubviews:@[
        title, note, self.status, self.runButton, self.shareButton, self.logView
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
        [stack.topAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.topAnchor constant:20],
        [stack.bottomAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.bottomAnchor constant:-20],
        [stack.widthAnchor constraintEqualToAnchor:scroll.frameLayoutGuide.widthAnchor constant:-40],
        [self.logView.heightAnchor constraintEqualToConstant:270]
    ]];
}
- (void)runParity {
    if (self.busy) return;
    self.busy = YES;
    self.runButton.enabled = NO;
    self.shareButton.enabled = NO;
    self.status.text = @"Running on iPhone...";
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
        NSString *uuid = DDK11UUID();
        char buffer[1024] = {0};
        BOOL ok = uuid != nil &&
            dd_k11_ios_parity(buffer, sizeof(buffer), uuid.UTF8String);
        NSString *text = uuid ? [NSString stringWithUTF8String:buffer] :
            @"DD_K11_IOS_ERROR=INVALID_MACHO_UUID\n";
        if (!text) { ok = NO; text = @"DD_K11_IOS_ERROR=INVALID_UTF8\n"; }
        dispatch_async(dispatch_get_main_queue(), ^{
            self.busy = NO;
            self.lastLog = text;
            self.runButton.enabled = YES;
            self.shareButton.enabled = YES;
            self.status.text = ok ? @"K11 native vectors: PASS" : @"K11 failed";
            self.status.textColor = ok ? UIColor.labelColor : UIColor.systemRedColor;
            self.logView.text = text;
        });
    });
}
- (void)shareLog {
    if (self.busy || !self.lastLog.length) return;
    UIActivityViewController *controller =
        [[UIActivityViewController alloc] initWithActivityItems:@[self.lastLog]
                                         applicationActivities:nil];
    controller.popoverPresentationController.sourceView = self.shareButton;
    [self presentViewController:controller animated:YES completion:nil];
}
@end

@interface DDK11AppDelegate : UIResponder <UIApplicationDelegate>
@property(nonatomic,strong) UIWindow *window;
@end
@implementation DDK11AppDelegate
- (BOOL)application:(UIApplication *)app
    didFinishLaunchingWithOptions:(NSDictionary *)opts {
    (void)app; (void)opts;
    self.window = [[UIWindow alloc] initWithFrame:UIScreen.mainScreen.bounds];
    self.window.rootViewController = [[UINavigationController alloc]
        initWithRootViewController:[DDK11Controller new]];
    [self.window makeKeyAndVisible];
    return YES;
}
@end
int main(int argc, char **argv) {
    @autoreleasepool {
        return UIApplicationMain(argc, argv, nil,
                                 NSStringFromClass(DDK11AppDelegate.class));
    }
}
