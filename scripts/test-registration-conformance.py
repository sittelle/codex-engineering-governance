#!/usr/bin/env python3
"""Regression coverage for WS4 phase 3 capability detection and drift
reporting (docs/business-led/implementation-plan.md).

There is no live IT Security review of real repositories in this
environment; per the maintainer's explicit direction, this test suite is
the heuristic stand-in: synthetic fixtures under tests/capabilities/
exercising every capability rule's recall (a deliberate positive trigger
per capability) and precision (a capability-free negative fixture that
must produce zero findings), plus end-to-end coverage of
scripts/run-registration-conformance.py's drift detection, request-record
creation, and DID_NOT_EXECUTE paths. Requires `semgrep` on PATH; if it is
not available, this entire test is DID_NOT_EXECUTE, not a pass.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_PY = ROOT / "governance.py"
CONFORMANCE = ROOT / "scripts" / "run-registration-conformance.py"
FIXTURES = ROOT / "tests" / "capabilities"

EXPECTED_CAPABILITIES = {
    "network_connections",
    "persistence",
    "authentication",
    "elevated_access",
    "write_or_delete_actions",
    "cloud",
    "external_recipients",
}

DID_NOT_EXECUTE = 3


def run(argv, cwd=None, stdin_text=None):
    return subprocess.run(
        argv,
        cwd=cwd,
        input=stdin_text,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def semgrep_findings(ruleset: Path, target: Path) -> list[dict]:
    semgrep = shutil.which("semgrep")
    proc = subprocess.run(
        [semgrep, "scan", "--config", str(ruleset), "--metrics=off", "--json", str(target)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return json.loads(proc.stdout).get("results", [])


def capability_ids(findings: list[dict]) -> set[str]:
    return {f.get("extra", {}).get("metadata", {}).get("capability") for f in findings} - {None}


def make_sealed_registration(directory: Path, *, approved: set[str] | None = None) -> Path:
    reg_path = directory / "registration.yml"
    text = (ROOT / "templates/repository/registration.yml").read_text(encoding="utf-8")
    text = text.replace('registration_id: "<assigned by IT Security>"', 'registration_id: "REG-TEST"')
    text = text.replace(
        'purpose: "<what this project is for and who uses it>"', 'purpose: "Conformance regression fixture."'
    )
    text = text.replace('business_owner: "<name>"', 'business_owner: "Test Owner"')
    text = text.replace('approval_authority: "<IT Security contact>"', 'approval_authority: "Test IT Security"')
    for cap in approved or set():
        text = text.replace(f"{cap}: false", f"{cap}: true")
    reg_path.write_text(text, encoding="utf-8", newline="\n")
    proc = run([sys.executable, str(GOVERNANCE_PY), "registration", "seal", "--registration", str(reg_path), "--by", "test"])
    if proc.returncode != 0:
        raise RuntimeError(f"registration seal failed: {proc.stdout}\n{proc.stderr}")
    return reg_path


def make_business_led_project(parent: Path, name: str, registration: Path) -> Path:
    proc = run(
        [
            sys.executable,
            str(GOVERNANCE_PY),
            "project",
            "new",
            "--parent",
            str(parent),
            "--name",
            name,
            "--no-git-init",
            "--mode",
            "business-led",
            "--registration",
            str(registration),
            "-y",
        ]
    )
    if proc.returncode != 0:
        raise RuntimeError(f"project new failed: {proc.stdout}\n{proc.stderr}")
    return parent / name


def run_conformance(project: Path) -> dict:
    proc = run([sys.executable, str(CONFORMANCE), "--project-root", str(project)])
    json_text = proc.stdout.split("\nOVERALL:")[0]
    return json.loads(json_text), proc.returncode


def assert_true(condition, message, failures):
    if not condition:
        failures.append(message)


def test_python_rules_recall_and_precision(failures: list[str]) -> None:
    ruleset = ROOT / "semgrep" / "capabilities" / "python.yml"
    positive = capability_ids(semgrep_findings(ruleset, FIXTURES / "python" / "positive.py"))
    assert_true(
        positive == EXPECTED_CAPABILITIES,
        f"Python capability rules recall mismatch: got {sorted(positive)}, expected {sorted(EXPECTED_CAPABILITIES)}",
        failures,
    )
    negative = semgrep_findings(ruleset, FIXTURES / "python" / "negative.py")
    assert_true(not negative, f"Python capability rules false-positived on the negative fixture: {negative}", failures)


def test_typescript_rules_recall_and_precision(failures: list[str]) -> None:
    ruleset = ROOT / "semgrep" / "capabilities" / "typescript.yml"
    positive = capability_ids(semgrep_findings(ruleset, FIXTURES / "typescript" / "positive.ts"))
    assert_true(
        positive == EXPECTED_CAPABILITIES,
        f"TypeScript capability rules recall mismatch: got {sorted(positive)}, expected {sorted(EXPECTED_CAPABILITIES)}",
        failures,
    )
    negative = semgrep_findings(ruleset, FIXTURES / "typescript" / "negative.ts")
    assert_true(not negative, f"TypeScript capability rules false-positived on the negative fixture: {negative}", failures)


def test_conformance_detects_drift_and_writes_request(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        registration = make_sealed_registration(td, approved={"network_connections"})
        project = make_business_led_project(td, "drift-demo", registration)
        (project / "src").mkdir(exist_ok=True)
        shutil.copy2(FIXTURES / "python" / "positive.py", project / "src" / "app.py")

        report, exit_code = run_conformance(project)
        assert_true(exit_code == 0, f"conformance script exited {exit_code}, expected 0 (never blocks)", failures)
        assert_true(
            report.get("status") == "REGISTRATION_RECONCILIATION_REQUIRED",
            f"expected REGISTRATION_RECONCILIATION_REQUIRED, got {report.get('status')}",
            failures,
        )
        expected_unregistered = EXPECTED_CAPABILITIES - {"network_connections"}
        assert_true(
            set(report.get("unregistered_capabilities", [])) == expected_unregistered,
            f"unregistered_capabilities mismatch: {report.get('unregistered_capabilities')}",
            failures,
        )
        assert_true(report.get("request_record"), "no request record was created for detected drift", failures)
        if report.get("request_record"):
            record_path = project / report["request_record"]
            assert_true(record_path.is_file(), f"reported request record does not exist: {record_path}", failures)
            record_text = record_path.read_text(encoding="utf-8")
            assert_true(
                "Routing outcome: update registration" in record_text,
                "request record does not declare the update registration routing outcome",
                failures,
            )


def test_conformance_clean_project_passes_no_request(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        registration = make_sealed_registration(td)
        project = make_business_led_project(td, "clean-demo", registration)
        (project / "src").mkdir(exist_ok=True)
        shutil.copy2(FIXTURES / "python" / "negative.py", project / "src" / "app.py")

        report, exit_code = run_conformance(project)
        assert_true(exit_code == 0, f"conformance script exited {exit_code}, expected 0", failures)
        assert_true(report.get("status") == "PASS", f"expected PASS on clean code, got {report.get('status')}", failures)
        assert_true(not report.get("unregistered_capabilities"), "clean project reported unregistered capabilities", failures)
        assert_true(report.get("request_record") is None, "clean project incorrectly created a request record", failures)


def test_missing_registration_is_did_not_execute(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        project = Path(td) / "no-registration"
        project.mkdir()
        proc = run([sys.executable, str(CONFORMANCE), "--project-root", str(project)])
        assert_true(
            proc.returncode == DID_NOT_EXECUTE,
            f"missing registration.yml should be DID_NOT_EXECUTE (exit {DID_NOT_EXECUTE}), got {proc.returncode}",
            failures,
        )
        report = json.loads(proc.stdout.split("\nOVERALL:")[0])
        assert_true(report.get("status") == "DID_NOT_EXECUTE", "missing registration did not report DID_NOT_EXECUTE status", failures)


def test_tampered_registration_seal_is_did_not_execute(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        registration = make_sealed_registration(td, approved={"network_connections"})
        project = make_business_led_project(td, "tampered-seal-demo", registration)
        reg_in_project = project / "registration.yml"
        text = reg_in_project.read_text(encoding="utf-8")
        text = text.replace('pathway: "green"', 'pathway: "red"')
        reg_in_project.write_text(text, encoding="utf-8", newline="\n")

        proc = run([sys.executable, str(CONFORMANCE), "--project-root", str(project)])
        assert_true(
            proc.returncode == DID_NOT_EXECUTE,
            f"tampered registration seal should be DID_NOT_EXECUTE, got {proc.returncode}",
            failures,
        )


def main() -> int:
    if not shutil.which("semgrep"):
        print("Registration conformance regression: DID_NOT_EXECUTE (semgrep not found on PATH)")
        return DID_NOT_EXECUTE

    failures: list[str] = []
    test_python_rules_recall_and_precision(failures)
    test_typescript_rules_recall_and_precision(failures)
    test_conformance_detects_drift_and_writes_request(failures)
    test_conformance_clean_project_passes_no_request(failures)
    test_missing_registration_is_did_not_execute(failures)
    test_tampered_registration_seal_is_did_not_execute(failures)

    if failures:
        print("Registration conformance regression: FAIL")
        for failure in failures:
            print("- " + failure)
        return 1

    print("Registration conformance regression: PASS")
    print("- Python capability rules: 7/7 recall on the positive fixture, 0 false positives on the negative fixture")
    print("- TypeScript capability rules: 7/7 recall on the positive fixture, 0 false positives on the negative fixture")
    print("- unregistered capabilities => REGISTRATION_RECONCILIATION_REQUIRED, exit 0 (never blocks), request record written")
    print("- fully registered/clean project => PASS, no request record")
    print("- missing registration.yml => DID_NOT_EXECUTE")
    print("- tampered registration seal => DID_NOT_EXECUTE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
