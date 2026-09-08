#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUNNER=ROOT/'assurance/run-verification.py'
PLAN=ROOT/'framework-verification-plan.json'
BASELINE=ROOT/'assurance/capability-baseline.json'

def main():
    ap=argparse.ArgumentParser(description='Canonical thin frontend for Governance Framework verification')
    ap.add_argument('stage',choices=['quick','full'])
    ap.add_argument('--execution-context',choices=['LOCAL','CI','SPECIALIZED'])
    ap.add_argument('--report')
    ap.add_argument('--precondition-failure')
    args=ap.parse_args()
    report=args.report or str(ROOT/'release-evidence/verification'/f'framework-{args.stage}.json')
    cmd=[sys.executable,str(RUNNER),args.stage,'--project-root',str(ROOT),'--plan',str(PLAN),'--baseline',str(BASELINE),'--report',report]
    if args.execution_context: cmd+=['--execution-context',args.execution_context]
    if args.precondition_failure: cmd+=['--precondition-failure',args.precondition_failure[:500]]
    return subprocess.run(cmd).returncode
if __name__=='__main__': raise SystemExit(main())
