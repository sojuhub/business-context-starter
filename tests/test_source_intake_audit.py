import importlib.util
import os
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_source_intake.py"


def load_ingest():
    spec = importlib.util.spec_from_file_location("audit_source_intake", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ingest


def record(
    *,
    source_id="fixture:business",
    record_id="page-1",
    company_id="fictional-audit.example",
    locator="fixture://page-1",
    text="Owner-confirmed business context.",
    checked_at="2026-09-18T12:00:00Z",
):
    return {
        "source_id": source_id,
        "record_id": record_id,
        "company_id": company_id,
        "locator": locator,
        "text": text,
        "checked_at": checked_at,
    }


class SourceIntakeAuditTests(unittest.TestCase):
    def setUp(self):
        self.ingest = load_ingest()

    def test_reimport_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "context"
            item = record()
            first = self.ingest([item], destination, "fictional-audit.example", {"fixture:business"})
            snapshot = sorted(
                (path.relative_to(destination), path.read_bytes())
                for path in destination.rglob("*")
                if path.is_file()
            )
            second = self.ingest([item], destination, "fictional-audit.example", {"fixture:business"})
            self.assertEqual(snapshot, sorted(
                (path.relative_to(destination), path.read_bytes())
                for path in destination.rglob("*")
                if path.is_file()
            ))
            self.assertEqual(first["records"], second["records"])

    def test_changed_record_identity_keeps_one_stable_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "context"
            self.ingest([record(text="v1")], destination, "fictional-audit.example", {"fixture:business"})
            self.ingest([record(text="v2", checked_at="2026-09-19T12:00:00Z")], destination, "fictional-audit.example", {"fixture:business"})
            files = [path for path in (destination / "sources" / "snapshots").glob("*.json")]
            self.assertEqual(len(files), 1)
            self.assertIn(b"v2", files[0].read_bytes())

    def test_source_provenance_is_retained(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "context"
            self.ingest([record()], destination, "fictional-audit.example", {"fixture:business"})
            text = "\n".join(path.read_text() for path in destination.rglob("*") if path.is_file())
            self.assertIn("fixture:business", text)
            self.assertIn("page-1", text)
            self.assertIn("fixture://page-1", text)

    def test_same_source_records_preserve_all_inspected_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "context"
            self.ingest(
                [record(record_id="page-1"), record(record_id="page-2", locator="fixture://page-2")],
                destination,
                "fictional-audit.example",
                {"fixture:business"},
            )
            manifest = (destination / "sources" / "manifest.json").read_text(encoding="utf-8")
            self.assertIn("page-1", manifest)
            self.assertIn("page-2", manifest)

    def test_metadata_fields_are_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "context"
            with self.assertRaises((ValueError, TypeError)):
                self.ingest([record(locator="x" * 12_000_001)], destination, "fictional-audit.example", {"fixture:business"})
            self.assertFalse(destination.exists())

    def test_unrelated_company_or_source_is_rejected_before_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "context"
            with self.assertRaises(ValueError):
                self.ingest([record(company_id="other.example")], destination, "fictional-audit.example", {"fixture:business"})
            with self.assertRaises(ValueError):
                self.ingest([record(source_id="gmail:personal")], destination, "fictional-audit.example", {"fixture:business"})
            self.assertFalse(destination.exists())

    def test_malformed_and_oversized_records_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "context"
            malformed = record()
            del malformed["locator"]
            with self.assertRaises((ValueError, TypeError)):
                self.ingest([malformed], destination, "fictional-audit.example", {"fixture:business"})
            with self.assertRaises((ValueError, TypeError)):
                self.ingest([record(text="x" * 1_000_001)], destination, "fictional-audit.example", {"fixture:business"})
            self.assertFalse(destination.exists())

    def test_destination_symlink_and_traversal_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / "outside"
            outside.mkdir()
            destination = root / "context-link"
            destination.symlink_to(outside, target_is_directory=True)
            with self.assertRaises((ValueError, OSError)):
                self.ingest([record()], destination, "fictional-audit.example", {"fixture:business"})
            self.assertEqual(list(outside.iterdir()), [])

    def test_parent_symlink_is_rejected_before_writing_outside(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / "outside"
            outside.mkdir()
            parent = root / "linked-parent"
            parent.symlink_to(outside, target_is_directory=True)
            with self.assertRaises((ValueError, OSError)):
                self.ingest([record()], parent / "context", "fictional-audit.example", {"fixture:business"})
            self.assertEqual(list(outside.iterdir()), [])

    def test_existing_snapshot_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            destination = root / "context"
            outside = root / "outside.json"
            outside.write_text("untouched", encoding="utf-8")
            self.ingest([record()], destination, "fictional-audit.example", {"fixture:business"})
            snapshot = next((destination / "sources" / "snapshots").glob("*.json"))
            snapshot.unlink()
            snapshot.symlink_to(outside)
            with self.assertRaises((ValueError, OSError)):
                self.ingest([record(text="changed")], destination, "fictional-audit.example", {"fixture:business"})
            self.assertEqual(outside.read_text(encoding="utf-8"), "untouched")

    def test_predictable_temp_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            destination = root / "context"
            outside = root / "outside.json"
            outside.write_text("untouched", encoding="utf-8")
            (destination / "sources").mkdir(parents=True)
            temp = destination / "sources" / f".manifest.json.tmp-{os.getpid()}"
            temp.symlink_to(outside)
            self.ingest([record()], destination, "fictional-audit.example", {"fixture:business"})
            self.assertEqual(outside.read_text(encoding="utf-8"), "untouched")

    def test_existing_owner_correction_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "context"
            destination.mkdir()
            existing = destination / "owner-correction.md"
            existing.write_text("Owner correction: use this wording.", encoding="utf-8")
            self.ingest([record()], destination, "fictional-audit.example", {"fixture:business"})
            self.assertEqual(existing.read_text(encoding="utf-8"), "Owner correction: use this wording.")

    def test_injected_write_failure_does_not_claim_transaction_and_retry_converges(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "context"
            item = record()
            original_replace = os.replace
            calls = {"count": 0}

            def fail_once(*args, **kwargs):
                calls["count"] += 1
                if calls["count"] == 1:
                    raise OSError("injected write failure")
                return original_replace(*args, **kwargs)

            os.replace = fail_once
            try:
                with self.assertRaises(OSError):
                    self.ingest([item], destination, "fictional-audit.example", {"fixture:business"})
            finally:
                os.replace = original_replace
            self.ingest([item], destination, "fictional-audit.example", {"fixture:business"})
            snapshots = list((destination / "sources" / "snapshots").glob("*.json"))
            self.assertEqual(len(snapshots), 1)
            self.assertIn(b"page-1", snapshots[0].read_bytes())


if __name__ == "__main__":
    unittest.main()
