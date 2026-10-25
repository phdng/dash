import Foundation
import UIKit
import CryptoKit

// K23: actual iOS runtime byte verifier for a BUNDLED K14 specimen.
// Not a self-integrity verifier, not an immutable trust anchor, and not Crane.
// The SHA-256 reference is compiled into this standalone lab app; a repackager
// controlling both app and reference can rewrite them. K18 is not invoked.
#if targetEnvironment(simulator)
#error("K23 only supports an iOS physical-device arm64 lab")
#endif
#if !arch(arm64)
#error("K23 requires iOS arm64")
#endif

private enum K23 {
    enum Failure: Error { case invalid(String) }

    static func hash(_ bytes: [UInt8]) -> String {
        Data(SHA256.hash(data: Data(bytes))).map {
            String(format: "%02x", $0)
        }.joined()
    }

    static func u32(_ data: [UInt8], _ pos: Int) throws -> UInt32 {
        guard pos >= 0, pos <= data.count, data.count - pos >= 4 else {
            throw Failure.invalid("TRUNCATED_U32")
        }
        return (0..<4).reduce(UInt32(0)) {
            $0 | (UInt32(data[pos + $1]) << UInt32(8 * $1))
        }
    }

    static func uuid(_ data: [UInt8]) throws -> String {
        guard data.count >= 56, data.count <= 32 * 1024 * 1024,
              try u32(data, 0) == 0xfeedfacf,
              try u32(data, 4) == 0x0100000c,
              try u32(data, 8) == 0,
              try u32(data, 12) == 2 else {
            throw Failure.invalid("NOT_K14_ARM64_EXECUTABLE")
        }
        let count = Int(try u32(data, 16))
        let commands = Int(try u32(data, 20))
        guard (1...4096).contains(count), commands >= 24,
              commands <= 4 * 1024 * 1024,
              commands <= data.count - 32 else {
            throw Failure.invalid("INVALID_COMMAND_TABLE")
        }
        let end = 32 + commands
        var at = 32
        var identifier: String?
        for _ in 0..<count {
            guard at <= end, end - at >= 8 else {
                throw Failure.invalid("TRUNCATED_COMMAND")
            }
            let kind = try u32(data, at)
            let size = Int(try u32(data, at + 4))
            guard size >= 8, size % 8 == 0, size <= end - at else {
                throw Failure.invalid("INVALID_COMMAND_SIZE")
            }
            if kind == 0x1b {
                guard size == 24, identifier == nil else {
                    throw Failure.invalid("DUPLICATE_OR_BAD_UUID")
                }
                let b = Array(data[(at + 8)..<(at + 24)])
                let hex = b.map { String(format: "%02x", $0) }
                identifier = hex[0..<4].joined() + "-" +
                    hex[4..<6].joined() + "-" + hex[6..<8].joined() +
                    "-" + hex[8..<10].joined() + "-" + hex[10..<16].joined()
            }
            at += size
        }
        guard at == end, let result = identifier else {
            throw Failure.invalid("MISSING_UUID")
        }
        return result
    }

    static func verify(_ raw: [UInt8]) throws {
        // Fail closed on *any* mismatch. Do not catch an error and return true.
        guard hash(raw) == K23Expected.fullSHA256 else {
            throw Failure.invalid("WHOLE_REFERENCE_SHA_MISMATCH")
        }
        guard try uuid(raw) == K23Expected.uuid else {
            throw Failure.invalid("REFERENCE_MACHO_UUID_MISMATCH")
        }
        guard K23Expected.targetRanges.count == 2 else {
            throw Failure.invalid("EXPECTED_TARGET_COUNT")
        }
        for (offset, length, expected) in K23Expected.targetRanges {
            guard offset >= 0, offset % 4 == 0,
                  length >= 4, length % 4 == 0,
                  offset <= raw.count, length <= raw.count - offset else {
                throw Failure.invalid("INVALID_CODE_INTERVAL")
            }
            let code = Array(raw[offset..<(offset + length)])
            guard hash(code) == expected else {
                throw Failure.invalid("CODE_INTERVAL_SHA_MISMATCH")
            }
        }
    }

