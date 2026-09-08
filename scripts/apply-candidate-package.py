#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


class CandidateApplyError(RuntimeError):
    pass


@dataclass(frozen=True)
class CandidateArchive:
    version: str
    root: str
    manifest: dict
    infos: dict[str, zipfile.ZipInfo]


@dataclass(frozen=True)
class ApplyPlan:
    current_version: str
    candidate_version: str
    current_files: frozenset[str]
    candidate_files: frozenset[str]
    create: tuple[str, ...]
    update: tuple[str, ...]
    unchanged: tuple[str, ...]
    remove: tuple[str, ...]
    tracked_preserved: tuple[str, ...]


def _run(argv: list[str], *, cwd: Path, check: bool = False) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False)
    if check and proc.returncode != 0:
        detail = (proc.stdout or '') + (proc.stderr or '')
        raise CandidateApplyError(
            f"command failed ({proc.returncode}): {' '.join(argv)}" + (f"\n{detail.rstrip()}" if detail.strip() else '')
        )
    return proc


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return _run(['git', *args], cwd=repo, check=check)


def _load_preflight():
    path = Path(__file__).resolve().with_name('preflight-candidate-package.py')
    spec = importlib.util.spec_from_file_location('candidate_package_preflight', path)
    if spec is None or spec.loader is None:
        raise CandidateApplyError(f'cannot load package preflight helper: {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _validate_rel_path(rel: str) -> PurePosixPath:
    if not isinstance(rel, str) or not rel:
        raise CandidateApplyError('MANIFEST contains an empty/non-string path')
    if '\\' in rel:
        raise CandidateApplyError(f'MANIFEST path must use POSIX separators: {rel!r}')
    p = PurePosixPath(rel)
    if p.is_absolute() or any(part in ('', '.', '..') for part in p.parts):
        raise CandidateApplyError(f'unsafe MANIFEST path: {rel!r}')
    if any(part.casefold() == '.git' for part in p.parts):
        raise CandidateApplyError(f'candidate/current MANIFEST may not target Git metadata: {rel!r}')
    return p


def _validate_manifest_paths(paths: list[str], label: str) -> None:
    seen: dict[str, str] = {}
    for rel in paths:
        _validate_rel_path(rel)
        folded = rel.casefold()
        previous = seen.get(folded)
        if previous is not None and previous != rel:
            raise CandidateApplyError(
                f'{label} MANIFEST has a case-insensitive path collision: {previous!r} vs {rel!r}'
            )
        seen[folded] = rel


def _zip_member_is_symlink(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0xFFFF
    return stat.S_ISLNK(mode)


def _read_candidate_archive(zip_path: Path) -> CandidateArchive:
    with zipfile.ZipFile(zip_path) as zf:
        file_infos = [i for i in zf.infolist() if i.filename and not i.is_dir()]
        roots = {PurePosixPath(i.filename).parts[0] for i in file_infos}
        if len(roots) != 1:
            raise CandidateApplyError(
                f'candidate ZIP must contain exactly one package root directory, found {len(roots)}'
            )
        root = next(iter(roots))
        prefix = root + '/'
        infos: dict[str, zipfile.ZipInfo] = {}
        for info in file_infos:
            if not info.filename.startswith(prefix):
                raise CandidateApplyError('candidate ZIP contains files outside its package root')
            rel = info.filename[len(prefix):]
            _validate_rel_path(rel)
            if _zip_member_is_symlink(info):
                raise CandidateApplyError(f'candidate ZIP symlink member is not supported: {rel}')
            if rel in infos:
                raise CandidateApplyError(f'candidate ZIP contains duplicate file member: {rel}')
            infos[rel] = info

        if 'VERSION' not in infos or 'MANIFEST.json' not in infos:
            raise CandidateApplyError('candidate ZIP must contain VERSION and MANIFEST.json')
        version = zf.read(infos['VERSION']).decode('utf-8-sig').strip()
        if root != f'codex-engineering-governance-v{version}':
            raise CandidateApplyError(
                f'package root {root!r} does not match internal VERSION {version!r}'
            )
        manifest = json.loads(zf.read(infos['MANIFEST.json']).decode('utf-8'))
        if manifest.get('version') != version:
            raise CandidateApplyError('candidate MANIFEST version does not match candidate VERSION')
        files = manifest.get('files')
        if not isinstance(files, list):
            raise CandidateApplyError('candidate MANIFEST files is not a list')
        _validate_manifest_paths(files, 'candidate')
        if sorted(files) != sorted(infos):
            raise CandidateApplyError('candidate ZIP inventory does not exactly match its MANIFEST')
        return CandidateArchive(version=version, root=root, manifest=manifest, infos=infos)


def _assert_repo(repo: Path) -> None:
    if not repo.is_dir():
        raise CandidateApplyError(f'repository directory not found: {repo}')
    proc = _git(repo, 'rev-parse', '--show-toplevel', check=False)
    if proc.returncode != 0:
        raise CandidateApplyError(f'not a Git working tree: {repo}')
    top = Path(proc.stdout.strip()).resolve()
    if top != repo.resolve():
        raise CandidateApplyError(f'--repo must be the Git worktree root: expected {top}, got {repo.resolve()}')
    if not (repo / 'VERSION').is_file() or not (repo / 'MANIFEST.json').is_file():
        raise CandidateApplyError('current repository is missing VERSION or MANIFEST.json')


def _assert_clean(repo: Path) -> None:
    proc = _git(repo, 'status', '--porcelain=v1', '--untracked-files=all')
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    if lines:
        preview = '\n'.join(lines[:20])
        suffix = '' if len(lines) <= 20 else f'\n... and {len(lines) - 20} more'
        raise CandidateApplyError(
            'refusing candidate application: Git worktree has tracked or non-ignored untracked changes\n'
            + preview + suffix
        )


def _current_distribution(repo: Path) -> tuple[str, dict, list[str]]:
    version = (repo / 'VERSION').read_text(encoding='utf-8-sig').strip()
    manifest = json.loads((repo / 'MANIFEST.json').read_text(encoding='utf-8'))
    if manifest.get('version') != version:
        raise CandidateApplyError('current MANIFEST version does not match current VERSION')
    files = manifest.get('files')
    if not isinstance(files, list):
        raise CandidateApplyError('current MANIFEST files is not a list')
    _validate_manifest_paths(files, 'current')
    return version, manifest, files


def _assert_regular_repo_target(repo: Path, rel: str, *, allow_missing: bool = True) -> Path:
    p = _validate_rel_path(rel)
    current = repo
    for part in p.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise CandidateApplyError(f'refusing to traverse symlinked parent for managed path: {rel}')
        if current.exists() and not current.is_dir():
            raise CandidateApplyError(f'managed path parent is not a directory: {rel}')
    target = repo.joinpath(*p.parts)
    if target.is_symlink():
        raise CandidateApplyError(f'managed path itself is a symlink: {rel}')
    if target.exists() and not target.is_file():
        raise CandidateApplyError(f'managed path is not a regular file: {rel}')
    if not target.exists() and not allow_missing:
        raise CandidateApplyError(f'current MANIFEST-listed file is missing: {rel}')
    return target


def _tracked_files(repo: Path) -> set[str]:
    proc = _git(repo, 'ls-files', '-z')
    return {item for item in proc.stdout.split('\0') if item}


def _candidate_bytes(zip_path: Path, archive: CandidateArchive, rel: str) -> bytes:
    with zipfile.ZipFile(zip_path) as zf:
        return zf.read(archive.infos[rel])


def _build_plan(repo: Path, zip_path: Path, archive: CandidateArchive) -> ApplyPlan:
    current_version, _manifest, current_list = _current_distribution(repo)
    current = frozenset(current_list)
    candidate = frozenset(archive.manifest['files'])

    for rel in sorted(current):
        _assert_regular_repo_target(repo, rel, allow_missing=False)

    tracked = _tracked_files(repo)
    tracked_nonmanifest = tracked - set(current)
    tracked_nonmanifest_casefold = {rel.casefold(): rel for rel in tracked_nonmanifest}
    for rel in sorted(candidate):
        target = _assert_regular_repo_target(repo, rel, allow_missing=True)
        if rel not in current and target.exists():
            raise CandidateApplyError(
                f'candidate new MANIFEST path already exists outside the current MANIFEST; refusing overwrite: {rel}'
            )
        if rel not in current and rel.casefold() in tracked_nonmanifest_casefold:
            existing = tracked_nonmanifest_casefold[rel.casefold()]
            raise CandidateApplyError(
                f'candidate new MANIFEST path collides with tracked non-MANIFEST source path: {rel!r} vs {existing!r}'
            )

    create: list[str] = []
    update: list[str] = []
    unchanged: list[str] = []
    with zipfile.ZipFile(zip_path) as zf:
        for rel in sorted(candidate):
            target = repo.joinpath(*PurePosixPath(rel).parts)
            payload = zf.read(archive.infos[rel])
            if not target.exists():
                create.append(rel)
            elif target.read_bytes() == payload:
                unchanged.append(rel)
            else:
                update.append(rel)

    remove = sorted(current - candidate)
    tracked_preserved = sorted(tracked_nonmanifest)
    return ApplyPlan(
        current_version=current_version,
        candidate_version=archive.version,
        current_files=current,
        candidate_files=candidate,
        create=tuple(create),
        update=tuple(update),
        unchanged=tuple(unchanged),
        remove=tuple(remove),
        tracked_preserved=tuple(tracked_preserved),
    )


def _print_plan(plan: ApplyPlan, *, applying: bool) -> None:
    print('Candidate package application plan')
    print(f'- mode:              {"APPLY" if applying else "DRY RUN"}')
    print(f'- current version:   {plan.current_version}')
    print(f'- candidate version: {plan.candidate_version}')
    print(f'- create:            {len(plan.create)}')
    print(f'- update:            {len(plan.update)}')
    print(f'- unchanged:         {len(plan.unchanged)}')
    print(f'- remove:            {len(plan.remove)}')
    print(f'- tracked non-MANIFEST files preserved: {len(plan.tracked_preserved)}')
    if plan.create:
        print('Create:')
        for rel in plan.create:
            print(f'  + {rel}')
    if plan.remove:
        print('Remove (old MANIFEST only):')
        for rel in plan.remove:
            print(f'  - {rel}')
    if not applying:
        print('DRY RUN ONLY. Re-run with --apply to perform the bounded MANIFEST transition.')


def _mode_from_zip(info: zipfile.ZipInfo) -> int | None:
    mode = (info.external_attr >> 16) & 0xFFFF
    if mode == 0:
        return None
    perms = stat.S_IMODE(mode)
    return perms or None


def _atomic_write(target: Path, data: bytes, mode: int | None) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix='.candidate-apply-', dir=str(target.parent))
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        if mode is not None and os.name != 'nt':
            os.chmod(tmp, mode)
        os.replace(tmp, target)
        if mode is not None and os.name != 'nt':
            os.chmod(target, mode)
    finally:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass


def _snapshot(repo: Path, paths: set[str]) -> dict[str, tuple[bytes, int | None] | None]:
    snap: dict[str, tuple[bytes, int | None] | None] = {}
    for rel in sorted(paths):
        target = _assert_regular_repo_target(repo, rel, allow_missing=True)
        if target.exists():
            mode = stat.S_IMODE(target.stat().st_mode) if os.name != 'nt' else None
            snap[rel] = (target.read_bytes(), mode)
        else:
            snap[rel] = None
    return snap


def _rollback(repo: Path, snapshot: dict[str, tuple[bytes, int | None] | None]) -> list[str]:
    failures: list[str] = []
    # Remove paths that did not exist before, deepest paths first.
    for rel in sorted((r for r, state in snapshot.items() if state is None), key=lambda x: (-len(PurePosixPath(x).parts), x)):
        target = repo.joinpath(*PurePosixPath(rel).parts)
        try:
            if target.is_symlink():
                failures.append(f'rollback refused unexpected symlink: {rel}')
            elif target.exists():
                if target.is_file():
                    target.unlink()
                else:
                    failures.append(f'rollback found unexpected non-file: {rel}')
        except Exception as exc:
            failures.append(f'rollback remove failed for {rel}: {exc}')

    for rel in sorted(r for r, state in snapshot.items() if state is not None):
        data, mode = snapshot[rel]  # type: ignore[misc]
        target = repo.joinpath(*PurePosixPath(rel).parts)
        try:
            if target.exists() and not target.is_file():
                failures.append(f'rollback target is not a regular file: {rel}')
                continue
            _atomic_write(target, data, mode)
        except Exception as exc:
            failures.append(f'rollback restore failed for {rel}: {exc}')
    return failures


def _verify_applied(repo: Path, zip_path: Path, archive: CandidateArchive, plan: ApplyPlan) -> None:
    with zipfile.ZipFile(zip_path) as zf:
        for rel in sorted(plan.candidate_files):
            target = _assert_regular_repo_target(repo, rel, allow_missing=False)
            expected = zf.read(archive.infos[rel])
            actual = target.read_bytes()
            if actual != expected:
                raise CandidateApplyError(f'post-apply byte mismatch: {rel}')
        for rel in plan.remove:
            target = repo.joinpath(*PurePosixPath(rel).parts)
            if target.exists() or target.is_symlink():
                raise CandidateApplyError(f'old MANIFEST-only path still exists after apply: {rel}')

    version = (repo / 'VERSION').read_text(encoding='utf-8-sig').strip()
    if version != archive.version:
        raise CandidateApplyError(f'post-apply VERSION mismatch: expected {archive.version}, got {version}')
    manifest_bytes = (repo / 'MANIFEST.json').read_bytes()
    expected_manifest = _candidate_bytes(zip_path, archive, 'MANIFEST.json')
    if manifest_bytes != expected_manifest:
        raise CandidateApplyError('post-apply MANIFEST.json does not byte-match candidate package')


def _run_post_apply_validation(repo: Path) -> None:
    validator = repo / 'scripts' / 'validate-candidate.py'
    if not validator.is_file():
        raise CandidateApplyError('candidate did not install scripts/validate-candidate.py')
    print('\n===== Repository-owned candidate validation =====')
    proc = subprocess.run([sys.executable, str(validator)], cwd=repo, check=False)
    if proc.returncode != 0:
        raise CandidateApplyError(f'candidate local validation failed with exit code {proc.returncode}')


def _apply(repo: Path, zip_path: Path, archive: CandidateArchive, plan: ApplyPlan) -> None:
    touched = set(plan.current_files) | set(plan.candidate_files)
    snapshot = _snapshot(repo, touched)
    try:
        # Only old MANIFEST-owned files may be deleted. No directory is recursively removed.
        for rel in plan.remove:
            target = _assert_regular_repo_target(repo, rel, allow_missing=False)
            target.unlink()

        with zipfile.ZipFile(zip_path) as zf:
            for rel in sorted(plan.candidate_files):
                target = _assert_regular_repo_target(repo, rel, allow_missing=True)
                data = zf.read(archive.infos[rel])
                mode = _mode_from_zip(archive.infos[rel])
                if target.exists() and target.read_bytes() == data:
                    if mode is not None and os.name != 'nt':
                        os.chmod(target, mode)
                    continue
                _atomic_write(target, data, mode)

        _verify_applied(repo, zip_path, archive, plan)
        _run_post_apply_validation(repo)
        # Validation is expected to be non-mutating for distribution files. Recheck
        # the candidate bytes afterward so a buggy validator cannot leave the
        # MANIFEST-managed tree different from the verified package.
        _verify_applied(repo, zip_path, archive, plan)
    except BaseException as exc:
        print('\nCandidate application failed; restoring pre-apply MANIFEST-managed files.', file=sys.stderr)
        rollback_failures = _rollback(repo, snapshot)
        if rollback_failures:
            print('ROLLBACK INCOMPLETE:', file=sys.stderr)
            for failure in rollback_failures:
                print(f'- {failure}', file=sys.stderr)
            raise CandidateApplyError(
                f'{exc}\nrollback did not fully restore the pre-apply tree; manual recovery is required'
            ) from exc
        print('Rollback: PASS (pre-apply MANIFEST-managed file bytes restored)', file=sys.stderr)
        raise


def apply_candidate(repo: Path, zip_path: Path, expected_sha256: str, *, apply: bool) -> ApplyPlan:
    repo = repo.resolve()
    zip_path = zip_path.resolve()
    _assert_repo(repo)
    _assert_clean(repo)
    if not zip_path.is_file():
        raise CandidateApplyError(f'candidate ZIP not found: {zip_path}')

    # Operate on one private snapshot of the downloaded archive. The existing
    # package preflight validates that snapshot against the caller-provided digest,
    # so later planning/application cannot observe a different file if the download
    # path changes concurrently.
    with tempfile.TemporaryDirectory(prefix='governance-candidate-archive-') as td:
        stable_zip = Path(td) / 'candidate.zip'
        shutil.copyfile(zip_path, stable_zip)

        # Existing package preflight remains authoritative for digest/inventory and
        # behavioral evidence/scenario preservation. The apply tool orchestrates it;
        # it does not create a second preservation policy.
        preflight = _load_preflight()
        try:
            preflight_result = preflight.preflight(repo, stable_zip, expected_sha256)
        except Exception as exc:
            raise CandidateApplyError(f'candidate package preflight failed: {exc}') from exc

        archive = _read_candidate_archive(stable_zip)
        if archive.version != preflight_result.get('version'):
            raise CandidateApplyError('candidate version changed between preflight and application planning')
        plan = _build_plan(repo, stable_zip, archive)
        _print_plan(plan, applying=apply)
        if apply:
            _apply(repo, stable_zip, archive, plan)
        return plan


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            'Safely plan or apply a framework candidate package using the current and candidate MANIFESTs. '
            'Default is dry-run; --apply is required for mutation.'
        )
    )
    ap.add_argument('--zip', dest='zip_path', required=True, type=Path, help='Downloaded candidate ZIP.')
    ap.add_argument('--sha256', required=True, help='Expected SHA-256 for the candidate ZIP.')
    ap.add_argument('--repo', type=Path, default=ROOT, help='Current authoritative framework Git worktree.')
    ap.add_argument('--apply', action='store_true', help='Apply the bounded MANIFEST transition after preflight and dry-run planning.')
    args = ap.parse_args()

    try:
        plan = apply_candidate(args.repo, args.zip_path, args.sha256, apply=args.apply)
    except Exception as exc:
        print('\n========================================')
        print('Candidate package application: FAIL')
        print(f'- {exc}')
        return 1

    print('\n========================================')
    if args.apply:
        print(f'Candidate package application: PASS ({plan.candidate_version})')
        print('- package preflight: PASS')
        print('- bounded MANIFEST transition: PASS')
        print('- candidate MANIFEST files: byte-identical to ZIP')
        print('- old MANIFEST-only files: removed individually')
        print('- non-MANIFEST files: preserved')
        print('- repository-owned candidate validation: PASS')
    else:
        print(f'Candidate package application dry-run: PASS ({plan.candidate_version})')
        print('- package preflight: PASS')
        print('- repository mutation: none')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
