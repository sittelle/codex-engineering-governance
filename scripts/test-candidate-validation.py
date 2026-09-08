#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPLY = ROOT / 'scripts' / 'apply-candidate-package.py'


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'cannot load module {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(argv: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run(['git', *args], cwd=repo)


def write_fake_repo(root: Path) -> None:
    (root / 'tests/governance/evaluations/2026-09-04').mkdir(parents=True)
    (root / 'tests/governance').mkdir(parents=True, exist_ok=True)
    (root / 'tests/governance/evaluations/2026-09-04/GOV-001-attempt-1.md').write_text(
        'record\n', encoding='utf-8', newline='\n'
    )
    (root / 'tests/governance/GOV-001-example.md').write_text('scenario\n', encoding='utf-8', newline='\n')


def make_candidate(repo: Path, zip_path: Path, *, record_bytes: bytes = b'record\n', approved_redaction: bool = False) -> str:
    version = '9.9.9'
    root = f'codex-engineering-governance-v{version}'
    record_path = 'tests/governance/evaluations/2026-09-04/GOV-001-attempt-1.md'
    files = {
        'VERSION': (version + '\n').encode(),
        record_path: record_bytes,
        'tests/governance/GOV-001-example.md': b'scenario\n',
    }
    if approved_redaction:
        source = (repo / record_path).read_bytes()
        redaction = {
            'schema_version': '1',
            'target_version': version,
            'purpose': 'test publication redaction',
            'records': [{
                'path': record_path,
                'source_sha256': hashlib.sha256(source).hexdigest(),
                'candidate_sha256': hashlib.sha256(record_bytes).hexdigest(),
                'semantics_changed': False,
                'original_retained': 'test private archive',
                'replacement': '<GOVERNANCE_ROOT>/example',
            }],
        }
        files[f'release-evidence/{version}/publication-redaction.json'] = (json.dumps(redaction, indent=2) + '\n').encode()
    manifest_files = sorted(['MANIFEST.json', *files])
    manifest = {'version': version, 'files': manifest_files}
    files['MANIFEST.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in manifest_files:
            zf.writestr(f'{root}/{rel}', files[rel])
    return hashlib.sha256(zip_path.read_bytes()).hexdigest()


def init_apply_repo(root: Path) -> None:
    write_fake_repo(root)
    (root / 'scripts').mkdir(parents=True, exist_ok=True)
    (root / 'VERSION').write_text('1.0.0\n', encoding='utf-8', newline='\n')
    (root / 'managed.txt').write_text('old managed\n', encoding='utf-8', newline='\n')
    (root / 'retired.txt').write_text('retire me\n', encoding='utf-8', newline='\n')
    (root / 'scripts/validate-candidate.py').write_text(
        "print('fake current validator')\nraise SystemExit(0)\n", encoding='utf-8', newline='\n'
    )
    current_files = sorted([
        'MANIFEST.json',
        'VERSION',
        'managed.txt',
        'retired.txt',
        'scripts/validate-candidate.py',
        'tests/governance/GOV-001-example.md',
        'tests/governance/evaluations/2026-09-04/GOV-001-attempt-1.md',
    ])
    (root / 'MANIFEST.json').write_text(
        json.dumps({'version': '1.0.0', 'files': current_files}, indent=2) + '\n',
        encoding='utf-8', newline='\n'
    )
    # Tracked source-only content must survive a candidate application because it
    # is not owned by the distribution MANIFEST.
    (root / 'developer-source.txt').write_text('preserve tracked source\n', encoding='utf-8', newline='\n')
    (root / '.gitignore').write_text('ignored-local.txt\n', encoding='utf-8', newline='\n')
    (root / 'ignored-local.txt').write_text('preserve ignored local\n', encoding='utf-8', newline='\n')

    proc = git(root, 'init', '-q')
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    git(root, 'config', 'user.name', 'Candidate Tool Test')
    git(root, 'config', 'user.email', 'candidate-tool-test@example.invalid')
    git(root, 'add', '-A')
    proc = git(root, 'commit', '-qm', 'fixture baseline')
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout + proc.stderr)


def make_apply_candidate(zip_path: Path, *, validator_exit: int = 0, unsafe_git_path: bool = False, collide_nonmanifest: bool = False) -> str:
    version = '1.1.0'
    root = f'codex-engineering-governance-v{version}'
    validator = (
        "print('fake candidate validation: {}')\nraise SystemExit({})\n".format(
            'PASS' if validator_exit == 0 else 'FAIL', validator_exit
        )
    ).encode()
    files: dict[str, bytes] = {
        'VERSION': b'1.1.0\n',
        'managed.txt': b'new managed\n',
        'new-managed.txt': b'new file\n',
        'scripts/validate-candidate.py': validator,
        'tests/governance/evaluations/2026-09-04/GOV-001-attempt-1.md': b'record\n',
        'tests/governance/GOV-001-example.md': b'scenario\n',
    }
    if unsafe_git_path:
        files['.git/config'] = b'[malicious]\n'
    if collide_nonmanifest:
        files['developer-source.txt'] = b'candidate must not overwrite source-only file\n'
    manifest_files = sorted(['MANIFEST.json', *files])
    files['MANIFEST.json'] = (
        json.dumps({'version': version, 'files': manifest_files}, indent=2) + '\n'
    ).encode()
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in manifest_files:
            zf.writestr(f'{root}/{rel}', files[rel])
    return hashlib.sha256(zip_path.read_bytes()).hexdigest()


