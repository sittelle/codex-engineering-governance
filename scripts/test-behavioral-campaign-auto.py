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

import contextlib
import importlib.util
import io
import json
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


def test_failed_push_preserves_evidence_and_retries_cleanly(failures: list[str]) -> None:
    """A `git push` failure (simulated here by making origin briefly
    unreachable, standing in for a credential/network problem on the real
    VM) must not lose the captured campaign directory, and a retry against
    the same worktree must not fail with "already exists" against the copy
    the failed attempt already made."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        origin, work = make_scratch_repo(tmp)
        mod = load_runner_with_scratch_root(work)
        worktree_dir = tmp / "worktree"
        campaign_dir = make_campaign_dir(tmp, "c1", "GOV-001")

        mod.ensure_evidence_worktree(worktree_dir)
        unreachable_origin = tmp / "origin.git.unreachable"
        origin.rename(unreachable_origin)
        try:
            mod.push_evidence(worktree_dir, campaign_dir, "run-retry")
        except mod.Error:
            pass
        else:
            failures.append("push_evidence should have failed while origin was unreachable")
            return
        finally:
            unreachable_origin.rename(origin)

        assert_true(campaign_dir.is_dir(), "campaign_dir must survive a failed push", failures)
        assert_true((campaign_dir / "responses" / "GOV-001.txt").is_file(), "captured response must survive a failed push", failures)

        # Retry against the SAME worktree (as push_existing does): must not
        # re-copy (the failed attempt's commit already has the folder) and
        # must succeed now that origin is reachable again.
        mod.push_evidence(worktree_dir, campaign_dir, "run-retry")

        run(["git", "-C", str(work), "fetch", "origin", mod.EVIDENCE_BRANCH])
        log = run(["git", "-C", str(work), "log", f"origin/{mod.EVIDENCE_BRANCH}", "--oneline"]).stdout
        assert_true("run-retry" in log, "retried push did not land on the evidence branch", failures)
        # Exactly one evidence commit for this folder, not a duplicate from the retry.
        count = log.count("evidence run-retry")
        assert_true(count == 1, f"retry should not duplicate the evidence commit, found {count}", failures)


def test_multi_model_session_continues_without_restart(failures: list[str]) -> None:
    """After one model's scenarios are captured and pushed, the operator
    must be able to continue straight into the next model within the same
    script invocation -- no restart, and evidence-branch access verified
    once for the whole session, not once per model."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        origin, work = make_scratch_repo(tmp)
        (work / "VERSION").write_text("2.0.0\n", encoding="utf-8")
        run(["git", "-C", str(work), "add", "VERSION"])
        run(["git", "-C", str(work), "commit", "-m", "add VERSION for metadata"])
        mod = load_runner_with_scratch_root(work)

        def fake_invoke(prompt, cwd, model, effort):
            return {"status": "CAPTURED", "reason": None, "invocation": ["fake"], "response": "fake response\n"}
        mod.invoke_codex = fake_invoke
        mod.invoke_claude = fake_invoke

        kit = mod.load_campaign_kit()
        workspace = tmp / "workspace"
        workspace.mkdir()
        (workspace / "folders.json").write_text(json.dumps({"GLOBAL_KERNEL": str(tmp)}), encoding="utf-8")

        answers = iter(["1", "y"])
        mod.input = lambda prompt="": next(answers)

        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            exit_code = mod.run_automated(kit, workspace, "GOV-001")
        output = captured.getvalue()

        assert_true(exit_code == 0, f"multi-model session should exit 0, got {exit_code}", failures)
        access_checks = output.count("Verifying evidence-branch access")
        assert_true(access_checks == 1, f"evidence-branch access should be verified once per session, not {access_checks} times", failures)
        assert_true("All available models have been run this session" in output, "session should recognize both models were run without a restart", failures)

        run(["git", "-C", str(work), "fetch", "origin", mod.EVIDENCE_BRANCH])
        log = run(["git", "-C", str(work), "log", f"origin/{mod.EVIDENCE_BRANCH}", "--oneline"]).stdout
        assert_true("codex" in log, "codex model's evidence did not land on the evidence branch", failures)
        assert_true("claude" in log, "claude model's evidence did not land on the evidence branch", failures)


def test_git_remote_access_retries_through_browser_auth(failures: list[str]) -> None:
    """ensure_git_remote_access() must call the browser-authorization flow
    when the remote isn't reachable, re-check afterward, and stop retrying
    once access is confirmed -- exercised against stubs, since the real
    `gh auth login --web` flow needs a live VM and a human in a browser."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        origin, work = make_scratch_repo(tmp)
        mod = load_runner_with_scratch_root(work)

        reachable_calls = {"count": 0}
        auth_calls = {"count": 0}

        def fake_reachable(repo_root):
            reachable_calls["count"] += 1
            return reachable_calls["count"] > 1  # unreachable first, reachable after "authorizing"

        def fake_authorize(repo_root):
            auth_calls["count"] += 1

        mod.git_remote_reachable = fake_reachable
        mod.authorize_git_in_browser = fake_authorize

        mod.ensure_git_remote_access(work)
        assert_true(auth_calls["count"] == 1, f"browser authorization should run exactly once, ran {auth_calls['count']} times", failures)
        assert_true(reachable_calls["count"] == 2, f"should re-check reachability once after authorizing, checked {reachable_calls['count']} times", failures)

        # Already reachable: must not attempt browser authorization at all.
        reachable_calls["count"] = 10  # forces fake_reachable to keep returning True
        auth_calls["count"] = 0
        mod.ensure_git_remote_access(work)
        assert_true(auth_calls["count"] == 0, "already-reachable remote must not trigger browser authorization", failures)


def test_git_remote_access_gives_up_after_retry_limit(failures: list[str]) -> None:
    """A remote that never becomes reachable (e.g. authorization declined
    every time) must fail with a clear error after GIT_AUTH_RETRY_LIMIT
    attempts, not hang or loop forever, and must never call the real
    interactive retry prompt more than the bound allows."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        origin, work = make_scratch_repo(tmp)
        mod = load_runner_with_scratch_root(work)

        mod.git_remote_reachable = lambda repo_root: False
        mod.authorize_git_in_browser = lambda repo_root: None
        mod.input = lambda prompt="": "y"

        try:
            mod.ensure_git_remote_access(work)
        except mod.Error:
            pass
        else:
            failures.append("ensure_git_remote_access should raise when the remote never becomes reachable")


