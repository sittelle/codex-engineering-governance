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


def test_interactive_selection_retries_on_invalid_input(failures: list[str]) -> None:
    """choose_selection() with no --select must prompt interactively, accept
    the manual conductor's own selection syntax, and retry rather than crash
    the whole session on a typo."""
    mod = load_runner_with_scratch_root(ROOT)  # ROOT here is irrelevant; scenario_rows() reads the real framework
    kit = mod.load_campaign_kit()

    answers = iter(["GOV-999", "GOV-001,GOV-003"])
    prompts_seen = []

    def fake_input(prompt=""):
        prompts_seen.append(prompt)
        return next(answers)

    mod.input = fake_input
    rows = mod.choose_selection(kit, None)
    assert_true(len(prompts_seen) == 2, f"an invalid selection should re-prompt, saw {len(prompts_seen)} prompt(s)", failures)
    assert_true(sorted(r["test_id"] for r in rows) == ["GOV-001", "GOV-003"], f"selection should resolve to exactly GOV-001 and GOV-003, got {[r['test_id'] for r in rows]}", failures)

    # A blank answer (just Enter) means "all".
    mod.input = lambda prompt="": ""
    all_rows = mod.choose_selection(kit, None)
    assert_true(len(all_rows) == len(kit.scenario_rows()), "a blank interactive answer should select all scenarios", failures)

    # --select on the command line skips the prompt entirely.
    mod.input = lambda prompt="": (_ for _ in ()).throw(AssertionError("should not prompt when --select is given"))
    explicit_rows = mod.choose_selection(kit, "GOV-002-GOV-004")
    assert_true(sorted(r["test_id"] for r in explicit_rows) == ["GOV-002", "GOV-003", "GOV-004"], f"explicit --select should resolve the same range syntax, got {[r['test_id'] for r in explicit_rows]}", failures)


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
        mod.verify_instruction_loading = lambda model_entry, contexts, folders: []

        kit = mod.load_campaign_kit()
        workspace = tmp / "workspace"
        workspace.mkdir()
        (workspace / "folders.json").write_text(json.dumps({"GOVERNED_REPOSITORY": str(tmp), "UNGOVERNED": str(tmp)}), encoding="utf-8")

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


KERNEL_LINE = 'Vague answers such as "whatever" or "normal" are NOT resolution when material.'
END_LINE = "Add instructions specific to this repository here. They remain authoritative subject to the normal governance hierarchy."
ROUTED_LINE = "Do not act on an assumed root cause when a reversible containment step can reduce harm first."
LOADED_ANSWER = f"1. {KERNEL_LINE}\n2. {END_LINE}\n{ROUTED_LINE}\n"


def _probe_fixture(tmp: Path, mod) -> tuple[dict, dict]:
    """A governed project with the managed block first and the project section
    last (ADR 0005), an ungoverned directory, and a GOVERNANCE_ROOT locator."""
    governed = tmp / "governed-project"
    governed.mkdir()
    (governed / "AGENTS.md").write_text(f"{KERNEL_LINE}\n\n{END_LINE}\n", encoding="utf-8")
    template = tmp / "templates" / "repository" / "AGENTS.md"
    template.parent.mkdir(parents=True)
    template.write_text(f"{KERNEL_LINE}\n", encoding="utf-8")
    ungoverned = tmp / "ungoverned"
    ungoverned.mkdir()
    governance_root = tmp / "governance-root"
    routed = governance_root / mod.ROUTING_PROBE_FILE
    routed.parent.mkdir(parents=True)
    routed.write_text(ROUTED_LINE + "\n", encoding="utf-8")
    locator = tmp / "claude-config" / "GOVERNANCE_ROOT"
    locator.parent.mkdir()
    locator.write_text(str(governance_root), encoding="utf-8")
    mod.locator_path = lambda host: locator
    folders = {"GOVERNED_REPOSITORY": str(governed), "UNGOVERNED": str(ungoverned)}
    entry = {"label": "Claude test", "host": "claude", "model": "m", "effort": "high", "key": "k"}
    return folders, entry


def _answer(response: str) -> dict:
    return {"status": "CAPTURED", "reason": None, "invocation": ["fake"], "response": response}


