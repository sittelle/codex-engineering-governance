#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, shutil, subprocess, sys, tempfile, zipfile

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(*args):
    return subprocess.run([PYTHON, str(ROOT / 'scripts' / 'validate-governance.py'), *map(str,args)], cwd=ROOT, text=True, capture_output=True)


def test_deterministic_builder(base: Path) -> None:
    fixture = base / 'builder-repo'
    fixture.mkdir()
    (fixture / 'scripts').mkdir()
    shutil.copy2(ROOT / 'scripts' / 'build-release-package.py', fixture / 'scripts' / 'build-release-package.py')
    files = ['MANIFEST.json', 'VERSION', 'hello.txt', 'run.sh', 'scripts/build-release-package.py']
    (fixture / 'VERSION').write_text('1.2.3\n', encoding='utf-8', newline='\n')
    (fixture / 'hello.txt').write_text('hello\n', encoding='utf-8', newline='\n')
    (fixture / 'run.sh').write_text('#!/bin/sh\necho ok\n', encoding='utf-8', newline='\n')
    (fixture / 'run.sh').chmod(0o755)
    (fixture / 'MANIFEST.json').write_text(
        json.dumps({'version': '1.2.3', 'files': sorted(files)}, indent=2) + '\n',
        encoding='utf-8', newline='\n'
    )
    for args in (
        ['git', 'init', '-q'],
        ['git', 'config', 'user.name', 'Builder Test'],
        ['git', 'config', 'user.email', 'builder@example.invalid'],
    ):
        proc = subprocess.run(args, cwd=fixture, text=True, capture_output=True)
        if proc.returncode:
            raise RuntimeError(proc.stdout + proc.stderr)
    subprocess.run(['git', 'add', '-A'], cwd=fixture, check=True)
    # Preserve one executable mode in Git rather than relying on host filesystem mode.
    subprocess.run(['git', 'update-index', '--chmod=+x', 'run.sh'], cwd=fixture, check=True)
    subprocess.run(['git', 'commit', '-qm', 'fixture'], cwd=fixture, check=True)

    out1 = base / 'out1'
    out2 = base / 'out2'
    for out in (out1, out2):
        proc = subprocess.run(
            [PYTHON, str(fixture / 'scripts' / 'build-release-package.py'), '--repo', str(fixture), '--output-dir', str(out)],
            cwd=fixture, text=True, capture_output=True
        )
        if proc.returncode != 0:
            print(proc.stdout)
            print(proc.stderr, file=sys.stderr)
            raise SystemExit('deterministic builder rejected clean Git HEAD fixture')

    a = out1 / 'codex-engineering-governance-v1.2.3.zip'
    b = out2 / 'codex-engineering-governance-v1.2.3.zip'
    if a.read_bytes() != b.read_bytes():
        raise SystemExit('deterministic builder produced different archives across independent runs')
    digest = hashlib.sha256(a.read_bytes()).hexdigest()
    if (out1 / (a.name + '.sha256')).read_text(encoding='ascii') != f'{digest}  {a.name}\n':
        raise SystemExit('deterministic builder SHA-256 sidecar mismatch')
    with zipfile.ZipFile(a) as zf:
        names = zf.namelist()
        prefix = 'codex-engineering-governance-v1.2.3/'
        if names != [prefix + x for x in sorted(files)]:
            raise SystemExit('deterministic builder inventory/order mismatch')
        for name in names:
            if zf.getinfo(name).compress_type != zipfile.ZIP_STORED:
                raise SystemExit('deterministic builder must use ZIP_STORED for cross-host byte reproducibility')
        mode = (zf.getinfo(prefix + 'run.sh').external_attr >> 16) & 0o777
        if mode != 0o755:
            raise SystemExit('deterministic builder did not preserve Git executable mode')

    (fixture / 'hello.txt').write_text('dirty\n', encoding='utf-8', newline='\n')
    proc = subprocess.run(
        [PYTHON, str(fixture / 'scripts' / 'build-release-package.py'), '--repo', str(fixture), '--output-dir', str(base / 'dirty-out')],
        cwd=fixture, text=True, capture_output=True
    )
    if proc.returncode == 0 or 'clean Git worktree' not in proc.stdout:
        raise SystemExit('deterministic builder did not refuse dirty worktree')


def main():
    manifest=json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf-8'))
    listed=manifest['files']
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        source=td/'source'
        # The real development root may itself be a Git checkout. Exclude its
        # repository metadata so this fixture controls exactly which source-only
        # extras are under test and does not copy a live object database.
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        (source/'.git').mkdir()
        (source/'.git'/'HEAD').write_text('ref: refs/heads/test\n', encoding='utf-8')
        (source/'developer-local-helper.ps1').write_text('# local only\n', encoding='utf-8')
        proc=subprocess.run([PYTHON, str(source/'scripts'/'validate-governance.py')], cwd=source, text=True, capture_output=True)
        if proc.returncode != 0:
            print(proc.stdout); print(proc.stderr, file=sys.stderr)
            raise SystemExit('source validation incorrectly rejected non-distribution files')

        good=td/'good.zip'
        prefix=f'codex-engineering-governance-v{manifest["version"]}/'
        with zipfile.ZipFile(good,'w',compression=zipfile.ZIP_DEFLATED) as zf:
            for rel in listed:
                zf.write(ROOT/rel, prefix+rel)
        proc=run('--artifact',good)
        if proc.returncode != 0 or 'artifact inventory exactly matches MANIFEST' not in proc.stdout:
            print(proc.stdout); print(proc.stderr, file=sys.stderr)
            raise SystemExit('exact artifact inventory validation did not pass')

        bad=td/'bad.zip'
        shutil.copy2(good,bad)
        with zipfile.ZipFile(bad,'a',compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(prefix+'undeclared.txt','must be rejected')
        proc=run('--artifact',bad)
        if proc.returncode == 0 or 'artifact contains files omitted from MANIFEST' not in proc.stdout:
            print(proc.stdout); print(proc.stderr, file=sys.stderr)
            raise SystemExit('undeclared artifact member was not rejected')

        test_deterministic_builder(td)

    print('Manifest inventory regression: PASS')
    print('- live source extras do not become package contents')
    print('- exact ZIP inventory matches MANIFEST')
    print('- undeclared artifact file is rejected')
    print('- deterministic clean-HEAD package builder uses ZIP_STORED, preserves Git executable modes, is reproducible, and refuses dirty state')

if __name__=='__main__':
    main()
