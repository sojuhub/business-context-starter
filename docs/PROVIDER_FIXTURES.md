# Offline provider fixtures

`scripts/provider_pages.py` normalizes three caller-selected, upstream-shaped
JSON **joined fixtures**. The caller must join list metadata with separately
authorized content responses before invoking it. It has no network path and
does not authenticate, discover accounts, choose a business scope, or claim
that a Composio wrapper has the same schema. The fixtures are fictional and
contain no customer data.

## Contract

```json
{
  "http_status": 200,
  "successful": true,
  "data": {
    "records": [{
      "company_id": "...",
      "source_id": "...",
      "record_id": "...",
      "locator": "...",
      "text": "...",
      "checked_at": "..."
    }],
    "next_cursor": "...",
    "gaps": []
  }
}
```

`successful: true` means that this response page was parsed. A page can still
be partial: omitted content is left out of `records` and named in `gaps`.
Invalid top-level shapes, cursors, statuses, and base64 data raise `ValueError`
so a caller cannot silently report an invalid page as complete.

## Exact fixture limits

Google Drive fixtures join `files.list` metadata with a selected `files.get`
download (`text/plain`) or `files.export` result (`text/plain`). A selected
file is readable only when the joined fixture provides direct `text` with
`mimeType: text/plain`, or direct `exported_text` with
`exported_mime_type: text/plain`. `files.list` never supplies this content by
itself: listing metadata alone, `incompleteSearch: true`, binary files, and
unsupported export types remain gaps. The normalizer does not download files
or infer which Drive pages are business-approved.

Gmail fixtures join `users.messages.list` metadata with an authorized
`users.messages.get` result (`format=raw` or `format=full`). The list response
contains only message identifiers and does not contain full bodies. A selected
joined message must have either a full `raw` MIME message encoded as base64url
or a `payload` tree with `text/plain` body data encoded as base64url. A snippet
is not a body. Attachments are deliberately omitted and recorded as a gap; an
HTML-only, binary, or body-less message produces no complete normalized page.
The normalizer does not fetch an attachment or change labels/read state.

Square fixtures model `orders/search` response pages. Each selected order is
stored as a JSON snapshot, preserving nested order fields without interpreting
them as policy. A provider page total is copied into that order snapshot under
`page_total_snapshot`; it is diagnostic page evidence, never a durable price,
revenue, or policy fact. The provider `cursor` becomes `next_cursor`.
Orders with missing IDs or unserializable values remain visible in `gaps`.

The implementation does not cover Drive permissions or export downloads,
Gmail pagination beyond returning the cursor, Gmail attachment retrieval,
Square payments/catalog/customers, rate limits, token expiry, or retries. Those
belong to the caller and must be normalized into the same contract before
calling the bounded audit collector. No Composio adapter or wrapper schema is
implemented or verified here.

## Upstream references

These URLs describe the provider JSON shapes used by the fixtures:

- Google Drive `files.list`: <https://developers.google.com/workspace/drive/api/reference/rest/v3/files/list>
- Google Drive `files.get`: <https://developers.google.com/workspace/drive/api/reference/rest/v3/files/get>
- Google Drive `files.export`: <https://developers.google.com/workspace/drive/api/reference/rest/v3/files/export>
- Gmail `users.messages.list`: <https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list>
- Gmail `users.messages.get`: <https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get>
- Square `Search orders`: <https://developer.squareup.com/reference/square/orders-api/search-orders>

The links are provenance pointers for the fixture shapes. They are not proof of
live account access or of any Composio toolkit implementation.

Run the offline checks with:

```sh
python3 -m unittest tests.test_provider_pages -v
```