def test_instruction_probe_blocks_campaign_when_not_loaded(failures: list[str]) -> None:
    """A model that does not have the governance instructions in context
    (as with the former `--restricted` invocation) must stop the model's run
    before any scenario executes or any evidence is written or pushed."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        mod = load_runner_with_scratch_root(tmp)
        folders, entry = _probe_fixture(tmp, mod)
        scenario_calls = []
        probe_calls = []

        def fake_invoke(prompt, cwd, model, effort, extra_disallowed=()):
            if "Automated configuration check" in prompt:
                probe_calls.append(prompt)
            else:
                scenario_calls.append(prompt)
            return _answer("1. ABSENT\n2. ABSENT\n")
        mod.invoke_claude = fake_invoke

        workspace = tmp / "workspace"
        workspace.mkdir()
        rows = [{"test_id": "GOV-001", "context": "GOVERNED_REPOSITORY", "prompt": "p"}]
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            ok = mod.run_one_model(None, entry, rows, folders, {}, workspace, tmp / "unused-worktree")
        assert_true(ok is False, "run_one_model must report failure when the instructions are not loaded", failures)
        assert_true(len(probe_calls) == mod.PROBE_ATTEMPTS, f"a consistently failing check should be attempted {mod.PROBE_ATTEMPTS} times, was {len(probe_calls)}", failures)
        assert_true(not scenario_calls, "no scenario may be invoked after a failed instruction-loading check", failures)
        assert_true(not (workspace / "campaign-runs").exists(), "no campaign evidence may be written after a failed check", failures)
        assert_true("instruction-loading check FAILED" in captured.getvalue(), "the failure must be reported to the operator", failures)


def test_instruction_probe_passes_when_instructions_are_quoted(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        mod = load_runner_with_scratch_root(tmp)
        folders, entry = _probe_fixture(tmp, mod)
        calls = []

        def fake_invoke(prompt, cwd, model, effort, extra_disallowed=()):
            calls.append((prompt, cwd, extra_disallowed))
            if Path(cwd) == Path(folders["UNGOVERNED"]):
                return _answer("1. none\n2. ABSENT\n")
            if len(calls) == 1:  # a one-off misquote must be retried, not abort the run
                return _answer("1. ABSENT\n2. ABSENT\n")
            return _answer(LOADED_ANSWER.replace('"normal"', '**"normal"**'))
        mod.invoke_claude = fake_invoke

        with contextlib.redirect_stdout(io.StringIO()):
            results = mod.verify_instruction_loading(entry, {"GOVERNED_REPOSITORY"}, folders)
        assert_true(
            [r["context"] for r in results] == ["GOVERNED_REPOSITORY", "UNGOVERNED", "GOVERNANCE_ROOT_ROUTING"]
            and all(r["status"] == "PASS" for r in results),
            f"loading, ungoverned and routing checks should all PASS, got {results}",
            failures,
        )
        assert_true(
            len(calls) == 5,
            f"expected managed-block check (retried once), end-of-file check, ungoverned check and routing check (5 calls), got {len(calls)}",
            failures,
        )
        loading_denied = set(calls[1][2]) | set(calls[2][2]) | set(calls[3][2])
        assert_true(
            {"Read", "Glob", "Grep"} <= loading_denied,
            "the Claude loading checks must deny file tools so they cannot pass by reading the files instead of having them loaded",
            failures,
        )
        assert_true("Read" not in set(calls[4][2]), "the routing check must leave the Read tool available", failures)


def test_ungoverned_probe_blocks_campaign_on_governance_leak(failures: list[str]) -> None:
    """ADR 0005: governance text reaching a session outside any governed
    project (e.g. a host-level kernel still installed) must stop the run."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        mod = load_runner_with_scratch_root(tmp)
        folders, entry = _probe_fixture(tmp, mod)
        mod.invoke_claude = lambda prompt, cwd, model, effort, extra_disallowed=(): _answer(LOADED_ANSWER)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mod.verify_instruction_loading(entry, {"GOVERNED_REPOSITORY"}, folders)
        except mod.Error as exc:
            assert_true("UNGOVERNED" in str(exc), f"the failure should name the ungoverned check: {exc}", failures)
        else:
            failures.append("governance text in an ungoverned session must fail the instruction-loading check")


