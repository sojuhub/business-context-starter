import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "plugins/business-context-starter/scripts/compile_context.py"
spec = importlib.util.spec_from_file_location("compile_context", SCRIPT)
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)


class CompileContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=str(Path(tempfile.gettempdir()).resolve()))
        self.root = Path(self.temp.name)
        self.destination = self.root / "private-company"
        sources = self.destination / "sources"
        sources.mkdir(parents=True)
        (sources / "manifest.json").write_text(json.dumps({
            "company_id": "demo-company",
            "records": [{"id": "website", "kind": "website", "read_status": "partial"}, {"id": "orders", "kind": "orders", "update_mode": "snapshot"}],
        }) + "\n")
        (sources / "evidence.jsonl").write_text("\n".join([
            json.dumps({"id": "e1", "source_id": "website", "locator": "https://example.test/about", "claim": "A small studio serving local makers.", "status": "source-stated", "checked_at": "2026-09-19"}),
            json.dumps({"id": "e2", "source_id": "orders", "locator": "fixture://orders/1", "claim": "Current order snapshot: 3 open orders.", "status": "source-stated", "checked_at": "2026-09-19"}),
        ]) + "\n")
        self.plan = {"company_id": "demo-company", "overview": "A small studio serving local makers.", "claims": [
            {"evidence_id": "e1", "category": "company", "quote": "A small studio serving local makers.", "summary": "Studio serving local makers"},
            {"evidence_id": "e2", "category": "policies", "quote": "Current order snapshot: 3 open orders.", "summary": "Open order snapshot"},
        ], "unknowns": ["Current cancellation rule"]}

    def tearDown(self):
        self.temp.cleanup()

    def test_writes_fixed_routes_with_provenance_and_candidate_labels(self):
        result = cc.compile_context(self.destination, self.plan)
        self.assertEqual(result["status"], "written")
        for relative in ("INDEX.md", "context/company.md", "context/tone.md", "context/policies.md", "outputs/business-brief.md", "state/onboarding.json"):
            self.assertTrue((self.destination / relative).is_file(), relative)
        page = (self.destination / "context/policies.md").read_text()
        self.assertIn("e2", page)
        self.assertIn("fixture://orders/1", page)
        self.assertIn("unreviewed", page.lower())
        self.assertIn("snapshot only", page.lower())
        self.assertNotIn("owner-confirmed", page.lower())
        self.assertFalse((self.destination / "context/products.md").exists())
        self.assertFalse((self.destination / "context/workflows.md").exists())

    def test_same_evidence_can_support_multiple_categories(self):
        plan = json.loads(json.dumps(self.plan))
        plan["claims"].append({"evidence_id": "e1", "category": "products", "quote": "local makers", "summary": "Maker-focused offering"})
        cc.compile_context(self.destination, plan)
        self.assertIn("Maker-focused offering", (self.destination / "context/products.md").read_text())

    def test_repeat_is_idempotent(self):
        first = cc.compile_context(self.destination, self.plan)
        before = {p: (self.destination / p).read_bytes() for p in first["files"] + ["state/onboarding.json"]}
        second = cc.compile_context(self.destination, self.plan)
        self.assertEqual(second["status"], "unchanged")
        self.assertEqual(before, {p: (self.destination / p).read_bytes() for p in before})

    def test_external_owner_edit_refuses_before_any_write(self):
        cc.compile_context(self.destination, self.plan)
        policy = self.destination / "context/policies.md"
        policy.write_text(policy.read_text() + "\n## Ongoing owner correction\nNever promise same-day delivery.\n")
        before = {p: (self.destination / p).read_bytes() for p in ("INDEX.md", "context/company.md", "context/policies.md", "context/tone.md", "outputs/business-brief.md", "state/onboarding.json")}
        with self.assertRaises(cc.CompileError):
            cc.compile_context(self.destination, self.plan)
        self.assertEqual(before, {p: (self.destination / p).read_bytes() for p in before})

    def test_quote_must_match_evidence(self):
        bad = json.loads(json.dumps(self.plan))
        bad["claims"][0]["quote"] = "invented"
        with self.assertRaises(cc.CompileError):
            cc.compile_context(self.destination, bad)
        self.assertFalse((self.destination / "INDEX.md").exists())

    def test_direct_api_plan_size_is_limited(self):
        bad = json.loads(json.dumps(self.plan))
        bad["overview"] = "x" * (cc.MAX_PLAN_BYTES + 1)
        with self.assertRaises(cc.CompileError):
            cc.compile_context(self.destination, bad)
        self.assertFalse((self.destination / "INDEX.md").exists())

    def test_unknown_source_and_duplicate_evidence_are_rejected(self):
        bad = json.loads(json.dumps(self.plan))
        bad["claims"][0]["evidence_id"] = "missing"
        with self.assertRaises(cc.CompileError):
            cc.compile_context(self.destination, bad)
        evidence = self.destination / "sources/evidence.jsonl"
        evidence.write_text(evidence.read_text() + evidence.read_text().splitlines()[0] + "\n")
        with self.assertRaises(cc.CompileError):
            cc.compile_context(self.destination, self.plan)

    def test_empty_or_duplicate_manifest_scope_is_rejected(self):
        manifest = self.destination / "sources/manifest.json"
        manifest.write_text(json.dumps({"company_id": "demo-company", "records": []}) + "\n")
        with self.assertRaises(cc.CompileError):
            cc.compile_context(self.destination, self.plan)
        manifest.write_text(json.dumps({"company_id": "demo-company", "records": [{"id": "website"}, {"id": "website"}]}) + "\n")
        with self.assertRaises(cc.CompileError):
            cc.compile_context(self.destination, self.plan)

    def test_changed_plan_resets_review_status_and_adds_state_metadata(self):
        cc.compile_context(self.destination, self.plan)
        state_path = self.destination / "state/onboarding.json"
        state = json.loads(state_path.read_text())
        self.assertEqual(state["schema_version"], 1)
        self.assertIn("last_updated", state)
        state["review_status"] = "approved"
        state_path.write_text(json.dumps(state, indent=2) + "\n")
        changed = json.loads(json.dumps(self.plan))
        changed["claims"][0]["summary"] = "Updated studio description"
        cc.compile_context(self.destination, changed)
        self.assertEqual(json.loads(state_path.read_text())["review_status"], "needs-owner-review")

    def test_git_repository_destination_is_rejected(self):
        repo = self.root / "repo"
        (repo / ".git").mkdir(parents=True)
        with self.assertRaises(cc.CompileError):
            cc.compile_context(repo / "private-company", self.plan)

    def test_plugin_cache_destination_is_rejected(self):
        destination = Path.home() / ".codex/plugins/cache/business-context-test"
        with self.assertRaises(cc.CompileError):
            cc.compile_context(destination, self.plan)

    def test_model_cannot_supply_arbitrary_route(self):
        bad = json.loads(json.dumps(self.plan))
        bad["claims"][0]["filename"] = "../../AGENTS.md"
        with self.assertRaises(cc.CompileError):
            cc.compile_context(self.destination, bad)


if __name__ == "__main__":
    unittest.main()
