# LOG/session-141.md
_Date: 2026-10-07. Objective: continue after user-confirmed GREEN for session-140 commit `ca03cf3`; decode and promote exact data-only `3815C` plist-reader exception behavior, verify, and commit locally without pushing._

## Start state
- Branch `chore/reconstruction-build-ci`.
- HEAD `ca03cf3`.
- Workspace clean and synchronized with origin.
- User confirmed session-140 macOS CI/compiler GREEN.

## Target
- Function: `sub_3815C(path)`.
- LSDA: `0x1141AC`.
- Role: read plist bytes from path, deserialize, return retained NSDictionary/autoreleased result or nil.

## Exact LSDA table
1. `0x3815C..0x38184` -> no landing.
2. `0x38184..0x38194` -> `0x38208`, action 5.
3. `0x381A4..0x381DC` -> `0x3820C`, action 5.
4. `0x381DC..0x38240` -> no landing.

`0x38208` aliases the common typed catch at `0x3820C`.

Expected catch:
- compare discriminator with expected type;
- begin catch;
- end catch;
- set result register x22 = nil;
- release retained input x19;
- return nil.

Nonmatching type resumes unwind at `0x3823C`.

## Protected site 1 — NSData file read
`0x38184..0x38194` covers:
- `+[NSData dataWithContentsOfFile:]`;
- retain-autoreleased result.

Boundary:
- `mov x20,x0` is at `0x38194`, immediately outside the protected range.

Therefore an expected exception:
- returns nil;
- still releases input x19;
- does not establish committed NSData x20 cleanup-bypass metadata.

## Protected range 2 — plist decode and dictionary type check
The second LSDA range `0x381A4..0x381DC` spans two semantic sub-sites.

### Property-list decode sub-site
`0x381A4..0x381C0` covers:
- `+[NSPropertyListSerialization propertyListWithData:options:format:error:]`;
- retain-autoreleased plist result.

At entry:
- retained NSData x20 is already committed.

Expected exception:
- returns nil;
- bypasses normal NSData release at `0x381FC`;
- no plist x21 commit is guaranteed before every throw.

### Dictionary type-check sub-site
From `0x381C0`:
- `mov x21,x0` commits retained plist;
- class lookup for NSDictionary;
- `isKindOfClass:`.

Expected exception in this later sub-site:
- returns nil;
- bypasses retained plist release at `0x381EC`;
- bypasses retained NSData release at `0x381FC`;
- still releases input x19.

No local retry, alternate parser, or fallback object is synthesized.

## Promoted runtime contract
Added:
- `DDPropertyListReaderExceptionSite`:
  - `DataRead`;
  - `PropertyListDecode`;
  - `DictionaryTypeCheck`;
  - `UnprotectedRange`.
- `DDPropertyListReaderExceptionOutcome`.
- `DDResolvePropertyListReaderExceptionOutcome(site)`.

Data-read:
- swallow expected exception;
- return nil;
- continue input cleanup;
- no committed NSData release-bypass claim.

Property-list decode:
- same nil fallback;
- retained NSData definitely committed;
- NSData release could be bypassed;
- decode may already have started.

Dictionary type check:
- same nil fallback;
- retained NSData + retained plist definitely committed;
- both local releases could be bypassed.

Unprotected:
- propagates.

## Explicit exclusions
R-140 does not:
- read files;
- deserialize property lists;
- perform live class/type checks;
- mutate real retain/release ownership;
- synthesize/catch exceptions;
- execute unwind machinery.

## Verification
After runtime/verifier edit:
- `python scripts/verify_reconstruction.py` -> PASS.
- `python -m py_compile scripts/verify_reconstruction.py` -> PASS.

Final project verification and `git diff --check` are run immediately before commit.

## Scout for next batch — 37A7C
Next earlier LSDA-bearing function:
- `37A7C -> LSDA 0x11418C`.
- Role: keyboard-lost recovery / rebuild coordination.

Exact table:
1. `0x37A7C..0x37AD0` -> no landing.
2. `0x37AD0..0x37AEC` -> `0x37C20`, action 5.
3. `0x37AEC..0x37C40` -> no landing.

Protected range:
- `+[DDz2 shared]`;
- retain-autoreleased DDz2;
- `keyPaneSceneSummary`;
- retain-autoreleased summary.

Expected catch at `0x37C20`:
- begin/end catch;
- set x20 to fallback `&stru_146AD8` (empty/default summary);
- branch to `0x37B18`;
- continue NSFileManager marker check and keyboard-lost rebuild logic rather than returning.

Sub-site timing for R-141:
- shared-acquisition exceptions can occur before retained DDz2 x21 commit;
- summary-acquisition exceptions occur with x21 committed and can bypass DDz2 release;
- a retained summary temporary may have been produced before x22 commit, so its local release can also be bypassed;
- catch continuation intentionally keeps recovery flow alive with fallback summary.

Nonmatching type resumes unwind at `0x37C3C`.
The non-main-thread dispatch path and later rebuild/cleanup paths are unprotected.

## Scout after R-141 — 37924
The next earlier LSDA-bearing function is `37924 -> 0x114178`.
It has one catch-all action-1 range `0x3793C..0x37958 -> 0x37968` around:
- `+[DDz1 shared]` + retain;
- `noteCarPlayUIStatus:gen:ok:`.

Landing begin/end-catches and returns immediately. This is a compact R-142 candidate after R-141.

Known unresolved remain:
- `73E8/80D0`;
- full `7E908`;
- jailbroken-device smoke testing.
