#!/usr/bin/env python3
"""Regression coverage for WS1 governance-artifact integrity (business-led mode).

Exercises assurance/run-verification.py's governance_integrity_preflight,
release_baseline_preflight, and instruction_surface_audit against real
fixtures produced by governance.py and scripts/bootstrap-assurance.py:
a tampered managed block, a tampered project-governance.yml governance
field, a tampered verification-plan.json assurance object, a swapped
.governance/assurance-baseline.json copy, a swapped central
capability-baseline.json, and an unapproved instruction surface in
business-led mode. Confirms verification-plan schema v2 (report schema
v4) fixtures are entirely unaffected by all of the above, per the
"schema v2 and v4 paths unchanged" constraint.
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
BOOTSTRAP = ROOT / "scripts/bootstrap-assurance.py"
RUNNER = ROOT / "assurance/run-verification.py"
CENTRAL_BASELINE = ROOT / "assurance/capability-baseline.json"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8-sig").strip()


def run(argv, cwd=None):
    return subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False)


def assert_true(condition, message, failures):
    if not condition:
        failures.append(message)


def make_project(parent: Path, name: str) -> Path:
    proc = run([sys.executable, str(GOVERNANCE_PY), "project", "new", "--parent", str(parent), "--name", name, "--no-git-init", "-y"])
    if proc.returncode != 0:
        raise RuntimeError(f"governance.py project new failed: {proc.stdout}\n{proc.stderr}")
    return parent / name


def to_schema_v3(project: Path) -> None:
    plan_path = project / "verification-plan.json"
    data = json.loads(plan_path.read_text(encoding="utf-8-sig"))
    data["schema_version"] = "3"
    plan_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def quick_report(project: Path, *, plan: str = "verification-plan.json", baseline: Path | None = None) -> dict:
    report_path = project / "report.json"
    cmd = [
        sys.executable,
        str(RUNNER),
        "quick",
        "--project-root",
        str(project),
        "--plan",
        plan,
        "--baseline",
        str(baseline or CENTRAL_BASELINE),
        "--report",
        str(report_path),
    ]
    run(cmd)
    return json.loads(report_path.read_text(encoding="utf-8"))


def issue_codes(report: dict, section: str) -> set[str]:
    entry = report.get(section) or {}
    return {issue.get("code") for issue in entry.get("issues", [])}


def tamper_managed_block(project: Path) -> None:
    agents = project / "AGENTS.md"
    text = agents.read_text(encoding="utf-8-sig")
    assert "Do not bulk-load every skill/profile." in text, "fixture template changed; update tamper target"
    text = text.replace("Do not bulk-load every skill/profile.", "Load every skill/profile eagerly.")
    agents.write_text(text, encoding="utf-8", newline="\n")


def tamper_governance_fields(project: Path) -> None:
    manifest = project / "project-governance.yml"
    text = manifest.read_text(encoding="utf-8-sig")
    text = text.replace('baseline: "' + VERSION + '"', 'baseline: "' + VERSION + '"  # tampered')
    manifest.write_text(text, encoding="utf-8", newline="\n")


def tamper_verification_plan_assurance(project: Path) -> None:
    plan_path = project / "verification-plan.json"
    data = json.loads(plan_path.read_text(encoding="utf-8-sig"))
    data["assurance"]["facts"]["has_exposed_web_surface"] = True
    plan_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def enable_business_led_mode(project: Path) -> None:
    manifest = project / "project-governance.yml"
    text = manifest.read_text(encoding="utf-8-sig")
    assert "governance:\n  baseline:" in text, "fixture template changed; update mode injection point"
    text = text.replace("governance:\n  baseline:", 'governance:\n  mode: "business-led"\n  baseline:', 1)
    manifest.write_text(text, encoding="utf-8", newline="\n")


def test_clean_project_has_no_new_issues(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        project = make_project(Path(td), "clean")
        to_schema_v3(project)
        report = quick_report(project)
        assert_true(report.get("schema_version") == "5", "clean v3 project did not produce a v5 report", failures)
        assert_true(not issue_codes(report, "governance_integrity"), "clean v3 project reported governance-integrity issues", failures)
        assert_true(not issue_codes(report, "instruction_surface_audit"), "clean v3 professional-mode project reported instruction-surface issues", failures)


def test_tampered_managed_block(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        project = make_project(Path(td), "tampered-block")
        to_schema_v3(project)
        tamper_managed_block(project)
        report = quick_report(project)
        assert_true(
            "GOVERNANCE_INTEGRITY_FAILED" in issue_codes(report, "governance_integrity"),
            "tampered managed AGENTS.md block did not produce GOVERNANCE_INTEGRITY_FAILED",
            failures,
        )
        assert_true(report.get("overall") == "INCOMPLETE_ASSURANCE", "tampered managed block did not force INCOMPLETE_ASSURANCE", failures)


def test_tampered_governance_fields(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        project = make_project(Path(td), "tampered-fields")
        to_schema_v3(project)
        tamper_governance_fields(project)
        report = quick_report(project)
        assert_true(
            "GOVERNANCE_INTEGRITY_FAILED" in issue_codes(report, "governance_integrity"),
            "tampered project-governance.yml governance: fields did not produce GOVERNANCE_INTEGRITY_FAILED",
            failures,
        )


def test_tampered_verification_plan_assurance(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        project = make_project(Path(td), "tampered-plan")
        to_schema_v3(project)
        tamper_verification_plan_assurance(project)
        report = quick_report(project)
        assert_true(
            "GOVERNANCE_INTEGRITY_FAILED" in issue_codes(report, "governance_integrity"),
            "tampered verification-plan.json assurance object did not produce GOVERNANCE_INTEGRITY_FAILED",
            failures,
        )


def test_swapped_project_baseline_copy(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        project = make_project(Path(td), "swapped-copy")
        to_schema_v3(project)
        boot = run([sys.executable, str(BOOTSTRAP), "--project-root", str(project), "--apply", "--skip-ci"])
        if boot.returncode != 0:
            failures.append("bootstrap-assurance.py failed for swapped-copy fixture: " + boot.stdout + boot.stderr)
            return
        copied_baseline = project / ".governance/assurance-baseline.json"
        data = json.loads(copied_baseline.read_text(encoding="utf-8-sig"))
        data["governance_version"] = "0.0.0-tampered"
        copied_baseline.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        report = quick_report(project, baseline=copied_baseline)
        assert_true(
            "GOVERNANCE_INTEGRITY_FAILED" in issue_codes(report, "governance_integrity"),
            "swapped .governance/assurance-baseline.json copy did not produce GOVERNANCE_INTEGRITY_FAILED",
            failures,
        )


def test_central_release_baseline_mismatch(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        project = td / "project"
        project.mkdir()
        (project / "VERSION").write_text(VERSION + "\n", encoding="utf-8")
        assurance_dir = td / "assurance"
        assurance_dir.mkdir()
        shutil.copy2(ROOT / "assurance/release-baseline-hashes.json", assurance_dir / "release-baseline-hashes.json")
        tampered_baseline = assurance_dir / "capability-baseline.json"
        data = json.loads(CENTRAL_BASELINE.read_text(encoding="utf-8-sig"))
        data["notes"] = ["tampered"]
        tampered_baseline.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        plan = json.loads((ROOT / "framework-verification-plan.json").read_text(encoding="utf-8-sig"))
        (project / "verification-plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        report = quick_report(project, baseline=tampered_baseline)
        assert_true(
            "GOVERNANCE_INTEGRITY_FAILED" in issue_codes(report, "governance_integrity"),
            "tampered central capability-baseline.json did not produce GOVERNANCE_INTEGRITY_FAILED against release-baseline-hashes.json",
            failures,
        )


def test_unapproved_instruction_surface(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        project = make_project(Path(td), "business-led")
        to_schema_v3(project)
        enable_business_led_mode(project)
        claude_dir = project / ".claude"
        claude_dir.mkdir()
        (claude_dir / "settings.json").write_text("{}\n", encoding="utf-8")
        report = quick_report(project)
        assert_true(
            "UNAPPROVED_INSTRUCTION_SURFACE" in issue_codes(report, "instruction_surface_audit"),
            "unregistered .claude/settings.json in business-led mode did not produce UNAPPROVED_INSTRUCTION_SURFACE",
            failures,
        )
        assert_true(
            report.get("instruction_surface_audit", {}).get("mode") == "business-led",
            "instruction-surface audit did not read the business-led mode marker",
            failures,
        )

        (project / "registration.yml").write_text("registration_id: demo\n", encoding="utf-8")
        report2 = quick_report(project)
        assert_true(
            not issue_codes(report2, "instruction_surface_audit"),
            "presence of registration.yml did not suppress the placeholder instruction-surface flag",
            failures,
        )


def test_professional_mode_reports_only(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        project = make_project(Path(td), "professional-surfaces")
        to_schema_v3(project)
        claude_dir = project / ".claude"
        claude_dir.mkdir()
        (claude_dir / "settings.json").write_text("{}\n", encoding="utf-8")
        report = quick_report(project)
        audit = report.get("instruction_surface_audit") or {}
        assert_true(audit.get("mode") == "professional", "default project mode was not professional", failures)
        assert_true(any(s.get("path") == ".claude/settings.json" for s in audit.get("surfaces", [])), "professional-mode audit did not enumerate the surface", failures)
        assert_true(audit.get("status") == "PASS", "professional mode must never fail on enumerated surfaces", failures)
        assert_true(not issue_codes(report, "instruction_surface_audit"), "professional-mode surfaces incorrectly produced instruction-surface issues", failures)


def test_v2_plan_unaffected_by_tampering(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        project = make_project(Path(td), "v2-unaffected")
        # Leave verification-plan.json at its default schema_version "2".
        tamper_managed_block(project)
        tamper_governance_fields(project)
        tamper_verification_plan_assurance(project)
        report = quick_report(project)
        assert_true(report.get("schema_version") == "4", "v2 plan did not produce a v4 report", failures)
        assert_true("governance_integrity" not in report, "v2/v4 report unexpectedly carries a governance_integrity field", failures)
        assert_true("instruction_surface_audit" not in report, "v2/v4 report unexpectedly carries an instruction_surface_audit field", failures)


def main() -> int:
    failures: list[str] = []
    test_clean_project_has_no_new_issues(failures)
    test_tampered_managed_block(failures)
    test_tampered_governance_fields(failures)
    test_tampered_verification_plan_assurance(failures)
    test_swapped_project_baseline_copy(failures)
    test_central_release_baseline_mismatch(failures)
    test_unapproved_instruction_surface(failures)
    test_professional_mode_reports_only(failures)
    test_v2_plan_unaffected_by_tampering(failures)

    if failures:
        print("Governance integrity regression: FAIL")
        for failure in failures:
            print("- " + failure)
        return 1

    print("Governance integrity regression: PASS")
    print("- clean v3 project: no governance-integrity or instruction-surface issues")
    print("- tampered managed AGENTS.md block => GOVERNANCE_INTEGRITY_FAILED")
    print("- tampered project-governance.yml governance: fields => GOVERNANCE_INTEGRITY_FAILED")
    print("- tampered verification-plan.json assurance object => GOVERNANCE_INTEGRITY_FAILED")
    print("- swapped .governance/assurance-baseline.json copy => GOVERNANCE_INTEGRITY_FAILED")
    print("- swapped central capability-baseline.json vs release-baseline-hashes.json => GOVERNANCE_INTEGRITY_FAILED")
    print("- unapproved .claude/ surface in business-led mode => UNAPPROVED_INSTRUCTION_SURFACE, suppressed once registration.yml exists")
    print("- professional mode enumerates surfaces but never fails on them")
    print("- verification-plan schema v2 / report schema v4 is entirely unaffected by all of the above")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
