#!/usr/bin/env python3
"""Publish only the reviewed release files to a NEW private GitHub repository.

Default: local validation only. --publish authorizes remote creation/upload.
Requires an authenticated GitHub CLI on the machine running this script.
Never changes repository visibility, overwrites an existing remote, force pushes,
reads tokens, changes global git configuration, or includes unlisted files.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'RELEASE_MANIFEST.json'

class PublishError(RuntimeError):
    pass

# Deliberately limited heuristic check, NOT a security audit or a complete DLP scan.
SECRET_PATTERNS = [
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}'),
    re.compile(r'\bgithub_pat_[A-Za-z0-9_]{40,}'),
    re.compile(r'\bsk-proj-[A-Za-z0-9_-]{20,}'),
    re.compile(r'\bxox[baprs]-[A-Za-z0-9-]{20,}'),
]


def checked_files(root: Path) -> list[Path]:
    """Validate an explicit hash allowlist; never git-add the whole user folder."""
    root = root.resolve()
    manifest_path = root / MANIFEST
    if manifest_path.is_symlink():
        raise PublishError('Manifest must not be a symlink')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if not isinstance(manifest,dict) or manifest.get('schema_version') != 1:
        raise PublishError('Unsupported release manifest')
    entries = manifest.get('files')
    if not isinstance(entries,list) or not entries:
        raise PublishError('Release manifest has no files')
    files = []
    seen = set()
    for entry in entries:
        if not isinstance(entry,dict):
            raise PublishError('Invalid release entry')
        relative = entry.get('path','')
        if not isinstance(relative,str):
            raise PublishError('Invalid release path')
        rel = PurePosixPath(relative)
        if (not relative or rel.is_absolute() or '..' in rel.parts or
                '\\' in relative or relative in seen or relative == MANIFEST):
            raise PublishError('Unsafe or duplicate release path')
        seen.add(relative)
        if any(part in {'.git','private-workspaces','node_modules','__pycache__'}
               or part.startswith('.env') for part in rel.parts):
            raise PublishError(f'Private/generated path is not publishable: {relative}')
        file = root.joinpath(*rel.parts)
        probe = file
        while probe != root:
            if probe.is_symlink():
                raise PublishError(f'Symlink is not publishable: {relative}')
            probe = probe.parent
        if not file.is_file() or not file.resolve().is_relative_to(root):
            raise PublishError(f'Missing or outside-root release file: {relative}')
        data = file.read_bytes()
        if hashlib.sha256(data).hexdigest() != entry.get('sha256'):
            raise PublishError(f'File changed since review: {relative}. Review and regenerate the manifest, do not bypass it.')
        text = data.decode('utf-8')
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            raise PublishError(f'Possible credential found in: {relative}')
        files.append(file)
    return files


def run(args: list[str], *, cwd: Path, check: bool=True, capture: bool=True) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env['GH_HOST'] = 'github.com'
    env['GH_PROMPT_DISABLED'] = '1'
    result = subprocess.run(args,cwd=cwd,text=True,capture_output=capture,timeout=240,env=env)
    if check and result.returncode:
        detail = (result.stderr or result.stdout or '').strip()[-2500:]
        raise PublishError(f'Command failed: {args[0]} {args[1] if len(args)>1 else ""}\n{detail}')
    return result


def verify_private(meta: dict, full_name: str) -> None:
    if (not isinstance(meta,dict) or meta.get('isPrivate') is not True or
            meta.get('nameWithOwner','').casefold() != full_name.casefold() or
            meta.get('url','').casefold() != f'https://github.com/{full_name}'.casefold()):
        raise PublishError('Remote identity/private visibility could not be verified; do not push')


def publish_remote(snapshot: Path, owner: str, repo: str, user: dict, runner=run) -> dict:
    """Called only after local validation/tests and --publish. Testable with mocks."""
    full_name = f'{owner}/{repo}'
    if str(user.get('login','')).casefold() != owner.casefold():
        raise PublishError(f'Active GitHub CLI account is not {owner}; no remote write performed')
    user_id = user.get('id')
    if not isinstance(user_id,int) or user_id <= 0:
        raise PublishError('Authenticated user identity is incomplete')
    runner(['git','init','-b','main'],cwd=snapshot)
    runner(['git','add','--all'],cwd=snapshot)  # snapshot contains allowlisted files ONLY
    runner(['git','-c',f'user.name={owner}','-c',f'user.email={user_id}+{owner}@users.noreply.github.com',
            '-c','commit.gpgsign=false','commit','-m','Initialize tested Business Context Starter pilot'],cwd=snapshot)
    local_sha = runner(['git','rev-parse','HEAD'],cwd=snapshot).stdout.strip()
    # Creation MUST succeed. An existing name or any ambiguous error aborts; no reuse or retries.
    runner(['gh','repo','create',full_name,'--private','--disable-wiki','--description',
            'Copy-first business AI onboarding skills and reviewed project-context continuity. Private pilot.'],cwd=snapshot)
    try:
        meta = json.loads(runner(['gh','repo','view',full_name,'--json','isPrivate,nameWithOwner,url'],cwd=snapshot).stdout)
        verify_private(meta,full_name)
        remote=f'https://github.com/{full_name}.git'
        runner(['git','remote','add','origin',remote],cwd=snapshot)
        # Per-command credential helper: no global git config change and no token printed.
        runner(['git','-c','credential.helper=','-c','credential.https://github.com.helper=!gh auth git-credential',
                'push','--set-upstream','origin','main'],cwd=snapshot)
        meta = json.loads(runner(['gh','repo','view',full_name,'--json','isPrivate,nameWithOwner,url'],cwd=snapshot).stdout)
        verify_private(meta,full_name)
        remote_sha=runner(['gh','api',f'repos/{full_name}/git/ref/heads/main','--jq','.object.sha'],cwd=snapshot).stdout.strip()
        if not re.fullmatch(r'[a-f0-9]{40,64}',local_sha) or remote_sha != local_sha:
            raise PublishError('Remote commit does not match the tested local commit')
        return {'repository':full_name,'url':meta['url'],'is_private':True,
                'commit':local_sha,'remote_verified':True,'github_actions':'not_checked',
                'local_checkout':str(snapshot)}
    except Exception as exc:
        raise PublishError(f'A new repository may exist at {full_name}, but upload is NOT verified. '
                           f'Do not recreate, delete or force push it blindly. Local checkout: {snapshot}\n{exc}') from exc


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner',default='sojuhub')
    parser.add_argument('--repo',default='business-context-starter')
    parser.add_argument('--publish',action='store_true',help='Authorize creating a NEW PRIVATE repository and pushing reviewed files')
    args=parser.parse_args(argv)
    try:
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}',args.owner):
            raise PublishError('Invalid GitHub owner')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,99}',args.repo):
            raise PublishError('Invalid repository name')
        files=checked_files(ROOT)
        print(f'Validated {len(files)} reviewed files; extra local files will not be uploaded.',flush=True)
        run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture=False)
        # Recheck after tests, before any network write or snapshot creation.
        files=checked_files(ROOT)
        if not args.publish:
            print('LOCAL CHECKS PASSED. No repository created and nothing uploaded.')
            print('To publish after review, rerun with --publish. Default target: sojuhub/business-context-starter (PRIVATE).')
            return 0
        if not shutil.which('gh') or not shutil.which('git'):
            raise PublishError('GitHub CLI (gh) and git are required. Use an authenticated local Mac Codex; no token should be pasted into chat.')
        user=json.loads(run(['gh','api','--hostname','github.com','user'],cwd=ROOT).stdout)
        if str(user.get('login','')).casefold() != args.owner.casefold():
            raise PublishError(f'Authenticate GitHub CLI as {args.owner}; no repository created')
        snapshot=Path(tempfile.mkdtemp(prefix='business-context-release-')).resolve()
        for source in files+[ROOT/MANIFEST]:
            target=snapshot/source.relative_to(ROOT)
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,target)
        checked_files(snapshot)
        run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=snapshot,capture=False)
        checked_files(snapshot)
        result=publish_remote(snapshot,args.owner,args.repo,user)
        print(json.dumps(result,indent=2))
        (ROOT/'PUBLISH_RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        return 0
    except (PublishError,OSError,ValueError,KeyError,TypeError,subprocess.TimeoutExpired) as exc:
        print(f'STOP: {exc}',file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
