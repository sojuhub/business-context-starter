import json
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
PLUGIN=ROOT/'plugins/business-context-starter'

class PackageTests(unittest.TestCase):
    def read_json(self,p): return json.loads(p.read_text())
    def test_all_json_parse(self):
        for p in ROOT.rglob('*.json'):
            with self.subTest(path=str(p)):
                self.read_json(p)
    def test_portable_manifest_minimal_contract(self):
        m=self.read_json(PLUGIN/'plugin.json')
        self.assertEqual(m['$schema'],'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json')
        self.assertRegex(m['name'],r'^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$')
        self.assertLessEqual(len(m['name']),64)
        self.assertEqual(set(m)-{'$schema','name','version','description','author','homepage','repository','license','keywords','extensions'},set())
        self.assertIsInstance(m['extensions']['com.openai'],dict)
    def test_host_manifests_share_identity(self):
        m=self.read_json(PLUGIN/'plugin.json')
        for p in ['.codex-plugin/plugin.json','.claude-plugin/plugin.json']:
            a=self.read_json(PLUGIN/p)
            self.assertEqual((a['name'],a['version']),(m['name'],m['version']))
    def test_marketplace_points_inside_repo(self):
        m=self.read_json(ROOT/'.agents/plugins/marketplace.json')
        self.assertEqual(len(m['plugins']),1)
        p=m['plugins'][0]
        self.assertEqual(p['policy']['installation'],'AVAILABLE')
        path=(ROOT/p['source']['path']).resolve()
        self.assertEqual(path,PLUGIN.resolve())
    def test_exactly_two_internal_skills(self):
        skills=list((PLUGIN/'skills').glob('*/SKILL.md'))
        self.assertEqual({p.parent.name for p in skills},{'start','use-business-context'})
        for p in skills:
            text=p.read_text();self.assertTrue(text.startswith('---\n'))
            header=text.split('---',2)[1]
            self.assertIn('name:',header); self.assertIn('description:',header)
    def test_skill_links_are_internal_and_resolve(self):
        for p in (PLUGIN/'skills').glob('*/SKILL.md'):
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
                q=(p.parent/target).resolve()
                self.assertTrue(q.is_relative_to(PLUGIN.resolve()))
                self.assertTrue(q.exists(),str(q))
    def test_no_default_hooks_or_bundled_connections(self):
        for name in ['hooks','mcp.json','.mcp.json','.app.json','settings.json']:
            self.assertFalse((PLUGIN/name).exists(),name)
        self.assertFalse((ROOT/'.codex/config.toml').exists())
    def test_notices_present_in_installed_package(self):
        self.assertIn('MIT License',(PLUGIN/'LICENSE').read_text())
        for name in ['company-ai-os-LICENSE','openai-context-skill-LICENSE']:
            self.assertIn('Permission is hereby granted',(PLUGIN/'third_party'/name).read_text())
    def test_status_and_onboarding_bounds_visible(self):
        self.assertIn('NOT YET RUN',(ROOT/'docs/ACCEPTANCE.md').read_text())
        readme=(ROOT/'README.md').read_text()
        self.assertIn('public instruction alpha',readme)
        self.assertIn('End-to-end host behavior remains unverified',readme)
        s=(PLUGIN/'skills/start/SKILL.md').read_text()
        self.assertIn('No global instruction changes',s)
        self.assertIn('Do not replace requested real integration with fabricated',s)
    def test_brief_and_start_exist(self):
        for p in ['START_HERE.md','docs/PRODUCT_DECISION.md','docs/SOURCES.md','examples/alder-cup-owner-brief.md']:
            self.assertTrue((ROOT/p).is_file(),p)

if __name__=='__main__': unittest.main()
