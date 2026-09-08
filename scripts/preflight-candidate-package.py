#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _archive_root(names: list[str]) -> str:
    roots = {PurePosixPath(name).parts[0] for name in names if name and not name.endswith('/')}
    if len(roots) != 1:
        raise ValueError(f'candidate ZIP must contain exactly one package root directory, found {len(roots)}')
    return next(iter(roots))


def _record_paths(repo: Path) -> list[str]:
    base = repo / 'tests' / 'governance' / 'evaluations'
    if not base.is_dir():
        raise ValueError(f'behavioral evaluation directory missing: {base}')
    return sorted(
        p.relative_to(repo).as_posix()
        for p in base.rglob('GOV-*.md')
        if p.is_file()
    )


def _scenario_paths(repo: Path) -> list[str]:
    base = repo / 'tests' / 'governance'
    if not base.is_dir():
        raise ValueError(f'governance scenario directory missing: {base}')
    return sorted(p.relative_to(repo).as_posix() for p in base.glob('GOV-*.md') if p.is_file())




def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _publication_redactions(zf: zipfile.ZipFile, prefix: str, rel_names: list[str], version: str) -> dict[str, dict]:
    rel = f'release-evidence/{version}/publication-redaction.json'
    if rel not in rel_names:
        return {}
    record = json.loads(zf.read(prefix + rel).decode('utf-8'))
    if record.get('schema_version') != '1' or record.get('target_version') != version:
        raise ValueError('publication redaction record has invalid schema/target version')
    allowed: dict[str, dict] = {}
    for row in record.get('records') or []:
        path = row.get('path')
        if not isinstance(path, str) or not path.startswith('tests/governance/evaluations/') or not path.endswith('.md'):
            raise ValueError('publication redaction may target only durable behavioral evaluation records')
        if path in allowed:
            raise ValueError(f'duplicate publication redaction path: {path}')
        if row.get('semantics_changed') is not False:
            raise ValueError(f'publication redaction must declare semantics_changed false: {path}')
        for key in ('source_sha256', 'candidate_sha256'):
            value = str(row.get(key) or '')
            if len(value) != 64 or any(ch not in '0123456789abcdef' for ch in value.lower()):
                raise ValueError(f'publication redaction has invalid {key}: {path}')
        allowed[path] = row
    return allowed

