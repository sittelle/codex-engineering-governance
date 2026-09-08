#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, platform, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOOL_ROOT=ROOT/'.framework-tools'
LOCK=ROOT/'tools/framework-tools.lock.json'
OPERATIONAL_EXIT=125

def norm_os(v):
    raw=(v or '').lower()
    return 'Windows' if raw.startswith('win') else ('Linux' if raw=='linux' else v)

def norm_machine(v):
    v=(v or '').lower().replace('-','_')
    return 'x86_64' if v in {'amd64','x86_64','x64'} else ('arm64' if v in {'arm64','aarch64'} else v)

def host(): return {'os':norm_os(platform.system()),'machine':norm_machine(platform.machine())}

def locked(tool):
    h=host(); d=json.loads(LOCK.read_text(encoding='utf-8'))
    return next((x for x in d['tools'] if x['id']==tool and x['target']==h),None)

def run(argv,cwd=None):
    return subprocess.run(argv,cwd=cwd,text=True,capture_output=True,check=False)

def _bounded(result, limit=1000):
    parts=[]
    for text in (result.stdout or '', result.stderr or ''):
        text=text.strip()
        if text: parts.append(text)
    detail='\n'.join(parts)
    return detail[-limit:] if len(detail)>limit else detail

def evaluate_pair(name,pos,neg,positive_codes,operational_codes,failures,operational_issues):
    blocked=[]
    for phase,result in (('positive',pos),('negative',neg)):
        if result.returncode in operational_codes:
            detail=_bounded(result)
            msg=f'{name} {phase} fixture operational nonexecution (exit {result.returncode})'
            if detail: msg += ': ' + detail
            operational_issues.append(msg)
            blocked.append(phase)
    if blocked:
        return False
    if pos.returncode not in positive_codes:
        detail=_bounded(pos)
        msg=f'{name} positive fixture not detected (exit {pos.returncode})'
        if detail: msg += ': ' + detail
        failures.append(msg)
    if neg.returncode!=0:
        detail=_bounded(neg)
        msg=f'{name} negative fixture did not pass (exit {neg.returncode})'
        if detail: msg += ': ' + detail
        failures.append(msg)
    return True

def linux_tests(failures, operational_issues):
    operational=False
    with tempfile.TemporaryDirectory() as td:
        t=Path(td)
        # tempfile roots are commonly mode 0700. The pinned Semgrep image runs non-root,
        # so make only this synthetic fixture tree traversable/readable by the container.
        t.chmod(0o755)

        e=locked('gitleaks'); exe=TOOL_ROOT/'bin'/'gitleaks'
        if not e or not exe.exists(): return True
        pos=t/'gitleaks-pos'; neg=t/'gitleaks-neg'; pos.mkdir(); neg.mkdir()
        # Use a deterministic synthetic GitHub-PAT-shaped value that satisfies the
        # pinned Gitleaks rule without containing its global alphabet stopword. The
        # value is assembled at runtime so the framework source does not itself
        # contain a PAT-shaped positive fixture.
        synthetic_pat='ghp_'+'F7aQ2mN9xR4kT8vB1pD6sH3wJ0cL5yG7zK2u'
        (pos/'x.txt').write_text(f'token = {synthetic_pat}\n',encoding='utf-8')
        (neg/'x.txt').write_text('token = example-placeholder-not-a-secret\n',encoding='utf-8')
        config=ROOT/'.gitleaks.toml'
        p=run([str(exe),'dir','--no-banner','--redact','--exit-code','10','--config',str(config),str(pos)])
        n=run([str(exe),'dir','--no-banner','--redact','--exit-code','10','--config',str(config),str(neg)])
        if not evaluate_pair('gitleaks',p,n,{10},set(range(1,256))-{10},failures,operational_issues): operational=True

        e=locked('shellcheck'); exe=TOOL_ROOT/'bin'/'shellcheck'
        if not e or not exe.exists(): return True
        pos=t/'bad.sh'; neg=t/'good.sh'
        # The production policy intentionally uses --severity=warning. Exercise a
        # warning-level finding observed in real framework code (SC1007), rather
        # than SC2086, which is informational and correctly filtered at this threshold.
        pos.write_text("#!/bin/sh\ntarget=$(CDPATH= cd -- \".\" && pwd)\nprintf '%s\\n' \"$target\"\n",encoding='utf-8')
        neg.write_text("#!/bin/sh\ntarget=$(CDPATH='' cd -- \".\" && pwd)\nprintf '%s\\n' \"$target\"\n",encoding='utf-8')
        p=run([str(exe),'--severity=warning',str(pos)]); n=run([str(exe),'--severity=warning',str(neg)])
        if not evaluate_pair('shellcheck',p,n,{1},set(range(2,256)),failures,operational_issues): operational=True

        e=locked('semgrep'); docker=shutil.which('docker')
        if not e or not docker: return True
        bad_shell=t/'bad-shell.py'; bad_delete=t/'bad-delete.py'; good=t/'good.py'
        bad_shell.write_text('import subprocess\ndef f(cmd):\n    return subprocess.run(cmd, shell=True)\n',encoding='utf-8')
        bad_delete.write_text('import argparse, shutil\np=argparse.ArgumentParser(); p.add_argument("target"); args=p.parse_args()\nshutil.rmtree(args.target)\n',encoding='utf-8')
        good.write_text('import shutil, subprocess\nfrom pathlib import Path\ndef run(argv):\n    return subprocess.run(argv, check=True)\ndef clean(root, name):\n    root=Path(root).resolve(); target=(root/name).resolve()\n    if target.parent != root: raise ValueError("outside root")\n    shutil.rmtree(target)\n',encoding='utf-8')
        image=f"{e['image'].split(':',1)[0]}@{e['digest']}"
        base=[docker,'run','--rm','-v',f'{ROOT}:/src:ro','-v',f'{t}:/fixture:ro',image,'semgrep','scan','--config','/src/semgrep/framework.yml','--metrics=off','--error']
        for label,path in [('semgrep-shell',bad_shell),('semgrep-destructive-path',bad_delete)]:
            p=run(base+[f'/fixture/{path.name}']); n=run(base+['/fixture/good.py'])
            if not evaluate_pair(label,p,n,{1},set(range(2,256)),failures,operational_issues): operational=True

        e=locked('zizmor'); exe=TOOL_ROOT/'bin'/'zizmor'
        if not e or not exe.exists(): return True
        bad=t/'bad.yml'; goodwf=t/'good.yml'
        bad.write_text('name: bad\non: pull_request_target\njobs:\n  x:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@main\n',encoding='utf-8')
        goodwf.write_text('name: good\non: workflow_dispatch\npermissions:\n  contents: read\njobs:\n  x:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1\n        with:\n          persist-credentials: false\n',encoding='utf-8')
        p=run([str(exe),'--persona=auditor','--min-severity=medium',str(bad)])
        n=run([str(exe),'--persona=auditor','--min-severity=medium',str(goodwf)])
        if not evaluate_pair('zizmor',p,n,{13,14},{1,2,3},failures,operational_issues): operational=True
    return operational

