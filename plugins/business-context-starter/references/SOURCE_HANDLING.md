# Sources: one onboarding, progressive depth

This is a workflow contract, not a bundled connector implementation.
The product includes connecting and actually reading approved business sources; the package relies on the host's real tools or separately approved providers.

## Connection priority
1. A sufficient existing authorized host connector, file tool or company wiki.
2. A documented official integration available in that host.
3. An optional integration provider such as Composio when needed and approved.
4. Approved export/upload/public-only fallback when the required live path is unavailable; keep that gap visible.

No bundled empty MCP server, fabricated provider endpoints, prerequisite custom app server, or automatic paid subscription.
Before a proposed third-party connection, explain who processes data/holds credentials and known or unverified costs. Local Markdown storage is not local-only inference.
Composio's current docs recommend their agent plugin for Codex/Claude Code. Auth is a real provider-generated flow. Do not duplicate it here or hardcode returned connection IDs.

## What to collect
| Source | Business meaning | Bounds and caveats |
|---|---|---|
| Existing project | Approved context, tone, skills, workflow, wiki routing | Selected project only. Exclude secrets and unselected conversation archives. |
| Prior AI work | Selected business chats, owner-reviewed memory summaries, project notes and confirmed decisions | Follow [prior-context handling](PRIOR_CONTEXT.md). Native import/export first where suitable; explicit project/topic scope; no complete-memory promise. |
| Website | Offering, audience, channels, contact/booking links | Confirm official identity; marketing is source-stated, not independently verified. |
| Files / Drive | Price lists, procedures, templates, past outcomes | Owner-selected folder/files; preserve originals; do not follow symlinks outside approved roots. |
| Gmail | Inquiries, replies, repeat requests, workflow evidence | Confirm exact account/business filter/period. Proposed default is 90 days, not permission. |
| Calendar | Relevant event patterns and business schedules | Select actual calendar IDs and period; a calendar is not a complete booking ledger. |
| Instagram / other social | Voice, offerings, public engagement; private data only if specifically needed | Public posts and DMs/insights are separate. Verify account type and current provider support. |
| Booking tools | Services, approval/cancellation rules, booking flow | Ask service name only if not already found. Do not infer all bookings from confirmation email. |
| Sales/orders/accounting | Definitions, source-of-truth, allowed operating snapshot | Separate gross sales, refunds, payouts, taxes, invoices and profit. No full-period total from a partial sample. |
| Owner clarification | Exceptions and decisions not present in records | Mark as explicit owner statement; do not ask them to rewrite facts already in approved sources. |

## Source status
Use separate fields for selected, authorized, authenticated, read-status, inspected-scope, checked-at, update-mode, and review-status.
Read status: not-read / partial / read / blocked / unsupported / not-used.
Authentication success is not reading success; tool availability is not authorization.
Never store credentials. Minimize customer identifiers and raw message bodies. Keep exact locators where available.
Record pagination/sample limits. Never call a sample an exhaustive company dataset.

## Support statements
- Gmail / Calendar: proposed first real acceptance targets; not tested in this generated package.
- Website / selected files: use the host's available reader; no crawler shipped.
- Instagram: current Composio page limits its toolkit to Business and Creator accounts. Recheck for the actual customer's provider and requested actions.
- Booking / sales: discover the customer's provider and confirm exact reads; no universal support claim.

## Reuse existing Google account access
A Gmail connector already in the chosen Codex is a path to Gmail, not a second independent source to duplicate.
An account connected in this ChatGPT conversation is not automatically available in a separate local Codex process.
Do not reconnect or revoke an existing account solely to make all integrations use one vendor.
