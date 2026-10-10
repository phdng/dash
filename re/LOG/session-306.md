# Session-306 — LocaleFlow unused documentary functions

Theos arm64 CI reported `-Werror,-Wunused-function` for `DDVersionDeviceNotes`, `DDWriteLanguage`, `DDReadLanguage`, and `DDLanguageObservers` in `LocaleFlow.m`. Workspace search found no call sites. They contained documentation only except `DDReadLanguage`, which returned an unused approximation (`@"en"`). Removed the four static function wrappers while retaining notes. The actual executable locale APIs remain unchanged.

Added regression guard in `scripts/verify_reconstruction.py` to reject these documentation-only static declarations. PASS: `python scripts/verify_reconstruction.py`, `python -m py_compile scripts/verify_reconstruction.py`, `git diff --check` (only LF/CRLF warnings). Real Theos arm64 CI still required; no automatic push.
