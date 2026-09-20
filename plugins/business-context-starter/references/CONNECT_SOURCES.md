# Execute source connections

This procedure is run by the host agent using its actual tools. The package does
not provide OAuth credentials or a universal connector. Read tool schemas in the
current session; never assume another host's connection is accessible here.

## Discover, scope, execute

1. Inspect the supported tool catalog, including deferred tool discovery if the
   host provides it. Look for read/search tools and non-secret account labels for
   the intended business. Do not search message content to discover permissions.
   Reuse an existing company wiki and previously approved scope. Record all agreed
   sources in `state/onboarding.json.requested_source_ids`; do not omit blocked ones.
2. Explain the account, business filter, date range or folder, maximum records,
   attachment policy, AI/provider processing and private destination in one scope
   proposal. Ask only for missing authorization. A proposed 90-day window is not
   consent. A mixed inbox may require metadata discovery followed by confirmation
   of the business selection. If supplied context already authorizes body reads
   in an exact scope, proceed without asking again.
3. Use the sufficient existing connector. Verify the selected account via supported
   identity metadata when needed, then perform a real search and content read.
   A login, tool listing or search snippet alone is not a content-read receipt.
4. Keep bounds on every page and child read; stop at the approved record limit.
   Record outstanding cursors, omitted attachments and failed reads as gaps. Do
   not expand the query when it returns zero; record zero matches and ask about
   a changed scope only if useful. Preserve earlier evidence on failures.
5. Save minimal source-linked excerpts using the existing WORKSPACE.md manifest
   and evidence format, outside the public checkout. Reuse source/record IDs;
   preserve owner-confirmed corrections. Never run live responses through the
   developer audit importer, which deliberately labels records synthetic.
6. Continue to company synthesis and review using successful sources. Retain each
   blocked source and an exact next action. Resume from that step, not repository
   installation, and do not reconnect a working account.

## Existing Gmail / Drive route

Map these operations to the currently exposed schemas rather than copying names
from another host. In a host exposing Gmail `search_emails` and `batch_read_email`,
use the selected account reference for both calls, the approved business/date
query for search, then only returned approved message IDs for the body read.
Some hosts expose `search_email_ids`; prefer it when only IDs are needed. Respect
per-call limits. Verify the response's actual body fields; snippets are insufficient.
Do not mark read, modify labels, save drafts or send messages during collection.
For thread expansion, recheck each message against the scope; a matching message
is not permission to read the entire historical conversation. Attachments require
their own approved scope and supported retrieval path.

For Drive, search/list only the approved folder or selected files, then fetch the
selected contents using the host's document reader/export. Metadata without a
content fetch is partial. Do not recursively traverse unrelated folders or links.
When no native read tool is available, continue to the provider route below.

## Optional Composio route

First establish the missing capability. Explain signup, requested permissions,
Composio's processing/credential role and current or unverified costs; obtain
provider approval separately from source scope if it has not already been given.
Use the host's existing Composio integration when available. Discover tools and
accounts, choose the approved business account, and execute search/content reads
in that session. If authorization is needed, use the genuine generated Connect
Link and let the account holder complete consent, then re-read connection status.

For a supported existing SDK integration, current Composio documentation describes
`composio.create(...)` / `composio.use(...)`, `session.tools()`,
`session.authorize(...)` and `session.execute(...)`. Session tools must execute
through the session, not the separate direct-tool path. Discover exact tool schemas
and validate actual response/error shapes; the offline joined fixtures are not a
Composio response contract. Do not install another server or invent endpoint/tool
names when this integration is missing. Perform documented host setup within
approved scope; otherwise record `unsupported` with the concrete missing capability
and offer an approved export. Do not silently substitute an export or public page
for a requested live connection.

Official references checked 2026-09-20; recheck before setup:
- https://docs.composio.dev/docs/how-composio-works
- https://docs.composio.dev/reference/api-reference/tool-router

## Record and check progress

Use existing state and manifest files. These fictional fragments illustrate the
fields; they are not evidence of a real account read:

```json
{
  "company_id": "demo-company",
  "discovery_status": "complete",
  "requested_source_ids": ["business-mail"],
  "approved_scopes": [{
    "source_id": "business-mail", "account_ref": "business-account",
    "scope": "approved business query and dates; up to 5 bodies; no attachments",
    "approval_ref": "private-owner-decision-1"
  }],
  "next_action": "Review the source-linked company brief"
}
```

A collected manifest source uses the same account and scope:

```json
{
  "id": "business-mail", "kind": "gmail", "disposition": "collect",
  "route": "existing-host", "auth_status": "authenticated",
  "read_status": "read", "record_count": 1, "gaps": [],
  "read_receipt": {
    "evidence_mode": "fixture", "tool": "fictional body reader",
    "receipt_ref": "fixture://body-read-1", "checked_at": "2026-09-20",
    "account_ref": "business-account",
    "scope": "approved business query and dates; up to 5 bodies; no attachments",
    "coverage_complete": true
  }
}
```

`record_count` counts records actually read, not list hits. Save corresponding
`source_id` evidence for nonempty reads. `coverage_complete` means the agreed
bounded selection was read, never the whole business. A zero-match successful
search may use count 0, no evidence and complete coverage; it establishes no
business facts. Use `read_status: partial` for body failures or unconsumed pages.
Record an observed successful tool receipt before marking a read `live`; do not
copy the fictional example and relabel it. For files/public pages, authorization
still needs a scope entry; auth_status can be `not-required`.

Owner-chosen `deferred` / `not-used` sources require `decision_ref`; the agent cannot
assign these dispositions to hide a blocker. Deferred sources are always reported
and prevent a full source-complete result. A not-used source is outside the agreed
collection scope. Neither counts as a read.

Before handoff run:

```sh
python3 plugins/business-context-starter/scripts/check_onboarding.py \
  --destination /private/path/company
```

The command reads the existing state, manifest and evidence without changing them.
It exits 0 only for a recorded live source-complete result; pending, partial and
fixture results exit 1, invalid inputs exit 2. It checks consistency, not the
truth of agent-entered receipts or account access. Reconcile receipts with actual
tool responses. If Python is unavailable, apply these same checks manually and
state that the automated check did not run.

Report starter preparation, source collection, owner review and fresh-session
reuse separately. Even `source-complete` does not mean the brief was reviewed or
that a new session successfully read it. Keep exact blockers and next action in
state; continue available work rather than treating the check as a universal stop.
