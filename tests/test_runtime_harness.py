"""Harness mechanics only; these mocks are not actual-host acceptance evidence."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import verify_onboarding_runtime as runtime


class RuntimeHarnessTests(unittest.TestCase):
    def test_observed_reads_reject_scope_escape_and_shell_execution(self):
        project = Path('/tmp/fixture-case/project')
        for command in ('cat /Users/other/private.txt', 'cat $(env)', 'python3 -c pass'):
            with self.subTest(command=command), self.assertRaises(AssertionError):
                runtime.observed_reads([{'command': command, 'exit_code': 0}], project)
        expected = str((project.parent / 'private-company/context/policies.md').resolve())
        paths = runtime.observed_reads([{'command': "cat ../private-company/context/policies.md", 'exit_code': 0}], project)
        self.assertEqual(paths, {expected})

    def test_fixture_pipeline_uses_valid_bridge_receipt_and_preserves_correction(self):
        def fake_host(project, receipts, name, prompt, schema):
            private = project.parent / 'private-company'
            if name == 'synthesis':
                evidence = [json.loads(line) for line in (private / 'sources/evidence.jsonl').read_text().splitlines()]
                categories = {'fixture:profile': 'company', 'fixture:tone': 'tone', 'fixture:policy': 'policies', 'fixture:workflow': 'workflows'}
                claims = [{'evidence_id': row['id'], 'category': categories[row['source_id']], 'quote': row['claim'], 'summary': row['claim']}
                          for row in evidence if row['source_id'] in categories]
                return {'company_id': 'fir-cup', 'overview': 'Fictional cafe.', 'claims': claims, 'unknowns': ['Availability']}, [], name
            if name == 'fresh-session':
                policy = str((private / 'context/policies.md').resolve())
                self.assertIn('37 hours', Path(policy).read_text())
                self.assertIn('company-onboarding:fir-cup:start', (project / 'AGENTS.md').read_text())
                return {'draft': '37 hours of notice; staff must check availability.', 'files_read': [policy], 'unknowns': ['Availability'], 'sent': False}, [{'command': f'cat {policy}', 'exit_code': 0}], name
            if name == 'discovery':
                return {'business_preview': 'Fictional cafe.', 'next_question': 'Who are your main customers?', 'reason': 'Audience is missing.'}, [], name
            return {'answer': 10, 'explanation': 'Add the three values.'}, [], name

        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp).resolve() / 'run'
            with patch('sys.argv', ['verify', '--output', str(output), '--run-codex', '--case', 'fir-cup']), \
                 patch.object(runtime, 'host_run', side_effect=fake_host), \
                 patch.object(runtime.subprocess, 'check_output', return_value='mocked-test-host'), \
                 patch.object(runtime, 'verify_saved_run'), patch('builtins.print'):
                runtime.main()
            receipt = json.loads((output / 'fir-cup/private-company/integration/bridge-receipt.json').read_text())
            self.assertEqual(receipt['status'], 'applied')
            self.assertIn('37 hours', (output / 'fir-cup/private-company/context/policies.md').read_text())


if __name__ == '__main__':
    unittest.main()