def windows_tests(failures, operational_issues):
    operational=False
    with tempfile.TemporaryDirectory() as td:
        t=Path(td); e=locked('psscriptanalyzer'); pwsh=shutil.which('pwsh') or shutil.which('powershell') or shutil.which('powershell.exe')
        manifest=TOOL_ROOT/'modules'/'PSScriptAnalyzer'/e['version']/e['module_manifest'] if e else None
        if not e or not pwsh or not manifest or not manifest.exists(): return True
        bad=t/'bad.ps1'; good=t/'good.ps1'; display=t/'display.ps1'
        bad.write_text('param([string]$Command)\nInvoke-Expression $Command\n',encoding='utf-8')
        good.write_text('param([string]$Path)\nGet-Item -LiteralPath $Path | Out-Null\n',encoding='utf-8')
        display.write_text("Write-Host 'status'\n",encoding='utf-8')
        adapter=ROOT/'scripts'/'run-framework-scanner.py'
        def scan(path):
            return run([sys.executable,str(adapter),'psscriptanalyzer',str(path)])
        p=scan(bad); n=scan(good); d=scan(display)
        if not evaluate_pair('PSScriptAnalyzer',p,n,{1},{125},failures,operational_issues): operational=True
        if d.returncode==125:
            operational=True
            detail=_bounded(d)
            msg=f'PSScriptAnalyzer display fixture operational nonexecution (exit {d.returncode})'
            if detail: msg += ': ' + detail
            operational_issues.append(msg)
        elif d.returncode!=0:
            failures.append(f'PSScriptAnalyzer intentional Write-Host display fixture did not pass (exit {d.returncode})')
    return operational

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--platform',choices=['auto','linux','windows'],default='auto'); args=ap.parse_args()
    plat=args.platform
    if plat=='auto': plat='windows' if host()['os']=='Windows' else 'linux'
    failures=[]; operational_issues=[]
    if plat=='linux':
        needed=['gitleaks','shellcheck','zizmor']
        missing=[x for x in needed if not (TOOL_ROOT/'bin'/x).exists()]
        sem=locked('semgrep')
        if missing or not sem or not shutil.which('docker'):
            print('Framework scanner regression: DID_NOT_EXECUTE (locked Linux scanner tooling unavailable)')
            return OPERATIONAL_EXIT
        operational=linux_tests(failures, operational_issues)
    else:
        e=locked('psscriptanalyzer'); manifest=(TOOL_ROOT/'modules'/'PSScriptAnalyzer'/e['version']/e['module_manifest']) if e else None
        if not e or not manifest or not manifest.exists() or not (shutil.which('pwsh') or shutil.which('powershell') or shutil.which('powershell.exe')):
            print('Framework scanner regression: DID_NOT_EXECUTE (locked Windows scanner tooling unavailable)')
            return OPERATIONAL_EXIT
        operational=windows_tests(failures, operational_issues)
    if operational:
        print(f'Framework scanner regression ({plat}): DID_NOT_EXECUTE (scanner operational failure)')
        for item in operational_issues: print('- '+item)
        return OPERATIONAL_EXIT
    if failures:
        print(f'Framework scanner regression ({plat}): FAIL')
        for item in failures: print('- '+item)
        return 1
    print(f'Framework scanner regression ({plat}): PASS')
    if plat=='linux': print('- Gitleaks, Semgrep (shell/destructive-path), ShellCheck, and Zizmor positive/negative fixtures')
    else: print('- PSScriptAnalyzer positive/negative fixtures')
    return 0

if __name__=='__main__': raise SystemExit(main())
