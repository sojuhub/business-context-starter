# Business discovery

Business onboarding discovers how the owner actually works, collects approved
evidence, and leaves a reviewable private workspace. Installing the plugin or
reading one connector is not completion. Follow this procedure after the
initial project and tool fit check in `start/SKILL.md`.

## Stages

1. **Service interview.** Ask progressively which sites and services the owner
   uses most and what they do there. Include services beyond the installed tool
   catalog. Record the answer, including an owner-confirmed `none`, and the
   reason for each service. Do not infer service use from a tool being listed.
2. **Service inventory.** Turn the interview into a nonempty inventory. Give
   each service an `id`, name, purpose, owner reference, and source IDs. Every
   agreed source ID, including a blocked or deferred one, must appear in
   `requested_source_ids` and in `sources/manifest.json`; an owner explanation
   may be the source when the business has no digital service.
3. **Browser candidate discovery.** Offer this stage and obtain approval for
   the work profile, open tabs and bounded history window. If the owner selects
   a work browser and
   the host supports it, use the approved host browser route (Aside on Mac
   Codex) to inspect only open-tab and
   recent-history metadata for the selected work profile. This proposes service
   candidates; it does not authorize page-body reads. Do not scan raw browser
   profiles, cookies, or unrelated history.
4. **Owner confirmation.** Show the candidate list and let the owner confirm
   business services. Record the confirmation before reading content. If
   supported browser access is unavailable, offer a manual inventory; record
   the reason and the owner's acceptance of that fallback. Respect `not-used`.
5. **Scoped collection.** For each confirmed service, propose the account or
   identity, business filter, date/folder scope, record limit, attachment
   handling, processing, and private destination. Read only that scope through
   the supported host route. A browser candidate, login, tool listing, or
   search snippet is not a content-read receipt. Record partial, blocked, and
   deferred sources and their next action.
6. **Coverage loop.** Build the evidence-backed brief, then ask only targeted
   questions for material gaps or conflicts. Continue collection and questions
   until the owner has reviewed each category: `customers`, `products`,
   `pricing`, `workflows`, `policies`, `tone`, and `services`. Each category is
   `confirmed` with evidence and owner reference, or explicitly
   `not-applicable` with a reason.
7. **Review and save.** Review the whole brief with the owner. Save knowledge,
   source locators, key excerpts, required originals, and provenance in the
   existing private workspace or the already-authoritative wiki. A wiki
   readback may use scoped local receipts/excerpts with original locators and a
   link map; do not create a competing canonical writer.
8. **Fresh-session check.** In a fresh session, read `INDEX.md` and a saved
   coverage page, then produce a real task draft using confirmed evidence.
   Record the read hashes, applied evidence IDs, draft path, and draft hash.

Stop, pause, or defer when the owner requests it. Keep incomplete evidence and
the exact resume action. `run_status` may be `active`, `paused`, `stopped`, or
`deferred`; paused/stopped/deferred runs cannot be marked complete.

## Retention and provenance

Retain synthesized company knowledge, source locators, and key excerpts by
default. Retain an original only when it is needed to support the saved
knowledge, such as a price list or manual. Keep originals in the approved
private destination and bind their paths and hashes in the completion record.
Do not retain credentials or unrelated personal data. Preserve source status
(`source-stated`, `owner-confirmed`, `inferred`, or `disputed`) and the actual
read receipt; a model summary or repeated copy is not independent evidence.

## Completion record

Store the following `completion` object in `state/onboarding.json`. It is a
receipt contract; it does not establish the semantic truth of an owner's
answers or a provider response. Store actual owner/tool/session references, never example receipts. The following
is the field map; all paths are relative to the approved private workspace.

