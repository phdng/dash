# Session-308 — SiriProbe documentary hook compile exclusion

Theos arm64 CI reported 11 `-Werror,-Wunused-parameter` diagnostics on nine never-wired Siri hook synthesis helpers: DDProbeGate, DDProbeLog, DDPressEligible, DDShouldSwallow, DDHookActivationRequest, DDHookButtonDown, DDHookButtonUp, DDHookLongPress, DDHookPrewarm, DDHookHandleRequest. The entire documentary region (installer through rescan) is now bounded by `#if 0`/`#endif`, preserving analysis and excluding unimplemented hooks without changing the executable Siri probe functions above it. The script verifier checks the explicit documentary guard.

Local verification PASS: `python scripts/verify_reconstruction.py`, `python -m py_compile scripts/verify_reconstruction.py`, `git diff --check` (LF/CRLF warning only). Exact Theos arm64 CI pending. Do not push.
