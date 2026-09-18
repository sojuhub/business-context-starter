"""Offline unit tests for the private-only publisher; GitHub calls are mocked."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('publisher',ROOT/'scripts/publish_private.py')
p=importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name).resolve()
        self.file=self.root/'README.md'
        self.file.write_text('Synthetic safe release\n')
        self.write_manifest()
    def tearDown(self):
        self.tmp.cleanup()
    def write_manifest(self,entries=None):
        entries=entries if entries is not None else [{'path':'README.md','sha256':hashlib.sha256(self.file.read_bytes()).hexdigest()}]
        (self.root/p.MANIFEST).write_text(json.dumps({'schema_version':1,'files':entries}))
    def test_valid_manifest(self):
        self.assertEqual(p.checked_files(self.root),[self.file])
    def test_changed_file_is_rejected(self):
        self.file.write_text('Modified after review')
        with self.assertRaises(p.PublishError): p.checked_files(self.root)
    def test_unlisted_private_file_is_not_selected(self):
        (self.root/'private-email.txt').write_text('Not part of the release')
        self.assertEqual(p.checked_files(self.root),[self.file])
    def test_traversal_is_rejected(self):
        self.write_manifest([{'path':'../secret.txt','sha256':'0'*64}])
        with self.assertRaises(p.PublishError): p.checked_files(self.root)
    def test_duplicate_is_rejected(self):
        e={'path':'README.md','sha256':hashlib.sha256(self.file.read_bytes()).hexdigest()}
        self.write_manifest([e,e])
        with self.assertRaises(p.PublishError): p.checked_files(self.root)
    def test_symlink_is_rejected(self):
        target=self.root/'original.md';self.file.rename(target);self.file.symlink_to(target)
        with self.assertRaises(p.PublishError): p.checked_files(self.root)
    def test_obvious_token_is_rejected(self):
        self.file.write_text('gh'+'p_'+'X'*36)
        self.write_manifest()
        with self.assertRaises(p.PublishError): p.checked_files(self.root)
    def test_environment_file_is_rejected(self):
        f=self.root/'.env';f.write_text('example')
        self.write_manifest([{'path':'.env','sha256':hashlib.sha256(f.read_bytes()).hexdigest()}])
        with self.assertRaises(p.PublishError): p.checked_files(self.root)

class RemoteSafetyTests(unittest.TestCase):
    def setUp(self):
        self.calls=[];self.visibility=True;self.creation_fails=False;self.remote_sha='a'*40
        self.user={'login':'sojuhub','id':237377310}
    def runner(self,args,**kwargs):
        self.calls.append(args)
        if args[:3]==['gh','repo','create'] and self.creation_fails:
            raise p.PublishError('Name exists or creation failed')
        output=''
        if args[:3]==['gh','repo','view']:
            output=json.dumps({'isPrivate':self.visibility,'nameWithOwner':'sojuhub/business-context-starter',
                               'url':'https://github.com/sojuhub/business-context-starter'})
        elif args[:3]==['git','rev-parse','HEAD']:
            output='a'*40
        elif args[:2]==['gh','api']:
            output=self.remote_sha
        return subprocess.CompletedProcess(args,0,stdout=output,stderr='')
    def publish(self):
        return p.publish_remote(Path('/synthetic'),'sojuhub','business-context-starter',self.user,runner=self.runner)
    def test_creates_private_and_verifies_before_push(self):
        result=self.publish()
        create=next(c for c in self.calls if c[:3]==['gh','repo','create'])
        self.assertIn('--private',create);self.assertNotIn('--push',create);self.assertNotIn('--public',create)
        check_index=next(i for i,c in enumerate(self.calls) if c[:3]==['gh','repo','view'])
        push_index=next(i for i,c in enumerate(self.calls) if c[0]=='git' and 'push' in c)
        self.assertLess(check_index,push_index)
        self.assertTrue(result['remote_verified']);self.assertEqual(result['github_actions'],'not_checked')
    def test_public_remote_blocks_push(self):
        self.visibility=False
        with self.assertRaises(p.PublishError): self.publish()
        self.assertFalse(any('push' in c for c in self.calls))
    def test_existing_name_does_not_get_overwritten(self):
        self.creation_fails=True
        with self.assertRaises(p.PublishError): self.publish()
        self.assertFalse(any('push' in c for c in self.calls))
    def test_wrong_account_has_no_side_effects(self):
        self.user['login']='different-account'
        with self.assertRaises(p.PublishError): self.publish()
        self.assertEqual(self.calls,[])
    def test_remote_commit_mismatch_is_not_success(self):
        self.remote_sha='b'*40
        with self.assertRaises(p.PublishError): self.publish()
    def test_remote_identity_mismatch_is_rejected(self):
        with self.assertRaises(p.PublishError):
            p.verify_private({'isPrivate':True,'nameWithOwner':'another/repo','url':'https://github.com/another/repo'},
                             'sojuhub/business-context-starter')
    def test_false_like_private_is_rejected(self):
        with self.assertRaises(p.PublishError):
            p.verify_private({'isPrivate':'false','nameWithOwner':'sojuhub/business-context-starter',
                              'url':'https://github.com/sojuhub/business-context-starter'},'sojuhub/business-context-starter')

if __name__=='__main__': unittest.main()
