#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ASSERTION_REL = Path("tests/eval-verification.py")
ALLOWED_FIXTURE_PATHS = {
    "AGENTS.md",
    "CLAUDE.md",
    "project-governance.yml",
    ASSERTION_REL.as_posix(),
}
BACKUP_PATTERNS = (
    "AGENTS.md.governance-backup-*",
    "CLAUDE.md.governance-backup-*",
    "project-governance.yml.governance-backup-*",
)


class ActivationError(RuntimeError):
    pass


def run(
    argv: list[str],
    *,
    cwd: Path | None = None,
    input_text: str | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        text=True,
        input=input_text,
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
    if result.returncode == 0:
        return
    detail = "\n".join(
        x for x in (result.stdout.strip(), result.stderr.strip()) if x
    )
    suffix = f":\n{detail}" if detail else ""
    raise ActivationError(f"{label} failed (exit {result.returncode}){suffix}")


def git_status(fixture: Path) -> list[str]:
    result = run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=fixture,
    )
    require_success(result, "git status")
    return [line for line in result.stdout.splitlines() if line]


def status_path(line: str) -> str:
    if len(line) < 4:
        return ""
    path = line[3:]
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path.strip('"').replace("\\", "/")


def snapshot_tree(root: Path) -> dict[str, bytes]:
    if not root.exists():
        return {}
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file() and ".git" not in p.parts
    }