def apply_cmd(repo: Path, zip_path: Path, sha: str, *, apply: bool = False) -> list[str]:
    cmd = [
        sys.executable, str(APPLY), '--repo', str(repo), '--zip', str(zip_path), '--sha256', sha,
    ]
    if apply:
        cmd.append('--apply')
    return cmd


def repo_snapshot(repo: Path) -> dict[str, bytes]:
    return {
        p.relative_to(repo).as_posix(): p.read_bytes()
        for p in repo.rglob('*')
        if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts
    }


def main() -> int:
    failures: list[str] = []
    preflight = load_module('candidate_preflight', ROOT / 'scripts/preflight-candidate-package.py')

    # Existing package preflight contracts.
    with tempfile.TemporaryDirectory(prefix='gov-candidate-preflight-test-') as td:
        base = Path(td)
        repo = base / 'repo'
        repo.mkdir()
        write_fake_repo(repo)

        good_zip = base / 'good.zip'
        good_sha = make_candidate(repo, good_zip)
        try:
            result = preflight.preflight(repo, good_zip, good_sha)
            if result.get('behavioral_records') != 1 or result.get('scenarios') != 1:
                failures.append('preflight good package returned unexpected counts')
        except Exception as exc:
            failures.append(f'preflight rejected valid package: {exc}')

        try:
            preflight.preflight(repo, good_zip, '0' * 64)
            failures.append('preflight accepted incorrect ZIP SHA-256')
        except ValueError:
            pass

        bad_zip = base / 'bad-record.zip'
        bad_sha = make_candidate(repo, bad_zip, record_bytes=b'changed\n')
        try:
            preflight.preflight(repo, bad_zip, bad_sha)
            failures.append('preflight accepted changed behavioral evidence')
        except ValueError as exc:
            if 'behavioral evaluation byte mismatch' not in str(exc):
                failures.append(f'preflight failed changed record for unexpected reason: {exc}')

        redacted_zip = base / 'approved-redaction.zip'
        redacted_sha = make_candidate(repo, redacted_zip, record_bytes=b'redacted path only\n', approved_redaction=True)
        try:
            result = preflight.preflight(repo, redacted_zip, redacted_sha)
            if result.get('publication_redactions') != 1 or result.get('behavioral_records_identical') != 0:
                failures.append('preflight approved-redaction package returned unexpected accounting')
        except Exception as exc:
            failures.append(f'preflight rejected exact hash-bound publication redaction: {exc}')

    # Candidate application is dry-run by default, then performs only the bounded
    # current-MANIFEST -> candidate-MANIFEST transition when --apply is explicit.
    with tempfile.TemporaryDirectory(prefix='gov-candidate-apply-test-') as td:
        base = Path(td)
        repo = base / 'repo'
        repo.mkdir()
        init_apply_repo(repo)
        candidate = base / 'candidate.zip'
        sha = make_apply_candidate(candidate)
        before = repo_snapshot(repo)

        dry = run(apply_cmd(repo, candidate, sha), cwd=ROOT)
        if dry.returncode != 0:
            failures.append('apply-candidate dry-run rejected valid candidate: ' + (dry.stdout + dry.stderr).strip())
        elif 'DRY RUN ONLY' not in dry.stdout or 'repository mutation: none' not in dry.stdout:
            failures.append('apply-candidate dry-run did not report non-mutation contract')
        if repo_snapshot(repo) != before or git(repo, 'status', '--porcelain=v1', '--untracked-files=all').stdout.strip():
            failures.append('apply-candidate dry-run mutated the repository')

        applied = run(apply_cmd(repo, candidate, sha, apply=True), cwd=ROOT)
        if applied.returncode != 0:
            failures.append('apply-candidate rejected valid bounded transition: ' + (applied.stdout + applied.stderr).strip())
        else:
            checks = {
                'candidate version installed': (repo / 'VERSION').read_text(encoding='utf-8').strip() == '1.1.0',
                'managed file updated': (repo / 'managed.txt').read_bytes() == b'new managed\n',
                'new MANIFEST file created': (repo / 'new-managed.txt').read_bytes() == b'new file\n',
                'old MANIFEST-only file removed': not (repo / 'retired.txt').exists(),
                'tracked non-MANIFEST source preserved': (repo / 'developer-source.txt').read_bytes() == b'preserve tracked source\n',
                'ignored local file preserved': (repo / 'ignored-local.txt').read_bytes() == b'preserve ignored local\n',
            }
            for label, ok in checks.items():
                if not ok:
                    failures.append('apply-candidate failed contract: ' + label)
            if 'repository-owned candidate validation: PASS' not in applied.stdout:
                failures.append('apply-candidate did not run post-apply candidate validation')

    # Dirty tracked and non-ignored untracked state are refused before mutation.
    for dirty_kind in ('tracked', 'untracked'):
        with tempfile.TemporaryDirectory(prefix=f'gov-candidate-dirty-{dirty_kind}-') as td:
            base = Path(td)
            repo = base / 'repo'
            repo.mkdir()
            init_apply_repo(repo)
            candidate = base / 'candidate.zip'
            sha = make_apply_candidate(candidate)
            if dirty_kind == 'tracked':
                (repo / 'developer-source.txt').write_text('dirty\n', encoding='utf-8', newline='\n')
            else:
                (repo / 'unexpected.txt').write_text('unexpected\n', encoding='utf-8', newline='\n')
            before = repo_snapshot(repo)
            proc = run(apply_cmd(repo, candidate, sha, apply=True), cwd=ROOT)
            if proc.returncode == 0 or 'worktree has tracked or non-ignored untracked changes' not in proc.stdout:
                failures.append(f'apply-candidate did not refuse {dirty_kind} worktree state')
            if repo_snapshot(repo) != before:
                failures.append(f'apply-candidate mutated repository after refusing {dirty_kind} state')

    # A candidate may not claim/overwrite a file that exists outside the current
    # distribution MANIFEST, even when the Git worktree is otherwise clean.
    with tempfile.TemporaryDirectory(prefix='gov-candidate-nonmanifest-collision-') as td:
        base = Path(td)
        repo = base / 'repo'
        repo.mkdir()
        init_apply_repo(repo)
        candidate = base / 'candidate.zip'
        sha = make_apply_candidate(candidate, collide_nonmanifest=True)
        before = (repo / 'developer-source.txt').read_bytes()
        proc = run(apply_cmd(repo, candidate, sha, apply=True), cwd=ROOT)
        if proc.returncode == 0 or 'outside the current MANIFEST' not in proc.stdout:
            failures.append('apply-candidate accepted overwrite of an existing non-MANIFEST file')
        if (repo / 'developer-source.txt').read_bytes() != before:
            failures.append('apply-candidate modified non-MANIFEST file while rejecting collision')

    # Candidate paths may never target .git, even if a malicious archive includes
    # such a path in its own MANIFEST.
    with tempfile.TemporaryDirectory(prefix='gov-candidate-git-path-') as td:
        base = Path(td)
        repo = base / 'repo'
        repo.mkdir()
        init_apply_repo(repo)
        candidate = base / 'candidate.zip'
        sha = make_apply_candidate(candidate, unsafe_git_path=True)
        before_config = (repo / '.git/config').read_bytes()
        proc = run(apply_cmd(repo, candidate, sha, apply=True), cwd=ROOT)
        if proc.returncode == 0 or 'Git metadata' not in proc.stdout:
            failures.append('apply-candidate accepted candidate MANIFEST path under .git')
        if (repo / '.git/config').read_bytes() != before_config:
            failures.append('apply-candidate modified .git metadata while rejecting unsafe candidate')

    # If candidate validation fails after mutation, restore the exact pre-apply
    # MANIFEST-managed bytes and remove newly-created candidate files.
    with tempfile.TemporaryDirectory(prefix='gov-candidate-rollback-test-') as td:
        base = Path(td)
        repo = base / 'repo'
        repo.mkdir()
        init_apply_repo(repo)
        candidate = base / 'candidate.zip'
        sha = make_apply_candidate(candidate, validator_exit=1)
        before = repo_snapshot(repo)
        proc = run(apply_cmd(repo, candidate, sha, apply=True), cwd=ROOT)
        if proc.returncode == 0:
            failures.append('apply-candidate accepted candidate whose post-apply validation failed')
        elif 'Rollback: PASS' not in proc.stderr:
            failures.append('apply-candidate validation failure did not report successful rollback')
        after = repo_snapshot(repo)
        if after != before:
            failures.append('apply-candidate rollback did not restore pre-apply repository bytes')
        status = git(repo, 'status', '--porcelain=v1', '--untracked-files=all').stdout.strip()
        if status:
            failures.append('apply-candidate rollback did not restore clean Git worktree: ' + status)

    proc = subprocess.run(
        [sys.executable, str(ROOT / 'scripts/validate-candidate.py'), '--self-test'],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        failures.append('validate-candidate self-test failed: ' + (proc.stdout + proc.stderr).strip())

    if failures:
        print('Candidate validation tooling regression: FAIL')
        for failure in failures:
            print('- ' + failure)
        return 1

    print('Candidate validation tooling regression: PASS')
    print('- package hash/inventory/evidence/scenario preservation preflight')
    print('- invalid package SHA rejected')
    print('- changed behavioral evidence rejected')
    print('- candidate application dry-run is non-mutating')
    print('- bounded MANIFEST transition preserves non-MANIFEST files')
    print('- dirty tracked/untracked state is refused')
    print('- existing non-MANIFEST path collisions are refused')
    print('- candidate paths under .git are rejected')
    print('- failed post-apply validation rolls back managed bytes')
    print('- local-full report semantics self-test')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