def test_push_existing_accepts_a_full_path_by_mistake(failures: list[str]) -> None:
    """--push-existing is documented as a bare folder name, but pathlib
    silently discards the workspace base if a full/absolute path is passed
    instead (Path("a") / "/abs/b" == Path("/abs/b")), which previously
    surfaced as a confusing "evidence folder already exists" error instead
    of doing what the operator obviously meant."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        origin, work = make_scratch_repo(tmp)
        mod = load_runner_with_scratch_root(work)
        workspace = tmp / "workspace"
        campaign_dir = workspace / "campaign-runs" / "run-pathcase"
        (campaign_dir / "responses").mkdir(parents=True)
        (campaign_dir / "responses" / "GOV-001.txt").write_text("response\n", encoding="utf-8")
        (campaign_dir / "EVALUATION-METADATA.json").write_text("{}", encoding="utf-8")

        # Simulate pasting a full path instead of the bare folder name.
        mistaken_arg = "/some/unrelated/evaluation-evidence-worktree/tests/governance/evaluations/run-pathcase"
        exit_code = mod.push_existing(workspace, mistaken_arg)
        assert_true(exit_code == 0, "push_existing should recover from a full-path argument, not fail", failures)
        assert_true(not campaign_dir.exists(), "campaign_dir should be cleaned up after a successful push", failures)

        run(["git", "-C", str(work), "fetch", "origin", mod.EVIDENCE_BRANCH])
        log = run(["git", "-C", str(work), "log", f"origin/{mod.EVIDENCE_BRANCH}", "--oneline"]).stdout
        assert_true("run-pathcase" in log, "the corrected folder name's evidence did not land on the evidence branch", failures)


def test_push_existing_recovers_from_worktree_alone(failures: list[str]) -> None:
    """If campaign_dir is already gone (older script version, or a
    since-cleaned workspace) but the evidence worktree still has a local,
    not-yet-pushed commit for that folder from a prior failed push,
    push_existing must still be able to push it -- not require the local
    source copy to exist."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        origin, work = make_scratch_repo(tmp)
        mod = load_runner_with_scratch_root(work)
        workspace = tmp / "workspace"
        workspace.mkdir()
        worktree_dir = workspace / "evaluation-evidence-worktree"

        # Build the "prior failed attempt already committed, but its local
        # source copy is gone" state directly.
        campaign_dir = tmp / "throwaway-source"
        (campaign_dir / "responses").mkdir(parents=True)
        (campaign_dir / "responses" / "GOV-001.txt").write_text("response\n", encoding="utf-8")
        mod.ensure_evidence_worktree(worktree_dir)
        target = worktree_dir / mod.EVIDENCE_ROOT / "run-worktree-only"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(campaign_dir, target)
        run(["git", "-C", str(worktree_dir), "add", "--", f"{mod.EVIDENCE_ROOT}/run-worktree-only"])
        run(["git", "-C", str(worktree_dir), "-c", "user.email=t@t.com", "-c", "user.name=t",
             "commit", "-m", mod._commit_subject("run-worktree-only")])
        shutil.rmtree(campaign_dir)  # the local source copy is gone

        exit_code = mod.push_existing(workspace, "run-worktree-only")
        assert_true(exit_code == 0, "push_existing should recover from the worktree's own commit alone", failures)

        run(["git", "-C", str(work), "fetch", "origin", mod.EVIDENCE_BRANCH])
        log = run(["git", "-C", str(work), "log", f"origin/{mod.EVIDENCE_BRANCH}", "--oneline"]).stdout
        assert_true("run-worktree-only" in log, "the worktree-only recovery evidence did not land on the evidence branch", failures)


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
    test_failed_push_preserves_evidence_and_retries_cleanly(failures)
    test_multi_model_session_continues_without_restart(failures)
    test_git_remote_access_retries_through_browser_auth(failures)
    test_git_remote_access_gives_up_after_retry_limit(failures)
    test_push_existing_accepts_a_full_path_by_mistake(failures)
    test_push_existing_recovers_from_worktree_alone(failures)
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
    print("- a failed push preserves the captured campaign directory and retries cleanly, no duplicate commit")
    print("- a multi-model session continues to the next model without restarting or re-verifying access")
    print("- unreachable git remote access retries through browser authorization until reachable")
    print("- unreachable git remote access gives up with a clear error after the retry limit")
    print("- push-existing recovers when a full path is passed instead of a bare folder name")
    print("- push-existing recovers from the evidence worktree's own commit alone, no local source copy needed")
    print("- a commit touching anything outside the dedicated evidence folder is refused before it can be pushed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
