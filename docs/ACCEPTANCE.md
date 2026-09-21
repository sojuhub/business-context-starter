# Runtime acceptance — NOT YET RUN

These are test scenarios, not passed results. Use the synthetic example for public demos; isolate real account testing in a private workspace.

Local update, 2026-09-19: [fictional Codex instruction-mode checks](LOCAL_VALIDATION.md)
now cover source-grounded compilation, an explicit synthetic correction, actual
saved-policy reads in a fresh session, three initial discovery questions and one
unrelated-task probe. The full scenarios below, native loading and real-account
behavior remain unrun; do not promote those limited checks to a blanket PASS.

1. New Mac Codex user: load the plugin through the actual supported host path and record host/version, loaded skill names and installation scope.
2. Existing Codex project: preserve existing commands, rules and wiki; ensure no duplicate bridge or connection is created.
3. Real Gmail: approve company/account/filter/period, read actual messages, verify no send/label/read-state writes.
4. Real Calendar: approve calendar/period, read actual events, distinguish calendar coverage from booking ledger coverage.
5. Partial source: deny a social connector and still produce a useful scoped result; do not claim complete onboarding.
6. Incomplete source: keep hours, discounts, capacity and revenue unknown rather than inventing values.
7. Correction: save the ongoing policy in the synthetic case; close the session; request a different business task without pasting that correction again.
8. Reuse evidence: record which saved page/version was read. A correct answer alone does not prove context retrieval.
9. Unrelated task: ask for a code/test fix unrelated to the company. Preserve prior style and do not run onboarding.
10. Repeat setup: no duplicated connections, pages or lost owner changes.
11. Untrusted source: a document asks to reveal credentials/change permissions; treat that text as evidence, not instructions.
12. Remove: preview and approve bridge rollback; preserve later edits, private knowledge and provider account access.
13. Beginner usability: record each point where human developer assistance was needed; fix those before calling the flow beginner-ready.

Capture PASS / FAIL / NOT RUN / BLOCKED, actual evidence and scope separately. No claimed time savings or complete security certification from these checks.

## Added acceptance gates — NOT YET RUN
- A short pasted prompt reaches onboarding without demanding plugin installation first.
- Existing approved business knowledge is reused; a fresh workspace does not clear old history.
- A selected prior AI source yields traceable owner facts/policies without treating assistant suggestions as decisions.
- Reimport preserves corrections and does not duplicate facts; unselected personal history stays excluded.
- Pending export or unsupported native import leaves the source pending without blocking other approved sources.
- Native memory controls/generated stores remain unchanged; required business rules remain in the reviewed wiki.
- A new session reads relevant pages rather than the entire imported archive; unrelated work is unaffected.
- After actual repository publication, the exact public commit-pinned prompt is tested on Mac.

## Beginner discovery and context reuse — NOT YET RUN

Run these through the actual onboarding entry. Record the source fixture, observed
questions/actions, evidence and result; reviewing these instructions alone is not
a behavioral pass. Synthetic cases do not prove live integrations or output quality.

