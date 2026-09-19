# Public instruction release checks

Canonical repository: https://github.com/sojuhub/business-context-starter
The short customer prompt in COPY_PROMPT.md points to this repository.
The agent resolves the current HEAD once and reads the entry and package at the
SAME commit. Record that SHA in the private run receipt. Do not silently mix
moving-branch files during a run. No curl-to-shell or global bootstrap.

## Maintainer checks

- Select an explicit public allowlist; preserve MIT notices.
- Exclude handoff/session records, local hosting metadata, verification files,
  private account data, credentials and unreviewed local artifacts.
- Verify every README and skill link resolves within the published package.
- Run local unit/contract checks in the clean release checkout.
- Regenerate RELEASE_MANIFEST.json from that exact public file set. Its own hash
  is excluded; the Git commit binds the manifest and all content together.
- Push to the existing repository only. After making it public, verify README.md,
  START_HERE.md, COPY_PROMPT.md and linked skills at the actual pushed SHA without
  authentication. Record that SHA in the publication receipt.
- Keep the website's prompt and repository visibility copy in sync.

## What requires separate host evidence

A common instruction entry is not proof of native plugin loading, provider setup,
private reads, sending or fresh-session reuse. Test each claimed host behavior in
that host with a fictional business before advertising it as verified. Keep
account tests and real sends within explicit user authorization.
