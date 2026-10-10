# Session-305 — CrashReporting unused documentary functions

CI reported `-Werror,-Wunused-function` on DDCrashReportSend, DDCrashMayCollect, DDCollectCrashReport and DDUploadCrashReport. These are uncalled reverse-engineering placeholders. Converted their wrappers into comments, preserving evidence. Also removed the orphaned helper DDCrashEndpoint whose sole caller was the placeholder upload function; executable DDCrashReportingEndpoint remains unchanged. No changes to real crash-reporting gates/queue logic.

Added verification guard rejecting these five static placeholders. Local PASS: reconstruction verifier, Python py_compile, git diff --check (LF/CRLF warning only). Theos arm64 build still requires CI. Do not push automatically.