def preflight(repo: Path, zip_path: Path, expected_sha256: str) -> dict:
    repo = repo.resolve()
    zip_path = zip_path.resolve()
    expected = expected_sha256.strip().lower()
    if len(expected) != 64 or any(ch not in '0123456789abcdef' for ch in expected):
        raise ValueError('--sha256 must be exactly 64 hexadecimal characters')
    if not zip_path.is_file():
        raise ValueError(f'candidate ZIP not found: {zip_path}')

    actual = sha256_file(zip_path)
    if actual != expected:
        raise ValueError(f'ZIP SHA-256 mismatch: expected {expected}, got {actual}')

    current_records = _record_paths(repo)
    current_scenarios = _scenario_paths(repo)

    with zipfile.ZipFile(zip_path) as zf:
        names = [n for n in zf.namelist() if n and not n.endswith('/')]
        root = _archive_root(names)
        prefix = root + '/'
        rel_names = sorted(n[len(prefix):] for n in names if n.startswith(prefix))
        if len(rel_names) != len(names):
            raise ValueError('candidate ZIP contains files outside its package root')

        for required in ('VERSION', 'MANIFEST.json'):
            if required not in rel_names:
                raise ValueError(f'candidate ZIP missing {required}')

        version = zf.read(prefix + 'VERSION').decode('utf-8-sig').strip()
        if root != f'codex-engineering-governance-v{version}':
            raise ValueError(f'package root {root!r} does not match internal VERSION {version!r}')

        manifest = json.loads(zf.read(prefix + 'MANIFEST.json').decode('utf-8'))
        if manifest.get('version') != version:
            raise ValueError('MANIFEST version does not match VERSION')
        listed = sorted(manifest.get('files') or [])
        if rel_names != listed:
            extra = sorted(set(rel_names) - set(listed))
            missing = sorted(set(listed) - set(rel_names))
            detail = []
            if extra:
                detail.append('extra=' + ', '.join(extra[:8]))
            if missing:
                detail.append('missing=' + ', '.join(missing[:8]))
            raise ValueError('candidate ZIP inventory does not exactly match MANIFEST' + (': ' + '; '.join(detail) if detail else ''))

        packaged_records = sorted(
            rel for rel in rel_names
            if rel.startswith('tests/governance/evaluations/') and PurePosixPath(rel).name.startswith('GOV-') and rel.endswith('.md')
        )
        if current_records != packaged_records:
            raise ValueError(
                f'behavioral evaluation path sets differ: current={len(current_records)} packaged={len(packaged_records)}'
            )
        redactions = _publication_redactions(zf, prefix, rel_names, version)
        used_redactions: set[str] = set()
        identical_records = 0
        for rel in current_records:
            current_bytes = (repo / rel).read_bytes()
            candidate_bytes = zf.read(prefix + rel)
            if current_bytes == candidate_bytes:
                identical_records += 1
                continue
            row = redactions.get(rel)
            if not row:
                raise ValueError(f'behavioral evaluation byte mismatch: {rel}')
            if _sha256_bytes(current_bytes) != row['source_sha256'].lower():
                raise ValueError(f'publication redaction source hash mismatch: {rel}')
            if _sha256_bytes(candidate_bytes) != row['candidate_sha256'].lower():
                raise ValueError(f'publication redaction candidate hash mismatch: {rel}')
            used_redactions.add(rel)
        stale = sorted(set(redactions) - used_redactions)
        if stale:
            raise ValueError('publication redaction record declares unchanged/nonexistent mismatch: ' + ', '.join(stale))

        packaged_scenarios = sorted(
            rel for rel in rel_names
            if PurePosixPath(rel).parent.as_posix() == 'tests/governance'
            and PurePosixPath(rel).name.startswith('GOV-')
            and rel.endswith('.md')
        )
        if current_scenarios != packaged_scenarios:
            raise ValueError(
                f'governance scenario path sets differ: current={len(current_scenarios)} packaged={len(packaged_scenarios)}'
            )
        for rel in current_scenarios:
            if (repo / rel).read_bytes() != zf.read(prefix + rel):
                raise ValueError(f'governance scenario byte mismatch: {rel}')

    return {
        'version': version,
        'sha256': actual,
        'manifest_files': len(rel_names),
        'behavioral_records': len(current_records),
        'behavioral_records_identical': identical_records,
        'publication_redactions': len(used_redactions),
        'scenarios': len(current_scenarios),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description='Preflight a downloaded framework candidate before replacing the current working tree.')
    ap.add_argument('--zip', dest='zip_path', required=True, type=Path, help='Downloaded candidate ZIP.')
    ap.add_argument('--sha256', required=True, help='Expected SHA-256 for the candidate ZIP.')
    ap.add_argument('--repo', type=Path, default=ROOT, help='Current authoritative framework repository used for evidence/scenario preservation comparison.')
    args = ap.parse_args()

    try:
        result = preflight(args.repo, args.zip_path, args.sha256)
    except Exception as exc:
        print('Candidate package preflight: FAIL')
        print(f'- {exc}')
        return 1

    print(f"Candidate package preflight: PASS ({result['version']})")
    print('- ZIP SHA-256: verified')
    print(f"- exact MANIFEST inventory: {result['manifest_files']} files")
    print(f"- behavioral evaluation records: {result['behavioral_records_identical']}/{result['behavioral_records']} byte-identical")
    print(f"- approved publication redactions: {result['publication_redactions']}")
    print(f"- frozen GOV scenarios: {result['scenarios']}/{result['scenarios']} byte-identical")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
