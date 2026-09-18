"""Regression and real subprocess tests; no Codex runtime or account access."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1]/'plugins/business-context-starter/scripts/context_bridge.py'
spec = importlib.util.spec_from_file_location('bridge_hardened', SCRIPT)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

class HardeningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=str(Path(tempfile.gettempdir()).resolve()))
        self.root = Path(self.tmp.name)
        self.workspace = self.root/'private'
        (self.workspace/'state').mkdir(parents=True)
        (self.workspace/'integration').mkdir()
        (self.workspace/'INDEX.md').write_text('# Test company\n')
        self.state = self.workspace/'state/onboarding.json'
        self.state.write_text(json.dumps({'company_id':'test-company'}))
        self.project = self.root/'project'
        self.project.mkdir()
        self.target = self.project/'AGENTS.md'
        self.target.write_text('# Existing rules\n')
        self.receipt = self.workspace/'integration/receipt.json'
        self.plan_file = self.workspace/'integration/plan.json'
    def tearDown(self):
        self.tmp.cleanup()
    def plan(self):
        return b.make_plan(self.target,self.workspace,'test-company')
    def cli(self,*args):
        return subprocess.run([sys.executable,str(SCRIPT),*args],text=True,capture_output=True,timeout=10)
    def test_large_instruction_receipt_can_be_rolled_back(self):
        original=b'A'*100000+b'\n'
        self.target.write_bytes(original)
        b.apply_plan(self.plan(),self.receipt,approved=True)
        b.rollback(self.receipt,approved=True)
        self.assertEqual(self.target.read_bytes(),original)
    def test_final_instruction_size_is_checked_before_plan(self):
        original=b'A'*(b.MAX_BYTES-20)
        self.target.write_bytes(original)
        with self.assertRaises(b.BridgeError):
            self.plan()
        self.assertEqual(self.target.read_bytes(),original)
    def test_state_must_be_json_object(self):
        self.state.write_text('[]')
        with self.assertRaises(b.BridgeError):
            self.plan()
    def test_cli_plan_apply_rollback_round_trip(self):
        original=self.target.read_bytes()
        r=self.cli('plan','--target',str(self.target),'--workspace',str(self.workspace),'--company-id','test-company','--out',str(self.plan_file))
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(self.target.read_bytes(),original)
        r=self.cli('apply','--plan',str(self.plan_file),'--receipt',str(self.receipt),'--approved')
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn(b'Company context',self.target.read_bytes())
        r=self.cli('rollback','--receipt',str(self.receipt),'--approved')
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(self.target.read_bytes(),original)
    def test_cli_rejects_non_object_plan_without_traceback(self):
        self.plan_file.write_text('[]')
        r=self.cli('apply','--plan',str(self.plan_file),'--receipt',str(self.receipt),'--approved')
        self.assertEqual(r.returncode,2,r.stderr)
        self.assertNotIn('Traceback',r.stderr)
    def test_cli_apply_requires_approval(self):
        original=self.target.read_bytes()
        self.plan_file.write_text(json.dumps(self.plan()))
        r=self.cli('apply','--plan',str(self.plan_file),'--receipt',str(self.receipt))
        self.assertEqual(r.returncode,2)
        self.assertEqual(self.target.read_bytes(),original)
    def test_large_plan_cli_round_trip(self):
        self.target.write_bytes(b'A'*100000+b'\n')
        original=self.target.read_bytes()
        r=self.cli('plan','--target',str(self.target),'--workspace',str(self.workspace),'--company-id','test-company','--out',str(self.plan_file))
        self.assertEqual(r.returncode,0,r.stderr)
        r=self.cli('apply','--plan',str(self.plan_file),'--receipt',str(self.receipt),'--approved')
        self.assertEqual(r.returncode,0,r.stderr)
        r=self.cli('rollback','--receipt',str(self.receipt),'--approved')
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(self.target.read_bytes(),original)

if __name__=='__main__':
    unittest.main()
