import Foundation
import UIKit
import CryptoKit
import MachO
import UniformTypeIdentifiers

// K24 reads __TEXT,__text of THIS RUNNING MAIN EXECUTABLE in memory.
// Unlike K23 it does not use a bundled K14 reference binary.
// A detached Ed25519 statement must be signed EXTERNALLY and imported;
// no CI signing key or "pass by default" path. This does NOT guarantee
// anti-tamper against a patched verifier/public key or device attestation.
#if targetEnvironment(simulator)
#error("K24 lab only supports a physical iOS arm64 device")
#endif
#if !arch(arm64)
#error("K24 lab requires arm64")
#endif

private enum K24 {
    enum Failure: Error { case invalid(String) }
    static let domain = Data("DuoDash/K24/OnDeviceSelfText/v1\0".utf8)
    static let scope = "OWN_RUNNING_MAIN_EXECUTABLE_TEXT_ONLY"

    struct Sample {
        let uuid: String
        let text: Data
        var digest: String { K24.sha(text) }
    }

    static func sha(_ bytes: Data) -> String {
        SHA256.hash(data: bytes).map { String(format: "%02x", $0) }.joined()
    }

    static func name(_ p: UnsafeRawPointer) -> String {
        var chars: [UInt8] = []
        for i in 0..<16 {
            let b = p.load(fromByteOffset: i, as: UInt8.self)
            if b == 0 { break }
            chars.append(b)
        }
        return String(decoding: chars, as: UTF8.self)
    }

    static func hex(_ bytes: [UInt8]) -> String {
        bytes.map { String(format: "%02x", $0) }.joined()
    }

    static func measureRunningSelf() throws -> Sample {
        guard let h = _dyld_get_image_header(0) else {
            throw Failure.invalid("NO_MAIN_DYLD_HEADER")
        }
        let base = UnsafeRawPointer(h)
        let m = base.load(as: mach_header_64.self)
        guard m.magic == 0xfeedfacf, m.cputype == 0x0100000c,
              m.cpusubtype == 0, m.filetype == 2, m.ncmds >= 1, m.ncmds <= 4096,
              m.sizeofcmds >= 24, m.sizeofcmds <= 4 * 1024 * 1024 else {
            throw Failure.invalid("BAD_MAIN_MACHO_HEADER")
        }
        var at = 0
        let maxCmd = Int(m.sizeofcmds)
        let commands = base.advanced(by: MemoryLayout<mach_header_64>.size)
        var uuids: [String] = []
        var regions: [(UInt64, UInt64)] = []
        for _ in 0..<Int(m.ncmds) {
            guard at <= maxCmd, maxCmd - at >= 8 else {
                throw Failure.invalid("LOAD_COMMAND_OVERFLOW")
            }
            let p = commands.advanced(by: at)
            let lc = p.load(as: load_command.self)
            let size = Int(lc.cmdsize)
            guard size >= 8, size % 8 == 0, size <= maxCmd - at else {
                throw Failure.invalid("BAD_LOAD_COMMAND_SIZE")
            }
            if lc.cmd == 0x1b {
                guard size == 24 else { throw Failure.invalid("BAD_LC_UUID") }
                let bytes = (0..<16).map {
                    p.load(fromByteOffset: 8 + $0, as: UInt8.self)
                }
                let hs = bytes.map { String(format: "%02x", $0) }
                let uid = hs[0..<4].joined() + "-" + hs[4..<6].joined() +
                    "-" + hs[6..<8].joined() + "-" + hs[8..<10].joined() +
                    "-" + hs[10..<16].joined()
                uuids.append(uid)
            }
            if lc.cmd == 0x19 {
                guard size >= 72 else { throw Failure.invalid("BAD_SEGMENT64") }
                let seg = p.load(as: segment_command_64.self)
                let cnt = Int(seg.nsects)
                guard cnt >= 0, cnt <= 8192,
                      cnt <= (size - 72) / 80, 72 + cnt * 80 == size else {
                    throw Failure.invalid("BAD_SECTION_COUNT")
                }
                for i in 0..<cnt {
                    let secptr = p.advanced(by: 72 + i * 80)
                    let sect = secptr.load(as: section_64.self)
                    if name(secptr) == "__text" &&
                        name(secptr.advanced(by: 16)) == "__TEXT" &&
                        name(p.advanced(by: 8)) == "__TEXT" {
                        guard sect.size >= 16, sect.size <= 16 * 1024 * 1024,
                              sect.addr >= seg.vmaddr,
                              sect.addr - seg.vmaddr <= seg.vmsize,
                              sect.size <= seg.vmsize -
                                  (sect.addr - seg.vmaddr) else {
                            throw Failure.invalid("BAD_SELF_TEXT_BOUNDS")
                        }
                        regions.append((sect.addr, sect.size))
                    }
                }
            }
            at += size
        }
        guard at == maxCmd, uuids.count == 1, regions.count == 1 else {
            throw Failure.invalid("MISSING_OR_DUPLICATE_UUID_TEXT")
        }
        let slide = Int64(_dyld_get_image_vmaddr_slide(0))
        let (loaded, overflow) =
            Int64(bitPattern: regions[0].0).addingReportingOverflow(slide)
        guard !overflow, loaded > 0,
              let ptr = UnsafeRawPointer(bitPattern: UInt(loaded)) else {
            throw Failure.invalid("INVALID_SLID_TEXT_POINTER")
        }
        let text = Data(bytes: ptr, count: Int(regions[0].1))
        return Sample(uuid: uuids[0], text: text)
    }

