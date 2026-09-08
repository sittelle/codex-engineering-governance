#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

def main()->int:
    ap=argparse.ArgumentParser(description="Run project CI bootstrap and canonical governed full verification.")
    ap.add_argument('--project-root',default='.')
    ap.add_argument('--plan',default='verification-plan.json')
    ap.add_argument('--baseline',default='.governance/assurance-baseline.json')
    ap.add_argument('--report',default='.governance/evidence/ci-full.json')
    args=ap.parse_args()
    project=Path(args.project_root).resolve()
    runner=project/'.governance/run-verification.py'
    if not runner.exists():
        print('managed verification runner is missing',file=sys.stderr); return 3
    bootstrap=project/'.governance/ci-bootstrap.py'
    failure=None
    if bootstrap.exists():
        print('[ci-bootstrap] running project assurance environment bootstrap')
        try:
            proc=subprocess.run([sys.executable,str(bootstrap)],cwd=str(project),check=False)
            if proc.returncode!=0:
                failure=f'CI bootstrap exited {proc.returncode}'
                print(f'[ci-bootstrap] DID_NOT_EXECUTE ({failure})')
        except Exception as exc:
            failure=f'CI bootstrap could not execute: {type(exc).__name__}: {exc}'
            print(f'[ci-bootstrap] DID_NOT_EXECUTE ({failure})')
    cmd=[sys.executable,str(runner),'full','--project-root',str(project),'--plan',args.plan,'--baseline',args.baseline,'--execution-context','CI','--report',args.report]
    if failure:
        cmd += ['--precondition-failure',failure]
    return subprocess.run(cmd,cwd=str(project),check=False).returncode

if __name__=='__main__':
    raise SystemExit(main())
