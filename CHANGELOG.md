# Changelog

## 0.4.0 — public instruction alpha
- Published the existing Business Onboarding repository as the single public entry point.
- Added one short repository-read prompt for Codex, Claude Code, Hermes and OpenClaw.
- Kept native plugin loading, account connections and end-to-end host behavior explicitly unverified.
- Removed the obsolete new-private-repository upload route from the public package.

## 0.3.2 — private-upload preparation
- Historical release notes for the private pilot; the publisher files from this release are not part of the public package.
- Reproduced the original 38 local tests.
- Fixed large-instruction receipt/plan size handling and preflight output limits.
- Reject malformed JSON state/plan objects without an unhandled traceback.
- Added real subprocess bridge tests and mocked private-publication safety tests.
- Added an explicit hash-allowlisted, new-private-repository publisher and CI.
- No live account, model, Mac host, remote repository or CI success is claimed.

# Changes

## 0.3.1 — Copy-paste first; reuse prior AI work
- The owner pastes one prompt. Plugin installation is optional and developer notes are moved out of the primary path.
- Existing authoritative company knowledge is preferred. A clean workspace does not mean deleting prior memories or configuration.
- Selected prior chats, memory summaries and native agent imports are part of onboarding with explicit limits, provenance, review and deduplication requirements.
- The existing private Markdown structure and project bridge are retained; no graph service, new app or migration engine is introduced.
- Public repository bootstrap is a release-gated template because no approved repository URL or published commit exists yet.
- Changes are instructions, documentation and static contract tests. Real import parsers, authentication and behavioral verification are not implemented by this update.
