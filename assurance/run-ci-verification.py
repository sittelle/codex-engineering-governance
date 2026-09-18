#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, subprocess, sys
from pathlib import Path


def version_tuple(value: str) -> tuple[int, ...] | None:
    parts = value.strip().split(".")
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return None


def below_minimum(current: str, minimum: str) -> bool:
    c, m = version_tuple(current), version_tuple(minimum)
    if c is None or m is None:
        return False
    return c < m


def check_minimum_version(project: Path) -> str | None:
    """Return a precondition-failure message if GOVERNANCE_MIN_VERSION is set
    and the project's bootstrapped baseline is below it, else None. A
    project that has never run bootstrap-assurance.py has no
    assurance-bootstrap.json to compare and is not evaluated here; its
    absence is already surfaced by other required-control evidence.
    """
    minimum = os.environ.get("GOVERNANCE_MIN_VERSION")
    if not minimum:
        return None
    record_path = project / ".governance/assurance-bootstrap.json"
    if not record_path.is_file():
        return None
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    current = record.get("governance_baseline")
    if not isinstance(current, str):
        return None
    if below_minimum(current, minimum):
        return f"governance baseline {current} is below required minimum {minimum}"
    return None


def annotate_ci_enforcement(report_path: Path) -> None:
    """Record the enforcement mode observed in the CI environment and its
    source (MANAGED if GOVERNANCE_ENFORCEMENT is set, ABSENT otherwise),
    per the fail-closed rule that a missing enforcement variable means
    inform and is visible as ABSENT rather than silently assumed.
    """
    if not report_path.is_file():
        return
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        return
    mode = os.environ.get("GOVERNANCE_ENFORCEMENT")
    report["ci_enforcement"] = {
        "source": "MANAGED" if mode else "ABSENT",
        "mode": mode or "inform",
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


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
    failure=check_minimum_version(project)
    if failure:
        print(f'[governance-min-version] INCOMPLETE_ASSURANCE ({failure})')
    elif bootstrap.exists():
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
    result=subprocess.run(cmd,cwd=str(project),check=False).returncode
    report_path=args.report if Path(args.report).is_absolute() else project/args.report
    annotate_ci_enforcement(Path(report_path))
    return result

if __name__=='__main__':
    raise SystemExit(main())