| Field under `completion` | Required content |
| --- | --- |
| `service_interview` | Nonempty `most_used`, `purpose`, `other_services`, `confirmation_ref` |
| `services[]` | `id`, `name`, `purpose`, `source_ids[]`, `owner_ref` |
| `browser_discovery` | `status`, `owner_confirmation_ref`; confirmed discovery also has `profile_ref`, `history_scope`, `discovery_approval_ref`, `receipt_ref`, `candidate_service_ids[]`; fallback/not-used has `reason` |
| `business_coverage` | The seven category keys listed below, each with reviewed evidence and a saved location |
| `material_gaps` | Explicit list; empty only after material gaps/conflicts are resolved |
| `retention` | `mode: selective-originals`, `originals[]` entries with `path`, `source_id`, `reason`; empty list when none needed |
| `storage.files` | Map of saved relative paths to their actual SHA-256 hashes |
| `owner_review` | `status: approved`, `receipt_ref`, `files` matching the reviewed storage map |
| `fresh_session` | `status: passed`, distinct `onboarding_session_id` / `session_id`, `receipt_ref`, `checked_at`, `files_read` hash map, `applied_evidence_ids[]`, `draft_path`, `draft_sha256` |

Each category in `business_coverage` uses this shape (illustrative only):

```json
{
  "status": "confirmed",
  "summary": "Source-backed business understanding reviewed by the owner",
  "owner_ref": "actual owner decision reference",
  "evidence_ids": ["actual evidence id"],
  "saved_paths": ["context/company.md"]
}
```

For `not-applicable`, retain the summary, owner reference and saved paths, and
supply `reason` instead of evidence IDs. A general refusal to answer is a pending
item, not proof that a category is inapplicable.

Required rules:

- Every `service_interview` field is a nonempty string. `none` is valid only
  when it is the owner's actual answer.
- `services` is nonempty. Each item maps to `requested_source_ids` and a
  manifest entry, and the union of its `source_ids` equals
  `requested_source_ids`; `source_ids` may point to the owner explanation for
  a no-digital-service result.
- `browser_discovery.status` is `confirmed`, `manual-fallback`, or `not-used`.
  Every status requires `owner_confirmation_ref`. `confirmed` additionally
  requires `profile_ref`, `history_scope`,
  `discovery_approval_ref`, `receipt_ref`, and `candidate_service_ids` as a
  subset of `services`. `manual-fallback` and `not-used` require `reason`.
- `business_coverage` includes `customers`, `products`, `pricing`, `workflows`,
  `policies`, `tone`, and `services`. A `confirmed`
  item needs a summary, owner reference, evidence IDs, and saved paths. Both
  statuses need a summary, owner reference, and saved paths; a
  `not-applicable` item uses a reason instead of evidence IDs.
- `material_gaps` is `[]` only when the owner has no material unresolved gap.
- `retention.mode` is `selective-originals`; `originals` may be empty.
- `storage.files` includes `INDEX.md`, `outputs/business-brief.md`,
  `sources/manifest.json`, `sources/evidence.jsonl`, every coverage
  `saved_path`, and every retained original. Values are SHA-256 hashes.
- Top-level `state.review_status` is `owner-approved`;
  `owner_review.status` is `approved`, and its `files` map is exactly the
  reviewed `storage.files` map.
- `fresh_session.onboarding_session_id` and `session_id` are distinct.
  `files_read` includes `INDEX.md` and a saved coverage page, matches
  `storage.files`, and `applied_evidence_ids` are confirmed category evidence mapped to pages
  observed in that session. Reading only the index cannot pass.
  The draft must exist on disk and match `draft_sha256`.

Keep source and onboarding results separate. The checker returns both
`source_status` and `onboarding_status`; its default exit 0 means only
`onboarding-complete`. Use `--sources-only` for the earlier source-only
diagnostic behavior.

Run `python3 plugins/business-context-starter/scripts/check_onboarding.py
--destination /private/path/company` as one command before announcing completion.
An exit of 1 means incomplete; 2 means invalid inputs. A 0 validates the recorded
gates and current file contents, not semantic quality, source authenticity or the
truth of a claimed session. Never invent receipts to satisfy this check. If the
host cannot run the script, apply the criteria manually and report automated
validation unavailable.
