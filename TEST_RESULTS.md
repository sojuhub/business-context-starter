# Verification scope

Run the current checks with `python3 -m unittest discover -s tests -v` on Python
3.10 or newer. These test local bridge behavior and static package contracts.
They do not invoke an AI host, authenticate a provider or send a message.

Separate actual Codex instruction-mode checks used three fictional businesses
on 2026-09-19. Their limits and opt-in reproduction command are in
[LOCAL_VALIDATION.md](docs/LOCAL_VALIDATION.md). Source publication does not
constitute a new tagged release or live-provider certification.

Historical reports live in docs/HISTORICAL_TEST_RESULTS.md. They describe the
older package, not the current public commit. Current host acceptance items are
in docs/ACCEPTANCE.md; unrun items remain unverified.

Connection-first update, 2026-09-20: 91 local tests pass, including a new
18-scenario source-receipt consistency check and its subprocess exit codes.
It covers setup-only, absent scope, mismatched account/scope, metadata-only,
partial/failed reads, fixture mode, empty search and explicit deferral. These
are fictional records, including the cases declaring `live`; no real account
or Composio authentication is established by those tests. The start skill's
frontmatter and internal links also pass local validation.

Scoped native Gmail check, 2026-09-20: after explicit owner authorization,
account identity, bounded ID search and actual HTML body retrieval succeeded.
The selected records were website-delivery tests explicitly excluding customer
inquiries/orders; they are not evidence of real customer workflows or policies.
The private source manifest and completion checker agreed on the bounded read.
No send, label, read-state or attachment tool was called. Minimal receipts remain
outside this repository; no account identifiers, message IDs or bodies are published.
This does not verify Composio OAuth, full business onboarding or fresh-session reuse.

Required discovery update: full-completion and source-only regression tests pass
on Python 3.12. The suite contains 92 tests. Two local full runs each encountered
one existing 10-second bridge subprocess timeout (large-plan, then rollback),
so neither full run is reported as all-green. Both timeout cases passed on
targeted retries. No timeout policy was weakened; use the commit-specific GitHub
CI results for the independent full-suite outcome.

The full check now requires the service interview/inventory, confirmed browser
candidates or accepted fallback, seven reviewed knowledge areas, no material gaps,
selective retention, current saved-file hashes, owner approval and a distinct
fresh-session draft with evidence tied to pages actually read. Stop/defer, changed
files and index-only reuse cannot pass. These cases use fictional receipts and
validate logic rather than independent semantic truth or actual browser access.

Rechecking the earlier private native Gmail receipt now reports source-complete
and onboarding-incomplete, correctly preserving its limited read success without
promoting it to complete business understanding. No new private account or browser
collection was performed for this update.