    static func lines(_ measured: Sample) -> String {
        [
            "DD_K24_SCHEMA=1",
            "DD_K24_SCOPE=OWN_RUNNING_MAIN_EXECUTABLE_TEXT_ONLY",
            "DD_K24_MAIN_UUID=\(measured.uuid)",
            "DD_K24_RUNTIME_TEXT_BYTES=\(measured.text.count)",
            "DD_K24_RUNTIME_TEXT_SHA256=\(measured.digest)",
            "DD_K24_EXTERNAL_KEY=\(K24Pinned.keyConfigured ? "PINNED_AT_BUILD" : "NOT_CONFIGURED")",
            "DD_K24_EXTERNAL_SIGNATURE=NOT_IMPORTED",
            "DD_K24_COMPLETE=MEASUREMENT_ONLY"
        ].joined(separator: "\n") + "\n"
    }

    static func canonicalBase64(_ b64: String, max: Int) -> Data? {
        guard b64.count >= 4, b64.count <= max * 2,
              let raw = Data(base64Encoded: b64),
              raw.count <= max, raw.base64EncodedString() == b64 else {
            return nil
        }
        return raw
    }

    static func signedPayload(_ m: Sample) -> Data {
        Data((
            "DD_K24_SCHEMA=1\n" +
            "DD_K24_SCOPE=OWN_RUNNING_MAIN_EXECUTABLE_TEXT_ONLY\n" +
            "DD_K24_UUID=\(m.uuid)\n" +
            "DD_K24_TEXT_SIZE=\(m.text.count)\n" +
            "DD_K24_TEXT_SHA256=\(m.digest)\n"
        ).utf8)
    }

    static func verifyEnvelope(_ input: Data, measured: Sample) throws -> String {
        guard K24Pinned.keyConfigured,
              K24Pinned.publicKey.count == 32 else {
            throw Failure.invalid("NO_EXTERNALLY_CONFIGURED_KEY")
        }
        guard input.count < 8192,
              let item = try? JSONSerialization.jsonObject(with: input) as? [String: Any],
              Set(item.keys) == Set(["payload_b64", "signature_b64"]),
              let statement = item["payload_b64"] as? String,
              let signature = item["signature_b64"] as? String,
              let payload = canonicalBase64(statement, max: 512),
              let sig = canonicalBase64(signature, max: 64),
              sig.count == 64 else {
            throw Failure.invalid("BAD_SIGNED_ENVELOPE")
        }
        let key: Curve25519.Signing.PublicKey
        do {
            key = try Curve25519.Signing.PublicKey(
                rawRepresentation: Data(K24Pinned.publicKey))
        } catch { throw Failure.invalid("INVALID_PINNED_ED25519_PUBLIC_KEY") }
        let signed = domain + payload
        guard key.isValidSignature(sig, for: signed) else {
            throw Failure.invalid("EXTERNAL_ED25519_SIGNATURE_INVALID")
        }
        // Independent Ed25519 statement is authenticated; a correct
        // measurement must also match the statement byte-for-byte.
        guard payload == signedPayload(measured) else {
            throw Failure.invalid("RUNTIME_SELF_TEXT_DIFFERS_FROM_SIGNED_EXPECTED")
        }
        // Negative controls run on RAM COPIES; do not modify live pages.
        var bad = measured.text
        bad[bad.startIndex] ^= 1
        let truncated = measured.text.dropLast()
        guard sha(bad) != measured.digest,
              sha(Data(truncated)) != measured.digest else {
            throw Failure.invalid("MUTATION_OR_TRUNCATION_UNEXPECTEDLY_ACCEPTED")
        }
        var forged = payload
        forged[forged.startIndex] ^= 1
        guard !key.isValidSignature(sig, for: domain + forged) else {
            throw Failure.invalid("FORGED_SIGNATURE_UNEXPECTEDLY_ACCEPTED")
        }
        return [
            "DD_K24_SCHEMA=1",
            "DD_K24_SCOPE=OWN_RUNNING_MAIN_EXECUTABLE_TEXT_ONLY",
            "DD_K24_MAIN_UUID=\(measured.uuid)",
            "DD_K24_RUNTIME_TEXT_SHA256=\(measured.digest)",
            "DD_K24_EXTERNAL_ED25519=PASS",
            "DD_K24_SIGNED_EXPECTED_MATCH=PASS",
            "DD_K24_MUTATED_COPY=REJECTED",
            "DD_K24_TRUNCATED_COPY=REJECTED",
            "DD_K24_FORGED_STATEMENT=REJECTED",
            "DD_K24_SELF_SECURITY=NOT_PROVEN",
            "DD_K24_COMPLETE=PASS_LAB_ONLY"
        ].joined(separator: "\n") + "\n"
    }
}

