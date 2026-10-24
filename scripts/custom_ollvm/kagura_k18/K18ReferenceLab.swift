import Foundation
import UIKit
import CryptoKit

// K18 read-only reference verification. The measured Mach-O is a BUNDLED
// K14 specimen, NOT the K18 app's own executable or in-memory machine code.
// The public key and fingerprint in the IPA are not an immutable trust root.
#if targetEnvironment(simulator)
#error("K18 is an isolated iPhoneOS device lab, not an iOS simulator test")
#endif
#if !arch(arm64)
#error("K18 research lab requires iOS arm64")
#endif

private enum K18 {
    static let domain = Data("DuoDash/K17/K16/MachOTextOfflineEd25519/v1".utf8) + Data([0])
    static let legacyTestFingerprint = "2e91a1403ffc97eb66c2c1717205eb054ce3c341898b6978b007cb5c56241f40"
    static let referenceName = "KaguraCSEBreakLab"
    static let expectedScope = "K16_OFFLINE_POST_LINK_TEXT_MEASUREMENTS_NO_RUNTIME_PROTECTION"

    static func hex(_ data: Data) -> String { data.map { String(format: "%02x", $0) }.joined() }
    static func digest(_ data: Data) -> String { hex(Data(SHA256.hash(data: data))) }

    static func resource(_ name: String, _ ext: String) throws -> Data {
        guard let url = Bundle.main.url(forResource: name, withExtension: ext) else {
            throw Failure.invalid("MISSING_\(name)")
        }
        return try Data(contentsOf: url)
    }

    enum Failure: Error { case invalid(String) }

    private static func u32(_ bytes: Data, _ pos: Int) throws -> UInt32 {
        guard pos >= 0 && bytes.count - pos >= 4 else { throw Failure.invalid("TRUNCATED_MACHO") }
        return (0..<4).reduce(UInt32(0)) { $0 | (UInt32(bytes[pos + $1]) << (8 * $1)) }
    }
    private static func u64(_ bytes: Data, _ pos: Int) throws -> UInt64 {
        guard pos >= 0 && bytes.count - pos >= 8 else { throw Failure.invalid("TRUNCATED_MACHO") }
        return (0..<8).reduce(UInt64(0)) { $0 | (UInt64(bytes[pos + $1]) << (8 * $1)) }
    }
    private static func ascii(_ bytes: Data, _ pos: Int) throws -> String {
        guard pos >= 0 && bytes.count - pos >= 16 else { throw Failure.invalid("BAD_NAME") }
        let raw = Array(bytes[pos..<(pos + 16)])
        return String(bytes: raw.prefix(while: { $0 != 0 }), encoding: .ascii) ?? ""
    }

