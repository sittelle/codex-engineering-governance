#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, io, json, os, platform, shutil, stat, subprocess, sys, tarfile, urllib.request, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LOCK=ROOT/'tools/framework-tools.lock.json'
TOOL_ROOT=ROOT/'.framework-tools'

def norm_os(v):
    v=(v or '').strip().lower()
    if v.startswith('win'): return 'Windows'
    if v=='linux': return 'Linux'
    if v in {'darwin','macos','mac'}: return 'Darwin'
    return platform.system() if not v else v

def norm_machine(v):
    v=(v or '').strip().lower()
    if v in {'amd64','x86_64','x64'}: return 'x86_64'
    if v in {'arm64','aarch64'}: return 'arm64'
    return v

def sha256(data): return hashlib.sha256(data).hexdigest()

def download(url):
    req=urllib.request.Request(url,headers={'User-Agent':'codex-engineering-governance-tool-bootstrap/1.0.0'})
    with urllib.request.urlopen(req,timeout=90) as r: return r.read()

def target_tools(lock):
    host={'os':norm_os(platform.system()),'machine':norm_machine(platform.machine())}
    return host,[x for x in lock['tools'] if x['target']==host]

def safe_extract_member(tf, member, dest):
    obj=tf.getmember(member)
    if not obj.isfile(): raise RuntimeError(f'archive member is not a regular file: {member}')
    src=tf.extractfile(obj)
    if src is None: raise RuntimeError(f'cannot read archive member: {member}')
    dest.write_bytes(src.read())
    dest.chmod(dest.stat().st_mode|stat.S_IXUSR|stat.S_IXGRP|stat.S_IXOTH)

def install_archive(entry, bin_dir):
    data=download(entry['url'])
    got=sha256(data)
    if got.lower()!=entry['sha256'].lower(): raise RuntimeError(f"{entry['id']} SHA-256 mismatch: {got}")
    mode='r:gz' if entry['archive']=='tar.gz' else 'r:xz'
    with tarfile.open(fileobj=io.BytesIO(data),mode=mode) as tf:
        safe_extract_member(tf,entry['member'],bin_dir/entry['executable'])

def install_ps_module(entry, modules_dir):
    data=download(entry['url']); got=sha256(data)
    if got.lower()!=entry['sha256'].lower(): raise RuntimeError(f"{entry['id']} SHA-256 mismatch: {got}")
    target=modules_dir/entry['module']/entry['version']
    if target.exists(): shutil.rmtree(target)
    target.mkdir(parents=True)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for info in zf.infolist():
            name=info.filename.replace('\\','/')
            if name.startswith('/') or '..' in Path(name).parts: raise RuntimeError('unsafe path in PowerShell module package')
            if name.endswith('/'): continue
            out=target/Path(name)
            out.parent.mkdir(parents=True,exist_ok=True)
            out.write_bytes(zf.read(info))
    if not (target/entry['module_manifest']).exists(): raise RuntimeError('PowerShell module manifest missing after extraction')

def verify_output_version(entry, argv):
    p=subprocess.run(argv,text=True,capture_output=True,check=False)
    output=(p.stdout or '')+'\n'+(p.stderr or '')
    if p.returncode != 0:
        raise RuntimeError(f"{entry['id']} version probe failed with exit {p.returncode}")
    if entry['version'] not in output:
        raise RuntimeError(f"{entry['id']} version probe did not report locked version {entry['version']}")

def install_docker(entry):
    docker=shutil.which('docker')
    if not docker: raise RuntimeError('docker executable is unavailable for pinned Semgrep image')
    image=f"{entry['image'].split(':',1)[0]}@{entry['digest']}"
    p=subprocess.run([docker,'pull',image],text=True)
    if p.returncode: raise RuntimeError(f"docker pull failed for {image}")
    verify_output_version(entry,[docker,'run','--rm',image,'semgrep','--version'])

def verify_ps_module(entry, modules_dir):
    pwsh=shutil.which('pwsh') or shutil.which('powershell') or shutil.which('powershell.exe')
    if not pwsh: raise RuntimeError('PowerShell executable unavailable for PSScriptAnalyzer version verification')
    manifest=modules_dir/entry['module']/entry['version']/entry['module_manifest']
    escaped=str(manifest).replace("'","''")
    command=("$ErrorActionPreference='Stop'; Import-Module '"+escaped+"' -Force; "
             "(Get-Module PSScriptAnalyzer).Version.ToString()")
    verify_output_version(entry,[pwsh,'-NoProfile','-NonInteractive','-Command',command])

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--apply',action='store_true'); ap.add_argument('--list',action='store_true'); args=ap.parse_args()
    lock=json.loads(LOCK.read_text(encoding='utf-8'))
    if lock.get('schema_version')!='1': raise SystemExit('unsupported framework tool lock schema')
    host,tools=target_tools(lock)
    print(f"Framework tool target: {host['os']}/{host['machine']}")
    if not tools: raise SystemExit('no locked framework tools for this target')
    for e in tools: print(f"- {e['id']} {e['version']} ({e['kind']})")
    if args.list or not args.apply:
        if not args.list: print('DRY RUN ONLY. Re-run with --apply.')
        return 0
    bin_dir=TOOL_ROOT/'bin'; modules_dir=TOOL_ROOT/'modules'; bin_dir.mkdir(parents=True,exist_ok=True); modules_dir.mkdir(parents=True,exist_ok=True)
    installed=[]
    for e in tools:
        print(f"Installing {e['id']} {e['version']}...")
        if e['kind']=='archive':
            install_archive(e,bin_dir)
            verify_output_version(e,[str(bin_dir/e['executable']),*e.get('version_args',[])])
        elif e['kind']=='powershell-module':
            install_ps_module(e,modules_dir)
            verify_ps_module(e,modules_dir)
        elif e['kind']=='docker': install_docker(e)
        else: raise RuntimeError(f"unsupported tool kind: {e['kind']}")
        installed.append({'id':e['id'],'version':e['version'],'target':e['target'],'kind':e['kind'],'integrity':e.get('sha256') or e.get('digest')})
    state={'schema_version':'1','host':host,'lock_sha256':sha256(LOCK.read_bytes()),'installed':installed}
    TOOL_ROOT.mkdir(parents=True,exist_ok=True)
    (TOOL_ROOT/'state.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
    print('Framework tool bootstrap: PASS')
    return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except Exception as exc:
        print(f'Framework tool bootstrap: FAIL: {type(exc).__name__}: {exc}',file=sys.stderr); raise SystemExit(1)
