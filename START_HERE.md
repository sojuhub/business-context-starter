# Start Business Onboarding

One repository-read workflow for Codex, Claude Code, Hermes and OpenClaw.
This is a public instruction alpha. Native plugin loading and end-to-end behavior
in every host are not verified by the package's offline tests.

## For the business owner

Paste [the short setup instruction](COPY_PROMPT.md) into the AI tool you already
use. It will guide you. Start with a website, a selected document, or a few
sentences about your business. You do not need to choose a technical setup.

## Retrieve and prepare the starter

For the agent: handle these details yourself using your existing GitHub, network
and filesystem tools. Do not ask the owner to choose between host-specific paths.

1. Use only `https://github.com/sojuhub/business-context-starter`. If the matching
   package is already available, reuse it without overwriting local changes.
2. Otherwise resolve the repository's current default-branch HEAD to a full commit
   SHA once, record it, and retrieve START_HERE.md and referenced package files at
   that SAME commit. Use a host-approved checkout or file fetch. A stable public
   URL is the customer's entry point; the resolved revision is the run's source.
3. Inspect the files before executing anything. The default route is reading the
   instructions, not installing a native plugin or creating another app. There is
   no application dependency install. Python 3.10+ is needed only if using the
   existing optional local context bridge. No curl-to-shell or global installs.
4. Preserve the selected project and its instructions. Prepare public starter
   files in a separate task-local folder if needed; keep private company knowledge
   out of the starter checkout and plugin caches. Reuse an existing business wiki.
5. If the host cannot read the repository or write local files, explain the one
   missing capability and offer the same downloaded package. Do not guess that a
   different repository or an unverified install succeeded. Continue conversation
   from the approved source material when possible.
6. Once the files are available, follow the same onboarding below in all four
   agents. Ask only about missing business context, private-source scope or a
   consequential change. Do the supported setup work; leave only login/consent
   actions to the account holder when necessary.

## For the agent reading this file
This is an onboarding run, not a request to invent an AIOS application or a migration platform.
Use the existing files in this package. If the package cannot be found, ask for its approved folder or exact repository reference; do not search for similarly named projects and substitute one.

1. Read `plugins/business-context-starter/skills/start/SKILL.md`. Read the linked source, workspace, continuity and prior-context reference only as needed.
2. Preserve the host's existing instructions, permissions, tools, account connections and memory controls. Do not make native plugin installation a prerequisite to a useful first result. Label this route `instruction-mode` unless native loading is actually verified.
3. Establish the real company and selected project using already supplied information. Use the current project when appropriate; do not treat this public starter checkout as the private business workspace. Ask for approved private input paths and output destination before reading or writing them.
4. Offer prior-context reuse as part of the same onboarding. Existing curated company files come first. When switching agents, inspect which native import is supported and preview its scope before any approved change. Otherwise use the current host's approved access or user-selected exports. Never assume ChatGPT web memory is Codex local memory. Never rewrite generated native memory stores.
5. Discover available source tools and account labels before asking for another document. Use existing evidence for a short company preview, then propose one bounded private-source scope. Follow `plugins/business-context-starter/references/CONNECT_SOURCES.md`: reuse a sufficient existing connector, execute approved reads, and offer a separately approved provider only for a real gap. Continue after scope approval without per-record questions. A first document is optional; a blocked source must not block others. Repository setup is only "starter prepared", not completed onboarding.
6. Apply the source-handling evidence checks and automatically include qualifying facts in one reviewable business brief; ask only about consequential ambiguity/conflicts. After owner review, merge accepted facts, tone, policies, decisions and workflow references into the existing company wiki. Create the minimum private Markdown workspace only if there is none. A fresh workspace never means erasing the old setup.
7. Show review items and preserve uncertainty. Use the continuity helper only after a necessary project-only diff is reviewed and approved. Never overwrite project instructions, create a priority override, clear memories or change global configuration.
8. Produce one useful draft. Guide a new-session test of the saved context and a test of unrelated existing work. Do not report these tests passed unless they actually ran.

Stop before sending, posting, changing bookings, deleting originals, publishing a repository, deploying a site or scheduling a watcher. Authentication is performed through the genuine host/provider flow, never by collecting credentials in chat.

## Product boundaries
A pasted prompt starts a guided process. It does not grant account access or guarantee unattended setup.
Private local output does not mean local-only model processing. Minimize data and explain the approved processing path.
Existing plugin metadata remains for optional later installation; see `docs/OPTIONAL_PLUGIN.md`. Do not install duplicate skill copies into one host.