    static func inspect(_ bytes: Data) throws -> (uuid: String, textOffset: Int, textSize: Int) {
        guard bytes.count >= 56 && bytes.count <= 32 * 1024 * 1024,
              try u32(bytes, 0) == 0xfeedfacf,
              try u32(bytes, 4) == 0x0100000c,
              try u32(bytes, 8) == 0,
              try u32(bytes, 12) == 2 else { throw Failure.invalid("NON_ARM64_EXECUTABLE") }
        let commands = Int(try u32(bytes, 16)), size = Int(try u32(bytes, 20))
        guard (1...4096).contains(commands), size >= 24, size <= 4 * 1024 * 1024,
              bytes.count - 32 >= size else { throw Failure.invalid("INVALID_LOAD_COMMANDS") }
        let end = 32 + size
        var pos = 32
        var uuid: String?
        var section: (Int, Int)?
        for _ in 0..<commands {
            guard end - pos >= 8 else { throw Failure.invalid("TRUNCATED_COMMAND") }
            let kind = try u32(bytes, pos)
            let cmdSize = Int(try u32(bytes, pos + 4))
            guard cmdSize >= 8, cmdSize % 8 == 0, cmdSize <= end - pos else {
                throw Failure.invalid("INVALID_COMMAND_SIZE")
            }
            if kind == 0x1b {
                guard cmdSize == 24, uuid == nil else { throw Failure.invalid("DUPLICATE_UUID") }
                let a = Array(bytes[(pos + 8)..<(pos + 24)])
                let h = a.map { String(format: "%02x", $0) }
                uuid = h[0..<4].joined() + "-" + h[4..<6].joined() + "-" +
                    h[6..<8].joined() + "-" + h[8..<10].joined() + "-" + h[10..<16].joined()
            }
            if kind == 0x19 {
                guard cmdSize >= 72 else { throw Failure.invalid("BAD_SEGMENT") }
                let nsections = Int(try u32(bytes, pos + 64))
                guard nsections <= 8192, nsections <= (cmdSize - 72) / 80,
                      72 + nsections * 80 == cmdSize else { throw Failure.invalid("BAD_SECTION_COUNT") }
                let segname = try ascii(bytes, pos + 8)
                let vmaddr = try u64(bytes, pos + 24)
                let vmsize = try u64(bytes, pos + 32)
                let fileoff = try u64(bytes, pos + 40)
                let filesize = try u64(bytes, pos + 48)
                for n in 0..<nsections {
                    let p = pos + 72 + n * 80
                    let sectionName = try ascii(bytes, p)
                    let sectionSegment = try ascii(bytes, p + 16)
                    if sectionName == "__text" && sectionSegment == "__TEXT" {
                        guard segname == "__TEXT", section == nil else {
                            throw Failure.invalid("DUPLICATE_TEXT_SECTION")
                        }
                        let address = try u64(bytes, p + 32)
                        let length = try u64(bytes, p + 40)
                        let offset = UInt64(try u32(bytes, p + 48))
                        guard length >= 16, offset >= UInt64(end),
                              offset >= fileoff, offset <= UInt64(bytes.count),
                              fileoff <= UInt64(bytes.count),
                              filesize <= UInt64(bytes.count) - fileoff,
                              length <= UInt64(bytes.count) - offset,
                              offset - fileoff <= filesize, length <= filesize - (offset - fileoff),
                              address >= vmaddr, length <= vmsize,
                              address - vmaddr <= vmsize - length,
                              address - vmaddr == offset - fileoff else {
                            throw Failure.invalid("INVALID_TEXT_BOUNDS")
                        }
                        section = (Int(offset), Int(length))
                    }
                }
            }
            pos += cmdSize
        }
        guard pos == end, let id = uuid, let sectionBounds = section else {
            throw Failure.invalid("MISSING_UUID_OR_TEXT")
        }
        return (id, sectionBounds.0, sectionBounds.1)
    }

