#!/usr/bin/env python3
"""Regression coverage for run-behavioral-campaign-auto.py's evidence
mechanism (docs/adr/0003-automated-behavioral-campaign.md).

Exercises the git worktree/orphan-branch/path-confinement logic against a
throwaway scratch repository -- never the framework's own git state --
since this is the highest-risk, fully offline-testable part of the
automated campaign tooling (the actual Codex/Claude CLI invocations
require live tools and a real VM and are not exercised here). Confirms:
first-ever push creates the orphan evaluation-evidence branch; a second
run reuses/extends it; a worktree directory removed without `git worktree
remove` (simulating interrupted cleanup) self-heals via `git worktree
prune` rather than failing; and a commit that would touch anything outside
the dedicated tests/governance/evaluations/<name>/ path is refused before
it can be pushed.
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER_SOURCE = ROOT / "scripts" / "run-behavioral-campaign-auto.py"


def run(argv, cwd=None, check=True):
    proc = subprocess.run(argv, cwd=cwd, text=True, capture_output=True)
    if check and proc.returncode != 0:
        raise RuntimeError(f"{argv} failed: {proc.stdout}\n{proc.stderr}")
    return proc


def assert_true(condition, message, failures):
    if not condition:
        failures.append(message)


def load_runner_with_scratch_root(scratch_root: Path):
    spec = importlib.util.spec_from_file_location("run_behavioral_campaign_auto_test", RUNNER_SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = scratch_root
    return module


def make_scratch_repo(tmp: Path) -> tuple[Path, Path]:
    origin = tmp / "origin.git"
    work = tmp / "work"
    run(["git", "init", "--bare", str(origin)])
    run(["git", "init", str(work)])
    run(["git", "-C", str(work), "config", "user.email", "t@t.com"])
    run(["git", "-C", str(work), "config", "user.name", "t"])
    (work / "README.md").write_text("scratch\n", encoding="utf-8")
    run(["git", "-C", str(work), "add", "README.md"])
    run(["git", "-C", str(work), "commit", "-m", "init"])
    run(["git", "-C", str(work), "branch", "-M", "main"])
    run(["git", "-C", str(work), "remote", "add", "origin", str(origin)])
    run(["git", "-C", str(work), "push", "-u", "origin", "main"])
    return origin, work


def make_campaign_dir(tmp: Path, name: str, test_id: str) -> Path:
    campaign_dir = tmp / name
    (campaign_dir / "responses").mkdir(parents=True)
    (campaign_dir / "responses" / f"{test_id}.txt").write_text("response\n", encoding="utf-8")
    return campaign_dir


def test_first_push_creates_orphan_branch(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        origin, work = make_scratch_repo(tmp)
        mod = load_runner_with_scratch_root(work)
        worktree_dir = tmp / "worktree"
        mod.ensure_evidence_worktree(worktree_dir)
        assert_true(worktree_dir.is_dir(), "orphan worktree directory was not created", failures)
        branch = run(["git", "-C", str(worktree_dir), "branch", "--show-current"]).stdout.strip()
        assert_true(branch == mod.EVIDENCE_BRANCH, f"worktree is not on {mod.EVIDENCE_BRANCH}: {branch}", failures)

        mod.push_evidence(worktree_dir, make_campaign_dir(tmp, "c1", "GOV-001"), "run1")
        run(["git", "-C", str(work), "fetch", "origin", mod.EVIDENCE_BRANCH])
        log = run(["git", "-C", str(work), "log", f"origin/{mod.EVIDENCE_BRANCH}", "--oneline"]).stdout
        assert_true("run1" in log, "evidence commit for run1 is not on the pushed branch", failures)
        show = run(["git", "-C", str(work), "show", "--stat", f"origin/{mod.EVIDENCE_BRANCH}"]).stdout
        assert_true(f"{mod.EVIDENCE_ROOT}/run1" in show, "pushed commit does not touch the dedicated evidence path", failures)


def test_second_run_reuses_and_extends_branch(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        origin, work = make_scratch_repo(tmp)
        mod = load_runner_with_scratch_root(work)
        worktree_dir = tmp / "worktree"

        mod.ensure_evidence_worktree(worktree_dir)
        mod.push_evidence(worktree_dir, make_campaign_dir(tmp, "c1", "GOV-001"), "run1")
        run(["git", "-C", str(work), "worktree", "remove", "--force", str(worktree_dir)])

        mod.ensure_evidence_worktree(worktree_dir)
        mod.push_evidence(worktree_dir, make_campaign_dir(tmp, "c2", "GOV-002"), "run2")
        run(["git", "-C", str(work), "worktree", "remove", "--force", str(worktree_dir)])

        run(["git", "-C", str(work), "fetch", "origin", mod.EVIDENCE_BRANCH])
        log = run(["git", "-C", str(work), "log", f"origin/{mod.EVIDENCE_BRANCH}", "--oneline"]).stdout
        assert_true("run1" in log and "run2" in log, f"both runs' evidence commits should be on the branch: {log}", failures)


def test_stale_worktree_registry_self_heals(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        origin, work = make_scratch_repo(tmp)
        mod = load_runner_with_scratch_root(work)
        worktree_dir = tmp / "worktree"

        mod.ensure_evidence_worktree(worktree_dir)
        # Simulate an interrupted prior run: the directory is gone but git's
        # own worktree registry was never told (no `git worktree remove`).
        shutil.rmtree(worktree_dir)
        try:
            mod.ensure_evidence_worktree(worktree_dir)
        except mod.Error as exc:
            failures.append(f"a manually-removed worktree directory did not self-heal via prune: {exc}")
            return
        assert_true(worktree_dir.is_dir(), "worktree did not recreate after self-heal", failures)


def test_path_confinement_guard_refuses_stray_changes(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        origin, work = make_scratch_repo(tmp)
        mod = load_runner_with_scratch_root(work)
        worktree_dir = tmp / "worktree"

        mod.ensure_evidence_worktree(worktree_dir)
        (worktree_dir / "stray.txt").write_text("should never be committed\n", encoding="utf-8")
        run(["git", "-C", str(worktree_dir), "add", "stray.txt"])

        try:
            mod.push_evidence(worktree_dir, make_campaign_dir(tmp, "c1", "GOV-001"), "run-guard")
        except mod.Error:
            pass
        else:
            failures.append("push_evidence did not refuse a commit touching a path outside the dedicated evidence folder")
            return

        run(["git", "-C", str(work), "fetch", "origin", mod.EVIDENCE_BRANCH], check=False)
        remote_branches = run(["git", "-C", str(work), "branch", "-r"]).stdout
        assert_true(
            f"origin/{mod.EVIDENCE_BRANCH}" not in remote_branches,
            "the guarded (refused) commit must never have been pushed",
            failures,
        )


def main() -> int:
    failures: list[str] = []
    test_first_push_creates_orphan_branch(failures)
    test_second_run_reuses_and_extends_branch(failures)
    test_stale_worktree_registry_self_heals(failures)
    test_path_confinement_guard_refuses_stray_changes(failures)

    if failures:
        print("Automated behavioral campaign evidence regression: FAIL")
        for failure in failures:
            print("- " + failure)
        return 1

    print("Automated behavioral campaign evidence regression: PASS")
    print("- first-ever push creates the orphan evaluation-evidence branch, confined to its own path")
    print("- a second run reuses and extends the same branch")
    print("- a worktree directory removed without `git worktree remove` self-heals via `git worktree prune`")
    print("- a commit touching anything outside the dedicated evidence folder is refused before it can be pushed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
