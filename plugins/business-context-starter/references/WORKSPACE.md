# Minimal private workspace

The folder roles are stable; the number of files should grow only when the business needs them.
Retain a compatible v0.2 workspace instead of migrating it for cosmetic reasons.
If an authoritative company wiki already exists, bind to it and avoid duplicate facts.

## Initial files for a new business
```text
<private-company>/
  INDEX.md
  context/
    company.md
    tone.md
    policies.md
  sources/
    manifest.json
    evidence.jsonl
  state/
    onboarding.json
    decisions.jsonl
  integration/
  outputs/
```
Add operator, strategy, current-state, products, workflows and further knowledge pages only with useful evidence. No empty department agents or database service.
Create new folders and files with private permissions where supported. Do not copy business data into a publicly tracked repo, plugin install cache, or demo folder.

## INDEX
Company ID, verification status, a short business overview, task-to-page routing, authoritative external wiki pointers, live-data caveats, and material unknowns.
It is the reading map, not the archive. Treat roughly 400 words as a design budget, not a quality guarantee.

## Content pages
Each page contains a concise purpose/when-to-read, source locators or owner-confirmed statements, reviewed/uncertain status, and last checked date when known.
Tone and business policy are separate. Approved policy has explicit owner provenance and effective scope. Link back to originals.

## State contracts
- state/onboarding.json: schema_version, company_id, phase, review_status, private_destination, approved_scopes, last_updated, blockers. Unknown timestamps are null.
- sources/manifest.json: company_id, sources[] with id, kind, locator, account_ref (not a token), scope, auth_status, read_status, inspected_scope, checked_at, update_mode.
- sources/evidence.jsonl: one minimal claim/excerpt per line: id, source_id, locator, claim, status (source-stated/owner-confirmed/inferred/disputed), checked_at.
- state/decisions.jsonl: owner change, one-off/ongoing scope, prior value, new value, revision, evidence, impacted drafts.
- integration/bindings.json: approved project, active company, INDEX, existing authoritative pages and source routes. Never credentials.
- outputs: first brief and useful drafts. Generated/reviewed/approved are distinct; no sent state without an actual external action, which this plugin does not perform.

Use the existing v0.2 conventions if the workspace already has them. Migration requires a reviewed plan; do not maintain two competing canonical stores.

## Linked Markdown wiki, not a graph service
The logical graph is the existing pages and their explicit links. No code graph is required for company knowledge. Use the existing folder names; do not migrate context/ or knowledge/ just to rename them wiki/. INDEX is a short reading map, not a complete archive or parallel source of truth.
Group useful knowledge into company facts, applicable tone, reviewed policies, confirmed decisions and source-to-result workflow references. Create extra pages only when evidence warrants them. Source archives stay at approved private locations; the manifest records their provenance and the actually inspected subset.
Optional relationships are derived from reviewed pages and evidence, never a separate authoritative database. Any edge must retain source/status and be updated when a source claim is corrected or removed. No always-on graph generation or code indexing.
Prior AI imports use the same source manifest. Imported model statements remain candidates until reviewed; missing identifiers and dates remain unknown. Follow PRIOR_CONTEXT.md for import scope, deduplication and correction handling.