def test_routing_probe_blocks_campaign_when_locator_unreadable(failures: list[str]) -> None:
    """The instructions can be loaded while the GOVERNANCE_ROOT locator read is
    denied (the installer gap found in the first governed campaign); the run
    must stop before any scenario in that case too."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        mod = load_runner_with_scratch_root(tmp)
        folders, entry = _probe_fixture(tmp, mod)

        def fake_invoke(prompt, cwd, model, effort, extra_disallowed=()):
            if "file-read tool" in prompt:
                return _answer("BLOCKED: GOVERNANCE_ROOT read denied\n")
            if Path(cwd) == Path(folders["UNGOVERNED"]):
                return _answer("1. none\n2. ABSENT\n")
            return _answer(LOADED_ANSWER)
        mod.invoke_claude = fake_invoke

        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mod.verify_instruction_loading(entry, {"GOVERNED_REPOSITORY"}, folders)
        except mod.Error as exc:
            assert_true("GOVERNANCE_ROOT routing" in str(exc), f"the failure should name the routing check: {exc}", failures)
        else:
            failures.append("an unreadable GOVERNANCE_ROOT locator must fail the instruction-loading check")


def _run_session_with(tmp: Path, fake_invoke, answers: list[str], selection: str):
    """One automated Codex session against a scratch evidence repo; returns
    (runner module, console output, pushed EVALUATION-METADATA or None)."""
    origin, work = make_scratch_repo(tmp)
    (work / "VERSION").write_text("2.0.0\n", encoding="utf-8")
    run(["git", "-C", str(work), "add", "VERSION"])
    run(["git", "-C", str(work), "commit", "-m", "add VERSION for metadata"])
    mod = load_runner_with_scratch_root(work)
    mod.invoke_codex = fake_invoke
    mod.verify_instruction_loading = lambda model_entry, contexts, folders: []
    kit = mod.load_campaign_kit()
    workspace = tmp / "workspace"
    workspace.mkdir()
    (workspace / "folders.json").write_text(json.dumps({"GOVERNED_REPOSITORY": str(tmp), "UNGOVERNED": str(tmp)}), encoding="utf-8")
    replies = iter(answers)
    mod.input = lambda prompt="": next(replies)
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        mod.run_automated(kit, workspace, selection)
    run(["git", "-C", str(work), "fetch", "origin", mod.EVIDENCE_BRANCH])
    listing = run(["git", "-C", str(work), "ls-tree", "--name-only", f"origin/{mod.EVIDENCE_BRANCH}", f"{mod.EVIDENCE_ROOT}/"]).stdout.split()
    metadata = None
    if listing:
        shown = run(["git", "-C", str(work), "show", f"origin/{mod.EVIDENCE_BRANCH}:{listing[0]}/EVALUATION-METADATA.json"]).stdout
        metadata = json.loads(shown)
    return mod, captured.getvalue(), metadata


def test_usage_limit_pauses_and_resumes_in_the_same_run(failures: list[str]) -> None:
    """A token/usage limit must pause the run; after the operator confirms,
    the aborted scenario and all following ones run in the same campaign, so
    the whole test never has to be repeated."""
    with tempfile.TemporaryDirectory() as tmp:
        calls = []

        def fake_invoke(prompt, cwd, model, effort, extra_disallowed=()):
            calls.append(prompt)
            if len(calls) == 3:
                return {"status": "DID_NOT_EXECUTE", "reason": "codex exec exited 1: You've hit your usage limit.", "invocation": ["fake"], "response": None}
            return _answer("fake response\n")

        mod, output, metadata = _run_session_with(Path(tmp), fake_invoke, ["1", "", "n"], "GOV-004-GOV-011")
        assert_true("PAUSED" in output and "usage limit" in output, "a usage limit must pause the run and show the error", failures)
        assert_true(len(calls) == 9, f"expected 8 scenarios plus 1 retry (9 calls), got {len(calls)}", failures)
        results = (metadata or {}).get("results", [])
        assert_true(
            [r["test_id"] for r in results] == [f"GOV-{n:03d}" for n in range(4, 12)]
            and all(r["status"] == "CAPTURED" for r in results),
            f"the resumed run must yield one complete campaign with one record per scenario, got {[(r['test_id'], r['status']) for r in results]}",
            failures,
        )


def test_repeated_failures_pause_and_can_stop(failures: list[str]) -> None:
    """Unrecognized repeated failures also pause the run; choosing 'stop'
    pushes what was captured and names the scenarios still to run."""
    with tempfile.TemporaryDirectory() as tmp:
        calls = []

        def fake_invoke(prompt, cwd, model, effort, extra_disallowed=()):
            calls.append(prompt)
            if len(calls) <= 2:
                return _answer("fake response\n")
            return {"status": "DID_NOT_EXECUTE", "reason": "codex exec exited 1: unexpected failure", "invocation": ["fake"], "response": None}

        mod, output, metadata = _run_session_with(Path(tmp), fake_invoke, ["1", "stop", "n"], "GOV-004-GOV-011")
        limit = mod.CONSECUTIVE_FAILURE_LIMIT
        assert_true(len(calls) == 2 + limit, f"expected 2 captured plus {limit} failed calls before the pause, got {len(calls)}", failures)
        assert_true("PAUSED" in output, "repeated failures must pause the run", failures)
        assert_true("--select GOV-006,GOV-007,GOV-008,GOV-009,GOV-010,GOV-011" in output,
                    f"the rerun hint must start at the first failed scenario: {output[-400:]}", failures)
        assert_true(metadata is not None and sum(r["status"] == "CAPTURED" for r in metadata["results"]) == 2,
                    "the scenarios captured before stopping must still be pushed", failures)


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


def test_push_existing_handles_leftovers_all_and_collisions(failures: list[str]) -> None:
    """A local copy of an already-pushed campaign is a leftover, not a git
    problem: it is removed without a new commit. `all` pushes what is missing
    and cleans the rest. A different campaign under the same name is refused
    without a misleading credentials hint."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        origin, work = make_scratch_repo(tmp)
        mod = load_runner_with_scratch_root(work)
        mod.ensure_git_remote_access = lambda repo_root: None
        workspace = tmp / "workspace"
        runs = workspace / "campaign-runs"
        runs.mkdir(parents=True)

        def local_campaign(name: str, text: str) -> Path:
            d = runs / name
            (d / "responses").mkdir(parents=True)
            (d / "responses" / "GOV-001.txt").write_text(text, encoding="utf-8")
            (d / "EVALUATION-METADATA.json").write_text("{}", encoding="utf-8")
            return d

        old = local_campaign("old-run", "response\n")
        mod.ensure_evidence_worktree(workspace / "evaluation-evidence-worktree")
        mod.push_evidence(workspace / "evaluation-evidence-worktree", old, "old-run")
        run(["git", "-C", str(work), "worktree", "remove", "--force", str(workspace / "evaluation-evidence-worktree")])
        commits_before = run(["git", "-C", str(work), "rev-list", "--count", f"origin/{mod.EVIDENCE_BRANCH}"]).stdout.strip()

        local_campaign("new-run", "response\n")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = mod.push_existing(workspace, "all")
        assert_true(code == 0, f"push-existing all should succeed: {out.getvalue()[-300:]}", failures)
        assert_true(not old.exists() and not (runs / "new-run").exists(), "all handled folders must be removed locally", failures)
        assert_true("leftover" in out.getvalue(), "a leftover must be reported as such, not as a push", failures)
        run(["git", "-C", str(work), "fetch", "origin", mod.EVIDENCE_BRANCH])
        commits_after = run(["git", "-C", str(work), "rev-list", "--count", f"origin/{mod.EVIDENCE_BRANCH}"]).stdout.strip()
        assert_true(int(commits_after) == int(commits_before) + 1, "only the missing campaign may add a commit", failures)

        clash = local_campaign("old-run", "a different response\n")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mod.push_existing(workspace, "old-run")
        except mod.EvidenceCollision as exc:
            assert_true("credential" not in str(exc), f"a name collision must not suggest a git credential problem: {exc}", failures)
            assert_true(clash.exists(), "the local copy must be preserved on a collision", failures)
        else:
            failures.append("a different campaign under an existing name must be refused")


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
    test_interactive_selection_retries_on_invalid_input(failures)
    test_instruction_probe_blocks_campaign_when_not_loaded(failures)
    test_instruction_probe_passes_when_instructions_are_quoted(failures)
    test_ungoverned_probe_blocks_campaign_on_governance_leak(failures)
    test_routing_probe_blocks_campaign_when_locator_unreadable(failures)
    test_usage_limit_pauses_and_resumes_in_the_same_run(failures)
    test_repeated_failures_pause_and_can_stop(failures)
    test_git_remote_access_retries_through_browser_auth(failures)
    test_git_remote_access_gives_up_after_retry_limit(failures)
    test_push_existing_accepts_a_full_path_by_mistake(failures)
    test_push_existing_recovers_from_worktree_alone(failures)
    test_push_existing_handles_leftovers_all_and_collisions(failures)
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
    print("- interactive scenario selection retries on invalid input and --select skips the prompt")
    print("- a model without the governance instructions in context is stopped before any scenario runs or evidence is written")
    print("- the instruction-loading check retries a one-off misquote, passes on a correct quote, and denies the Claude probe its file tools")
    print("- governance text reaching an ungoverned session stops the run (ADR 0005)")
    print("- an unreadable GOVERNANCE_ROOT locator stops the run even when the instructions themselves are loaded")
    print("- a usage/token limit pauses the run; after confirmation the aborted and all following scenarios run in the same campaign")
    print("- repeated unrecognized failures pause the run; stopping keeps the captured evidence and names the scenarios to rerun")
    print("- unreachable git remote access retries through browser authorization until reachable")
    print("- unreachable git remote access gives up with a clear error after the retry limit")
    print("- push-existing recovers when a full path is passed instead of a bare folder name")
    print("- push-existing recovers from the evidence worktree's own commit alone, no local source copy needed")
    print("- push-existing removes leftovers of earlier pushes, `all` pushes what is missing, and a name collision is refused without a credentials hint")
    print("- a commit touching anything outside the dedicated evidence folder is refused before it can be pushed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