    static func run() throws -> String {
        let trustBytes = try resource("KaguraK18Trust", "plist")
        guard let trust = try PropertyListSerialization.propertyList(
            from: trustBytes, options: [], format: nil) as? [String: Any],
              let pub64 = trust["Ed25519PublicKeyRawBase64"] as? String,
              let fingerprint = trust["ExpectedSPKISHA256"] as? String,
              fingerprint.count == 64,
              fingerprint != legacyTestFingerprint,
              let raw = Data(base64Encoded: pub64), raw.count == 32 else {
            throw Failure.invalid("UNTRUSTED_KEY_CONFIGURATION")
        }
        // Ed25519 SPKI DER is RFC 8410 prefix followed by 32-byte raw key.
        let spki = Data([0x30,0x2a,0x30,0x05,0x06,0x03,0x2b,0x65,0x70,0x03,0x21,0x00]) + raw
        guard digest(spki) == fingerprint else { throw Failure.invalid("KEY_FINGERPRINT_MISMATCH") }

        let manifest = try resource("Kagura-K16-OFFLINE-TEXT-MANIFEST", "json")
        let signature = try resource("Kagura-K17-K16-MANIFEST", "ed25519")
        guard signature.count == 64 else { throw Failure.invalid("SIGNATURE_LENGTH") }
        let publicKey = try Curve25519.Signing.PublicKey(rawRepresentation: raw)
        guard publicKey.isValidSignature(signature, for: domain + manifest) else {
            throw Failure.invalid("ED25519_SIGNATURE_INVALID")
        }
        guard let json = try JSONSerialization.jsonObject(with: manifest) as? [String: Any],
              json["scope"] as? String == expectedScope,
              json["bbcheck_security_integrity"] as? String ==
                "BLOCKED_K15_WEAK_ALWAYS_PASS_STUB",
              json["metadata_authenticated"] as? Bool == false,
              json["runtime_verifier_implemented"] as? Bool == false,
              json["per_basic_block_identity_and_hashing"] as? Bool == false,
              json["adversarial_tamper_protection_proven"] as? Bool == false,
              let entries = json["linked_binaries"] as? [String: Any],
              let reference = entries["ios_csebreak_lab"] as? [String: Any],
              let expectedBinary = reference["binary_sha256"] as? String,
              let expectedText = reference["text_sha256"] as? String,
              let expectedUuid = reference["uuid"] as? String,
              let expectedSize = reference["text_size"] as? Int,
              let expectedOffset = reference["text_file_offset"] as? Int,
              reference["architecture"] as? String == "arm64:0x00000000",
              reference["filetype"] as? String == "MH_EXECUTE" else {
            throw Failure.invalid("MANIFEST_SCOPE_OR_SCHEMA")
        }
        let archive = try resource(referenceName, "reference")
        guard digest(archive) == expectedBinary else { throw Failure.invalid("BINARY_SHA_MISMATCH") }
        let mach = try inspect(archive)
        guard mach.uuid == expectedUuid,
              mach.textOffset == expectedOffset, mach.textSize == expectedSize,
              digest(archive.subdata(in: mach.textOffset..<(mach.textOffset + mach.textSize))) == expectedText
        else { throw Failure.invalid("MACHO_UUID_OR_TEXT_SHA_MISMATCH") }
        // Only the stored REFERENCE binary was checked, not this running app.
        return [
            "DD_K18_SCHEMA=1",
            "DD_K18_CONTEXT=IOS_DEVICE_USER_INITIATED",
            "DD_K18_SCOPE=BUNDLED_REFERENCE_ONLY",
            "DD_K18_ARCH=arm64:0x00000000",
            "DD_K18_REFERENCE_UUID=\(expectedUuid)",
            "DD_K18_TRUST_SPKI_SHA256=\(fingerprint)",
            "DD_K18_SIGNATURE=PASS",
            "DD_K18_REFERENCE_MACHO_TEXT=PASS",
            "DD_K18_SELF_INTEGRITY=NOT_IMPLEMENTED",
            "DD_K18_COMPLETE=PASS"
        ].joined(separator: "\n") + "\n"
    }
}

private final class K18Controller: UIViewController {
    private let output = UITextView()
    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        title = "K18 Signed Reference Lab"
        let heading = UILabel()
        heading.numberOfLines = 0
        heading.text = "Offline signed reference on iPhone\nNOT active-code integrity or device attestation"
        heading.font = .preferredFont(forTextStyle: .headline)
        let run = UIButton(type: .system)
        run.setTitle("Verify bundled K14 reference", for: .normal)
        run.addTarget(self, action: #selector(start), for: .touchUpInside)
        let share = UIButton(type: .system)
        share.setTitle("Share diagnostic text", for: .normal)
        share.addTarget(self, action: #selector(export), for: .touchUpInside)
        output.isEditable = false
        output.font = .monospacedSystemFont(ofSize: 11, weight: .regular)
        output.text = "Tap Verify. No CHECK/PASS is reported until all byte checks succeed."
        let stack = UIStackView(arrangedSubviews: [heading, run, share, output])
        stack.axis = .vertical
        stack.spacing = 14
        stack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 20),
            stack.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 18),
            stack.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -18),
            stack.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -16)
        ])
    }
    @objc private func start() {
        do { output.text = try K18.run() }
        catch {
            // No COMPLETE=PASS on failure; never ignore a parsing/signature error.
            output.text = "DD_K18_COMPLETE=FAIL\nDD_K18_ERROR=SIGNED_REFERENCE_VERIFICATION_FAILED\n"
        }
    }
    @objc private func export() {
        let sheet = UIActivityViewController(activityItems: [output.text ?? ""], applicationActivities: nil)
        present(sheet, animated: true)
    }
}

@main final class K18App: UIResponder, UIApplicationDelegate {
    var window: UIWindow?
    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions options: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        window = UIWindow(frame: UIScreen.main.bounds)
        window?.rootViewController = UINavigationController(rootViewController: K18Controller())
        window?.makeKeyAndVisible()
        return true
    }
}
