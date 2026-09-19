# Compile context contract

`compile_context(destination, plan)` renders an LLM-produced classification plan into a private workspace. It is a writer and validator, not a model and not a connector.

The plan has exactly these fields:

```json
{
  "company_id": "lowercase-slug",
  "overview": "short overview",
  "claims": [
    {"evidence_id": "...", "category": "company|tone|policies|products|workflows", "quote": "exact substring", "summary": "unreviewed candidate"}
  ],
  "unknowns": ["... "]
}
```

Evidence must already exist in `sources/evidence.jsonl`, and each `quote` must be an exact substring of its evidence claim. The manifest identity must match `company_id`. Summaries are always rendered as unreviewed candidates; the compiler never creates owner-confirmed policy.

Only these paths are generated: `INDEX.md`, the seeded `context/company.md`, `context/tone.md`, and `context/policies.md`, supported `context/products.md` or `context/workflows.md` pages when claims exist, `outputs/business-brief.md`, and `state/onboarding.json`. `products.md` and `workflows.md` are omitted until evidence supports them; no empty pages are created. Source IDs, locators, evidence status and source quotes are retained in every claim. Partial sources and current transaction/order records are marked snapshot-only.

The destination must be outside a Git repository and the Codex plugin cache, and all path components must be regular, non-symlink paths. Before any write, the compiler validates the plan, evidence, manifest, output paths and prior generation hashes. A changed generated page is treated as an owner correction and causes a visible stop. Repeating the same plan is idempotent. The compiler never accepts model-supplied filenames and never stores credentials. `state/onboarding.json` records top-level `schema_version` and `last_updated`; changed generated context returns `review_status` to `needs-owner-review`.

CLI:

```sh
python3 plugins/business-context-starter/scripts/compile_context.py \
  --destination /private/path/company \
  --plan /private/path/plan.json
```
