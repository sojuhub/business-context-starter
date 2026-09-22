# Local fictional-business validation

This describes source development after the public 0.4.0 instruction release.
It is not a new tagged release or a live-account connector certification.

## What is implemented

- The host model classifies selected evidence into company, tone, policy,
  product and workflow candidates. The bundled `compile_context.py` validates
  company/source identity and exact quotes and writes the existing private
  Markdown layout. It leaves uncertain information visible for review.
- A repeat run preserves identical output. A changed generated page stops a
  stale plan before writing, protecting owner corrections. This is conflict
  detection, not an automatic merge of edited policies.
- Google Drive, Gmail and Square joined-fixture mappings feed the existing
  bounded collection/storage checks. See [provider scope](PROVIDER_FIXTURES.md).
  No OAuth client, live Composio wrapper or background sync is installed.

## Actual-host evidence — 2026-09-19

Codex CLI 0.155.1 ran separate instruction-mode sessions against three fictional
businesses. Each used seven synthetic source records. The parent compiled the
model's plan, simulated owner review and an ongoing correction, and attached
the private reading map through the existing bridge.

| Fictional business | Observed saved-policy read in a fresh session | Corrected value present in draft |
| --- | --- | --- |
| Fir Cup, cafe | Yes | 37 hours of preorder notice |
| Sample Film, manufacturing | Yes | 43% deposit |
| Harbor Repair, service | Yes | CAD 93 diagnostic fee |

Each classification retains exact evidence quotes and source IDs. Known
unapproved AI suggestions and customer requests were not promoted to policy.
Source commands were not executed in the observed runs. Saved command traces
show the actual policy-file reads; model self-report alone is not the evidence.

Three first-contact probes produced a business preview and a relevant next
question without requiring a website or login or repeating the supplied tools.
One unrelated arithmetic prompt answered correctly without reading company
files. These are bounded probes, not a complete beginner-usability study.

The service draft initially overgeneralized a diagnostic fee into a blanket
no-free-repair policy. The compiler's policy notes and the reuse skill were
clarified to preserve stated scope. The targeted fresh-session retest passed:
it retained CAD 93 and declined to promise free repair without asserting a
blanket prohibition. Root prose review confirmed this bounded correction.
Do not treat presence of the corrected number alone as
proof of overall writing quality.

The host calls used read-only execution with user configuration omitted to
avoid loading account connections. This is not OS-level read confinement.
The receipt verifier audits observed `cat`, `pwd` and bounded project file-list
commands and rejects other tools or paths for explicit review. The source
business data is fictional; inference still uses the configured Codex service.

Not evaluated: real owner quality approval, native plugin loading, Claude,
Hermes or OpenClaw runtime behavior, live API extraction, real email/SMS sends,
all possible industries, or all provider schemas.

## Reproduce

Offline checks need Python 3.10+ and the standard library:

The 2026-09-19 local run passed 90 tests; see [current results](../TEST_RESULTS.md)
for later checks. The existing 0.4.0 release tag does not certify this newer
implementation.

```sh
python3 -m unittest discover -s tests -v
```

An actual Codex instruction-mode run is opt-in, uses existing CLI authentication
and may incur model usage. Choose a new dedicated output directory outside all
source repositories; the runner refuses to overwrite an existing case:

```sh
python3 scripts/verify_onboarding_runtime.py \
  --output /approved/private/test-run --run-codex
```

Audit saved results without further model calls:

```sh
python3 scripts/verify_onboarding_runtime.py \
  --output /approved/private/test-run --verify-saved
```

The runner saves prompts, schema-constrained output, command events, source
snapshots, generated pages, bridge receipts and separate session IDs. Root
review of the prose and questions remains necessary; those artifacts never
stand in for a real owner's approval. Unit tests that mock this runner verify
its mechanics and are not actual-host evidence.

Execution reference: [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode).

## Isolated browser and interview validation — 2026-09-21

Source under test: `66950e1e202b95eecc6534970eb1b54522e2eb98`.
Separate native headless browser profiles on G14 Windows and Ubuntu WSL used
loopback pages for fictional Sample Film Mail, Drive and CRM, plus an excluded
personal-page placeholder. No existing user profile, real service account or
canonical company wiki was read. This was profile isolation, not a VM or an
actual Chrome Context connector. The task-specific browser/interview harness and
raw receipts remain outside the public package; the reproduction command above
runs the earlier fixture harness, not this cross-host scenario.

| Observed check | Windows Chrome 153.0.8010.53 | WSL Chromium 136.0.7103.25 |
| --- | --- | --- |
| Discover actual open tabs and browser-written recent history | PASS | PASS |
| Discover a closed CRM tab from history | PASS | PASS |
| Read three fictional services selected by a synthetic owner | PASS | PASS |
| Separate concurrent profiles' cookies and localStorage | PASS | PASS |
| Separate stored history; preserve localStorage after restart | PASS | PASS |
| Preserve cookies after restart | FAIL: OS encryption error `0x5` | PASS |
| CDP close response and browser parent exit 0 | PASS | PASS |
| Two completion-check regression tests | PASS | PASS |

History discovery read at most 20 entries from new test profiles and combined
them with observed open tabs. The personal placeholder was excluded from source
collection. A newer cached WSL Chromium build did not exit promptly after
`Browser.close`; only the version shown above passed the final run. No browser
security settings or real authentication were changed to bypass either failure.

On WSL, nine actual Codex calls exercised seven staged interview steps and two
initial/stop probes. The model asked about the most-used service and its purpose,
other services beyond installed connectors, scoped collection, seven knowledge
areas, conflicting 25%/43% deposit terms, and whole-brief owner review. It retained
the synthetic owner's narrowed 30-day, five-record-per-service scope. The stop
probe deferred with no source approval or tool use.

The scenario supplied fixed owner answers and explicit stage instructions, carrying
the transcript between separate calls. Browser fixtures were prepared and selected
before the interview; the model received bodies only after its synthetic scope
approval. This does not prove autonomous long conversations, native session resume,
or authorization enforcement across a live provider pipeline.

The first browser-to-context run omitted owner-only workflow facts because the
test integration supplied browser records but left interview answers in the
transcript. Adding owner answers as separately identified evidence before
classification fixed that input omission without changing the compiler. The final
run produced 18 source-linked claims, eight citing owner answers, and saved both
CRM as the most-used service and the quote-approval/deposit-request sequence.
A distinct fresh Codex session read saved context pages and used the current 43%
deposit and that workflow in an unsent customer draft, without promising Friday
delivery. The instruction references now require this interview-evidence path;
one offline intake-to-compilation regression checks its saved facts and provenance.

The production completion check remained `onboarding-incomplete`, as expected for
fictional sources and synthetic owner approval. Native plugin loading, actual
Chrome Context, live service authentication and unscripted owner interviews remain
unverified. Private final receipt SHA-256:
`a61d603c3f301089138a8fe2a5193a5ad28e65f68069b23c1da74c54bcd063e2`.
