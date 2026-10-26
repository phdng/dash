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
    enum Failure: Error {
        case invalid(String)
        case detailed(String, String)
    }
    static let transportMagic = Array("K23-BUNDLED-K14-REFERENCE-BASE64-V1\n".utf8)

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

    static func decodeReference(_ packed: [UInt8]) throws -> [UInt8] {
        // ASCII/base64 is an inert carrier. It stops iOS installers from
        // treating the bundled specimen as a nested Mach-O executable.
        // The decoding itself is not authentication or anti-tamper.
        guard packed.count >= transportMagic.count + 5,
              packed.count <= 2 * 32 * 1024 * 1024,
              packed.starts(with: transportMagic),
              packed.last == 0x0a else {
            throw Failure.invalid("REFERENCE_TRANSPORT_HEADER_OR_LENGTH_INVALID")
        }
        let encoded = Data(packed.dropFirst(transportMagic.count).dropLast())
        guard !encoded.contains(0x0a), !encoded.contains(0x0d),
              let decoded = Data(base64Encoded: encoded),
              decoded.base64EncodedData() == encoded,
              (56...32 * 1024 * 1024).contains(decoded.count) else {
            throw Failure.invalid("REFERENCE_TRANSPORT_BASE64_INVALID")
        }
        return Array(decoded)
    }

    static func diagnostic(_ packed: [UInt8], _ decoded: [UInt8]?) -> String {
        var lines = [
            "DD_K23_DIAG_SCHEMA=1",
            "DD_K23_DIAG_TRANSPORT_BYTES_ACTUAL=\(packed.count)",
            "DD_K23_DIAG_TRANSPORT_BYTES_EXPECTED=\(K23Expected.transportSize)",
            "DD_K23_DIAG_TRANSPORT_SHA_ACTUAL=\(hash(packed))",
            "DD_K23_DIAG_TRANSPORT_SHA_EXPECTED=\(K23Expected.transportSHA256)",
            "DD_K23_DIAG_REFERENCE_BYTES_EXPECTED=\(K23Expected.fileSize)",
            "DD_K23_DIAG_REFERENCE_SHA_EXPECTED=\(K23Expected.fullSHA256)"
        ]
        if let raw = decoded {
            lines.append("DD_K23_DIAG_REFERENCE_BYTES_ACTUAL=\(raw.count)")
            lines.append("DD_K23_DIAG_REFERENCE_SHA_ACTUAL=\(hash(raw))")
            lines.append("DD_K23_DIAG_UUID_EXPECTED=\(K23Expected.uuid)")
            lines.append("DD_K23_DIAG_UUID_ACTUAL=\((try? uuid(raw)) ?? "INVALID_MACHO")")
            for (index, (offset, length, expected)) in
                K23Expected.targetRanges.enumerated() {
                guard offset >= 0, length >= 4, offset <= raw.count,
                      length <= raw.count - offset else {
                    lines.append("DD_K23_DIAG_CODE_\(index)=OUT_OF_BOUNDS")
                    continue
                }
                let actual = hash(Array(raw[offset..<(offset + length)]))
                lines.append("DD_K23_DIAG_CODE_\(index)=\(actual == expected ? "MATCH" : "MISMATCH")")
                lines.append("DD_K23_DIAG_CODE_\(index)_SHA_ACTUAL=\(actual)")
            }
        } else {
            lines.append("DD_K23_DIAG_REFERENCE_DECODE=FAIL")
        }
        return lines.joined(separator: "\n") + "\n"
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
        // A known-answer check separates any CryptoKit/environment problem
        // from a failure to locate or validate the K14 reference asset.
        guard hash(Array("abc".utf8)) ==
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad" else {
            throw Failure.invalid("CRYPTOKIT_SHA256_SELFTEST_FAILED")
        }
        let filename = "KaguraCSEBreakLab.reference.b64"
        // Preserve strict SHA/UUID/interval verification after the lookup.
        // The direct bundle-root fallback diagnoses installers whose resource
        // API does not resolve our inert encoded asset.
        let direct = Bundle.main.bundleURL.appendingPathComponent(filename,
                                                                 isDirectory: false)
        let lookedUp = Bundle.main.url(forResource: "KaguraCSEBreakLab.reference",
                                       withExtension: "b64")
        guard let url = lookedUp ??
            (FileManager.default.fileExists(atPath: direct.path) ? direct : nil)
        else { throw Failure.invalid("MISSING_BUNDLED_REFERENCE") }
        let values: URLResourceValues
        do { values = try url.resourceValues(forKeys: [.isRegularFileKey,
                                                        .isSymbolicLinkKey]) }
        catch { throw Failure.invalid("REFERENCE_RESOURCE_METADATA_READ_FAILED") }
        guard values.isRegularFile == true && values.isSymbolicLink != true else {
            throw Failure.invalid("REFERENCE_RESOURCE_NOT_REGULAR_FILE")
        }
        let packed: [UInt8]
        do { packed = Array(try Data(contentsOf: url, options: .mappedIfSafe)) }
        catch { throw Failure.invalid("REFERENCE_FILE_READ_FAILED") }
        let decoded = try? decodeReference(packed)
        guard hash(packed) == K23Expected.transportSHA256,
              packed.count == K23Expected.transportSize else {
            throw Failure.detailed("TRANSPORT_SHA_MISMATCH",
                                   diagnostic(packed, decoded))
        }
        guard let raw = decoded else {
            throw Failure.detailed("REFERENCE_TRANSPORT_DECODE_FAILED",
                                   diagnostic(packed, nil))
        }
        do {
            try verify(raw)
        } catch Failure.invalid(let reason) {
            throw Failure.detailed(reason, diagnostic(packed, raw))
        }
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
        title = "K23 Reference Runtime Lab v2"
        view.backgroundColor = .systemBackground
        let heading = UILabel()
        heading.numberOfLines = 0
        heading.text = "K23 v2 • encoded K14 reference digest verification\nNOT running-app integrity or anti-tamper"
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
        } catch K23.Failure.detailed(let reason, let details) {
            // Preserve fail-closed rejection while collecting raw file/region
            // comparisons from the actual installed iPhone app data.
            output.text = "DD_K23_SCHEMA=1\nDD_K23_COMPLETE=FAIL\nDD_K23_ERROR=\(reason)\n" + details
        } catch K23.Failure.invalid(let reason) {
            // Fail closed, but show a stable stage-specific reason so a
            // real device can distinguish missing asset, hash and negative-test failures.
            output.text = "DD_K23_SCHEMA=1\nDD_K23_COMPLETE=FAIL\nDD_K23_ERROR=\(reason)\n"
        } catch {
            // Never silently turn an unknown runtime exception into PASS.
            output.text = "DD_K23_SCHEMA=1\nDD_K23_COMPLETE=FAIL\nDD_K23_ERROR=UNEXPECTED_RUNTIME_ERROR\n"
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
