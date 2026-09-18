from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/business-context-starter"

class CopyFirstContractTests(unittest.TestCase):
    # These are static content-contract checks, not LLM or live-import tests.
    def test_entry_is_copy_first(self):
        text=(ROOT/"COPY_PROMPT.md").read_text()
        self.assertIn("Read START_HERE.md", text)
        self.assertIn("do not build another app or require plugin installation first", text)
    def test_start_uses_existing_skill(self):
        text=(ROOT/"START_HERE.md").read_text()
        self.assertIn("plugins/business-context-starter/skills/start/SKILL.md", text)
        self.assertIn("instruction-mode", text)
    def test_no_fake_remote_url_in_copy_prompt(self):
        text=(ROOT/"COPY_PROMPT.md").read_text()
        self.assertNotIn("github.com/", text)
        self.assertNotIn("OWNER", text)
    def test_prior_context_reference_is_linked(self):
        text=(PLUGIN/"skills/start/SKILL.md").read_text()
        self.assertIn("../../references/PRIOR_CONTEXT.md", text)
        self.assertTrue((PLUGIN/"references/PRIOR_CONTEXT.md").is_file())
    def test_native_memory_boundaries_present(self):
        text=(PLUGIN/"references/PRIOR_CONTEXT.md").read_text()
        self.assertIn("NOT an implemented universal import/export parser", text)
        self.assertIn("Do not claim a complete memory transfer", text)
        self.assertIn("Do not directly edit its generated memory files", text)
    def test_provenance_and_repeat_import_contract(self):
        text=(PLUGIN/"references/PRIOR_CONTEXT.md").read_text()
        self.assertIn("owner-confirmed ongoing policy", text)
        self.assertIn("a repeated import must not create duplicate policies", text)
        self.assertIn("awaiting-export", text)
    def test_release_requires_real_pinned_source(self):
        text=(ROOT/"docs/RELEASE_CHECKLIST.md").read_text()
        self.assertIn("NOT a usable end-user prompt yet", text)
        self.assertIn("SAME commit", text)
        self.assertIn("No curl-to-shell", text)

if __name__ == "__main__":
    unittest.main()
