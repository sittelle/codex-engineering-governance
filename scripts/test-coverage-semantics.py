#!/usr/bin/env python3
"""Regression coverage for WS7 coverage-floor semantics
(docs/business-led/implementation-plan.md phase 4).

Exercises assurance/run-verification.py's coverage_diagnostic/coverage_summary
against real fixtures produced by governance.py: a check whose coverage
report is above its declared floor, below it, missing entirely, and a plan
with no coverage block at all. Schema v3 (report schema v5) only, per the
plan's explicit "schema v2 and v4 unchanged" boundary for this feature.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_PY = ROOT / "governance.py"
RUNNER = ROOT / "assurance/run-verification.py"
CENTRAL_BASELINE = ROOT / "assurance/capability-baseline.json"


def run(argv, cwd=None):
    return subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False)


def assert_true(condition, message, failures):
    if not condition:
        failures.append(message)


def make_project(parent: Path, name: str) -> Path:
    proc = run(
        [sys.executable, str(GOVERNANCE_PY), "project", "new", "--parent", str(parent), "--name", name, "--no-git-init", "-y"]
    )
    if proc.returncode != 0:
        raise RuntimeError(f"governance.py project new failed: {proc.stdout}\n{proc.stderr}")
    return parent / name


def to_schema_v3_with_coverage_check(project: Path, *, floor: float | None = 80) -> None:
    """Upgrade to schema v3 and replace the template's unconfigured placeholder
    with one real, always-passing check whose `tests` capability entry
    declares a coverage block, so the plan is well-formed to execute (not
    left permanently DID_NOT_EXECUTE from the template placeholder)."""
    plan_path = project / "verification-plan.json"
    data = json.loads(plan_path.read_text(encoding="utf-8-sig"))
    data["schema_version"] = "3"
    data["checks"] = [
        {
            "id": "unit-tests",
            "stages": ["quick", "full"],
            "command": [sys.executable, "-c", "print('tests ran')"],
            "reason": "fixture",
            "timeout_seconds": 30,
            "working_directory": None,
            "environment": {},
            "verified_targets": [],
            "result_policy": {"mode": "STANDARD"},
            "execution": {"allowed_contexts": ["LOCAL", "CI", "SPECIALIZED"], "required_contexts": ["ANY"]},
            "coverage": {"report_path": "coverage-summary.json", "metric": "line", "floor": floor, "reason": "fixture floor"},
        }
    ]
    for cap in data["assurance"]["capabilities"]:
        cap["checks"] = ["unit-tests"] if cap["id"] == "tests" else []
        if cap["id"] == "tests":
            cap["decision"] = "REQUIRED"
        elif cap["decision"] == "REQUIRED":
            # Keep the fixture minimal: only the tests capability is REQUIRED,
            # everything else stays out of required_check_ids for this fixture.
            cap["decision"] = "OPTIONAL"
    plan_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def to_schema_v3_no_coverage(project: Path) -> None:
    """Upgrade to schema v3 with a real check that declares no coverage block at all."""
    plan_path = project / "verification-plan.json"
    data = json.loads(plan_path.read_text(encoding="utf-8-sig"))
    data["schema_version"] = "3"
    data["checks"] = [
        {
            "id": "unit-tests",
            "stages": ["quick", "full"],
            "command": [sys.executable, "-c", "print('tests ran')"],
            "reason": "fixture",
            "timeout_seconds": 30,
            "working_directory": None,
            "environment": {},
            "verified_targets": [],
            "result_policy": {"mode": "STANDARD"},
            "execution": {"allowed_contexts": ["LOCAL", "CI", "SPECIALIZED"], "required_contexts": ["ANY"]},
        }
    ]
    for cap in data["assurance"]["capabilities"]:
        cap["checks"] = ["unit-tests"] if cap["id"] == "tests" else []
        if cap["id"] == "tests":
            cap["decision"] = "REQUIRED"
        elif cap["decision"] == "REQUIRED":
            cap["decision"] = "OPTIONAL"
    plan_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def quick_report(project: Path) -> dict:
    report_path = project / "report.json"
    run(
        [
            sys.executable,
            str(RUNNER),
            "quick",
            "--project-root",
            str(project),
            "--baseline",
            str(CENTRAL_BASELINE),
            "--report",
            str(report_path),
        ]
    )
    return json.loads(report_path.read_text(encoding="utf-8"))


def test_coverage_above_floor_passes(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        project = make_project(Path(td), "coverage-above")
        to_schema_v3_with_coverage_check(project, floor=80)
        (project / "coverage-summary.json").write_text(json.dumps({"line": 90}), encoding="utf-8")
        report = quick_report(project)
        coverage = report.get("coverage")
        assert_true(coverage is not None, "v3 report with a declared coverage check has no coverage block", failures)
        if coverage is not None:
            assert_true(coverage.get("status") == "PASS", f"coverage above floor did not report PASS: {coverage}", failures)
            assert_true(not coverage.get("issues"), f"coverage above floor incorrectly produced issues: {coverage.get('issues')}", failures)
            diag = coverage.get("diagnostics", [{}])[0]
            assert_true(diag.get("measured") == 90, f"measured coverage value not recorded correctly: {diag}", failures)


def test_coverage_below_floor_produces_issue(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        project = make_project(Path(td), "coverage-below")
        to_schema_v3_with_coverage_check(project, floor=80)
        (project / "coverage-summary.json").write_text(json.dumps({"line": 50}), encoding="utf-8")
        report = quick_report(project)
        coverage = report.get("coverage") or {}
        assert_true(coverage.get("status") == "INCOMPLETE_ASSURANCE", f"coverage below floor did not report INCOMPLETE_ASSURANCE: {coverage}", failures)
        codes = {i.get("code") for i in coverage.get("issues", [])}
        assert_true("COVERAGE_BELOW_DECLARED_FLOOR" in codes, f"coverage below floor did not produce COVERAGE_BELOW_DECLARED_FLOOR: {coverage}", failures)
        assert_true(report.get("overall") == "INCOMPLETE_ASSURANCE", "a below-floor coverage measurement did not force overall INCOMPLETE_ASSURANCE", failures)


def test_missing_coverage_report_is_diagnostic_only(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        project = make_project(Path(td), "coverage-missing-report")
        to_schema_v3_with_coverage_check(project, floor=80)
        # Deliberately do not write coverage-summary.json.
        report = quick_report(project)
        coverage = report.get("coverage") or {}
        assert_true(coverage.get("status") == "PASS", f"a missing coverage report incorrectly gated overall coverage status: {coverage}", failures)
        assert_true(not coverage.get("issues"), "a missing coverage report incorrectly produced a COVERAGE_BELOW_DECLARED_FLOOR issue", failures)
        diag = coverage.get("diagnostics", [{}])[0]
        assert_true(diag.get("status") == "DID_NOT_EXECUTE", f"missing coverage report was not recorded as DID_NOT_EXECUTE on the diagnostic: {diag}", failures)
        results = report.get("results", [])
        check_result = next((r for r in results if r.get("id") == "unit-tests"), {})
        assert_true(check_result.get("result") == "PASS", f"a missing coverage report incorrectly affected the check's own result: {check_result}", failures)


def test_plan_without_coverage_block_unchanged(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        project = make_project(Path(td), "coverage-none")
        to_schema_v3_no_coverage(project)
        report = quick_report(project)
        assert_true(report.get("coverage") is None, f"a v3 plan with no declared coverage block should report coverage: null, got {report.get('coverage')}", failures)


def test_v2_plan_has_no_coverage_field(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        project = make_project(Path(td), "coverage-v2")
        # Leave verification-plan.json at its default schema_version "2".
        plan_path = project / "verification-plan.json"
        data = json.loads(plan_path.read_text(encoding="utf-8-sig"))
        data["checks"] = [
            {
                "id": "unit-tests",
                "stages": ["quick", "full"],
                "command": [sys.executable, "-c", "print('tests ran')"],
                "reason": "fixture",
                "timeout_seconds": 30,
                "working_directory": None,
                "environment": {},
                "verified_targets": [],
                "result_policy": {"mode": "STANDARD"},
                "execution": {"allowed_contexts": ["LOCAL", "CI", "SPECIALIZED"], "required_contexts": ["ANY"]},
            }
        ]
        for cap in data["assurance"]["capabilities"]:
            cap["checks"] = ["unit-tests"] if cap["id"] == "tests" else []
            if cap["id"] == "tests":
                cap["decision"] = "REQUIRED"
            elif cap["decision"] == "REQUIRED":
                cap["decision"] = "OPTIONAL"
        plan_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        report = quick_report(project)
        assert_true(report.get("schema_version") == "4", "v2 plan did not produce a v4 report", failures)
        assert_true("coverage" not in report, "v2/v4 report unexpectedly carries a coverage field", failures)


def main() -> int:
    failures: list[str] = []
    test_coverage_above_floor_passes(failures)
    test_coverage_below_floor_produces_issue(failures)
    test_missing_coverage_report_is_diagnostic_only(failures)
    test_plan_without_coverage_block_unchanged(failures)
    test_v2_plan_has_no_coverage_field(failures)

    if failures:
        print("Coverage semantics regression: FAIL")
        for failure in failures:
            print("- " + failure)
        return 1

    print("Coverage semantics regression: PASS")
    print("- coverage above the declared floor: PASS, measured value recorded")
    print("- coverage below the declared floor: COVERAGE_BELOW_DECLARED_FLOOR issue, overall INCOMPLETE_ASSURANCE")
    print("- missing coverage report: DID_NOT_EXECUTE on the diagnostic only, the check's own result is unaffected")
    print("- v3 plan with no declared coverage block: coverage is null, unchanged behavior")
    print("- verification-plan schema v2 / report schema v4 carries no coverage field at all")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
