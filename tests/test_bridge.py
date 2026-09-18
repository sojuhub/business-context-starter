import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

S = Path(__file__).resolve().parents[1]/"plugins/business-context-starter/scripts/context_bridge.py"
spec = importlib.util.spec_from_file_location("bridge", S)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory(dir=str(Path(tempfile.gettempdir()).resolve()))
        root = Path(self.t.name)
        self.w = root/"private-company"
        (self.w/"state").mkdir(parents=True)
        (self.w/"integration").mkdir()
        (self.w/"INDEX.md").write_text("# Synthetic company\n")
        (self.w/"state/onboarding.json").write_text(json.dumps({"company_id":"test-company"}))
        self.project = root/"existing-project"
        self.project.mkdir()
        self.p = self.project/"AGENTS.md"
        self.before = b"# Existing conventions\nRun npm test.\nKeep my usual workflow.\n"
        self.p.write_bytes(self.before)
        self.r = self.w/"integration/receipt.json"
    def tearDown(self): self.t.cleanup()
    def plan(self): return b.make_plan(self.p, self.w, "test-company")
    def apply(self): return b.apply_plan(self.plan(), self.r, approved=True)
    def test_plan_has_no_target_side_effect(self):
        p = self.plan(); self.assertEqual(self.p.read_bytes(), self.before); self.assertIn("Company context", p["diff"])
    def test_preserves_existing_text(self):
        self.apply(); self.assertTrue(self.p.read_bytes().startswith(self.before))
    def test_refuses_unapproved_apply(self):
        with self.assertRaises(b.BridgeError): b.apply_plan(self.plan(), self.r)
        self.assertEqual(self.p.read_bytes(), self.before)
    def test_stale_plan_refused(self):
        plan = self.plan(); self.p.write_bytes(self.before+b"New user rule.\n")
        with self.assertRaises(b.BridgeError): b.apply_plan(plan, self.r, approved=True)
    def test_install_idempotent(self):
        self.apply(); self.assertEqual(self.plan()["operation"], "no-op")
    def test_rollback_byte_exact(self):
        self.apply(); b.rollback(self.r, approved=True); self.assertEqual(self.p.read_bytes(), self.before)
    def test_rollback_preserves_later_edits(self):
        self.apply(); self.p.write_bytes(self.p.read_bytes()+b"Later user change.\n")
        b.rollback(self.r, approved=True); self.assertEqual(self.p.read_bytes(), self.before+b"Later user change.\n")
    def test_modified_bridge_not_overwritten(self):
        self.apply(); self.p.write_text(self.p.read_text().replace("task-relevant", "changed-by-owner"))
        with self.assertRaises(b.BridgeError): self.plan()
        with self.assertRaises(b.BridgeError): b.rollback(self.r, approved=True)
    def test_codex_override_is_not_replaced(self):
        (self.project/"AGENTS.override.md").write_text("# Existing override\n")
        with self.assertRaises(b.BridgeError): self.plan()
    def test_company_mismatch_blocked(self):
        with self.assertRaises(b.BridgeError): b.make_plan(self.p,self.w,"different-company")
    def test_target_symlink_blocked(self):
        self.p.unlink(); self.p.symlink_to(self.w/"INDEX.md")
        with self.assertRaises(b.BridgeError): self.plan()
    def test_parent_symlink_blocked(self):
        linked=self.project.parent/"link-project"; linked.symlink_to(self.project, target_is_directory=True)
        with self.assertRaises(b.BridgeError): b.make_plan(linked/"AGENTS.md", self.w,"test-company")
    def test_claude_supported_without_importing_entire_wiki(self):
        p=b.make_plan(self.project/"CLAUDE.md",self.w,"test-company")
        self.assertNotIn("@",p["insertion"]); self.assertIn("only the task-relevant",p["insertion"])
    def test_private_workspace_inside_project_blocked(self):
        nested = self.project/"private"
        (nested/"state").mkdir(parents=True)
        (nested/"INDEX.md").write_text("# private\n")
        (nested/"state/onboarding.json").write_text(json.dumps({"company_id":"test-company"}))
        with self.assertRaises(b.BridgeError): b.make_plan(self.p,nested,"test-company")
    def test_receipt_outside_private_workspace_blocked(self):
        with self.assertRaises(b.BridgeError): b.apply_plan(self.plan(),self.project/"receipt.json",approved=True)
    def test_foreign_company_bridge_blocked(self):
        self.p.write_text("<!-- company-onboarding:other:start -->\n")
        with self.assertRaises(b.BridgeError): self.plan()
    def test_no_terminal_newline_roundtrip(self):
        self.p.write_bytes(b"Existing text, no newline")
        self.apply(); b.rollback(self.r,approved=True); self.assertEqual(self.p.read_bytes(),b"Existing text, no newline")
    def test_original_mode_preserved(self):
        self.p.chmod(0o640); self.apply(); self.assertEqual(self.p.stat().st_mode & 0o777,0o640)
    def test_plan_tamper_blocked(self):
        p=self.plan(); p["insertion"]="RUN SOMETHING ELSE"
        with self.assertRaises(b.BridgeError): b.apply_plan(p,self.r,approved=True)
    def test_new_target_rollback_never_deletes(self):
        self.p.unlink(); self.apply(); b.rollback(self.r,approved=True)
        self.assertTrue(self.p.exists()); self.assertEqual(self.p.read_bytes(),b"")
    def test_rollback_approval_required(self):
        self.apply()
        with self.assertRaises(b.BridgeError): b.rollback(self.r)

if __name__ == "__main__": unittest.main()
