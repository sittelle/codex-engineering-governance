#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
MANAGED_RE = re.compile(
    r"(?s)<!-- BEGIN ENGINEERING-GOVERNANCE-MANAGED -->.*?"
    r"<!-- END ENGINEERING-GOVERNANCE-MANAGED -->"
)
TEMPLATE_AGENTS = (ROOT / "templates/repository/AGENTS.md").read_text(encoding="utf-8")
TEMPLATE_MANAGED_MATCH = MANAGED_RE.search(TEMPLATE_AGENTS)
TEMPLATE_MANAGED = TEMPLATE_MANAGED_MATCH.group(0) if TEMPLATE_MANAGED_MATCH else ""

PROPAGATION_MARKERS = (
    "Known vulnerability/finding risk acceptance is distinct from missing required-control evidence",
    "separate explicit governance/policy exception",
    "Reassess a `NOT_APPLICABLE` decision when its factual trigger changes",
    "Changing result classification for a required security control is a material C2 assurance-policy change",
    "same clean commit, verification plan, managed assurance baseline, runner semantics, and required-check inventory",
    "An attributable executed `FAIL` remains fail-dominant",
    "Service restoration is not governance completion",
    "after stabilization, run deferred verification",
    "Required-control response completeness",
    "finding risk acceptance is not the governance/policy exception required to proceed without the control",
    "any attributable executed `FAIL` remains fail-dominant even when another approved context passes",
    "A complete emergency answer explicitly states both post-stabilization duties",
    "Mentioning only deferred verification is incomplete",
)

GLOBAL_KERNEL_MARKERS = (
    "## Required-control response completeness",
    "finding-risk acceptance cannot substitute for that missing-control exception",
    "any attributable executed `FAIL` remains fail-dominant even if another approved context reports PASS",
    "### Emergency-response completeness",
    "Mentioning only deferred verification is incomplete",
)

WORKFLOW_COMPLETENESS_MARKERS = {
    "workflows/release/WORKFLOW.md": (
        "## Required-control response completeness",
        "known vulnerability/finding is a different decision from granting a governance/policy exception",
        "an attributable executed `FAIL` remains fail-dominant",
    ),
    "workflows/emergency-fix/WORKFLOW.md": (
        "### Emergency-response completeness",
        "complete/reconcile deferred verification",
        "review and remove or deliberately reconcile temporary bypasses",
    ),
}

ASSERTION_REL = Path("tests/eval-verification.py")


def run(argv, cwd=None, env=None):
    return subprocess.run(
        argv,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def assert_true(condition, message, failures):
    if not condition:
        failures.append(message)


def bounded_output(result, limit=1600):
    text = "\n".join(
        x.strip()
        for x in (result.stdout or "", result.stderr or "")
        if x and x.strip()
    )
    return text[-limit:]


def command_ok(result, label, failures):
    if result.returncode == 0:
        return True
    detail = bounded_output(result)
    failures.append(
        f"{label} (exit {result.returncode})" + (f": {detail}" if detail else "")
    )
    return False


def managed_block(text):
    match = MANAGED_RE.search(text)
    return match.group(0) if match else None


def assert_managed_template(text, label, failures):
    actual = managed_block(text)
    assert_true(bool(TEMPLATE_MANAGED), f"{label}: template managed block missing", failures)
    assert_true(
        actual == TEMPLATE_MANAGED,
        f"{label}: installed managed block differs from authoritative template block",
        failures,
    )
    if actual:
        for marker in PROPAGATION_MARKERS:
            assert_true(
                marker in actual,
                f"{label}: propagation-critical managed guidance missing {marker}",
                failures,
            )


def copy_template_project(target: Path):
    target.mkdir(parents=True, exist_ok=True)
    for rel in (
        "AGENTS.md",
        "CLAUDE.md",
        "project-governance.yml",
        "verification-plan.json",
        ".gitignore",
    ):
        shutil.copy2(ROOT / "templates/repository" / rel, target / rel)


def init_activation_fixture(base: Path, old_version: str, *, fail_full=False) -> Path:
    fixture = base / "eval-fixture"
    fixture.mkdir(parents=True)
    shutil.copy2(ROOT / "templates/repository/AGENTS.md", fixture / "AGENTS.md")

    manifest = (ROOT / "templates/repository/project-governance.yml").read_text(
        encoding="utf-8"
    )
    manifest = manifest.replace(
        f'baseline: "{VERSION}"', f'baseline: "{old_version}"', 1
    )
    (fixture / "project-governance.yml").write_text(
        manifest, encoding="utf-8", newline="\n"
    )

    tests = fixture / "tests"
    tests.mkdir()
    full_return = "1" if fail_full else "0"
    verifier = (
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "import sys\n"
        f"EXPECTED = 'baseline: \"{old_version}\"'\n"
        "\n"
        "def main():\n"
        "    root=Path(__file__).resolve().parents[1]\n"
        "    text=(root/'project-governance.yml').read_text(encoding='utf-8-sig')\n"
        "    mode=sys.argv[1] if len(sys.argv)>1 else 'quick'\n"
        "    if EXPECTED not in text:\n"
        "        print('Evaluation fixture verification: FAIL')\n"
        "        return 1\n"
        "    if mode == 'full':\n"
        f"        return {full_return}\n"
        "    print(f'Evaluation fixture verification: PASS ({mode})')\n"
        "    return 0\n"
        "\n"
        "if __name__ == '__main__':\n"
        "    raise SystemExit(main())\n"
    )
    (tests / "eval-verification.py").write_text(
        verifier, encoding="utf-8", newline="\n"
    )

    run(["git", "init", "-q"], cwd=fixture)
    run(["git", "config", "user.email", "activation@example.invalid"], cwd=fixture)
    run(["git", "config", "user.name", "Activation Test"], cwd=fixture)
    run(["git", "add", "-A"], cwd=fixture)
    committed = run(["git", "commit", "-qm", "fixture baseline"], cwd=fixture)
    if committed.returncode != 0:
        raise RuntimeError(committed.stdout + committed.stderr)
    return fixture


def activation_snapshot(root: Path):
    if not root.exists():
        return {}
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file() and ".git" not in p.parts
    }