    static func run() throws -> String {
        guard let url = Bundle.main.url(forResource: "KaguraCSEBreakLab",
                                        withExtension: "reference") else {
            throw Failure.invalid("MISSING_BUNDLED_REFERENCE")
        }
        let raw = Array(try Data(contentsOf: url))
        try verify(raw)
        // Negative control 1: flip a byte INSIDE a K21-measured code interval.
        guard let first = K23Expected.targetRanges.first else {
            throw Failure.invalid("MISSING_TEST_INTERVAL")
        }
        var mutated = raw
        guard first.0 >= 0, first.0 < mutated.count else {
            throw Failure.invalid("BAD_NEGATIVE_MUTATION_OFFSET")
        }
        mutated[first.0] ^= 0x01
        if (try? verify(mutated)) != nil {
            throw Failure.invalid("TAMPERED_REFERENCE_UNEXPECTEDLY_ACCEPTED")
        }
        // Negative control 2: truncated reference must always be rejected.
        var truncated = raw
        truncated.removeLast()
        if (try? verify(truncated)) != nil {
            throw Failure.invalid("TRUNCATED_REFERENCE_UNEXPECTEDLY_ACCEPTED")
        }
        return [
            "DD_K23_SCHEMA=1",
            "DD_K23_CONTEXT=IOS_DEVICE_USER_INITIATED",
            "DD_K23_SCOPE=BUNDLED_REFERENCE_ONLY",
            "DD_K23_REFERENCE_UUID=\(K23Expected.uuid)",
            "DD_K23_REFERENCE_SHA256=PASS",
            "DD_K23_CODE_INTERVALS=2",
            "DD_K23_MUTATED_CODE=REJECTED",
            "DD_K23_TRUNCATED_REFERENCE=REJECTED",
            "DD_K23_SELF_INTEGRITY=NOT_IMPLEMENTED",
            "DD_K23_COMPLETE=PASS"
        ].joined(separator: "\n") + "\n"
    }
}

private final class K23Controller: UIViewController {
    private let output = UITextView()
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "K23 Reference Runtime Lab"
        view.backgroundColor = .systemBackground
        let heading = UILabel()
        heading.numberOfLines = 0
        heading.text = "K23 • bundled K14 code digest verification\nNOT running-app integrity or anti-tamper"
        heading.font = .preferredFont(forTextStyle: .headline)
        let run = UIButton(type: .system)
        run.setTitle("Verify + run tamper negative tests", for: .normal)
        run.addTarget(self, action: #selector(start), for: .touchUpInside)
        let share = UIButton(type: .system)
        share.setTitle("Share full diagnostic log", for: .normal)
        share.addTarget(self, action: #selector(export), for: .touchUpInside)
        output.font = .monospacedSystemFont(ofSize: 11, weight: .regular)
        output.isEditable = false
        output.isSelectable = true
        output.text = "Tap Verify. A PASS is emitted only if positive AND negative checks succeed."
        let stack = UIStackView(arrangedSubviews: [heading, run, share, output])
        stack.axis = .vertical
        stack.spacing = 14
        stack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor, constant: 18),
            stack.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor, constant: -18),
            stack.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 18),
            stack.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -12),
        ])
    }
    @objc private func start() {
        do {
            output.text = try K23.run()
        } catch {
            // No PASS for corrupted, truncated or unavailable reference.
            output.text = "DD_K23_COMPLETE=FAIL\nDD_K23_ERROR=REFERENCE_RUNTIME_VERIFICATION_FAILED\n"
        }
    }
    @objc private func export() {
        let sheet = UIActivityViewController(activityItems: [output.text ?? ""],
                                             applicationActivities: nil)
        sheet.popoverPresentationController?.sourceView = view
        present(sheet, animated: true)
    }
}

@main final class K23App: UIResponder, UIApplicationDelegate {
    var window: UIWindow?
    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions options:
                     [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        window = UIWindow(frame: UIScreen.main.bounds)
        window?.rootViewController = UINavigationController(
            rootViewController: K23Controller())
        window?.makeKeyAndVisible()
        return true
    }
}
