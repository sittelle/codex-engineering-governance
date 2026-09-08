#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

MANAGED_RE = re.compile(
    r"(?s)<!-- BEGIN CODEX-GOVERNANCE-MANAGED -->.*?<!-- END CODEX-GOVERNANCE-MANAGED -->"
)
BASELINE_RE = re.compile(r'(?m)^\s*baseline:\s*["\']?([^"\']+)["\']?\s*$')
ASSERTION_REL = Path("tests/eval-verification.py")
ALLOWED_FIXTURE_PATHS = {
    "AGENTS.md",
    "project-governance.yml",
    ASSERTION_REL.as_posix(),
}


class ActivationError(RuntimeError):
    pass


def run(argv: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def emit_process(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)


def require_success(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode != 0:
        detail = "\n".join(x for x in (result.stdout.strip(), result.stderr.strip()) if x)
        if detail:
            raise ActivationError(f"{label} failed (exit {result.returncode}):\n{detail}")
        raise ActivationError(f"{label} failed (exit {result.returncode})")


def powershell() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell") or shutil.which("powershell.exe")


def parse_baseline(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    match = BASELINE_RE.search(text)
    if not match:
        raise ActivationError(f"Could not find governance baseline in {path}")
    return match.group(1).strip()


def managed_block(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    match = MANAGED_RE.search(text)
    if not match:
        raise ActivationError(f"Managed governance block not found in {path}")
    return match.group(0).replace("\r\n", "\n")


def git_status(fixture: Path) -> list[str]:
    result = run(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=fixture)
    require_success(result, "git status")
    return [line for line in result.stdout.splitlines() if line]


def status_path(line: str) -> str:
    if len(line) < 4:
        return ""
    path = line[3:]
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path.strip('"').replace("\\", "/")


def snapshot(path: Path) -> bytes | None:
    return path.read_bytes() if path.exists() else None


def restore(path: Path, data: bytes | None) -> None:
    if data is None:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def backup_names(fixture: Path) -> set[Path]:
    names: set[Path] = set()
    for pattern in ("AGENTS.md.governance-backup-*", "project-governance.yml.governance-backup-*"):
        names.update(p for p in fixture.glob(pattern) if p.is_file())
    return names


def codex_backup_names(codex_home: Path) -> set[Path]:
    if not codex_home.exists():
        return set()
    return {p for p in codex_home.glob("AGENTS.md.backup-*") if p.is_file()}


def update_command(framework: Path, fixture: Path, *, apply: bool) -> list[str]:
    if os.name == "nt":
        ps = powershell()
        if not ps:
            raise ActivationError("PowerShell is required for the Windows governed-project updater")
        cmd = [
            ps,
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(framework / "scripts/update-governed-project.ps1"),
            "-ProjectRoot",
            str(fixture),
        ]
        if apply:
            cmd.append("-Apply")
        return cmd
    sh = shutil.which("sh")
    if not sh:
        raise ActivationError("POSIX sh is required for the governed-project updater")
    cmd = [sh, str(framework / "scripts/update-governed-project.sh"), str(fixture)]
    if apply:
        cmd.append("--apply")
    return cmd


def install_command(framework: Path, codex_home: Path) -> tuple[list[str], dict[str, str] | None]:
    if os.name == "nt":
        ps = powershell()
        if not ps:
            raise ActivationError("PowerShell is required for the Windows Codex-home installer")
        return ([
            ps,
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(framework / "codex-home/install.ps1"),
            "-GovernanceRoot",
            str(framework),
            "-CodexHome",
            str(codex_home),
        ], None)
    sh = shutil.which("sh")
    if not sh:
        raise ActivationError("POSIX sh is required for the Codex-home installer")
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    return ([sh, str(framework / "codex-home/install.sh"), str(framework)], env)


def reconcile_fixture_assertion(path: Path, old: str, target: str) -> bool:
    text = path.read_text(encoding="utf-8-sig")
    old_literal = f'baseline: "{old}"'
    target_literal = f'baseline: "{target}"'

    if old == target:
        count = text.count(target_literal)
        if count != 1:
            raise ActivationError(
                f"Expected exactly one evaluation-fixture baseline assertion {target_literal!r}; found {count}"
            )
        return False

    count = text.count(old_literal)
    if count != 1:
        raise ActivationError(
            f"Expected exactly one evaluation-fixture baseline assertion {old_literal!r}; found {count}"
        )
    path.write_text(text.replace(old_literal, target_literal, 1), encoding="utf-8", newline="\n")
    return True


def verify_fixture(framework: Path, fixture: Path, target: str, old: str) -> tuple[list[str], bool]:
    manifest = fixture / "project-governance.yml"
    agents = fixture / "AGENTS.md"
    assertion = fixture / ASSERTION_REL

    actual = parse_baseline(manifest)
    if actual != target:
        raise ActivationError(f"Fixture baseline is {actual!r}, expected {target!r}")

    assertion_text = assertion.read_text(encoding="utf-8-sig")
    target_literal = f'baseline: "{target}"'
    if assertion_text.count(target_literal) != 1:
        raise ActivationError("Evaluation-fixture baseline assertion was not reconciled exactly once")
    if old != target and f'baseline: "{old}"' in assertion_text:
        raise ActivationError(f"Stale evaluation-fixture baseline assertion remains for {old}")

    template_block = managed_block(framework / "templates/repository/AGENTS.md")
    fixture_block = managed_block(agents)
    if template_block != fixture_block:
        raise ActivationError("Fixture managed AGENTS block does not match the authoritative framework template")

    for mode in ("quick", "full"):
        result = run([sys.executable, str(assertion), mode], cwd=fixture)
        emit_process(result)
        require_success(result, f"fixture {mode} verification")

    diff = run(["git", "diff", "--check"], cwd=fixture)
    require_success(diff, "fixture git diff --check")

    status = git_status(fixture)
    paths = [status_path(line) for line in status]
    unexpected = [
        path for path in paths
        if path not in ALLOWED_FIXTURE_PATHS and '.governance-backup-' not in path
    ]
    if unexpected:
        raise ActivationError("Unexpected fixture changes after activation: " + ", ".join(unexpected))

    agents_changed = "AGENTS.md" in paths
    return paths, agents_changed


def verify_global(framework: Path, codex_home: Path) -> str:
    source_kernel = framework / "codex-home/AGENTS.md"
    target_kernel = codex_home / "AGENTS.md"
    locator = codex_home / "GOVERNANCE_ROOT"

    if not target_kernel.is_file():
        raise ActivationError(f"Installed global kernel missing: {target_kernel}")
    if source_kernel.read_bytes() != target_kernel.read_bytes():
        raise ActivationError("Installed global AGENTS.md is not byte-identical to the framework kernel")
    if not locator.is_file():
        raise ActivationError(f"Installed GOVERNANCE_ROOT missing: {locator}")

    locator_text = locator.read_text(encoding="utf-8-sig").strip()
    try:
        actual = Path(locator_text).resolve()
    except Exception as exc:
        raise ActivationError(f"Installed GOVERNANCE_ROOT is invalid: {locator_text!r}: {exc}") from exc
    if actual != framework.resolve():
        raise ActivationError(f"Installed GOVERNANCE_ROOT points to {actual}, expected {framework.resolve()}")
    return locator_text


def activate(framework: Path, fixture: Path, codex_home: Path, *, apply: bool) -> int:
    framework = framework.resolve()
    fixture = fixture.resolve()
    codex_home = codex_home.expanduser().resolve()

    version_file = framework / "VERSION"
    if not version_file.is_file():
        raise ActivationError(f"Framework VERSION missing: {version_file}")
    target = version_file.read_text(encoding="utf-8-sig").strip()

    manifest = fixture / "project-governance.yml"
    agents = fixture / "AGENTS.md"
    assertion = fixture / ASSERTION_REL
    for path in (manifest, agents, assertion):
        if not path.is_file():
            raise ActivationError(f"Evaluation fixture is missing required file: {path}")
    if not (fixture / ".git").exists():
        raise ActivationError(f"Evaluation fixture is not a Git worktree: {fixture}")

    status = git_status(fixture)
    if status:
        raise ActivationError("Evaluation fixture worktree is dirty; commit/stash changes before activation")

    old = parse_baseline(manifest)
    assertion_text = assertion.read_text(encoding="utf-8-sig")
    expected_literal = f'baseline: "{old}"'
    if assertion_text.count(expected_literal) != 1:
        raise ActivationError(
            f"Expected exactly one evaluation-fixture baseline assertion {expected_literal!r} before activation"
        )

    # Validate updater compatibility in both dry-run and apply modes before any
    # wrapper-owned mutation. The updater itself is non-mutating without apply.
    preview = run(update_command(framework, fixture, apply=False), cwd=framework)
    emit_process(preview)
    require_success(preview, "governed-project update preview")

    template_block = managed_block(framework / "templates/repository/AGENTS.md")
    current_block = managed_block(agents)
    agents_equivalent = template_block == current_block

    print("\nFrozen baseline activation plan")
    print(f"- mode:              {'APPLY' if apply else 'DRY RUN'}")
    print(f"- framework version: {target}")
    print(f"- fixture baseline:  {old}")
    print(f"- target baseline:   {target}")
    print(f"- managed AGENTS:    {'already equivalent' if agents_equivalent else 'refresh required'}")
    print(f"- assertion:         {ASSERTION_REL.as_posix()} ({old} -> {target})")
    print(f"- fixture verify:    quick + full + git diff --check")
    print(f"- global Codex home: {codex_home}")

    if not apply:
        print("DRY RUN ONLY. Re-run with --apply to repin the fixture and install the global kernel.")
        print("\n========================================")
        print(f"Frozen baseline activation dry-run: PASS ({target})")
        print("- fixture mutation: none")
        print("- global Codex home mutation: none")
        return 0

    fixture_paths = [manifest, agents, assertion]
    fixture_snapshot = {path: snapshot(path) for path in fixture_paths}
    fixture_backups_before = backup_names(fixture)

    global_agents = codex_home / "AGENTS.md"
    global_locator = codex_home / "GOVERNANCE_ROOT"
    global_snapshot = {
        global_agents: snapshot(global_agents),
        global_locator: snapshot(global_locator),
    }
    global_backups_before = codex_backup_names(codex_home)

    try:
        applied = run(update_command(framework, fixture, apply=True), cwd=framework)
        emit_process(applied)
        require_success(applied, "governed-project update apply")

        # If the managed block was already authoritative before apply, the updater
        # has no semantic AGENTS change to make. Restore the exact original bytes
        # so host-native Set-Content/line-ending behavior cannot create a spurious
        # tracked AGENTS.md delta. The authoritative block is verified again below.
        if agents_equivalent:
            restore(agents, fixture_snapshot[agents])

        reconcile_fixture_assertion(assertion, old, target)
        changed_paths, agents_changed = verify_fixture(framework, fixture, target, old)

        # Updater backups are safety scaffolding, not fixture source/evidence.
        for path in backup_names(fixture) - fixture_backups_before:
            path.unlink(missing_ok=True)

        # Recheck after removing backup artifacts so the fixture is genuinely
        # commit-ready and contains only bounded tracked changes.
        status_after_cleanup = git_status(fixture)
        changed_paths = [status_path(line) for line in status_after_cleanup]
        unexpected = [path for path in changed_paths if path not in ALLOWED_FIXTURE_PATHS]
        if unexpected:
            raise ActivationError("Unexpected fixture changes after backup cleanup: " + ", ".join(unexpected))

        install_argv, install_env = install_command(framework, codex_home)
        installed = run(install_argv, cwd=framework, env=install_env)
        emit_process(installed)
        require_success(installed, "global kernel installation")
        locator_text = verify_global(framework, codex_home)

        print("\n========================================")
        print(f"Frozen baseline activation: PASS ({target})")
        print(f"- fixture baseline: {target}")
        print("- fixture quick/full: PASS")
        if agents_changed:
            print("- managed AGENTS: updated to authoritative block")
        else:
            print("- managed AGENTS: unchanged/equivalent")
        if changed_paths:
            print("- fixture diff: commit-ready (" + ", ".join(changed_paths) + ")")
        else:
            print("- fixture diff: no tracked changes")
        print(f"- global kernel: exact {target} copy")
        print(f"- GOVERNANCE_ROOT: {locator_text}")
        print("- publication/release state: unchanged")
        return 0
    except Exception as exc:
        rollback_errors: list[str] = []
        for path, data in fixture_snapshot.items():
            try:
                restore(path, data)
            except Exception as rollback_exc:
                rollback_errors.append(f"fixture {path}: {rollback_exc}")
        for path in backup_names(fixture) - fixture_backups_before:
            try:
                path.unlink(missing_ok=True)
            except Exception as rollback_exc:
                rollback_errors.append(f"fixture backup {path}: {rollback_exc}")

        for path, data in global_snapshot.items():
            try:
                restore(path, data)
            except Exception as rollback_exc:
                rollback_errors.append(f"global {path}: {rollback_exc}")
        for path in codex_backup_names(codex_home) - global_backups_before:
            try:
                path.unlink(missing_ok=True)
            except Exception as rollback_exc:
                rollback_errors.append(f"global backup {path}: {rollback_exc}")

        if rollback_errors:
            print("Activation rollback: FAIL", file=sys.stderr)
            for item in rollback_errors:
                print("- " + item, file=sys.stderr)
        else:
            print("Activation rollback: PASS", file=sys.stderr)
        raise ActivationError(str(exc)) from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Activate an already-frozen framework baseline in the evaluation fixture and global Codex home. "
            "Dry-run is the default; --apply is required for mutation."
        )
    )
    parser.add_argument("--fixture", required=True, help="codex-governance-eval worktree")
    parser.add_argument(
        "--codex-home",
        default=os.environ.get("CODEX_HOME") or str(Path.home() / ".codex"),
        help="Codex home to install/verify (default: $CODEX_HOME or ~/.codex)",
    )
    parser.add_argument(
        "--framework-root",
        default=str(Path(__file__).resolve().parents[1]),
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--apply", action="store_true", help="perform the bounded activation")
    args = parser.parse_args()

    try:
        return activate(Path(args.framework_root), Path(args.fixture), Path(args.codex_home), apply=args.apply)
    except ActivationError as exc:
        print(f"Frozen baseline activation: FAIL\n- {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
