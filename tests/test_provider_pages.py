"""Provider normalizer tests use checked-in upstream-shaped fixtures only."""

import base64
import json
import unittest
from pathlib import Path

from scripts.provider_pages import normalize_page

from scripts.audit_source_fetch import collect_for_audit


FIXTURES = Path(__file__).parent / "fixtures" / "provider-pages"
COMPANY = "fictional-provider-company"
CHECKED_AT = "2026-09-19T00:00:00Z"


def fixture(name):
    return json.loads((FIXTURES / name).read_text())


class ProviderPageTests(unittest.TestCase):
    def test_google_drive_accepts_selected_plain_text_and_export(self):
        page = normalize_page("google_drive", fixture("google-drive-page.json"),
                              company_id=COMPANY, source_id="google-drive:approved",
                              checked_at=CHECKED_AT)
        self.assertEqual(page["http_status"], 200)
        self.assertTrue(page["successful"])
        self.assertEqual(page["data"]["next_cursor"], "drive-page-2")
        self.assertEqual([row["record_id"] for row in page["data"]["records"]],
                         ["drive-brief-1", "drive-doc-2"])
        self.assertEqual(page["data"]["gaps"], [])

    def test_google_drive_metadata_only_is_partial(self):
        page = normalize_page("google_drive", fixture("google-drive-metadata-only.json"),
                              company_id=COMPANY, source_id="google-drive:approved",
                              checked_at=CHECKED_AT)
        self.assertEqual(page["data"]["records"], [])
        self.assertIn("google_drive:drive-metadata-only:metadata_only", page["data"]["gaps"])

    def test_google_drive_incomplete_search_is_visible(self):
        payload = fixture("google-drive-page.json")
        payload["incompleteSearch"] = True
        page = normalize_page("google_drive", payload, company_id=COMPANY,
                              source_id="google-drive:approved", checked_at=CHECKED_AT)
        self.assertIn("google_drive:incomplete_search", page["data"]["gaps"])

    def test_gmail_decodes_raw_mime_and_payload_body(self):
        page = normalize_page("gmail", fixture("gmail-page.json"),
                              company_id=COMPANY, source_id="gmail:approved",
                              checked_at=CHECKED_AT)
        texts = [row["text"] for row in page["data"]["records"]]
        self.assertEqual(texts, ["Hi from the customer.\n", "Plain body from Gmail"])
        self.assertEqual(page["data"]["next_cursor"], "gmail-page-2")
        self.assertEqual(page["data"]["gaps"], [])

    def test_gmail_missing_body_and_attachments_are_visible(self):
        page = normalize_page("gmail", fixture("gmail-missing-body.json"),
                              company_id=COMPANY, source_id="gmail:approved",
                              checked_at=CHECKED_AT)
        self.assertEqual(page["data"]["records"], [])
        self.assertIn("gmail:gmail-metadata-only:missing_plain_text_body", page["data"]["gaps"])
        self.assertIn("gmail:gmail-attachment-only:attachments_omitted", page["data"]["gaps"])
        self.assertIn("gmail:gmail-attachment-only:missing_plain_text_body", page["data"]["gaps"])

    def test_gmail_binary_part_and_attachment_text_are_not_body(self):
        plain = base64.urlsafe_b64encode(b"Approved plain body").decode().rstrip("=")
        attached = base64.urlsafe_b64encode(b"Do not include this attachment").decode().rstrip("=")
        page = normalize_page("gmail", {
            "messages": [{"id": "gmail-mixed", "payload": {
                "mimeType": "multipart/mixed",
                "parts": [
                    {"mimeType": "text/plain", "body": {"data": plain}},
                    {"mimeType": "text/plain", "filename": "note.txt",
                     "body": {"data": attached}},
                    {"mimeType": "application/octet-stream",
                     "body": {"data": "YmluYXJ5"}}
                ]
            }}]
        }, company_id=COMPANY, source_id="gmail:approved", checked_at=CHECKED_AT)
        self.assertEqual(page["data"]["records"][0]["text"], "Approved plain body")
        self.assertIn("gmail:gmail-mixed:attachments_omitted", page["data"]["gaps"])
        self.assertIn("gmail:gmail-mixed:unsupported_binary_part", page["data"]["gaps"])
        self.assertNotIn("Do not include this attachment", page["data"]["records"][0]["text"])

    def test_gmail_invalid_utf8_fails(self):
        invalid = base64.urlsafe_b64encode(b"\xff\xfe").decode().rstrip("=")
        with self.assertRaises(ValueError):
            normalize_page("gmail", {"messages": [{"id": "gmail-invalid",
                "payload": {"mimeType": "text/plain", "body": {"data": invalid}}}]},
                company_id=COMPANY, source_id="gmail:approved", checked_at=CHECKED_AT)

    def test_square_keeps_page_total_inside_order_snapshot(self):
        page = normalize_page("square", fixture("square-page.json"),
                              company_id=COMPANY, source_id="square:approved",
                              checked_at=CHECKED_AT)
        self.assertEqual(page["data"]["next_cursor"], "square-page-2")
        self.assertEqual(page["data"]["gaps"], [])
        snapshot = json.loads(page["data"]["records"][0]["text"])
        self.assertEqual(snapshot["page_total_snapshot"], {"field": "total_count", "value": 1})
        self.assertEqual(snapshot["order"]["id"], "square-order-1")

    def test_invalid_shapes_fail_instead_of_claiming_complete(self):
        with self.assertRaises(ValueError):
            normalize_page("google_drive", {"files": {}, "nextPageToken": None},
                            company_id=COMPANY, source_id="drive", checked_at=CHECKED_AT)
        with self.assertRaises(ValueError):
            normalize_page("gmail", {"messages": [{"id": "m", "raw": "!!!"}]},
                            company_id=COMPANY, source_id="gmail", checked_at=CHECKED_AT)
        with self.assertRaises(ValueError):
            normalize_page("square", {"orders": [], "cursor": 3},
                            company_id=COMPANY, source_id="square", checked_at=CHECKED_AT)
        with self.assertRaises(ValueError):
            normalize_page("square", {"orders": [], "errors": [{"code": "BAD_REQUEST"}]},
                            company_id=COMPANY, source_id="square", checked_at=CHECKED_AT)
        with self.assertRaises(ValueError):
            normalize_page("gmail", {"messages": [], "error": {"message": "denied"}},
                            company_id=COMPANY, source_id="gmail", checked_at=CHECKED_AT)

    def test_whitespace_identifiers_are_rejected(self):
        for kwargs in (
            {"company_id": " ", "source_id": "gmail", "checked_at": CHECKED_AT},
            {"company_id": COMPANY, "source_id": "\t", "checked_at": CHECKED_AT},
            {"company_id": COMPANY, "source_id": "gmail", "checked_at": "\n"},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    normalize_page("gmail", {"messages": []}, **kwargs)

    def test_normalized_pages_fit_collect_for_audit(self):
        first = normalize_page("square", fixture("square-page.json"),
                               company_id=COMPANY, source_id="square:approved",
                               checked_at=CHECKED_AT)
        second = normalize_page("square", fixture("square-page-2.json"),
                                company_id=COMPANY, source_id="square:approved",
                                checked_at=CHECKED_AT)
        pages = iter((first, second))
        receipt = collect_for_audit(lambda cursor: next(pages), COMPANY,
                                    {"square:approved"})
        self.assertEqual(receipt["status"], "complete")
        self.assertEqual([record["record_id"] for record in receipt["records"]],
                         ["square-order-1", "square-order-2"])


if __name__ == "__main__":
    unittest.main()
