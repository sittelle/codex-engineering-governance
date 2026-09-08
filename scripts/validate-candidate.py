#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CandidateValidationError(RuntimeError):
    pass


def run_command(label: str, argv: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    print(f'\n===== {label} =====')
    proc = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False)
    if proc.stdout:
        print(proc.stdout, end='' if proc.stdout.endswith('\n') else '\n')
    if proc.stderr:
        print(proc.stderr, end='' if proc.stderr.endswith('\n') else '\n', file=sys.stderr)
    if proc.returncode != 0:
        raise CandidateValidationError(f'{label} failed with exit code {proc.returncode}')
    return proc


def local_full_is_acceptable(report: dict) -> tuple[bool, str]:
    overall = report.get('overall')
    required = set(report.get('required_check_ids') or [])
    results = {row.get('id'): row for row in report.get('results') or []}

    missing_rows = sorted(required - set(results))
    if missing_rows:
        return False, 'required checks missing from report: ' + ', '.join(missing_rows)

    failing = sorted(cid for cid in required if results[cid].get('result') == 'FAIL')
    if failing:
        return False, 'required checks FAIL: ' + ', '.join(failing)

    unexpected = []
    for cid in sorted(required):
        row = results[cid]
        result = row.get('result')
        if result == 'PASS':
            continue
        if result != 'DID_NOT_EXECUTE':
            unexpected.append(f'{cid}={result}')
            continue
        if row.get('execution_disposition') != 'DEFERRED_TO_APPROVED_ENVIRONMENT':
            unexpected.append(f"{cid}=DID_NOT_EXECUTE/{row.get('execution_disposition')}")
            continue
        allowed = row.get('allowed_contexts') or []
        if 'CI' not in allowed:
            unexpected.append(f'{cid}=deferred without CI approved context')
    if unexpected:
        return False, 'unexpected required-check disposition(s): ' + ', '.join(unexpected)

    if overall == 'PASS':
        return True, 'PASS'
    if overall == 'INCOMPLETE_ASSURANCE':
        deferred = [cid for cid in sorted(required) if results[cid].get('result') == 'DID_NOT_EXECUTE']
        if not deferred:
            return False, 'overall is INCOMPLETE_ASSURANCE without any required approved-context deferral'
        return True, 'INCOMPLETE_ASSURANCE with only approved CI deferrals'
    return False, f'unexpected overall result: {overall}'


