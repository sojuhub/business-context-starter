"""Fictional receipt consistency checks; no provider/account calls."""
import copy
import hashlib
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
                    self.assertEqual(result['onboarding_status'], 'onboarding-incomplete')
                    self.assertEqual(before, {p: p.read_bytes() for p in destination.rglob('*') if p.is_file()})
                    if name in ('valid declared receipt', 'metadata only'):
                        cli = subprocess.run([sys.executable, str(SCRIPTS / 'check_onboarding.py'), '--destination', str(destination), '--sources-only'], capture_output=True, text=True)
                        self.assertEqual(cli.returncode, 0 if expected == 'source-complete' else 1, cli.stderr)
            malformed = {**state, 'company_id': 'another-company'}
            (destination / 'state/onboarding.json').write_text(json.dumps(malformed))
            with self.assertRaises(ValueError):
                check_onboarding(destination)


    def test_full_completion_and_every_required_stage(self):
        from check_onboarding import COVERAGE
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve() / 'private'
            for name in ('state', 'sources', 'context', 'outputs'):
                (root / name).mkdir(parents=True, exist_ok=True)
            source = {'id': 'owner', 'disposition': 'collect', 'auth_status': 'not-required',
                      'read_status': 'read', 'record_count': 1, 'gaps': [],
                      'read_receipt': {'evidence_mode': 'live', 'tool': 'fictional-owner-input',
                                       'receipt_ref': 'fixture-only-read', 'checked_at': '2026-09-20',
                                       'account_ref': 'owner', 'scope': 'selected business brief',
                                       'coverage_complete': True}}
            evidence = {'id': 'e1', 'source_id': 'owner', 'locator': 'fixture://owner/brief',
                        'claim': 'Fictional business statement.', 'status': 'owner-confirmed', 'checked_at': '2026-09-20'}
            contents = {'INDEX.md': 'Read context/company.md.',
                        'outputs/business-brief.md': 'Reviewed fictional brief.',
                        'context/company.md': 'Fictional business statement.',
                        'context/pricing.md': 'Fictional pricing terms.',
                        'sources/manifest.json': json.dumps({'company_id': 'demo', 'sources': [source]}),
                        'sources/evidence.jsonl': json.dumps(evidence) + '\n' + json.dumps({**evidence, 'id': 'e2', 'claim': 'Fictional pricing terms.'}) + '\n',
                        'outputs/fresh-draft.md': 'Fictional draft applying the saved company statement.'}
            for path, text in contents.items():
                (root / path).write_text(text)
            hashes = {path: hashlib.sha256((root / path).read_bytes()).hexdigest()
                      for path in contents if path != 'outputs/fresh-draft.md'}
            completion = {
                'service_interview': {'most_used': 'offline documents', 'purpose': 'quotes',
                                      'other_services': 'none', 'confirmation_ref': 'fixture-owner-review'},
                'services': [{'id': 'documents', 'name': 'Company documents', 'purpose': 'quotes',
                              'source_ids': ['owner'], 'owner_ref': 'fixture-owner-review'}],
                'browser_discovery': {'status': 'confirmed', 'profile_ref': 'fictional-work',
                                      'history_scope': 'selected recent window', 'discovery_approval_ref': 'fixture-consent',
                                      'receipt_ref': 'fixture-browser-read', 'candidate_service_ids': ['documents'],
                                      'owner_confirmation_ref': 'fixture-owner-review'},
                'business_coverage': {category: {'status': 'confirmed', 'summary': 'Fictional category summary.',
                                                'owner_ref': 'fixture-owner-review', 'evidence_ids': ['e1'],
                                                'saved_paths': ['context/company.md']} for category in COVERAGE},
                'material_gaps': [],
                'retention': {'mode': 'selective-originals', 'originals': []},
                'storage': {'files': hashes},
                'owner_review': {'status': 'approved', 'receipt_ref': 'fixture-owner-review', 'files': hashes.copy()},
                'fresh_session': {'status': 'passed', 'onboarding_session_id': 'fixture-session-a',
                                  'session_id': 'fixture-session-b', 'receipt_ref': 'fixture-session-read',
                                  'checked_at': '2026-09-20', 'files_read': {'INDEX.md': hashes['INDEX.md'],
                                                                       'context/company.md': hashes['context/company.md']},
                                  'applied_evidence_ids': ['e1'], 'draft_path': 'outputs/fresh-draft.md',
                                  'draft_sha256': hashlib.sha256((root / 'outputs/fresh-draft.md').read_bytes()).hexdigest()}}
            completion['business_coverage']['pricing'].update(evidence_ids=['e2'], saved_paths=['context/pricing.md'])
            state = {'company_id': 'demo', 'discovery_status': 'complete', 'requested_source_ids': ['owner'],
                     'review_status': 'owner-approved',
                     'approved_scopes': [{'source_id': 'owner', 'account_ref': 'owner',
                                          'scope': 'selected business brief', 'approval_ref': 'fixture-consent'}],
                     'completion': completion}
            cases = [
                ('all recorded gates', [], None, True),
                ('source-only run', ['completion'], {}, False),
                ('interview skipped', ['completion', 'service_interview'], {}, False),
                ('unconfirmed interview', ['completion', 'service_interview', 'confirmation_ref'], '', False),
                ('no inventory', ['completion', 'services'], [], False),
                ('unmapped service', ['completion', 'services', 0, 'source_ids'], [], False),
                ('browser skipped', ['completion', 'browser_discovery'], {}, False),
                ('browser unconfirmed', ['completion', 'browser_discovery', 'owner_confirmation_ref'], '', False),
                ('browser unapproved', ['completion', 'browser_discovery', 'discovery_approval_ref'], '', False),
                ('unknown candidate', ['completion', 'browser_discovery', 'candidate_service_ids'], ['unknown'], False),
                ('unsupported browser', ['completion', 'browser_discovery', 'status'], 'unsupported', False),
                ('accepted fallback', ['completion', 'browser_discovery'], {'status': 'manual-fallback', 'reason': 'history unavailable', 'owner_confirmation_ref': 'fixture-owner-fallback'}, True),
                ('unapproved fallback', ['completion', 'browser_discovery'], {'status': 'manual-fallback', 'reason': 'history unavailable'}, False),
                ('open conflict', ['completion', 'material_gaps'], ['Conflicting price terms'], False),
                ('unsaved knowledge', ['completion', 'storage', 'files'], {}, False),
                ('review pending', ['review_status'], 'needs-owner-review', False),
                ('old review', ['completion', 'owner_review', 'files'], {}, False),
                ('retention skipped', ['completion', 'retention'], {}, False),
                ('missing original', ['completion', 'retention', 'originals'], [{'path': 'sources/manual.pdf', 'source_id': 'owner', 'reason': 'Needed manual'}], False),
                ('session skipped', ['completion', 'fresh_session'], {}, False),
                ('same session', ['completion', 'fresh_session', 'session_id'], 'fixture-session-a', False),
                ('no observed reads', ['completion', 'fresh_session', 'files_read'], {}, False),
                ('index only', ['completion', 'fresh_session', 'files_read'], {'INDEX.md': hashes['INDEX.md']}, False),
                ('applied unread page', ['completion', 'fresh_session', 'applied_evidence_ids'], ['e2'], False),
                ('unapplied evidence', ['completion', 'fresh_session', 'applied_evidence_ids'], [], False),
                ('unknown evidence applied', ['completion', 'fresh_session', 'applied_evidence_ids'], ['absent'], False),
                ('draft changed', ['completion', 'fresh_session', 'draft_sha256'], '0' * 64, False),
                ('owner paused', ['run_status'], 'paused', False),
                ('owner stopped', ['run_status'], 'stopped', False),
                ('owner deferred', ['run_status'], 'deferred', False),
            ]
            cases += [(category + ' missing', ['completion', 'business_coverage', category], {}, False) for category in COVERAGE]
            cases += [('unknown evidence', ['completion', 'business_coverage', 'pricing', 'evidence_ids'], ['absent'], False),
                      ('explicit N/A', ['completion', 'business_coverage', 'pricing'], {'status': 'not-applicable', 'summary': 'No commercial pricing.', 'reason': 'Fictional free service.', 'owner_ref': 'fixture-owner-review', 'saved_paths': ['context/company.md']}, True),
                      ('unjustified N/A', ['completion', 'business_coverage', 'pricing', 'status'], 'not-applicable', False)]
            for name, path, value, passes in cases:
                with self.subTest(name=name):
                    current = copy.deepcopy(state)
                    target = current
                    for key in path[:-1]:
                        target = target[key]
                    if path:
                        target[path[-1]] = value
                    (root / 'state/onboarding.json').write_text(json.dumps(current))
                    before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
                    result = check_onboarding(root)
                    self.assertEqual(result['onboarding_status'], 'onboarding-complete' if passes else 'onboarding-incomplete', result['completion_blockers'])
                    if name in ('all recorded gates', 'source-only run'):
                        cli = subprocess.run([sys.executable, str(SCRIPTS / 'check_onboarding.py'), '--destination', str(root)], capture_output=True, text=True)
                        self.assertEqual(cli.returncode, 0 if passes else 1, cli.stderr)
                    self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})
            (root / 'state/onboarding.json').write_text(json.dumps(state))
            (root / 'context/company.md').write_text('Changed after owner review.')
            result = check_onboarding(root)
            self.assertIn('saved-artifact-missing-or-changed:context/company.md', result['completion_blockers'])
            (root / 'context/company.md').write_text(contents['context/company.md'])
            # Private-only traversal protection, even for otherwise valid receipts.
            state['completion']['fresh_session']['draft_path'] = '../outside.md'
            (root / 'state/onboarding.json').write_text(json.dumps(state))
            with self.assertRaises(ValueError):
                check_onboarding(root)
            state['completion'] = []
            (root / 'state/onboarding.json').write_text(json.dumps(state))
            with self.assertRaises(ValueError):
                check_onboarding(root)


if __name__ == '__main__':
    unittest.main()
