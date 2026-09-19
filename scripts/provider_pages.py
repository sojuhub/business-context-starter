"""Offline normalizers for selected provider-shaped joined fixtures.

The caller assembles each fixture from list metadata plus an authorized
content get/export response before calling this module.  Google Drive
``files.list`` and Gmail ``messages.list`` alone do not contain file/message
content.  These functions do not call Composio, authenticate, discover
accounts, or decide which business data is authorized.  Partial responses
remain visible in ``gaps``.
"""

from __future__ import annotations

import base64
import binascii
import email.policy
import json
from collections.abc import Mapping
from email.parser import BytesParser
from typing import Any


def normalize_page(provider: str, payload: Mapping[str, Any], *, company_id: str,
                   source_id: str, checked_at: str) -> dict[str, Any]:
    """Normalize one upstream response page into the audit collection contract."""
    if not isinstance(provider, str) or provider not in {"google_drive", "gmail", "square"}:
        raise ValueError("provider must be google_drive, gmail, or square")
    _required_string("company_id", company_id)
    _required_string("source_id", source_id)
    _required_string("checked_at", checked_at)
    if not isinstance(payload, Mapping):
        raise ValueError("provider payload must be an object")
    _check_response_status(payload)

    if provider == "google_drive":
        records, cursor, gaps = _google_drive(payload, company_id, source_id, checked_at)
    elif provider == "gmail":
        records, cursor, gaps = _gmail(payload, company_id, source_id, checked_at)
    else:
        records, cursor, gaps = _square(payload, company_id, source_id, checked_at)
    return {
        "http_status": 200,
        "successful": True,
        "data": {"records": records, "next_cursor": cursor, "gaps": gaps},
    }


def _check_response_status(payload: Mapping[str, Any]) -> None:
    if "http_status" in payload and payload["http_status"] != 200:
        raise ValueError("provider response is not HTTP 200")
    if "successful" in payload and payload["successful"] is not True:
        raise ValueError("provider response did not succeed")
    if "error" in payload and payload["error"] not in (None, "", [], {}):
        raise ValueError("provider response contains an error")
    if "errors" in payload:
        errors = payload["errors"]
        if not isinstance(errors, list):
            raise ValueError("provider errors must be a list")
        if errors:
            raise ValueError("provider response contains errors")


