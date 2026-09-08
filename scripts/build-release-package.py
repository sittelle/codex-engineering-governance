#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
EPOCH = (1980, 1, 1, 0, 0, 0)


class PackageBuildError(RuntimeError):
    pass


def _git(repo: Path, *args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(['git', *args], cwd=repo, capture_output=True, text=text, check=False)


def _require_clean_head(repo: Path) -> str:
    top = _git(repo, 'rev-parse', '--show-toplevel')
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != repo.resolve():
        raise PackageBuildError('--repo must be the root of a Git working tree')
    head = _git(repo, 'rev-parse', 'HEAD')
    if head.returncode != 0:
        raise PackageBuildError('cannot resolve Git HEAD')
    status = _git(repo, 'status', '--porcelain=v1', '--untracked-files=all')
    if status.returncode != 0:
        raise PackageBuildError('cannot inspect Git worktree status')
    if status.stdout.strip():
        raise PackageBuildError('release package build requires a clean Git worktree')
    return head.stdout.strip()


def _head_bytes(repo: Path, rel: str) -> bytes:
    proc = _git(repo, 'show', f'HEAD:{rel}', text=False)
    if proc.returncode != 0:
        raise PackageBuildError(f'MANIFEST path is not a file at Git HEAD: {rel}')
    return proc.stdout


def _head_tree(repo: Path) -> dict[str, str]:
    proc = _git(repo, 'ls-tree', '-r', '-z', 'HEAD', text=False)
    if proc.returncode != 0:
        raise PackageBuildError('cannot read Git HEAD tree')
    result: dict[str, str] = {}
    for entry in proc.stdout.split(b'\0'):
        if not entry:
            continue
        meta, raw_path = entry.split(b'\t', 1)
        mode, kind, _sha = meta.decode('ascii').split(' ', 2)
        path = raw_path.decode('utf-8')
        if kind == 'blob':
            result[path] = mode
    return result


def _load_distribution(repo: Path) -> tuple[str, list[str], dict[str, str]]:
    version = _head_bytes(repo, 'VERSION').decode('utf-8-sig').strip()
    if not version or '/' in version or '\\' in version:
        raise PackageBuildError(f'invalid VERSION at Git HEAD: {version!r}')
    manifest = json.loads(_head_bytes(repo, 'MANIFEST.json').decode('utf-8'))
    if manifest.get('version') != version:
        raise PackageBuildError('MANIFEST version does not match VERSION at Git HEAD')
    files = manifest.get('files')
    if not isinstance(files, list) or not files or any(not isinstance(x, str) or not x for x in files):
        raise PackageBuildError('MANIFEST files must be a non-empty string list')
    if len(files) != len(set(files)):
        raise PackageBuildError('MANIFEST contains duplicate paths')
    for rel in files:
        p = PurePosixPath(rel)
        if p.is_absolute() or '..' in p.parts or rel.startswith('.git/') or rel == '.git':
            raise PackageBuildError(f'unsafe MANIFEST path: {rel}')
    tree = _head_tree(repo)
    missing = sorted(set(files) - set(tree))
    if missing:
        raise PackageBuildError('MANIFEST path(s) absent from Git HEAD: ' + ', '.join(missing[:8]))
    return version, sorted(files), tree


def _build_once(repo: Path, target: Path, version: str, files: list[str], modes: dict[str, str]) -> None:
    prefix = f'codex-engineering-governance-v{version}/'
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_STORED) as zf:
        for rel in files:
            info = zipfile.ZipInfo(prefix + rel, date_time=EPOCH)
            info.create_system = 3
            mode = 0o755 if modes.get(rel) == '100755' else 0o644
            info.external_attr = ((0o100000 | mode) << 16)
            info.compress_type = zipfile.ZIP_STORED
            data = _head_bytes(repo, rel)
            zf.writestr(info, data, compress_type=zipfile.ZIP_STORED)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def build(repo: Path, output_dir: Path) -> tuple[Path, Path, str, str]:
    repo = repo.resolve()
    output_dir = output_dir.resolve()
    head = _require_clean_head(repo)
    version, files, modes = _load_distribution(repo)
    output_dir.mkdir(parents=True, exist_ok=True)
    final = output_dir / f'codex-engineering-governance-v{version}.zip'
    sidecar = Path(str(final) + '.sha256')
    with tempfile.TemporaryDirectory(prefix='gov-release-build-') as td:
        td = Path(td)
        first = td / 'first.zip'
        second = td / 'second.zip'
        _build_once(repo, first, version, files, modes)
        _build_once(repo, second, version, files, modes)
        if first.read_bytes() != second.read_bytes():
            raise PackageBuildError('independent deterministic rebuilds are not byte-identical')
        shutil.copyfile(first, final)
    digest = sha256(final)
    sidecar.write_text(f'{digest}  {final.name}\n', encoding='ascii', newline='\n')
    return final, sidecar, digest, head


def main() -> int:
    ap = argparse.ArgumentParser(description='Build the deterministic MANIFEST-bounded release ZIP from clean Git HEAD.')
    ap.add_argument('--repo', type=Path, default=ROOT, help='Framework Git worktree root.')
    ap.add_argument('--output-dir', type=Path, help='Destination directory; defaults to the repository parent.')
    args = ap.parse_args()
    output = args.output_dir if args.output_dir else args.repo.resolve().parent
    try:
        archive, sidecar, digest, head = build(args.repo, output)
    except Exception as exc:
        print('Deterministic release package build: FAIL')
        print(f'- {exc}')
        return 1
    print('Deterministic release package build: PASS')
    print(f'- Git HEAD: {head}')
    print(f'- ZIP: {archive}')
    print(f'- SHA-256: {digest}')
    print(f'- sidecar: {sidecar}')
    print('- independent rebuild: byte-identical')
    print('- publication/tag/push actions: none')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
