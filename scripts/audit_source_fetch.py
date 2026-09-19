"""Offline audit of normalized read pages, not a Composio/provider adapter.

request_page(cursor) supplies synthetic response dictionaries. Real adapters must
map their own schemas, child reads, attachments and coverage gaps to this contract.
No network, credentials, accounts, or production onboarding entry points are used.
"""

from __future__ import annotations

import time
from pathlib import Path

from scripts.audit_source_intake import MAX_RECORDS, _validate_records, ingest


def collect_for_audit(request_page, company_id, allowed_source_ids, *,
                      max_pages=10, max_retries=2, wait=time.sleep):
    """Collect bounded synthetic pages; incomplete results must not be ingested."""
    if type(max_pages) is not int or not 1 <= max_pages <= 100:
        raise ValueError("max_pages must be between 1 and 100")
    if type(max_retries) is not int or not 0 <= max_retries <= 3:
        raise ValueError("max_retries must be between 0 and 3")
    records, identities, cursors = [], {}, set()
    cursor, attempts, pages = None, 0, 0

    def result(issue=None):
        return {"status": "incomplete" if issue else "complete",
                "issue": issue, "records": records, "pages": pages,
                "attempts": attempts, "evidence": "synthetic-normalized-pages"}

    for _ in range(max_pages):
        for retry in range(max_retries + 1):
            attempts += 1
            try:
                response = request_page(cursor)
            except TimeoutError:
                response = {"http_status": 504}
            if not isinstance(response, dict) or type(response.get("http_status")) is not int:
                return result("malformed-response")
            status = response["http_status"]
            if status not in (429, 500, 502, 503, 504):
                break
            if retry == max_retries:
                return result("retry-exhausted")
            # ponytail: capped numeric delays for fixtures; real HTTP adapters must
            # parse Retry-After dates and preserve provider-specific retry rules.
            delay = response.get("retry_after", 2 ** retry)
            if type(delay) not in (int, float) or not 0 <= delay <= 60:
                return result("invalid-retry-delay")
            wait(delay)
        if status != 200:
            return result({401: "authentication", 403: "permission", 404: "missing"}.get(status, "http-error"))
        if response.get("successful") is not True:
            return result("action-failed")
        data = response.get("data")
        if not isinstance(data, dict) or "next_cursor" not in data or not isinstance(data.get("gaps"), list):
            return result("malformed-page")
        if data["gaps"]:
            return result("coverage-gap")
        next_cursor = data["next_cursor"]
        if next_cursor is not None and (not isinstance(next_cursor, str) or not next_cursor or len(next_cursor) > 2048):
            return result("malformed-cursor")
        try:
            batch = _validate_records(data.get("records"), company_id, allowed_source_ids)
        except ValueError:
            return result("invalid-records")
        for record in batch:
            identity = (record["company_id"], record["source_id"], record["record_id"])
            if identity in identities and identities[identity] != record:
                return result("conflicting-duplicate")
            if identity not in identities:
                identities[identity] = record
                records.append(record)
        if len(records) > MAX_RECORDS:
            return result("record-limit")
        try:
            _validate_records(records, company_id, allowed_source_ids)
        except ValueError:
            return result("invalid-records")
        pages += 1
        if next_cursor is None:
            return result()
        if next_cursor in cursors:
            return result("cursor-loop")
        cursors.add(next_cursor)
        cursor = next_cursor
    return result("page-limit")


def collect_and_ingest_for_audit(request_page, destination: Path, company_id: str,
                                 allowed_source_ids: set[str], **options):
    receipt = collect_for_audit(request_page, company_id, allowed_source_ids, **options)
    # Buffer the bounded batch so an API failure cannot replace prior evidence.
    # ponytail: max 200 records in memory; streaming needs an explicit checkpoint.
    if receipt["status"] == "complete":
        receipt["storage"] = ingest(receipt["records"], destination, company_id, allowed_source_ids)
    return receipt
