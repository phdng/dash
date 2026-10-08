# LOG/session-212.md
_Date: 2026-10-08. Objective: leave picker/UI mutation work and promote exact Keyinput secure-field gate 45568 as a standalone executable helper without compiling KeyinputRelay hooks._

## Start state
- Branch chore/reconstruction-build-ci.
- HEAD 5330d5c.
- Working tree clean; branch ahead 27.

## Exact 45568 semantics
- Retain input field.
- Nil field => false.
- Non-nil field that does not respond to `isSecureTextEntry` => true.
- If selector exists, call it.
- `isSecureTextEntry == YES` => false.
- `isSecureTextEntry == NO` => true.
- Release input and return the gate result.

## Observed consumers
The helper is called from the Keyinput focus path `4B90C`, publish path `4C000`, and apply path `44B1C`, making it the common secure-field admission boundary.

## Executable promotion
Added standalone compiled `KeyinputGate.m` with `DDKeyinputFieldMayRelay(id field)` and exported it in `DuoDashShared.h`. Added the module to the Makefile target and verifier.

## Boundary
The synthesis-only `KeyinputRelay.m` remains uncompiled. No keyboard hooks, relay plist IO, Darwin observers, card state, teardown/recovery, or KeyApp assumptions are enabled.

## Next
After compiler green, inspect another pure Keyinput helper only if it can be isolated from relay globals/private hooks; otherwise switch subsystem.