private final class K24Controller: UIViewController, UIDocumentPickerDelegate {
    private let output = UITextView()
    private var measured: K24.Sample?
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "K24 Running Text Lab"
        view.backgroundColor = .systemBackground
        let intro = UILabel()
        intro.numberOfLines = 0
        intro.text = "K24 • measure OWN executing __TEXT,__text\n" +
            "External Ed25519 statement required to verify; no anti-tamper claim"
        intro.font = .preferredFont(forTextStyle: .headline)
        let measure = UIButton(type: .system)
        measure.setTitle("Measure actual running app code", for: .normal)
        measure.addTarget(self, action: #selector(runMeasure), for: .touchUpInside)
        let importReference = UIButton(type: .system)
        importReference.setTitle("Import EXTERNAL signed statement (.json)", for: .normal)
        importReference.addTarget(self, action: #selector(openFile), for: .touchUpInside)
        let share = UIButton(type: .system)
        share.setTitle("Share full diagnostic text", for: .normal)
        share.addTarget(self, action: #selector(export), for: .touchUpInside)
        output.font = .monospacedSystemFont(ofSize: 10, weight: .regular)
        output.isEditable = false
        output.text = "Measure first. Signature PASS is unavailable without separately signed statement and pinned public key."
        let stack = UIStackView(arrangedSubviews: [intro, measure, importReference, share, output])
        stack.axis = .vertical
        stack.spacing = 12
        stack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor, constant: 16),
            stack.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor, constant: -16),
            stack.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 18),
            stack.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -12)
        ])
    }
    @objc private func runMeasure() {
        do {
            let m = try K24.measureRunningSelf()
            measured = m
            output.text = K24.lines(m)
        } catch K24.Failure.invalid(let code) {
            measured = nil
            output.text = "DD_K24_COMPLETE=FAIL\nDD_K24_ERROR=\(code)\n"
        } catch {
            measured = nil
            output.text = "DD_K24_COMPLETE=FAIL\nDD_K24_ERROR=UNEXPECTED_RUNTIME_ERROR\n"
        }
    }
    @objc private func openFile() {
        guard measured != nil else {
            output.text = "DD_K24_COMPLETE=FAIL\nDD_K24_ERROR=MEASURE_BEFORE_IMPORT\n"
            return
        }
        let picker = UIDocumentPickerViewController(
            forOpeningContentTypes: [UTType.json], asCopy: true)
        picker.delegate = self
        present(picker, animated: true)
    }
    func documentPicker(_ controller: UIDocumentPickerViewController,
                        didPickDocumentsAt urls: [URL]) {
        guard let url = urls.first, let previous = measured else {
            output.text = "DD_K24_COMPLETE=FAIL\nDD_K24_ERROR=NO_SIGNED_STATEMENT\n"
            return
        }
        let authorized = url.startAccessingSecurityScopedResource()
        defer { if authorized { url.stopAccessingSecurityScopedResource() } }
        do {
            // Never trust only the earlier button snapshot: sample memory
            // again at the actual signed-statement verification point.
            let now = try K24.measureRunningSelf()
            guard previous.uuid == now.uuid &&
                  previous.digest == now.digest &&
                  previous.text.count == now.text.count else {
                throw K24.Failure.invalid("SELF_TEXT_CHANGED_BETWEEN_MEASURE_AND_VERIFY")
            }
            let bytes = try Data(contentsOf: url)
            output.text = try K24.verifyEnvelope(bytes, measured: now)
        } catch K24.Failure.invalid(let code) {
            output.text = "DD_K24_COMPLETE=FAIL\nDD_K24_ERROR=\(code)\n"
        } catch {
            output.text = "DD_K24_COMPLETE=FAIL\nDD_K24_ERROR=IMPORT_READ_OR_VERIFY_FAILED\n"
        }
    }
    @objc private func export() {
        let sheet = UIActivityViewController(activityItems: [output.text ?? ""],
                                             applicationActivities: nil)
        sheet.popoverPresentationController?.sourceView = view
        present(sheet, animated: true)
    }
}

@main final class K24App: UIResponder, UIApplicationDelegate {
    var window: UIWindow?
    func application(_ app: UIApplication,
                     didFinishLaunchingWithOptions options:
                     [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        window = UIWindow(frame: UIScreen.main.bounds)
        window?.rootViewController = UINavigationController(rootViewController: K24Controller())
        window?.makeKeyAndVisible()
        return true
    }
}
