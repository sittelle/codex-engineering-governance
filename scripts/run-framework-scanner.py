#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, platform, shutil, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LOCK=ROOT/'tools/framework-tools.lock.json'
TOOL_ROOT=ROOT/'.framework-tools'
OPERATIONAL_EXIT=125

def norm_machine(v):
    v=(v or '').strip().lower().replace('-','_')
    return 'x86_64' if v in {'amd64','x86_64','x64'} else ('arm64' if v in {'arm64','aarch64'} else v)

def norm_os(v):
    raw=(v or '').strip().lower()
    if raw.startswith('win'): return 'Windows'
    if raw=='linux': return 'Linux'
    if raw in {'darwin','macos','mac'}: return 'Darwin'
    return v

def entry(tool):
    host={'os':norm_os(platform.system()),'machine':norm_machine(platform.machine())}
    data=json.loads(LOCK.read_text(encoding='utf-8'))
    for e in data['tools']:
        if e['id']==tool and e['target']==host:
            return e
    raise RuntimeError(f'no {tool} lock for {host}')

def run(argv,cwd=None):
    return subprocess.run(argv,cwd=cwd or ROOT,check=False).returncode

def classify(tool: str, code: int) -> int:
    """Adapter contract: 0 clean, 1 finding/policy failure, 125 operational nonexecution."""
    if code == 0:
        return 0
    if tool == 'gitleaks':
        # Production invocation sets --exit-code 10, separating findings from
        # Gitleaks' otherwise ambiguous default exit 1 (finding OR error).
        return 1 if code == 10 else OPERATIONAL_EXIT
    if tool == 'semgrep':
        # Semgrep --error uses 1 for findings; other nonzero outcomes are tool/config/runtime errors.
        return 1 if code == 1 else OPERATIONAL_EXIT
    if tool == 'shellcheck':
        # ShellCheck: 1 means issues found; 2+ are invocation/processing failures.
        return 1 if code == 1 else OPERATIONAL_EXIT
    if tool == 'zizmor':
        # Zizmor 11..14 are finding severities; 1..3 are audit/argument/input errors.
        return 1 if code in {11,12,13,14} else OPERATIONAL_EXIT
    if tool == 'psscriptanalyzer':
        # The PowerShell command below explicitly reserves 125 for import/runtime failures.
        return 1 if code == 1 else OPERATIONAL_EXIT
    return OPERATIONAL_EXIT

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('tool',choices=['gitleaks','semgrep','shellcheck','psscriptanalyzer','zizmor'])
    ap.add_argument('paths',nargs='*')
    args=ap.parse_args()
    e=entry(args.tool)

    if args.tool in {'gitleaks','shellcheck','zizmor'}:
        exe=TOOL_ROOT/'bin'/e['executable']
        if not exe.exists():
            print(f'{args.tool} not bootstrapped',file=sys.stderr)
            return OPERATIONAL_EXIT
        if args.tool=='gitleaks':
            code=run([str(exe),'git','--redact','--no-banner','--exit-code','10','--config',str(ROOT/'.gitleaks.toml')])
            return classify('gitleaks',code)
        if args.tool=='shellcheck':
            paths=args.paths or [str(p) for p in sorted(list((ROOT/'codex-home').glob('*.sh'))+list((ROOT/'scripts').glob('*.sh')))]
            code=run([str(exe),'--severity=warning',*paths]) if paths else 0
            return classify('shellcheck',code)
        paths=args.paths or [str(ROOT/'.github/workflows/framework-verify.yml')]
        code=run([str(exe),'--persona=auditor','--min-severity=medium',*paths])
        return classify('zizmor',code)

    if args.tool=='semgrep':
        docker=shutil.which('docker')
        if not docker:
            print('docker unavailable for Semgrep',file=sys.stderr)
            return OPERATIONAL_EXIT
        image=f"{e['image'].split(':',1)[0]}@{e['digest']}"
        targets=args.paths or ['/src/assurance','/src/scripts']
        normalized=[p if p.startswith('/src') else '/src/'+Path(p).as_posix().lstrip('./') for p in targets]
        code=run([docker,'run','--rm','-v',f'{ROOT}:/src:ro','--workdir','/src',image,'semgrep','scan','--config','/src/semgrep/framework.yml','--metrics=off','--error',*normalized])
        return classify('semgrep',code)

    pwsh=shutil.which('pwsh') or shutil.which('powershell') or shutil.which('powershell.exe')
    if not pwsh:
        print('PowerShell unavailable',file=sys.stderr)
        return OPERATIONAL_EXIT
    manifest=TOOL_ROOT/'modules'/'PSScriptAnalyzer'/e['version']/e['module_manifest']
    if not manifest.exists():
        print('PSScriptAnalyzer not bootstrapped',file=sys.stderr)
        return OPERATIONAL_EXIT
    paths=args.paths or [str(ROOT/'codex-home'),str(ROOT/'scripts')]
    quoted=','.join("'"+str(Path(x)).replace("'","''")+"'" for x in paths)
    escaped_manifest=str(manifest).replace("'","''")
    command=("$ErrorActionPreference='Stop'; try { "
             f"Import-Module '{escaped_manifest}' -Force; "
             f"$r=@({quoted}) | ForEach-Object {{ Invoke-ScriptAnalyzer -Path $_ -Recurse -ExcludeRule 'PSAvoidUsingWriteHost' }}; "
             "$r | Format-Table -AutoSize; if ($r.Count -gt 0) { exit 1 } else { exit 0 } "
             "} catch { Write-Error $_; exit 125 }")
    return classify('psscriptanalyzer',run([pwsh,'-NoProfile','-NonInteractive','-Command',command]))

if __name__=='__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f'framework scanner error: {type(exc).__name__}: {exc}',file=sys.stderr)
        raise SystemExit(OPERATIONAL_EXIT)
