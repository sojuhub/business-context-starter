# Keep the original workflow

## New user
Propose a dedicated business project and a separate private knowledge directory, both outside this public plugin repo. Obtain approval for actual paths.
Guide opening the project in the host. Create only its minimum local instruction pointer once business identity is confirmed.
Do not reset the host, erase memories, change global permissions, add a global agent team, or require a new editor.

## Existing user
Inspect the selected project's applicable instructions and approved company routing. Reuse it if it already loads the correct context.
Do not copy our files over AGENTS.md / CLAUDE.md or override a company wiki. Preserve names, tests, skills and integrations.
Add a project-scoped pointer only when necessary. Read INDEX then task-relevant pages, not every source at startup.

## Reused local helper
`scripts/context_bridge.py` is copied unchanged from the user's Company Onboarding v0.2 pilot.
It requires Python 3.10+ and writes only after explicit approval. It is not a sandbox or a hook.
Paths below are placeholders for actual approved paths, not executable commands to run unchanged.
Resolve the script relative to the loaded plugin directory; do not hardcode a plugin cache location.

```sh
python3 <plugin-root>/scripts/context_bridge.py plan \
  --target <approved-project>/AGENTS.md \
  --workspace <approved-private-company> \
  --company-id <company-slug> \
  --out <approved-private-company>/integration/plan.json

# Only after showing the exact diff and receiving approval:
python3 <plugin-root>/scripts/context_bridge.py apply \
  --plan <approved-private-company>/integration/plan.json \
  --receipt <approved-private-company>/integration/receipt.json \
  --approved
```

Choose new receipt filenames for separately approved installations. Do not overwrite an existing receipt.
The helper validates INDEX.md and state/onboarding.json. It refuses global/home instruction files, symlinks, an existing conflicting bridge, and a nonempty AGENTS.override.md.
Private knowledge must be outside the target project directory. A layout outside this contract needs review rather than a bypass.
It checks for common concurrent changes but is not a transactional security boundary. Do not run simultaneous writers.
An absolute private INDEX path in a shared/public project may disclose local path/company information; review before committing it. Do not push such patches automatically.

## Uninstall and undo
First identify the exact approved receipt and show what removing the managed block changes.
```sh
python3 <plugin-root>/scripts/context_bridge.py rollback \
  --receipt <approved-private-company>/integration/receipt.json \
  --approved
```
The helper preserves edits outside its exact managed block and refuses a modified block. It never deletes the instruction file.
Disable/uninstall the plugin through the host separately. Private knowledge stays, and provider authorization stays until separately revoked by the owner.
No uninstall hook or silent data deletion is bundled.

## Host behavior to verify
Codex reads applicable project instructions on a fresh session; overrides and sandbox scope matter.
A namespaced plugin avoids command-name collisions but does not guarantee semantic instruction compatibility.
Claude compatibility metadata is included, but macOS Codex is the first acceptance target.
Plugin install/update may use a cache. It must never be the private knowledge location.
Test one business task, one unrelated task, an existing skill, an existing test command and rollback before public release.