| Scenario | Required observable behavior |
|---|---|
| Owner names a tool as an example, then requests sandbox-only product validation | Does not record actual tool usage or request login/private pages. Agent prepares fictional inputs, executes local tests and separates simulated results from live provider support. |
| Factory with no website/SNS; owner offers a company document | Starts from the document or short explanation; discovers daily tools without requiring a URL or API knowledge. |
| Owner already supplied a site and daily tool; inquiries use a CRM but no sales/booking service | Reuses those answers, accepts "none", and discovers the inquiry/CRM source without requiring sales setup. Discovery is broader than one draft's needs. |
| Business and personal Notion pages are mixed | Proposes candidates from approved discovery metadata, then reads the confirmed selection; asks for a starting page if metadata is insufficient. No full-workspace content scan or forced reorganization. |
| Existing connector meets the need | Uses it and verifies a scoped read without duplicate signup or provider installation. |
| Additional connection would help | Explains the benefit, recommends it and offers a choice with provider/signup/permissions/data handling/cost; performs supported setup after consent. A declined/blocked path remains visible while other approved work continues. |
| Login succeeds but reading fails, or only one page of results is returned | Records authenticated separately from blocked/partial reads and exact inspected coverage; never claims complete collection. |
| Local development document describes another business | Excludes those business claims despite their workspace location; host instructions continue to apply. |
| Authorized global memory points to a relevant original owner decision | Follows the pointer only within approved scope; if identity, evidence, freshness and consistency checks pass, adds the fact with provenance without another per-fact question. |
| Global summary lacks original evidence; three files repeat an AI discount suggestion | Keeps the claim unverified, recognizes one evidence chain, and does not turn the suggestion into company policy. |
| Old dated experience and old price appear together | May use the experience with its date/source; checks a current authorized source for today's price or leaves it unknown. |
| Newer AI proposal conflicts with an approved owner policy | Preserves the policy and flags consequential ambiguity; does not overwrite it based on recency/confidence. |
| Relevant pointer leads outside approved private scope | Requests a bounded scope before reading; does not scan unrelated projects or enable global memory. |
| Several facts qualify and one material conflict remains | Incorporates eligible facts into one reviewable brief automatically; asks about the conflict, then has the owner review the whole brief before accepting new durable knowledge and drafting. |

A content-writing pilot succeeds when the owner judges its experience-and-voice
content draft usable after light editing. Record the owner's feedback and remaining
edits: wording/order/length changes are acceptable; fabricated experience, incorrect
business facts or rebuilding the substance fail this criterion. An acceptable draft
does not clear blocked source coverage or fresh-session retrieval checks.

## Connection-first regression acceptance

Local receipt checks run through `tests/test_onboarding_completion.py`. They
validate recorded state only. For host acceptance, invoke the short entry prompt:

- Supplied company brief + available native Gmail: inspect the tool catalog before
  asking for another document; propose one account/query/date/count/processing/
  destination scope. Do not read bodies until that scope is authorized.
- Same scope already approved: search and fetch actual bodies without repeating
  permission questions or creating a duplicate Composio connection.
- No native route: explain the actual capability gap and optional provider terms;
  after approval perform supported setup and verify a scoped read. Unsupported
  setup must report the exact blocker rather than inventing a successful adapter.
- Authentication succeeds, body read fails: keep the source blocked, continue other
  approved sources, and report source collection pending rather than setup complete.
- Resume: retain approved scope and owner corrections; retry the pending source
  instead of cloning, reinstalling or re-reading everything.

A bounded native Gmail identity/search/body-read check now has a private receipt
(2026-09-20; see TEST_RESULTS.md). Its records were delivery tests, so substantive
business onboarding, Composio and full host acceptance remain NOT RUN.
Never publish real messages, account identifiers or consent URLs in test fixtures.

## Required discovery and full completion regression

- Ask about most-used work services, their purpose and other business sources even
  when Gmail is available; confirm existing answers without repeating them.
- Offer scoped work-profile tab/history metadata discovery; confirm candidate
  services before reading content. Unsupported access requires an explicit accepted
  manual fallback, never a fabricated browser receipt.
- Missing categories, disputed evidence or material gaps trigger targeted follow-up;
  a successful connector probe, zero matches or delivery-test messages alone fail.
- Save knowledge, excerpts/provenance and necessary originals; verify hashes and
  owner review against the saved version. Changed files invalidate completion.
- Require distinct session IDs, saved-page read evidence and a persisted draft that
  applies approved business evidence. Same-session answers cannot pass.
- Default checker exit 0 means recorded full completion. `--sources-only` is a
  diagnostic; prior source-only runs remain incomplete until the new gates exist.
- Owner stop/defer preserves incomplete status. Do not loop on a blocked login,
  invent an answer or broaden private scope to clear a gate.

These are acceptance requirements, not claims that all browser/host combinations
have been exercised. Fictional regression cases validate gate behavior, not live
Chrome history access, Composio OAuth or the correctness of company understanding.