def _required_string(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _cursor(payload: Mapping[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string or null")
    return value


def _record(company_id: str, source_id: str, record_id: str, locator: str,
            text: str, checked_at: str) -> dict[str, str]:
    _required_string("record id", record_id)
    _required_string("locator", locator)
    if not isinstance(text, str) or not text:
        raise ValueError("record text must be a non-empty string")
    return {"company_id": company_id, "source_id": source_id,
            "record_id": record_id, "locator": locator, "text": text,
            "checked_at": checked_at}


def _google_drive(payload: Mapping[str, Any], company_id: str, source_id: str,
                  checked_at: str) -> tuple[list[dict[str, str]], str | None, list[str]]:
    files = payload.get("files")
    if not isinstance(files, list):
        raise ValueError("Google Drive response must contain a files list")
    records: list[dict[str, str]] = []
    gaps: list[str] = []
    if payload.get("incompleteSearch") is True:
        gaps.append("google_drive:incomplete_search")
    for item in files:
        if not isinstance(item, Mapping):
            gaps.append("google_drive:item_not_object")
            continue
        file_id = item.get("id")
        if not isinstance(file_id, str) or not file_id.strip():
            gaps.append("google_drive:item_missing_id")
            continue
        content_key = next((key for key in ("exported_text", "text", "content")
                            if key in item), None)
        if content_key is None:
            gaps.append(f"google_drive:{file_id}:metadata_only")
            continue
        text = item[content_key]
        if not isinstance(text, str):
            gaps.append(f"google_drive:{file_id}:content_not_text")
            continue
        if not text:
            gaps.append(f"google_drive:{file_id}:empty_content")
            continue
        mime = item.get("mimeType")
        exported_mime = item.get("exported_mime_type")
        if content_key == "exported_text":
            if exported_mime is not None and exported_mime != "text/plain":
                gaps.append(f"google_drive:{file_id}:unsupported_export_mime")
                continue
        elif mime != "text/plain":
            gaps.append(f"google_drive:{file_id}:unsupported_mime")
            continue
        locator = item.get("webViewLink") or item.get("webContentLink")
        if not isinstance(locator, str) or not locator:
            locator = f"gdrive://files/{file_id}"
        records.append(_record(company_id, source_id, file_id, locator, text, checked_at))
    return records, _cursor(payload, "nextPageToken"), gaps


def _decode_base64url(value: Any, label: str) -> bytes:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty base64url string")
    padded = value + "=" * (-len(value) % 4)
    try:
        return base64.b64decode(padded, altchars=b"-_", validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError(f"invalid base64url in {label}") from exc


def _gmail(payload: Mapping[str, Any], company_id: str, source_id: str,
           checked_at: str) -> tuple[list[dict[str, str]], str | None, list[str]]:
    messages = payload.get("messages")
    if not isinstance(messages, list):
        raise ValueError("Gmail response must contain a messages list")
    records: list[dict[str, str]] = []
    gaps: list[str] = []
    for item in messages:
        if not isinstance(item, Mapping):
            gaps.append("gmail:item_not_object")
            continue
        message_id = item.get("id")
        if not isinstance(message_id, str) or not message_id.strip():
            gaps.append("gmail:item_missing_id")
            continue
        if "raw" in item:
            raw = _decode_base64url(item["raw"], f"gmail:{message_id}:raw")
            message = BytesParser(policy=email.policy.default).parsebytes(raw)
            text, attachment_seen, binary_seen = _mime_text(message)
            if attachment_seen:
                gaps.append(f"gmail:{message_id}:attachments_omitted")
            if binary_seen:
                gaps.append(f"gmail:{message_id}:unsupported_binary_part")
        elif isinstance(item.get("payload"), Mapping):
            text, attachment_seen, html_seen, binary_seen = _gmail_payload_text(item["payload"])
            if attachment_seen:
                gaps.append(f"gmail:{message_id}:attachments_omitted")
            if html_seen and not text:
                gaps.append(f"gmail:{message_id}:html_only")
            if binary_seen:
                gaps.append(f"gmail:{message_id}:unsupported_binary_part")
        else:
            text = ""
        if not text:
            gaps.append(f"gmail:{message_id}:missing_plain_text_body")
            continue
        locator = item.get("webLink")
        if not isinstance(locator, str) or not locator:
            locator = f"gmail://messages/{message_id}"
        records.append(_record(company_id, source_id, message_id, locator, text, checked_at))
    return records, _cursor(payload, "nextPageToken"), gaps


def _mime_text(message: Any) -> tuple[str, bool, bool]:
    attachment_seen = False
    binary_seen = False
    text_parts: list[str] = []
    for part in message.walk() if message.is_multipart() else (message,):
        if part.is_multipart():
            continue
        is_attachment = bool(part.get_filename()) or part.get_content_disposition() == "attachment"
        if is_attachment:
            attachment_seen = True
            continue
        content_type = part.get_content_type()
        if content_type != "text/plain":
            if not content_type.startswith("text/"):
                binary_seen = True
            continue
        raw_content = part.get_payload(decode=True)
        if raw_content is None:
            raw_content = part.get_payload()
        if isinstance(raw_content, bytes):
            charset = part.get_content_charset() or "utf-8"
            try:
                content = raw_content.decode(charset)
            except (LookupError, UnicodeDecodeError) as exc:
                raise ValueError("invalid Gmail text/plain charset or UTF-8 body") from exc
        elif isinstance(raw_content, str):
            content = raw_content
        else:
            raise ValueError("Gmail text/plain body is not text")
        if content:
            text_parts.append(content)
    return "\n".join(text_parts), attachment_seen, binary_seen


def _gmail_payload_text(payload: Mapping[str, Any]) -> tuple[str, bool, bool, bool]:
    text_parts: list[str] = []
    attachment_seen = False
    html_seen = False
    binary_seen = False

    def walk(part: Mapping[str, Any]) -> None:
        nonlocal attachment_seen, html_seen, binary_seen
        mime = part.get("mimeType")
        filename = part.get("filename")
        body = part.get("body")
        body = body if isinstance(body, Mapping) else {}
        is_attachment = bool(filename) or bool(body.get("attachmentId"))
        if is_attachment:
            attachment_seen = True
        if mime == "text/html":
            html_seen = True
        elif mime and not mime.startswith("text/") and not is_attachment:
            binary_seen = True
        if mime == "text/plain" and not is_attachment:
            if "data" in body:
                decoded = _decode_base64url(body["data"], "gmail payload body")
                try:
                    value = decoded.decode("utf-8")
                except UnicodeDecodeError as exc:
                    raise ValueError("invalid UTF-8 in Gmail payload body") from exc
                if value:
                    text_parts.append(value)
        parts = part.get("parts")
        if parts is not None:
            if not isinstance(parts, list):
                raise ValueError("Gmail payload parts must be a list")
            for child in parts:
                if not isinstance(child, Mapping):
                    raise ValueError("Gmail payload part must be an object")
                walk(child)

    walk(payload)
    return "\n".join(text_parts), attachment_seen, html_seen, binary_seen


def _square(payload: Mapping[str, Any], company_id: str, source_id: str,
            checked_at: str) -> tuple[list[dict[str, str]], str | None, list[str]]:
    orders = payload.get("orders")
    if not isinstance(orders, list):
        raise ValueError("Square response must contain an orders list")
    page_total_key = next((key for key in ("page_total", "total", "total_count")
                           if key in payload), None)
    records: list[dict[str, str]] = []
    gaps: list[str] = []
    for order in orders:
        if not isinstance(order, Mapping):
            gaps.append("square:order_not_object")
            continue
        order_id = order.get("id")
        if not isinstance(order_id, str) or not order_id.strip():
            gaps.append("square:order_missing_id")
            continue
        try:
            snapshot: Any = dict(order)
            if page_total_key is not None:
                snapshot = {"order": dict(order),
                            "page_total_snapshot": {"field": page_total_key,
                                                     "value": payload[page_total_key]}}
            text = json.dumps(snapshot, ensure_ascii=False, sort_keys=True,
                              separators=(",", ":"))
        except (TypeError, ValueError) as exc:
            gaps.append(f"square:{order_id}:unserializable_order")
            continue
        records.append(_record(company_id, source_id, order_id,
                               f"square://orders/{order_id}", text, checked_at))
    if page_total_key is not None and not records:
        gaps.append("square:page_total_without_orders")
    return records, _cursor(payload, "cursor"), gaps