def test_management(mode: str, failures):
    result = run(
        [sys.executable, str(ROOT / "scripts/test-management.py"), "--mode", mode]
    )
    command_ok(result, f"unified management regression ({mode}) failed", failures)


def test_common(failures):
    assert_true(bool(TEMPLATE_MANAGED), "authoritative template managed block missing", failures)
    assert_managed_template(TEMPLATE_AGENTS, "template", failures)

    kernel = (ROOT / "codex-home/AGENTS.md").read_text(encoding="utf-8")
    for marker in GLOBAL_KERNEL_MARKERS:
        assert_true(
            marker in kernel,
            f"global kernel response-completeness guidance missing {marker}",
            failures,
        )

    for rel, markers in WORKFLOW_COMPLETENESS_MARKERS.items():
        workflow = (ROOT / rel).read_text(encoding="utf-8")
        for marker in markers:
            assert_true(
                marker in workflow,
                f"{rel}: response-completeness guidance missing {marker}",
                failures,
            )

    for rel in (
        "codex-home/install.ps1",
        "codex-home/install.sh",
        "scripts/manage-governed-project.ps1",
        "scripts/manage-governed-project.sh",
        "scripts/update-governed-project.ps1",
        "scripts/update-governed-project.sh",
    ):
        assert_true(not (ROOT / rel).exists(), f"obsolete management entry point still exists: {rel}", failures)

    manager = (ROOT / "governance.py").read_text(encoding="utf-8")
    assert_true(
        "## Central governance integration" not in manager,
        "governance.py hard-codes the project managed block instead of sourcing the template",
        failures,
    )
    assert_true(
        "permissions.additionalDirectories" not in manager,
        "governance.py grants Claude a broad additional directory instead of a Read allow rule",
        failures,
    )
    for marker in ("permissions.allow", "Read(/", "Apply these changes? [y/N]:"):
        assert_true(marker in manager, f"governance.py missing management marker: {marker}", failures)

    test_management("common", failures)
    if failures:
        return

    candidate_tools = run([sys.executable, str(ROOT / "scripts/test-candidate-validation.py")])
    if not command_ok(candidate_tools, "candidate validation tooling regression failed", failures):
        return

    activation = ROOT / "scripts/activate-frozen-baseline.py"
    old_version = "0.5.24" if VERSION != "0.5.24" else "0.5.23"

    with tempfile.TemporaryDirectory(prefix="gov-activation-test-") as td:
        base = Path(td)
        fixture = init_activation_fixture(base, old_version)
        codex_home = base / "codex-home"
        before_fixture = activation_snapshot(fixture)
        before_home = activation_snapshot(codex_home)

        dry = run(
            [
                sys.executable,
                str(activation),
                "--fixture",
                str(fixture),
                "--codex-home",
                str(codex_home),
            ]
        )
        if not command_ok(dry, "frozen baseline activation dry-run failed", failures):
            return
        assert_true(
            "Frozen baseline activation dry-run: PASS" in dry.stdout,
            "activation dry-run missing PASS summary",
            failures,
        )
        assert_true(
            activation_snapshot(fixture) == before_fixture
            and activation_snapshot(codex_home) == before_home,
            "activation dry-run mutated fixture or Codex home",
            failures,
        )

        applied = run(
            [
                sys.executable,
                str(activation),
                "--fixture",
                str(fixture),
                "--codex-home",
                str(codex_home),
                "--apply",
            ]
        )
        if not command_ok(applied, "frozen baseline activation apply failed", failures):
            return
        assert_true(
            "Frozen baseline activation: PASS" in applied.stdout,
            "activation apply missing PASS summary",
            failures,
        )

        manifest = (fixture / "project-governance.yml").read_text(encoding="utf-8-sig")
        verifier = (fixture / ASSERTION_REL).read_text(encoding="utf-8-sig")
        assert_true(
            f'baseline: "{VERSION}"' in manifest
            and f'baseline: "{VERSION}"' in verifier,
            "activation did not reconcile fixture baseline/assertion",
            failures,
        )
        assert_true(
            (fixture / "CLAUDE.md").is_file()
            and "@AGENTS.md" in (fixture / "CLAUDE.md").read_text(encoding="utf-8-sig"),
            "activation did not add the Claude project adapter",
            failures,
        )

        status = run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=fixture
        ).stdout.splitlines()
        status_paths = {line[3:].replace("\\", "/") for line in status if line}
        assert_true(
            status_paths
            == {"CLAUDE.md", "project-governance.yml", ASSERTION_REL.as_posix()},
            "activation produced unexpected fixture changes: " + repr(status),
            failures,
        )
        assert_true(
            not any(fixture.glob("*.governance-backup-*")),
            "activation left updater backup artifacts in fixture",
            failures,
        )

        env = os.environ.copy()
        env["CODEX_HOME"] = str(codex_home)
        verified = run(
            [sys.executable, str(ROOT / "governance.py"), "host", "verify", "--host", "codex"],
            env=env,
        )
        command_ok(verified, "activation Codex host verification failed", failures)

    with tempfile.TemporaryDirectory(prefix="gov-activation-rollback-test-") as td:
        base = Path(td)
        fixture = init_activation_fixture(base, old_version, fail_full=True)
        codex_home = base / "codex-home"
        before_fixture = activation_snapshot(fixture)
        before_home = activation_snapshot(codex_home)
        failed = run(
            [
                sys.executable,
                str(activation),
                "--fixture",
                str(fixture),
                "--codex-home",
                str(codex_home),
                "--apply",
            ]
        )
        assert_true(
            failed.returncode != 0 and "Activation rollback: PASS" in failed.stderr,
            "activation did not fail/rollback after fixture verification failure",
            failures,
        )
        assert_true(
            activation_snapshot(fixture) == before_fixture
            and not run(
                ["git", "status", "--porcelain=v1", "--untracked-files=all"],
                cwd=fixture,
            ).stdout.strip(),
            "activation rollback did not restore clean fixture bytes",
            failures,
        )
        assert_true(
            activation_snapshot(codex_home) == before_home,
            "activation rollback unexpectedly changed global Codex home",
            failures,
        )

    with tempfile.TemporaryDirectory(prefix="gov-activation-dirty-test-") as td:
        base = Path(td)
        fixture = init_activation_fixture(base, old_version)
        codex_home = base / "codex-home"
        manifest = fixture / "project-governance.yml"
        manifest.write_text(
            manifest.read_text(encoding="utf-8") + "# dirty\n",
            encoding="utf-8",
            newline="\n",
        )
        before = activation_snapshot(fixture)
        dirty = run(
            [
                sys.executable,
                str(activation),
                "--fixture",
                str(fixture),
                "--codex-home",
                str(codex_home),
                "--apply",
            ]
        )
        assert_true(
            dirty.returncode != 0 and "worktree is dirty" in dirty.stderr,
            "activation accepted dirty fixture worktree",
            failures,
        )
        assert_true(
            activation_snapshot(fixture) == before,
            "activation mutated dirty fixture before refusal",
            failures,
        )

    with tempfile.TemporaryDirectory(prefix="gov-bootstrap-test-") as td:
        project = Path(td) / "project"
        copy_template_project(project)
        bootstrap = ROOT / "scripts/bootstrap-assurance.py"
        before = {
            p.relative_to(project).as_posix(): p.read_bytes()
            for p in project.rglob("*")
            if p.is_file()
        }
        dry = run(
            [
                sys.executable,
                str(bootstrap),
                "--project-root",
                str(project),
                "--allow-unconfigured-ci",
            ]
        )
        if not command_ok(dry, "assurance bootstrap dry-run failed", failures):
            return
        after = {
            p.relative_to(project).as_posix(): p.read_bytes()
            for p in project.rglob("*")
            if p.is_file()
        }
        assert_true(
            before == after and not (project / ".governance").exists(),
            "assurance bootstrap dry-run mutated project",
            failures,
        )
        applied = run(
            [
                sys.executable,
                str(bootstrap),
                "--project-root",
                str(project),
                "--allow-unconfigured-ci",
                "--apply",
            ]
        )
        if not command_ok(applied, "assurance bootstrap apply failed", failures):
            return
        for rel in (
            ".governance/run-verification.py",
            ".governance/run-ci-verification.py",
            ".governance/aggregate-verification.py",
            ".governance/assurance-baseline.json",
            ".governance/assurance-bootstrap.json",
        ):
            assert_true((project / rel).exists(), f"assurance bootstrap missing {rel}", failures)
        owned = project / ".governance/run-verification.py"
        owned.write_text("# project owned\n", encoding="utf-8", newline="\n")
        again = run(
            [
                sys.executable,
                str(bootstrap),
                "--project-root",
                str(project),
                "--allow-unconfigured-ci",
                "--apply",
            ]
        )
        assert_true(
            again.returncode == 0 and owned.read_text(encoding="utf-8") == "# project owned\n",
            "assurance bootstrap overwrote project-owned runner",
            failures,
        )


