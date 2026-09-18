# Optional developer route — not the default start

# Start in your Mac Codex

Open the extracted repository in the Codex you already use. Paste this:

```text
Read README.md and inspect the plugin under plugins/business-context-starter.
Use this existing package; do not create another AIOS app or rewrite my global setup.
First check which local plugin loading method this Codex version supports.
Use the included local marketplace where supported, with my approval for installation changes.
If loading is unavailable, read skills/start/SKILL.md inside that plugin directly for this pilot;
label that as instruction-mode, not successful plugin installation.
Use English. Help me set up my business in a dedicated or existing project.
Reuse my current instructions, company knowledge and working connections.
Show an early business preview, offer approved source connections,
and produce one useful draft before proposing optional expansion.
Create private business files outside this public repo and outside the plugin cache.
Show and confirm any project instruction change. No global edits or background tasks.
Do not send, post, modify bookings, read unrelated personal data, publish or deploy.
Report separately: files created, local tests run, sources actually read,
plugin loaded, and fresh-session behavior verified.
```

## Native package path
The repo catalog is `.agents/plugins/marketplace.json`; its source is `./plugins/business-context-starter` relative to this repo root.
Official current docs describe local marketplace discovery in supported desktop hosts. Local UI and CLI support depend on the installed host/version; verify them before changing configuration.
Where the installed CLI supports it, the documented registration command is:

```sh
codex plugin marketplace add .
```

Registration is not installation, account authorization, or proof of fresh-session behavior. Use the host's local plugin install UI and verify the plugin is loaded.
Do not overwrite an existing marketplace or config. This repository contains no global auto-installer.

## Secondary Claude developer smoke test
The documented local test method is:
```sh
claude --plugin-dir ./plugins/business-context-starter
```
Then invoke `/business-context-starter:start`.
This is a developer test route, not a claim that it was executed in this environment.
Do not install both host variants into the same runtime as duplicate copies.

## The first live run
You may use your real Gmail and Calendar, but choose the company/project and the permitted business scope in that session.
Do not paste credentials. A provider or host handles login.
Check fresh-session reuse and one unrelated task after the setup. Keep outputs labelled partial when a selected source is blocked.
