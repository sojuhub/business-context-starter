# Business Onboarding

You know your business. Give your AI the details it needs to help.

Business Onboarding guides your existing AI through learning your prices,
policies, customers and ways of working. You review what it learns and keep
readable business notes for later work.

[See the website](https://business-onboarding.sojulee.chatgpt.site) ·
[Try the examples](https://business-onboarding.sojulee.chatgpt.site/examples.html) ·
[Get help](https://business-onboarding.sojulee.chatgpt.site/contact.html)

## Start with one message

Copy this into **Codex, Claude Code, Hermes or OpenClaw**:

```text
Read https://github.com/sojuhub/business-context-starter, set it up in my current workspace, and guide me through business onboarding.
```

Your AI reads the starter and handles the available local setup. You answer the
business questions. No manual clone command, tool selection or plugin installation
is required for this instruction-based route.

**For agents:** begin with [START_HERE.md](START_HERE.md). Resolve and record one
repository revision and read the linked onboarding skill from that same revision.
Do not build another application. Keep private business records outside this repo.

## What happens next

1. **Tell it about your business.** A website, a selected document or a short
   explanation is enough to start. You choose any private material it may read.
2. **Check what it learned.** Review the facts, policies and missing information.
3. **Try it on your work.** Get one useful draft based on the approved information.
   Check that a new session can find the same business notes.

The agent reuses your project, instructions and working connections. It performs
supported setup itself, asking you for account login or consent when necessary.
It must report unavailable tools and unverified reads clearly.

## What this release does

This is a **public instruction alpha**. It provides the same repository-read
onboarding path for all four agents, a private workspace contract, synthetic
examples and a local project-link helper with plan/apply/rollback.

The shared instruction path does not mean native plugins or account connectors
are identical across hosts. **End-to-end host behavior remains unverified for live
business accounts and across all advertised hosts.** Local development has tested
saved-context retrieval in fresh Codex CLI sessions for three fictional businesses;
see [the exact scope](docs/LOCAL_VALIDATION.md). Offline unit tests alone do not
establish that result. See [remaining acceptance checks](docs/ACCEPTANCE.md).

The website shows simulated email and SMS workflows. This starter first prepares
business context and a reviewed draft; actual sending requires separately
configured tools and explicit permissions. Installing or reading this package
does not authorize messages, bookings, publication or background jobs.

## What you keep

- Readable business notes and policies with their sources.
- Unknowns and conflicting information left visible for your review.
- One useful draft and a record of what was actually connected or read.
- Your existing project and unrelated coding workflow.

Live orders, bookings and payments remain in the systems that own them. Business
notes are not a second transaction database. A local file does not mean the AI
model processes data only on your device.

## For developers

The main route is [START_HERE.md](START_HERE.md) and the existing
[start skill](plugins/business-context-starter/skills/start/SKILL.md).
The [use-business-context skill](plugins/business-context-starter/skills/use-business-context/SKILL.md)
handles later business work without repeating onboarding.

The optional bridge uses Python 3.10+ and the standard library:

```sh
python3 -m unittest discover -s tests -v
python3 plugins/business-context-starter/scripts/context_bridge.py --help
```

The optional [context compiler](plugins/business-context-starter/references/COMPILE_CONTEXT.md)
materializes a source-linked model plan in an approved private directory and
refuses to overwrite owner edits. Developer-only [provider fixtures](docs/PROVIDER_FIXTURES.md)
exercise collection mappings without accounts. [Runtime checks](docs/LOCAL_VALIDATION.md)
use fictional inputs and explicitly opt in to actual Codex inference.

It proposes additive changes to existing project instructions. Review the diff
before applying it. It does not grant filesystem access or install connectors.
See [optional native packaging](docs/OPTIONAL_PLUGIN.md),
[source handling](plugins/business-context-starter/references/SOURCE_HANDLING.md),
[release verification](docs/RELEASE_CHECKLIST.md), and
[the fictional cafe brief](examples/alder-cup-owner-brief.md).

## License and provenance

MIT. Upstream notices are retained in the package's `third_party` directory.
See [sources](docs/SOURCES.md). Business Onboarding is independent and is not
endorsed by the featured AI providers. No private business data belongs here.

For setup questions: [business@sojulee.com](mailto:business@sojulee.com).