def test_posix(failures):
    if os.name == "nt":
        failures.append("POSIX lifecycle evidence ran on Windows")
        return
    test_management("posix", failures)
    sh = shutil.which("sh")
    if not sh:
        failures.append("POSIX sh unavailable for assurance bootstrap wrapper regression")
        return
    with tempfile.TemporaryDirectory(prefix="gov-posix-wrapper-") as td:
        project = Path(td) / "project"
        copy_template_project(project)
        result = run(
            [
                sh,
                str(ROOT / "scripts/bootstrap-assurance.sh"),
                "--project-root",
                str(project),
                "--allow-unconfigured-ci",
            ]
        )
        command_ok(result, "POSIX assurance bootstrap wrapper failed", failures)


def powershell():
    return shutil.which("pwsh") or shutil.which("powershell") or shutil.which("powershell.exe")


def test_windows(failures):
    if os.name != "nt":
        failures.append("Windows lifecycle evidence ran on non-Windows OS")
        return
    test_management("windows", failures)
    ps = powershell()
    if not ps:
        failures.append("PowerShell unavailable for assurance bootstrap wrapper regression")
        return
    with tempfile.TemporaryDirectory(prefix="gov-windows-wrapper-") as td:
        project = Path(td) / "project"
        copy_template_project(project)
        result = run(
            [
                ps,
                "-NoProfile",
                "-NonInteractive",
                "-File",
                str(ROOT / "scripts/bootstrap-assurance.ps1"),
                "-ProjectRoot",
                str(project),
            ]
        )
        command_ok(result, "Windows assurance bootstrap wrapper failed", failures)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode", choices=["common", "posix", "windows", "auto"], default="auto"
    )
    args = parser.parse_args()
    failures = []
    modes = (
        [args.mode]
        if args.mode != "auto"
        else ["common", "windows" if os.name == "nt" else "posix"]
    )
    for mode in modes:
        if mode == "common":
            test_common(failures)
        elif mode == "posix":
            test_posix(failures)
        else:
            test_windows(failures)

    if failures:
        print("Framework lifecycle regression: FAIL")
        for failure in failures:
            print("- " + failure)
        return 1

    print("Framework lifecycle regression: PASS (" + ", ".join(modes) + ")")
    print(
        "- unified governance.py host/project lifecycle, ownership-safe uninstall, "
        "managed-block propagation, candidate tooling, frozen-baseline activation "
        "dry-run/apply/rollback, assurance bootstrap, dirty-Git refusal, and host-native "
        "distribution contracts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