def self_test() -> int:
    base = {
        'required_check_ids': ['local', 'ci'],
        'results': [
            {'id': 'local', 'result': 'PASS', 'execution_disposition': 'COMPLETED', 'allowed_contexts': ['LOCAL', 'CI']},
            {'id': 'ci', 'result': 'DID_NOT_EXECUTE', 'execution_disposition': 'DEFERRED_TO_APPROVED_ENVIRONMENT', 'allowed_contexts': ['CI']},
        ],
        'overall': 'INCOMPLETE_ASSURANCE',
    }
    ok, _ = local_full_is_acceptable(base)
    if not ok:
        print('Candidate validation self-test: FAIL - approved CI deferral was rejected')
        return 1

    bad_fail = json.loads(json.dumps(base))
    bad_fail['results'][1]['result'] = 'FAIL'
    bad_fail['overall'] = 'FAIL'
    if local_full_is_acceptable(bad_fail)[0]:
        print('Candidate validation self-test: FAIL - real FAIL was accepted')
        return 1

    bad_operational = json.loads(json.dumps(base))
    bad_operational['results'][1]['execution_disposition'] = 'OPERATIONAL_FAILURE'
    if local_full_is_acceptable(bad_operational)[0]:
        print('Candidate validation self-test: FAIL - operational nonexecution was accepted as approved deferral')
        return 1

    all_pass = {
        'required_check_ids': ['a'],
        'results': [{'id': 'a', 'result': 'PASS', 'execution_disposition': 'COMPLETED', 'allowed_contexts': ['LOCAL']}],
        'overall': 'PASS',
    }
    if not local_full_is_acceptable(all_pass)[0]:
        print('Candidate validation self-test: FAIL - valid PASS report was rejected')
        return 1

    print('Candidate validation self-test: PASS')
    print('- PASS accepted')
    print('- approved CI-only deferral accepted as local INCOMPLETE_ASSURANCE')
    print('- real FAIL rejected')
    print('- operational DID_NOT_EXECUTE rejected')
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description='Run the framework candidate local validation bundle.')
    ap.add_argument('--repo', type=Path, default=ROOT, help='Framework repository to validate.')
    ap.add_argument('--self-test', action='store_true', help='Run only the candidate-report classification regression.')
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    repo = args.repo.resolve()
    python = sys.executable
    host_mode = 'windows' if os.name == 'nt' else 'posix'

    checks = [
        ('Governance validator', [python, str(repo / 'scripts/validate-governance.py')]),
        ('Manifest inventory', [python, str(repo / 'scripts/test-manifest-inventory.py')]),
        ('Lifecycle common', [python, str(repo / 'scripts/test-framework-lifecycle.py'), '--mode', 'common']),
        (f'Lifecycle {host_mode}', [python, str(repo / 'scripts/test-framework-lifecycle.py'), '--mode', host_mode]),
        ('Assurance integration', [python, str(repo / 'scripts/test-assurance-integration.py')]),
        ('Canonical quick', [python, str(repo / 'scripts/verify-framework.py'), 'quick', '--execution-context', 'LOCAL']),
    ]

    try:
        for label, argv in checks:
            run_command(label, argv, cwd=repo)

        print('\n===== Canonical local full =====')
        with tempfile.TemporaryDirectory(prefix='gov-candidate-full-') as td:
            report_path = Path(td) / 'framework-full.json'
            proc = subprocess.run(
                [python, str(repo / 'scripts/verify-framework.py'), 'full', '--execution-context', 'LOCAL', '--report', str(report_path)],
                cwd=repo,
                text=True,
                capture_output=True,
                check=False,
            )
            if proc.stdout:
                print(proc.stdout, end='' if proc.stdout.endswith('\n') else '\n')
            if proc.stderr:
                print(proc.stderr, end='' if proc.stderr.endswith('\n') else '\n', file=sys.stderr)
            if not report_path.is_file():
                raise CandidateValidationError('canonical local full did not emit its JSON report')
            report = json.loads(report_path.read_text(encoding='utf-8'))
            acceptable, detail = local_full_is_acceptable(report)
            if not acceptable:
                raise CandidateValidationError('canonical local full is not an acceptable local assurance slice: ' + detail)
            expected_exit = 0 if report.get('overall') == 'PASS' else 2
            if proc.returncode != expected_exit:
                raise CandidateValidationError(
                    f"canonical local full exit code {proc.returncode} does not match report overall {report.get('overall')}"
                )

        print('\n===== Git whitespace integrity =====')
        git = shutil.which('git')
        if not git:
            raise CandidateValidationError('git executable not found')
        diff = subprocess.run([git, 'diff', '--check'], cwd=repo, text=True, capture_output=True, check=False)
        if diff.stdout:
            print(diff.stdout, end='' if diff.stdout.endswith('\n') else '\n')
        if diff.stderr:
            # Git may emit harmless platform line-ending warnings on stderr while returning zero.
            print(diff.stderr, end='' if diff.stderr.endswith('\n') else '\n', file=sys.stderr)
        if diff.returncode != 0:
            raise CandidateValidationError(f'git diff --check failed with exit code {diff.returncode}')

    except CandidateValidationError as exc:
        print('\n========================================')
        print('Candidate local validation: FAIL')
        print(f'- {exc}')
        return 1

    print('\n========================================')
    print('Candidate local validation: PASS')
    print('- governance validator: PASS')
    print('- manifest inventory: PASS')
    print('- lifecycle common: PASS')
    print(f'- lifecycle {host_mode}: PASS')
    print('- assurance integration: PASS')
    print('- canonical quick: PASS')
    print(f'- canonical local full: {detail}')
    print('- git diff --check: clean')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
