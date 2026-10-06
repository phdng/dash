# LOG/session-080.md
_Date: 2026-10-06. Objective: continue after session-079 GitHub Actions build GREEN; promote the exact aux-scene normalization/capability/state boundary without instantiating private SpringBoard scene/view objects._

## R-078 — aux-scene pre/private state boundary

Directly re-read:
- `3C368.c` createAuxSceneForBid:native:orient:
- `3C808.c` teardownAuxScene
- `3E4A8.c` hosted-bid conflict gate
- `3E590.c` orientation-mutation capability
- `3ECD0.c` setter method-signature validator
- `3E428.c` aux generation/state reset
- `3C918.c` / `3C934.c` aux getters

### Exact preconditions
The original rejects before private class/application lookup when:
- bid length == 0;
- native width < 1 or native height < 1;
- private `self->_auxVC` already exists;
- `3E4A8` says the bid exactly matches any non-empty hosted slot whose CarPlay-UI flag is OFF.

Promoted:
- `DDHostMirrorRejectsAuxBundle` mirrors 3E4A8 over the reconstruction host-slot arrays.
- `DDPrepareAuxSceneCandidate(..., auxControllerAlreadyExists)` takes the private controller-exists condition explicitly instead of inventing a reconstruction controller.

### Exact orientation/native-size normalization
Only when requested orientation is 3 or 4 and `UIApplicationSceneSettings` does not expose `_interfaceOrientation`:
- probe 3E590 capability;
- if capability exists, leave requested orientation and native size unchanged;
- if capability does not exist:
  - orientation becomes 0;
  - width = min(native width, native height);
  - height = max(native width, native height).

3E590 is reconstructed by runtime introspection:
- `FBScene` must have `updateSettingsWithBlock:`;
- its type encoding must return void and contain `@?`;
- `UIMutableApplicationSceneSettings` must have `setInterfaceOrientation:`;
- 3ECD0 contract is preserved: exactly 3 ObjC method arguments, void return, third argument type q/Q.

Promoted:
- `DDClassHasVoidIntegerSetter`.
- `DDAuxSceneOrientationMutationSupported`.
- `DDAuxScenePreparation`.

No private framework is linked.

### Post-application-lookup commit boundary
Original 3C368 does **not** write qword_163D70/xmmword_163DD0/qword_163DE0 until:
- SBApplicationController exists;
- SBDeviceApplicationSceneEntity exists;
- SBAppViewController exists;
- `applicationWithBundleIdentifier:` returns a valid application.

Promoted:
- `DDCommitAuxSceneMirrorAfterApplicationLookup(..., applicationLookupSucceeded)`.
- Commit is impossible unless preparation is valid and the caller explicitly confirms private application lookup success.
- No re-check is silently added at commit time; original conflict/controller gates already happened before lookup.

Committed state:
- aux bid copy;
- normalized native size;
- normalized orientation;
- aux generation increment via 3E428 state subset;
- `swapEnabled = !fileExists(/var/tmp/duodash_kp_auxnoswap)`;
- `noAuxSID = fileExists(/var/tmp/duodash_kp_noauxsid)`;
- `noApplyDiff = fileExists(/var/tmp/duodash_kp_noapplydiff)`.

Promoted:
- `DDCurrentAuxSceneMirror()`.

### Teardown state half
3C808 clears aux bid/native size/orientation and then calls 3E428 again.

Promoted:
- `DDClearAuxSceneMirror()`.
- Because the reconstruction owns no private aux controller/view, empty aux-bid state is its no-op boundary.
- 3E428 generation increments and refreshes auxnoswap.
- noAuxSID/noApplyDiff are intentionally not cleared because original 3E428 does not clear byte_163DE8/byte_163DE9.

Explicit omissions:
- SBApplicationController / applicationWithBundleIdentifier: execution itself;
- SBDeviceApplicationSceneEntity creation;
- SBAppViewController construction/configuration;
- view acquisition/removal;
- private controller invalidate;
- requested mode/lifecycle flags.

## R-079 — pure aux desired-settings plan

Directly re-read:
- `3E604.c`
- `3E670.c`
- `3EA0C.c`
- `3EB9C.c`

3E604/3E670 eventually call private `auxSceneObject` and `updateSettingsWithBlock:`, so the executor is not promoted.

Pure 3E670 desired-state contract:
- aux bid must be non-empty;
- direct `UIApplicationSceneSettings._interfaceOrientation` support must be absent;
- aux orientation must be 3 or 4;
- native width/height must each be >= 1;
- desired orientation = aux orientation;
- when aux swap is enabled (default unless `duodash_kp_auxnoswap` exists):
  - desired width = native height;
  - desired height = native width;
- when swap disabled:
  - desired width = native width;
  - desired height = native height.

Promoted:
- `DDAuxSceneSettingsPlan`.
- `DDCurrentAuxSceneSettingsPlan()`.

### Exact applied/current-settings early-out
When the original has never successfully applied settings, it continues toward the executor.

When settings were previously applied:
- if no current settings object is available, return without update;
- otherwise compare current frame to desired frame:
  - abs(width delta) <= 0.5
  - abs(height delta) <= 0.5
- orientation is considered already acceptable when current orientation is 0 or equals desired orientation;
- if frame + orientation are already acceptable, return without update;
- otherwise continue toward executor.

Promoted:
- `DDAuxSceneSettingsNeedUpdate(plan, previouslyApplied, hasCurrentSettings, currentFrameSize, currentOrientation)`.

Explicit boundary:
- scene-geometry enable gate, private reentrancy flags, attempt count (<8), retry budget, `respondsToSelector(updateSettingsWithBlock:)`, block dispatch, and 3EA0C/3EB9C settings mutation remain private-executor scope.
- `40514` noapplydiff behavior remains tied to private settings mutation/re-read and was not approximated.

## Verification
- `python scripts/verify_reconstruction.py` PASS.
- `python -m py_compile scripts/verify_reconstruction.py` PASS.
- `git diff --check` PASS (Windows LF/CRLF warnings only).
- CatDesk standard verifier = NOT_CONFIGURED, expected for this Theos-only repo without Cargo.toml/package.json/Python project manifest.

Session-079 GitHub Actions build was GREEN per user. Session-080 Objective-C runtime-introspection/aux-state changes require the next pushed macOS CI compiler run.

## Next
R-080 after CI green:
- inspect exact 3C368 retry delays (0.1/0.5/1.5) plus 3E604/3E670/3EA0C generation, applied, in-flight, attempt-count and budget transitions;
- promote only data/state-machine descriptors or explicit caller-driven transition APIs;
- never invoke `auxSceneObject` or `updateSettingsWithBlock:`;
- never mark an apply successful unless an external caller explicitly reports the private executor result;
- keep 73E8/80D0 and full 7E908 unresolved until missing contracts are recovered.
