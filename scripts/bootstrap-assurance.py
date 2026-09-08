#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, shutil, sys
from pathlib import Path

WORKFLOW_MARKER="# CODEX-GOVERNANCE-MANAGED-WORKFLOW v1"
RUNNER_MARKER="# CODEX-GOVERNANCE-MANAGED-RUNNER v1"
AGGREGATOR_MARKER="# CODEX-GOVERNANCE-MANAGED-AGGREGATOR v1"
CI_RUNNER_MARKER="# CODEX-GOVERNANCE-MANAGED-CI-RUNNER v1"
BASELINE_MARKER="managed assurance baseline"
GI_BEGIN="# BEGIN CODEX-GOVERNANCE-ASSURANCE"
GI_END="# END CODEX-GOVERNANCE-ASSURANCE"

def fail(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr); raise SystemExit(code)
def sha(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def baseline_version(path: Path) -> str:
    m=re.search(r'(?m)^\s*baseline:\s*["\']?([^"\']+)["\']?\s*$',path.read_text(encoding="utf-8"))
    if not m: fail("project-governance.yml has no governance baseline")
    return m.group(1)
def plan_state(path: Path) -> tuple[str,bool]:
    try: data=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: fail(f"verification plan invalid JSON: {exc}")
    version=str(data.get("schema_version"))
    if version!="2": return version,False
    checks=data.get("checks")
    if not isinstance(checks,list) or not checks: return version,False
    if any((not isinstance(c.get("command"),list) or not c["command"] or c["command"][0]=="__NOT_CONFIGURED__") for c in checks): return version,False
    return version,True
def managed_runner(source: Path, version: str) -> bytes:
    lines=source.read_text(encoding="utf-8").splitlines()
    marker=f"{RUNNER_MARKER} source-governance={version}"
    if lines and lines[0].startswith("#!"): lines.insert(1,marker)
    else: lines.insert(0,marker)
    return ("\n".join(lines).rstrip()+"\n").encode()
def managed_aggregator(source: Path, version: str) -> bytes:
    lines=source.read_text(encoding="utf-8").splitlines()
    marker=f"{AGGREGATOR_MARKER} source-governance={version}"
    if lines and lines[0].startswith("#!"): lines.insert(1,marker)
    else: lines.insert(0,marker)
    return ("\n".join(lines).rstrip()+"\n").encode()

def managed_ci_runner(source: Path, version: str) -> bytes:
    lines=source.read_text(encoding="utf-8").splitlines()
    marker=f"{CI_RUNNER_MARKER} source-governance={version}"
    if lines and lines[0].startswith("#!"): lines.insert(1,marker)
    else: lines.insert(0,marker)
    return ("\n".join(lines).rstrip()+"\n").encode()

def gitignore_text(existing: str) -> str:
    block=f"{GI_BEGIN}\n.governance/evidence/\n{GI_END}"
    if GI_BEGIN in existing:
        return re.sub(re.escape(GI_BEGIN)+r".*?"+re.escape(GI_END),block,existing,flags=re.S).rstrip()+"\n"
    return existing.rstrip()+("\n\n" if existing.strip() else "")+block+"\n"
def add_manifest_metadata(text: str) -> str:
    if not re.search(r'(?m)^verification:\s*$',text): fail("project manifest has no verification block")
    wanted=[('plan','"verification-plan.json"'),('plan_schema','"2"'),('assurance_baseline','".governance/assurance-baseline.json"'),('evidence_directory','".governance/evidence"'),('local_ci_parity_required','true')]
    additions=[]
    for key,value in wanted:
        if not re.search(rf'(?m)^\s+{re.escape(key)}:\s*',text): additions.append(f"  {key}: {value}")
    if not additions: return text
    lines=text.splitlines(); start=next(i for i,l in enumerate(lines) if l.strip()=="verification:"); end=start+1
    while end<len(lines) and (not lines[end] or lines[end].startswith((" ","\t"))): end+=1
    lines[end:end]=additions; return "\n".join(lines).rstrip()+"\n"
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project-root'); ap.add_argument('--apply',action='store_true'); ap.add_argument('--skip-ci',action='store_true'); ap.add_argument('--allow-unconfigured-ci',action='store_true'); args=ap.parse_args()
    root=Path(__file__).resolve().parents[1]; version=(root/'VERSION').read_text().strip()
    project=Path(args.project_root or input('Project root: ').strip()).expanduser().resolve()
    if not project.is_dir(): fail(f"project root does not exist: {project}")
    manifest=project/'project-governance.yml'
    if not manifest.exists(): fail('project-governance.yml required; adopt project first')
    pv=baseline_version(manifest)
    if pv!=version: fail(f"project baseline {pv} != central governance {version}; update project first")
    plan=project/'verification-plan.json'; central_plan=root/'templates/repository/verification-plan.json'; create_plan=not plan.exists(); effective=plan if plan.exists() else central_plan
    plan_version,configured=plan_state(effective)
    if plan_version!='2': configured=False
    runner_target=project/'.governance/run-verification.py'; runner_bytes=managed_runner(root/'assurance/run-verification.py',version)
    if runner_target.exists() and RUNNER_MARKER not in runner_target.read_text(encoding='utf-8',errors='replace'):
        print('NOTE: preserving project-owned .governance/run-verification.py'); runner_bytes=None
    baseline_target=project/'.governance/assurance-baseline.json'; baseline_source=root/'assurance/capability-baseline.json'
    aggregator_target=project/'.governance/aggregate-verification.py'; aggregator_bytes=managed_aggregator(root/'assurance/aggregate-verification.py',version)
    ci_runner_target=project/'.governance/run-ci-verification.py'; ci_runner_bytes=managed_ci_runner(root/'assurance/run-ci-verification.py',version)
    if aggregator_target.exists() and AGGREGATOR_MARKER not in aggregator_target.read_text(encoding='utf-8',errors='replace'):
        print('NOTE: preserving project-owned .governance/aggregate-verification.py'); aggregator_bytes=None
    if ci_runner_target.exists() and CI_RUNNER_MARKER not in ci_runner_target.read_text(encoding='utf-8',errors='replace'):
        print('NOTE: preserving project-owned .governance/run-ci-verification.py'); ci_runner_bytes=None
    workflow_target=project/'.github/workflows/governance-verify.yml'; install_ci=(not args.skip_ci) and (configured or args.allow_unconfigured_ci)
    if workflow_target.exists() and install_ci and WORKFLOW_MARKER not in workflow_target.read_text(encoding='utf-8',errors='replace'):
        fail('existing governance-verify.yml is not governance-managed; refusing overwrite')
    print('Governed assurance bootstrap preview'); print(f'Project: {project}'); print(f'Governance baseline: {version}'); print(f'Plan schema: {plan_version}'); print(f'Plan configured: {configured}'); print(f'Install CI workflow: {install_ci}')
    if plan_version!='2': print('CI deferred: schema-v1 verification plan requires reconciliation to v2.')
    elif not install_ci and not args.skip_ci and not configured: print('CI deferred: verification plan is still unconfigured.')
    if not args.apply: print('DRY RUN ONLY. Re-run with --apply.'); return 0
    (project/'.governance').mkdir(parents=True,exist_ok=True)
    if create_plan: shutil.copy2(central_plan,plan)
    manifest.write_text(add_manifest_metadata(manifest.read_text(encoding='utf-8')),encoding='utf-8')
    gi=project/'.gitignore'; gi.write_text(gitignore_text(gi.read_text(encoding='utf-8') if gi.exists() else ''),encoding='utf-8')
    if runner_bytes is not None: runner_target.write_bytes(runner_bytes)
    if aggregator_bytes is not None: aggregator_target.write_bytes(aggregator_bytes)
    if ci_runner_bytes is not None: ci_runner_target.write_bytes(ci_runner_bytes)
    shutil.copy2(baseline_source,baseline_target)
    if install_ci:
        workflow_target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(root/'templates/github/governance-verify.yml',workflow_target)
    record={'schema_version':'2','governance_baseline':version,'verification_plan':'verification-plan.json','verification_plan_schema':plan_version,'runner':'.governance/run-verification.py' if runner_target.exists() else None,'runner_sha256':sha(runner_target.read_bytes()) if runner_target.exists() else None,'aggregator':'.governance/aggregate-verification.py' if aggregator_target.exists() else None,'aggregator_sha256':sha(aggregator_target.read_bytes()) if aggregator_target.exists() else None,'ci_runner':'.governance/run-ci-verification.py' if ci_runner_target.exists() else None,'ci_runner_sha256':sha(ci_runner_target.read_bytes()) if ci_runner_target.exists() else None,'assurance_baseline':'.governance/assurance-baseline.json','assurance_baseline_sha256':sha(baseline_target.read_bytes()),'ci_workflow':'.github/workflows/governance-verify.yml' if workflow_target.exists() else None,'ci_workflow_sha256':sha(workflow_target.read_bytes()) if workflow_target.exists() else None,'ci_installed':workflow_target.exists(),'plan_configured_at_bootstrap':configured}
    (project/'.governance/assurance-bootstrap.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print('Assurance bootstrap applied.')
    if plan_version!='2': print('Full assurance remains INCOMPLETE until verification-plan.json is reconciled to schema v2.')
    elif not configured: print('Verification remains UNVERIFIED until the plan is configured and executed.')
    return 0
if __name__=='__main__': raise SystemExit(main())
