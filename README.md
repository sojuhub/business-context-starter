# Business Context Starter

**Bring what your AI already knows about your business into the work you do next.**

v0.3.2 — copy-paste-first local pilot, not a published or end-to-end validated product.
First acceptance target: MacBook Codex. Product and business outputs: English.

## Start with one prompt
For this local pilot, open the extracted folder in Codex and paste:

```text
Read START_HERE.md in this Business Context Starter folder and guide me through setup in English. Run the existing onboarding; do not build another app or require plugin installation first.

Reuse my current project, instructions, skills, connections and company knowledge. Offer to bring in relevant prior AI conversations or memories using supported imports or exports; explain what is and is not available, and do not scan unrelated history.

Ask before private reads or configuration changes. Keep business knowledge private, source-linked and separate from this public package. Show one useful business result, then guide a fresh-session check without disrupting unrelated work. Ask only for missing information. Do not send, post, delete, publish or enable background jobs.
```

The public release will replace the local-file opening line with the actual reviewed, commit-pinned repository entry point. No public URL has been created. Maintainers: see `docs/RELEASE_CHECKLIST.md`; do not ship an OWNER/REPO placeholder to users.

## What happens
Reuse the selected business setup → bring in approved prior AI context and business sources → review the smallest useful company wiki → create one useful result → reuse the context in later work.

Use an existing company workspace by default. Offer a separate clean workspace only when requested or when there is no suitable one. Preserve originals and prior memories in either route.
Prior conversations are evidence, not a current policy database. AI suggestions are not owner decisions. Native imports and exports are reused where available rather than replaced by a new universal migration engine.

## What is reused
The v0.3 package structure, two internal skills, v0.2 continuity helper and original notices are retained. The plugin is an optional distribution form, not the user's first required step.
No new agent team, graph/vector service, custom OAuth server, chat application, global memory replacement or background watcher is added.

## What is implemented versus described
- Implemented: existing reviewed local project-bridge helper; copy-first entry instructions; prior-context handling procedure; minimal wiki contracts.
- Tested locally: see `TEST_RESULTS.md` for exact test results and limits.
- Not implemented: a universal export parser, account authentication UI, direct ChatGPT-memory API, graph engine, automatic sync, or SaaS.
- Not tested here: live accounts, native imports, real archives, plugin loading, model behavior, Mac fresh-session reuse or beginner usability.

## Privacy and ownership
Company files, exports, raw mail, credentials and customer records stay outside this public package and outside the plugin cache. Original archives are kept at approved private locations; only necessary evidence and reviewed knowledge are added to the working wiki.
The starter does not erase native memories or disable account controls. A project pointer is added only when needed and approved. Removing the starter does not delete company knowledge.

## Test locally
The bridge helper and tests require Python 3.10+; there are no new dependencies.
```sh
python3 -m unittest discover -s tests -v
```

## Optional distribution
Native plugin metadata is retained. Installation is neither account authorization nor proof of correct future behavior. See `docs/OPTIONAL_PLUGIN.md` for the earlier developer route and verify current host support before changing anything.

## Private GitHub upload
This delivery has **not** been uploaded from ChatGPT. The connected GitHub tool
exposes reads but no repository-create or file-write action in this session.
Use [PRIVATE_UPLOAD.md](PRIVATE_UPLOAD.md) from a Mac with an authenticated GitHub CLI.
The helper creates a NEW private repository, validates visibility before pushing,
uploads only hash-allowlisted release files, and verifies the remote commit.
It never reuses/overwrites an existing repository or changes visibility.

GitHub Actions is configured for Ubuntu and macOS with Python 3.10/3.13;
remote runs and Mac Codex behavior remain unverified until executed there.
