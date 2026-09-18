#!/usr/bin/env python3
"""Compare a governed project's detected capabilities against its sealed
registration.yml, per WS4 phase 3 of docs/business-led/implementation-plan.md.

Detection uses the semgrep rules in semgrep/capabilities/<language>.yml
(first languages: Python, TypeScript/JavaScript). A capability with at
least one match that is not approved in the registration produces
REGISTRATION_RECONCILIATION_REQUIRED and a request record under
docs/governance/requests/ in the project. This never blocks development;
it only reports and records, per the framework's "never blocks development
on its own" invariant -- the exit code distinguishes DID_NOT_EXECUTE
(status could not be determined) from a determined PASS or
REGISTRATION_RECONCILIATION_REQUIRED, neither of which is a failure exit.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import governance  # noqa: E402

DID_NOT_EXECUTE = 3

CAPABILITY_RULESETS = {
    ".py": ROOT / "semgrep" / "capabilities" / "python.yml",
    ".ts": ROOT / "semgrep" / "capabilities" / "typescript.yml",
    ".tsx": ROOT / "semgrep" / "capabilities" / "typescript.yml",
    ".js": ROOT / "semgrep" / "capabilities" / "typescript.yml",
    ".jsx": ROOT / "semgrep" / "capabilities" / "typescript.yml",
}

EXCLUDED_DIR_NAMES = {".git", "node_modules", ".governance", "__pycache__", ".venv", "venv", "dist", "build"}


def project_source_files(project: Path, ext: str) -> list[Path]:
    return [
        p
        for p in project.rglob(f"*{ext}")
        if not any(part in EXCLUDED_DIR_NAMES for part in p.relative_to(project).parts)
    ]


def detected_languages(project: Path) -> set[str]:
    return {ext for ext in CAPABILITY_RULESETS if project_source_files(project, ext)}


def run_semgrep(project: Path, ruleset: Path) -> list[dict] | None:
    """Return matched results, or None if the tool could not run (a genuine
    operational failure, distinct from "zero findings")."""
    semgrep = shutil.which("semgrep")
    if not semgrep:
        return None
    proc = subprocess.run(
        [semgrep, "scan", "--config", str(ruleset), "--metrics=off", "--json", str(project)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode not in (0, 1):
        return None
    try:
        data = json.loads(proc.stdout)
    except Exception:
        return None
    return data.get("results", [])


def detect_capabilities(project: Path) -> tuple[set[str], bool]:
    """Return (detected capability ids, tool_available)."""
    langs = detected_languages(project)
    rulesets = {CAPABILITY_RULESETS[ext] for ext in langs}
    if not rulesets:
        return set(), True
    detected: set[str] = set()
    tool_available = True
    for ruleset in rulesets:
        results = run_semgrep(project, ruleset)
        if results is None:
            tool_available = False
            continue
        for result in results:
            capability = result.get("extra", {}).get("metadata", {}).get("capability")
            if capability:
                detected.add(capability)
    return detected, tool_available


def next_request_number(requests_dir: Path) -> int:
    highest = 0
    for path in requests_dir.glob("REQUEST-*.md"):
        match = re.match(r"REQUEST-(\d+)", path.stem)
        if match:
            highest = max(highest, int(match.group(1)))
    return highest + 1


def write_request_record(project: Path, unregistered: set[str]) -> Path:
    requests_dir = project / "docs" / "governance" / "requests"
    requests_dir.mkdir(parents=True, exist_ok=True)
    number = next_request_number(requests_dir)
    path = requests_dir / f"REQUEST-{number:04d}-capability-drift.md"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    caps = ", ".join(sorted(unregistered))
    text = f"""# REQUEST-{number:04d}: Registration update needed for detected capabilities

Status: Open
Date: {stamp}
Routing outcome: update registration
Registered pathway: (see registration.yml)

## What changed
Automated capability detection (scripts/run-registration-conformance.py)
found the project now exhibits: {caps}. This is not currently approved in
registration.yml's `capabilities` block.

## Why it matters
A capability outside the registration is unreviewed by IT Security; the
registration is the reference the framework derives assurance facts and
drift detection from.

## What IT Security is asked to decide
Whether to approve {caps} for this project's registration, or whether the
detected code should be removed/reworked instead.

## Business owner's understanding
(to be filled in by the business owner)

## IT Security's decision
(pending)
"""
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def emit(report: dict, report_path: str | None) -> None:
    text = json.dumps(report, indent=2) + "\n"
    print(text, end="")
    if report_path:
        out = Path(report_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare detected project capabilities against registration.yml.")
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--registration", default=None)
    ap.add_argument("--report", default=None)
    ap.add_argument("--no-request-record", action="store_true", help="Report only; do not write a request record.")
    args = ap.parse_args()

    project = Path(args.project_root).resolve()
    registration_path = Path(args.registration).resolve() if args.registration else project / "registration.yml"

    if not registration_path.is_file():
        emit(
            {
                "schema_version": "1",
                "status": "DID_NOT_EXECUTE",
                "reason": f"no registration file at {registration_path}",
            },
            args.report,
        )
        print("\nOVERALL: DID_NOT_EXECUTE")
        return DID_NOT_EXECUTE

    reg_text = governance.read_text(registration_path)
    if not governance.registration_seal_valid(reg_text):
        emit(
            {
                "schema_version": "1",
                "status": "DID_NOT_EXECUTE",
                "reason": "registration.yml integrity seal is missing or invalid",
            },
            args.report,
        )
        print("\nOVERALL: DID_NOT_EXECUTE")
        return DID_NOT_EXECUTE

    data = governance.parse_registration(reg_text)
    approved = {key for key, value in data.get("capabilities", {}).items() if value}

    detected, tool_available = detect_capabilities(project)
    if not tool_available:
        emit(
            {
                "schema_version": "1",
                "status": "DID_NOT_EXECUTE",
                "reason": "semgrep is not available on PATH; capability detection could not run",
            },
            args.report,
        )
        print("\nOVERALL: DID_NOT_EXECUTE")
        return DID_NOT_EXECUTE

    unregistered = detected - approved
    request_record = None
    if unregistered and not args.no_request_record:
        request_record = str(write_request_record(project, unregistered).relative_to(project))

    status = "REGISTRATION_RECONCILIATION_REQUIRED" if unregistered else "PASS"
    emit(
        {
            "schema_version": "1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "project": project.name,
            "registration_id": data.get("registration_id"),
            "status": status,
            "detected_capabilities": sorted(detected),
            "approved_capabilities": sorted(approved),
            "unregistered_capabilities": sorted(unregistered),
            "request_record": request_record,
        },
        args.report,
    )
    print(f"\nOVERALL: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
