# Session-356 — Switch guard and two-pane wrapper regression coverage

Started clean on chore/reconstruction-build-ci. Modified compiled Objective-C `HostFlowAdapter.m` self-test:
- Verify `DDHostSplitBids` preserves two pane positions and nil->empty string semantics for either/both missing identifiers.
- Individually inject each of the four early-guard refusal categories (interaction, consistency, slot capacity, host phase), assert the exact diagnostic bit and restore the baseline before later tests.
- No private calls, live host operation or tweak-startup tests added.

Local checks: `python scripts/verify_reconstruction.py` PASS (30 modules), `git diff --check` PASS. Objective-C runtime tests/macOS and arm64 Theos CI not executed. No commit/push.
