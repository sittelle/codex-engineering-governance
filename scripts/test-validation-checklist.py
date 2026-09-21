#!/usr/bin/env python3
"""Regression coverage for WS7's automated_test heuristic on
`governance.py project validation-checklist` (docs/business-led/
implementation-plan.md phase 4).

This is a keyword-based presence heuristic over the project's tests/ tree,
not a formal acceptance-criteria-to-test link -- the framework has no
acceptance-criteria file format for it to bind to. Confirms a plausibly
related test file is found for an approved capability, that an unrelated
test file does not produce a false match, and that a capability with no
matching test file stays null.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_PY = ROOT / "governance.py"


def run(argv, cwd=None):
    return subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False)


def assert_true(condition, message, failures):
    if not condition:
        failures.append(message)


def make_sealed_registration(directory: Path, *, approved: set[str]) -> Path:
    reg_path = directory / "registration.yml"
    text = (ROOT / "templates/repository/registration.yml").read_text(encoding="utf-8")
    text = text.replace('registration_id: "<assigned by the Professional>"', 'registration_id: "REG-TEST"')
    text = text.replace('purpose: "<what this project is for and who uses it>"', 'purpose: "Checklist regression fixture."')
    text = text.replace('business_owner: "<name>"', 'business_owner: "Test Owner"')
    text = text.replace('approval_authority: "<name of the Professional responsible for this project>"', 'approval_authority: "Test Professional"')
    for cap in approved:
        text = text.replace(f"{cap}: false", f"{cap}: true")
    reg_path.write_text(text, encoding="utf-8", newline="\n")
    proc = run([sys.executable, str(GOVERNANCE_PY), "registration", "seal", "--registration", str(reg_path), "--by", "test"])
    if proc.returncode != 0:
        raise RuntimeError(f"registration seal failed: {proc.stdout}\n{proc.stderr}")
    return reg_path


def make_non_professional_project(parent: Path, name: str, registration: Path) -> Path:
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
            "--developer-language",
            "non-professional",
            "--registration",
            str(registration),
            "-y",
        ]
    )
    if proc.returncode != 0:
        raise RuntimeError(f"project new failed: {proc.stdout}\n{proc.stderr}")
    return parent / name


def checklist_for(project: Path) -> dict:
    proc = run([sys.executable, str(GOVERNANCE_PY), "project", "validation-checklist", "--project", str(project)])
    if proc.returncode != 0:
        raise RuntimeError(f"validation-checklist failed: {proc.stdout}\n{proc.stderr}")
    return json.loads(proc.stdout)


def item_for(checklist: dict, source: str) -> dict | None:
    return next((item for item in checklist.get("items", []) if item.get("source") == source), None)


def test_matching_test_file_is_found(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        registration = make_sealed_registration(td, approved={"authentication"})
        project = make_non_professional_project(td, "checklist-match", registration)
        (project / "tests").mkdir(exist_ok=True)
        (project / "tests" / "test_login.py").write_text("def test_login_rejects_bad_password(): pass\n", encoding="utf-8")

        checklist = checklist_for(project)
        item = item_for(checklist, "capability:authentication")
        assert_true(item is not None, "no checklist item for the approved authentication capability", failures)
        if item is not None:
            assert_true(
                item.get("automated_test") == ["tests/test_login.py"],
                f"authentication item did not find the matching test file: {item.get('automated_test')}",
                failures,
            )


def test_unrelated_test_file_does_not_match(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        registration = make_sealed_registration(td, approved={"cloud"})
        project = make_non_professional_project(td, "checklist-nomatch", registration)
        (project / "tests").mkdir(exist_ok=True)
        (project / "tests" / "test_math.py").write_text("def test_sum_adds_numbers(): pass\n", encoding="utf-8")

        checklist = checklist_for(project)
        item = item_for(checklist, "capability:cloud")
        assert_true(item is not None, "no checklist item for the approved cloud capability", failures)
        if item is not None:
            assert_true(
                item.get("automated_test") is None,
                f"an unrelated test file incorrectly matched the cloud capability: {item.get('automated_test')}",
                failures,
            )


def test_purpose_item_is_never_matched(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        registration = make_sealed_registration(td, approved=set())
        project = make_non_professional_project(td, "checklist-purpose", registration)
        checklist = checklist_for(project)
        item = item_for(checklist, "purpose")
        assert_true(item is not None, "no purpose checklist item", failures)
        if item is not None:
            assert_true(item.get("automated_test") is None, "purpose item unexpectedly has an automated_test value", failures)


def main() -> int:
    failures: list[str] = []
    test_matching_test_file_is_found(failures)
    test_unrelated_test_file_does_not_match(failures)
    test_purpose_item_is_never_matched(failures)

    if failures:
        print("Validation checklist regression: FAIL")
        for failure in failures:
            print("- " + failure)
        return 1

    print("Validation checklist regression: PASS")
    print("- a plausibly related test file is found for an approved capability")
    print("- an unrelated test file does not produce a false match")
    print("- the purpose item never gets a heuristic match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