def restore_tree(root: Path, snapshot: dict[str, bytes]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for path in sorted(root.rglob("*"), reverse=True):
        if ".git" in path.parts:
            continue
        if path.is_file() or path.is_symlink():
            path.unlink(missing_ok=True)
        elif path.is_dir():
            try:
                path.rmdir()
            except OSError:
                pass
    for rel, data in snapshot.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def backup_names(fixture: Path) -> set[Path]:
    names: set[Path] = set()
    for pattern in BACKUP_PATTERNS:
        names.update(p for p in fixture.glob(pattern) if p.is_file())
    return names


def reconcile_fixture_assertion(path: Path, target: str) -> None:
    text = path.read_text(encoding="utf-8-sig")
    matches = list(re.finditer(r'baseline: "[^"]+"', text))
    if len(matches) != 1:
        raise ActivationError(
            f"Expected exactly one evaluation-fixture baseline assertion; found {len(matches)}"
        )
    start, end = matches[0].span()
    path.write_text(
        text[:start] + f'baseline: "{target}"' + text[end:],
        encoding="utf-8",
        newline="\n",
    )


def verify_fixture(fixture: Path, target: str) -> list[str]:
    manifest = fixture / "project-governance.yml"
    assertion = fixture / ASSERTION_REL
    claude = fixture / "CLAUDE.md"

    manifest_text = manifest.read_text(encoding="utf-8-sig")
    if f'baseline: "{target}"' not in manifest_text:
        raise ActivationError(f"Fixture baseline was not updated to {target}")
    if 'source: "host-adapter-locator"' not in manifest_text:
        raise ActivationError("Fixture governance source is not host-adapter-locator")
    if 'locator: "GOVERNANCE_ROOT"' not in manifest_text:
        raise ActivationError("Fixture governance locator is not host-neutral")
    if not claude.is_file() or "@AGENTS.md" not in claude.read_text(encoding="utf-8-sig"):
        raise ActivationError("Fixture Claude project adapter is missing or invalid")

    assertion_text = assertion.read_text(encoding="utf-8-sig")
    if assertion_text.count(f'baseline: "{target}"') != 1:
        raise ActivationError("Evaluation-fixture baseline assertion was not reconciled exactly once")

    for mode in ("quick", "full"):
        result = run([sys.executable, str(assertion), mode], cwd=fixture)
        emit_process(result)
        require_success(result, f"fixture {mode} verification")

    diff = run(["git", "diff", "--check"], cwd=fixture)
    require_success(diff, "fixture git diff --check")

    paths = [status_path(line) for line in git_status(fixture)]
    unexpected = [
        path
        for path in paths
        if path not in ALLOWED_FIXTURE_PATHS and ".governance-backup-" not in path
    ]
    if unexpected:
        raise ActivationError(
            "Unexpected fixture changes after activation: " + ", ".join(unexpected)
        )
    return paths


def verify_codex_host(framework: Path, codex_home: Path) -> None:
    governance = framework / "governance.py"
    env = dict(__import__("os").environ)
    env["CODEX_HOME"] = str(codex_home)
    result = run(
        [sys.executable, str(governance), "host", "verify", "--host", "codex"],
        cwd=framework,
        env=env,
    )
    emit_process(result)
    require_success(result, "Codex host verification")


def activate(framework: Path, fixture: Path, codex_home: Path, *, apply: bool) -> int:
    framework = framework.resolve()
    fixture = fixture.resolve()
    codex_home = codex_home.expanduser().resolve()
    governance = framework / "governance.py"

    if not governance.is_file():
        raise ActivationError(f"Unified management entry point missing: {governance}")
    version_file = framework / "VERSION"
    if not version_file.is_file():
        raise ActivationError(f"Framework VERSION missing: {version_file}")
    target = version_file.read_text(encoding="utf-8-sig").strip()

    required = (
        fixture / "project-governance.yml",
        fixture / "AGENTS.md",
        fixture / ASSERTION_REL,
    )
    for path in required:
        if not path.is_file():
            raise ActivationError(f"Evaluation fixture is missing required file: {path}")
    if not (fixture / ".git").exists():
        raise ActivationError(f"Evaluation fixture is not a Git worktree: {fixture}")
    if git_status(fixture):
        raise ActivationError(
            "Evaluation fixture worktree is dirty; commit/stash changes before activation"
        )

    before_fixture = snapshot_tree(fixture)
    before_home = snapshot_tree(codex_home)

    env = dict(__import__("os").environ)
    env["CODEX_HOME"] = str(codex_home)

    preview = run(
        [
            sys.executable,
            str(governance),
            "project",
            "update",
            "--project",
            str(fixture),
        ],
        cwd=framework,
        input_text="n\n",
    )
    emit_process(preview)
    require_success(preview, "governed-project update preview")

    print("\nFrozen baseline activation plan")
    print(f"- mode:              {'APPLY' if apply else 'DRY RUN'}")
    print(f"- framework version: {target}")
    print(f"- fixture:           {fixture}")
    print("- project lifecycle: governance.py project update")
    print("- fixture verify:    quick + full + git diff --check")
    print(f"- global Codex home: {codex_home}")
    print("- host lifecycle:    governance.py host install/verify")

    if not apply:
        if snapshot_tree(fixture) != before_fixture or snapshot_tree(codex_home) != before_home:
            raise ActivationError("dry-run mutated fixture or Codex home")
        print("DRY RUN ONLY. Re-run with --apply to activate the frozen baseline.")
        print("\n========================================")
        print(f"Frozen baseline activation dry-run: PASS ({target})")
        print("- fixture mutation: none")
        print("- global Codex home mutation: none")
        return 0

    fixture_backups_before = backup_names(fixture)

    try:
        updated = run(
            [
                sys.executable,
                str(governance),
                "project",
                "update",
                "--project",
                str(fixture),
                "-y",
            ],
            cwd=framework,
        )
        emit_process(updated)
        require_success(updated, "governed-project update apply")

        reconcile_fixture_assertion(fixture / ASSERTION_REL, target)
        changed_paths = verify_fixture(fixture, target)

        for path in backup_names(fixture) - fixture_backups_before:
            path.unlink(missing_ok=True)

        status_after_cleanup = git_status(fixture)
        changed_paths = [status_path(line) for line in status_after_cleanup]
        unexpected = [path for path in changed_paths if path not in ALLOWED_FIXTURE_PATHS]
        if unexpected:
            raise ActivationError(
                "Unexpected fixture changes after backup cleanup: " + ", ".join(unexpected)
            )

        status = run(
            [sys.executable, str(governance), "host", "status", "--host", "codex"],
            cwd=framework,
            env=env,
        )
        require_success(status, "Codex host status")
        status_text = status.stdout.strip().split(":", 1)[-1].strip()
        action = (
            "update"
            if status_text.startswith("INSTALLED")
            or status_text.startswith("LEGACY CODEX INSTALLATION")
            else "install"
        )
        installed = run(
            [
                sys.executable,
                str(governance),
                "host",
                action,
                "--host",
                "codex",
                "-y",
            ],
            cwd=framework,
            env=env,
        )
        emit_process(installed)
        require_success(installed, f"Codex host {action}")
        verify_codex_host(framework, codex_home)

        print("\n========================================")
        print(f"Frozen baseline activation: PASS ({target})")
        print("- fixture quick/full: PASS")
        print("- project lifecycle: unified governance.py")
        print("- global Codex host: unified governance.py")
        print(
            "- fixture diff: "
            + (", ".join(changed_paths) if changed_paths else "no tracked changes")
        )
        print("- publication/release state: unchanged")
        return 0
    except Exception as exc:
        rollback_errors: list[str] = []
        try:
            restore_tree(fixture, before_fixture)
        except Exception as rollback_exc:
            rollback_errors.append(f"fixture: {rollback_exc}")
        try:
            restore_tree(codex_home, before_home)
        except Exception as rollback_exc:
            rollback_errors.append(f"Codex home: {rollback_exc}")

        if rollback_errors:
            raise ActivationError(
                f"{exc}\nActivation rollback: FAIL: " + "; ".join(rollback_errors)
            ) from exc
        print("Activation rollback: PASS", file=sys.stderr)
        if isinstance(exc, ActivationError):
            raise
        raise ActivationError(str(exc)) from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Activate the current framework baseline in a frozen evaluation fixture and Codex home."
    )
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--codex-home", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    framework = Path(__file__).resolve().parents[1]
    try:
        return activate(framework, args.fixture, args.codex_home, apply=args.apply)
    except ActivationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
