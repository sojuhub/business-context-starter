"""Fictional receipt consistency checks; no provider/account calls."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'plugins/business-context-starter/scripts'
sys.path.insert(0, str(SCRIPTS))
from check_onboarding import check_onboarding


class CompletionTests(unittest.TestCase):
    def test_source_completion_requires_scoped_content_receipts(self):
        state = {'company_id': 'demo', 'discovery_status': 'complete',
                 'requested_source_ids': ['mail'],
                 'approved_scopes': [{'source_id': 'mail', 'account_ref': 'business',
                                      'scope': 'selected 5 bodies', 'approval_ref': 'owner-1'}]}
        source = {'id': 'mail', 'disposition': 'collect', 'auth_status': 'authenticated',
                  'read_status': 'read', 'record_count': 1, 'gaps': [],
                  'read_receipt': {'evidence_mode': 'live', 'tool': 'fictional-reader',
                                   'receipt_ref': 'fictional-receipt', 'checked_at': '2026-09-20',
                                   'scope': 'selected 5 bodies', 'account_ref': 'business',
                                   'coverage_complete': True}}
        evidence = {'id': 'e1', 'source_id': 'mail', 'locator': 'fixture://mail/1',
                    'claim': 'Fictional company.', 'status': 'source-stated', 'checked_at': '2026-09-20'}
        # "live" here exercises validation of a declared mode, not live verification.
        cases = [
            ('valid declared receipt', {}, {}, True, 'source-complete'),
            ('setup only', {'discovery_status': 'pending'}, {}, True, 'source-blocked'),
            ('source selection skipped', {'requested_source_ids': []}, {}, True, 'source-blocked'),
            ('missing agreed source', {'requested_source_ids': ['mail', 'drive']}, {}, True, 'source-blocked'),
            ('no scope', {'approved_scopes': []}, {}, True, 'source-blocked'),
            ('authenticated only', {}, {'read_status': 'not-read'}, True, 'source-blocked'),
            ('metadata only', {}, {'record_count': 1}, False, 'source-blocked'),
            ('page limit', {}, {'gaps': ['page-limit'], 'read_status': 'partial'}, True, 'source-blocked'),
            ('expired auth', {}, {'auth_status': 'expired'}, True, 'source-blocked'),
            ('no tool receipt', {}, {'read_receipt': {}}, True, 'source-blocked'),
            ('wrong account', {}, {'read_receipt': {**source['read_receipt'], 'account_ref': 'other'}}, True, 'source-blocked'),
            ('wrong scope', {}, {'read_receipt': {**source['read_receipt'], 'scope': 'all mail'}}, True, 'source-blocked'),
            ('fixture', {}, {'read_receipt': {**source['read_receipt'], 'evidence_mode': 'fixture'}}, True, 'fixture-only'),
            ('empty search', {}, {'record_count': 0}, False, 'source-complete'),
            ('silent defer', {}, {'disposition': 'deferred'}, True, 'source-blocked'),
            ('owner defer', {}, {'disposition': 'deferred', 'decision_ref': 'owner-2'}, True, 'source-partial'),
            ('not used', {}, {'disposition': 'not-used', 'decision_ref': 'owner-2'}, False, 'no-sources-read'),
            ('boolean count', {}, {'record_count': True}, True, 'source-blocked'),
        ]
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder).resolve() / 'private'
            (destination / 'state').mkdir(parents=True)
            (destination / 'sources').mkdir()
            for name, state_change, source_change, has_evidence, expected in cases:
                with self.subTest(name=name):
                    (destination / 'state/onboarding.json').write_text(json.dumps({**state, **state_change}))
                    (destination / 'sources/manifest.json').write_text(json.dumps({'company_id': 'demo', 'sources': [{**copy.deepcopy(source), **source_change}]}))
                    (destination / 'sources/evidence.jsonl').write_text(json.dumps(evidence) + '\n' if has_evidence else '')
                    before = {p: p.read_bytes() for p in destination.rglob('*') if p.is_file()}
                    result = check_onboarding(destination)
                    self.assertEqual(result['source_status'], expected)
                    self.assertEqual(before, {p: p.read_bytes() for p in destination.rglob('*') if p.is_file()})
                    cli = subprocess.run([sys.executable, str(SCRIPTS / 'check_onboarding.py'), '--destination', str(destination)], capture_output=True, text=True)
                    self.assertEqual(cli.returncode, 0 if expected == 'source-complete' else 1, cli.stderr)
            malformed = {**state, 'company_id': 'another-company'}
            (destination / 'state/onboarding.json').write_text(json.dumps(malformed))
            with self.assertRaises(ValueError):
                check_onboarding(destination)


if __name__ == '__main__':
    unittest.main()
