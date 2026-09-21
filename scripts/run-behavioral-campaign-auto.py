#!/usr/bin/env python3
"""Automated behavioral campaign runner
(docs/adr/0003-automated-behavioral-campaign.md).

Offers manual (hands off to manual-behavioral-campaign.py's existing
`conduct` command, unchanged) or automated. The automated path invokes the
selected Codex/Claude CLI non-interactively per scenario, working directory
confined to that scenario's context folder, captures the plain-text
response, builds evaluation metadata, and pushes evidence to the dedicated
`evaluation-evidence` orphan branch under tests/governance/evaluations/ --
confined to that path only; the push aborts if the commit touches anything
else. Intended only for the dedicated, isolated automated-campaign test VM;
see the ADR for why raw responses are retained and pushed here specifically.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# Without this, `git ls-remote`/`fetch`/`push` fall back to git's own raw
# terminal username/password prompt whenever no credential is cached --
# exactly the prompt this script's browser-authorization flow exists to
# replace (GitHub's HTTPS remotes haven't accepted typed passwords in
# years, so that prompt could never succeed anyway). Disabling it makes
# those commands fail fast instead, so ensure_git_remote_access() gets a
# clean, quick "not reachable" signal and can run the browser flow itself,
# rather than git silently taking over the terminal first. Has no effect
# on `gh`'s own login prompts (different program, different variable) or
# on git operations once `gh auth setup-git` has installed its credential
# helper, since a working helper answers non-interactively either way.
os.environ.setdefault("GIT_TERMINAL_PROMPT", "0")

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_KIT = ROOT / "scripts" / "manual-behavioral-campaign.py"
EVIDENCE_BRANCH = "evaluation-evidence"
EVIDENCE_ROOT = "tests/governance/evaluations"
INVOCATION_TIMEOUT_SECONDS = 600
GIT_AUTH_RETRY_LIMIT = 3
# Official Debian/Ubuntu apt install for the GitHub CLI, verbatim from
# https://github.com/cli/cli/blob/trunk/docs/install_linux.md -- run through
# bash rather than re-derived, so this matches the documented commands
# exactly instead of risking a transcription error the way this session's
# earlier CLI-flag assumptions (sourced from search summaries, not the
# primary docs directly) turned out wrong against the real VM.
GH_INSTALL_SCRIPT = r"""
set -e
(type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y))
sudo mkdir -p -m 755 /etc/apt/keyrings
out=$(mktemp)
wget -nv -O "$out" https://cli.github.com/packages/githubcli-archive-keyring.gpg
sudo cp "$out" /etc/apt/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
sudo mkdir -p -m 755 /etc/apt/sources.list.d
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh -y
"""

MODELS = [
    {
        "key": "gpt-5.6-terra-high",
        "label": "GPT-5.6 Terra (High effort)",
        "host": "codex",
        "model": "gpt-5.6-terra",
        "effort": "high",
    },
    {
        "key": "claude-sonnet-5-high",
        "label": "Claude Sonnet 5 (High effort)",
        "host": "claude",
        "model": "claude-sonnet-5",
        "effort": "high",
    },
]


class Error(RuntimeError):
    pass


def load_campaign_kit():
    spec = importlib.util.spec_from_file_location("manual_behavioral_campaign", CAMPAIGN_KIT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(argv, cwd=None, check=True, timeout=None):
    proc = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=timeout)
    if check and proc.returncode != 0:
        raise Error(f"command failed ({' '.join(str(a) for a in argv)}): {proc.stdout}\n{proc.stderr}")
    return proc


def git_remote_reachable(repo_root: Path) -> bool:
    """PUSH access is what actually matters here, not read access -- a
    public/anonymously-readable repo (or one with a cached read-only
    credential) can satisfy `ls-remote`/`fetch` with no credentials at all
    while still rejecting `push` outright. That happened live: the
    original read-only version of this check passed, so the
    browser-authorization flow never even ran, and the real push later
    still hit the same terminal-prompt dead end. `--dry-run` performs the
    real authentication/permission handshake for a push without
    transferring anything or touching the remote; the target ref name is
    one that cannot already exist, so this can never be rejected for an
    unrelated non-fast-forward reason (a stale local branch, a diverged
    HEAD) and mistaken for a credential failure. This relies on GitHub
    gating the git-receive-pack info/refs request behind authentication
    for every repo, public or not, and doing that check before any pack
    data transfers -- which a dry run still triggers, since network
    transports always need that round trip to compute what a real push
    would send. Note this cannot be exercised against a local
    (filesystem-path) remote the way this script's own regression tests
    use: local transport skips that negotiation and lets a dry-run push
    succeed even against a remote configured to reject every push (a
    pre-receive hook), so this function is verified against the real
    GitHub remote only, not in scripts/test-behavioral-campaign-auto.py."""
    proc = run(
        ["git", "-C", str(repo_root), "push", "--dry-run", "origin", "HEAD:refs/heads/__evidence-push-access-check__"],
        check=False,
    )
    return proc.returncode == 0


def ensure_gh_installed() -> None:
    if shutil.which("gh"):
        return
    print("Installing GitHub CLI (gh) via apt, per https://github.com/cli/cli/blob/trunk/docs/install_linux.md ...")
    proc = subprocess.run(["bash", "-c", GH_INSTALL_SCRIPT])
    if proc.returncode != 0 or not shutil.which("gh"):
        raise Error(
            "gh install failed; install it yourself "
            "(https://github.com/cli/cli/blob/trunk/docs/install_linux.md) and rerun"
        )


def authorize_git_in_browser(repo_root: Path) -> None:
    """Directs the operator through GitHub's own browser device-code flow --
    no typed username/password, which GitHub's HTTPS git remotes have not
    accepted in years anyway (this is very likely why a typed password
    failed in the first place). Inherits this process's stdio so the
    operator sees the one-time code and URL directly, including the
    plain-URL fallback `gh` prints when the VM is headless and can't open
    a browser itself."""
    ensure_gh_installed()
    print("\nAuthorizing this machine for git access to GitHub via your browser...")
    print("If this VM has no browser, gh will print a URL and one-time code to open on another device.")
    login = subprocess.run(["gh", "auth", "login", "--hostname", "github.com", "--git-protocol", "https", "--web"], cwd=str(repo_root))
    if login.returncode != 0:
        raise Error("gh auth login did not complete successfully")
    setup = subprocess.run(["gh", "auth", "setup-git"], cwd=str(repo_root))
    if setup.returncode != 0:
        raise Error("gh auth setup-git failed to wire git's credential helper")


def ensure_git_remote_access(repo_root: Path) -> None:
    if git_remote_reachable(repo_root):
        return
    print("Cannot reach origin with the current git credentials.")
    attempts = 0
    while True:
        attempts += 1
        authorize_git_in_browser(repo_root)
        if git_remote_reachable(repo_root):
            print("Git access to origin confirmed via GitHub CLI.")
            return
        if attempts >= GIT_AUTH_RETRY_LIMIT:
            raise Error(f"still cannot reach origin after {GIT_AUTH_RETRY_LIMIT} browser-authorization attempts")
        answer = input("Still cannot reach origin. Try browser authorization again? [y/N] ").strip().lower()
        if answer != "y":
            raise Error("git authorization declined; unable to push evidence")


def choose_mode() -> str:
    while True:
        answer = input("Run this campaign (m)anually via the VS Code profile, or (a)utomated? [m/a] ").strip().lower()
        if answer in ("m", "manual"):
            return "manual"
        if answer in ("a", "auto", "automated"):
            return "automated"


def choose_model(available: list[dict]) -> dict:
    if len(available) == 1:
        print(f"Only {available[0]['label']} remains this session.")
        return available[0]
    print("Select a model:")
    for index, entry in enumerate(available, start=1):
        print(f"  {index}. {entry['label']}")
    while True:
        choice = input(f"Model [1-{len(available)}]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(available):
            return available[int(choice) - 1]
        print("Invalid selection.")


def context_directory(context: str, folders: dict[str, str]) -> Path:
    if context not in folders:
        raise Error(f"unknown execution context: {context}")
    return Path(folders[context])


def invoke_codex(prompt: str, cwd: Path, model: str, effort: str) -> dict:
    executable = shutil.which("codex")
    if not executable:
        raise Error("'codex' executable is not on PATH")
    with tempfile.TemporaryDirectory() as tmp:
        output_file = Path(tmp) / "response.txt"
        # `--ask-for-approval` is a top-level/interactive-TUI flag only; the
        # `exec` subcommand's own parser (confirmed against a real
        # `codex exec --help` on codex-cli 0.155.1) does not accept it and
        # rejects the invocation outright. `exec` is inherently
        # non-interactive -- there is no human to prompt -- so any action
        # beyond the `--sandbox workspace-write` boundary simply fails back
        # to the model rather than blocking on approval.
        argv = [
            executable, "exec",
            "--sandbox", "workspace-write",
            "--model", model,
            "-c", f'model_reasoning_effort="{effort}"',
            "--skip-git-repo-check",
            "--output-last-message", str(output_file),
            prompt,
        ]
        try:
            proc = run(argv, cwd=cwd, check=False, timeout=INVOCATION_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            return {"status": "DID_NOT_EXECUTE", "reason": "invocation timed out", "invocation": argv, "response": None}
        if proc.returncode != 0:
            return {
                "status": "DID_NOT_EXECUTE",
                "reason": f"codex exec exited {proc.returncode}: {(proc.stderr or proc.stdout).strip()[:500]}",
                "invocation": argv,
                "response": None,
            }
        response = output_file.read_text(encoding="utf-8") if output_file.is_file() else proc.stdout
        return {"status": "CAPTURED", "reason": None, "invocation": argv, "response": response}


def invoke_claude(prompt: str, cwd: Path, model: str, effort: str) -> dict:
    executable = shutil.which("claude")
    if not executable:
        raise Error("'claude' executable is not on PATH")
    argv = [
        executable, "-p",
        "--restricted",
        "--model", model,
        "--effort", effort,
        "--output-format", "text",
        prompt,
    ]
    try:
        proc = run(argv, cwd=cwd, check=False, timeout=INVOCATION_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return {"status": "DID_NOT_EXECUTE", "reason": "invocation timed out", "invocation": argv, "response": None}
    if proc.returncode != 0:
        return {
            "status": "DID_NOT_EXECUTE",
            "reason": f"claude -p exited {proc.returncode}: {(proc.stderr or proc.stdout).strip()[:500]}",
            "invocation": argv,
            "response": None,
        }
    return {"status": "CAPTURED", "reason": None, "invocation": argv, "response": proc.stdout}


def run_scenario(kit, row: dict, model_entry: dict, folders: dict[str, str], campaign_dir: Path) -> dict:
    cwd = context_directory(row["context"], folders)
    if model_entry["host"] == "codex":
        result = invoke_codex(row["prompt"], cwd, model_entry["model"], model_entry["effort"])
    else:
        result = invoke_claude(row["prompt"], cwd, model_entry["model"], model_entry["effort"])
    (campaign_dir / "prompts" / f"{row['test_id']}.txt").write_text(row["prompt"] + "\n", encoding="utf-8", newline="\n")
    response_path = campaign_dir / "responses" / f"{row['test_id']}.txt"
    response_path.write_text(result["response"] or "", encoding="utf-8", newline="\n")
    return {
        "test_id": row["test_id"],
        "context": row["context"],
        "scenario_sha256": row["scenario_sha256"],
        "prompt_sha256": row["prompt_sha256"],
        "status": result["status"],
        "reason": result["reason"],
        "response_file": f"responses/{row['test_id']}.txt",
        "invocation": [a if a != row["prompt"] else "<PROMPT>" for a in result["invocation"]],
    }


def build_metadata(kit, model_entry: dict, records: list[dict], source: dict) -> dict:
    executable = shutil.which(model_entry["host"])
    version_probe = kit.tool_probe([executable, "--version"]) if executable else {"state": "NOT_FOUND"}
    return {
        "schema_version": "1",
        "kind": "AUTOMATED_BEHAVIORAL_EVALUATION_METADATA",
        "framework_version": (ROOT / "VERSION").read_text(encoding="utf-8-sig").strip(),
        "evaluation_protocol": kit.EVALUATION_PROTOCOL,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign_source_commit": source.get("git_commit"),
        "campaign_source_binding": source.get("binding"),
        "agent_session": {
            "host": model_entry["host"],
            "requested_model": model_entry["model"],
            "runtime_settings": {"effort": model_entry["effort"]},
        },
        "cli": {"executable": executable, "version_probe": version_probe},
        "tool_access_mode": "workspace-write, sandboxed to the scenario's context directory"
        if model_entry["host"] == "codex"
        else "--restricted, file tools scoped to the working directory only",
        "environment": {
            "operating_system": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
            }
        },
        "results": records,
        "privacy": {"local_paths": "NOT_RECORDED", "credentials": "NOT_COLLECTED", "chat_contents": "NOT_APPLICABLE (single-turn, plain text captured verbatim)"},
    }


def ensure_evidence_worktree(worktree_dir: Path) -> None:
    """Create (or reuse) a separate git worktree checked out to the orphan
    evaluation-evidence branch, so the framework's own checkout -- whose
    exact commit this campaign is testing -- is never touched."""
    if worktree_dir.exists():
        return
    # If a prior run's cleanup was interrupted (crash, kill) the directory
    # can be gone while git's own worktree registry still thinks it exists,
    # which makes `worktree add` refuse the branch. Prune first so a
    # missing directory never blocks recreating it.
    run(["git", "-C", str(ROOT), "worktree", "prune"], check=False)
    fetch = run(["git", "-C", str(ROOT), "fetch", "origin", EVIDENCE_BRANCH], check=False)
    if fetch.returncode == 0:
        run(["git", "-C", str(ROOT), "worktree", "add", "-B", EVIDENCE_BRANCH, str(worktree_dir), f"origin/{EVIDENCE_BRANCH}"])
        return
    # Remote branch does not exist yet. A prior attempt may have already
    # created the local orphan branch and been interrupted before its first
    # push (crash, kill) -- `checkout --orphan` would then fail because the
    # branch already exists. Reuse that local branch instead of re-creating it.
    local_branch_exists = run(["git", "-C", str(ROOT), "rev-parse", "--verify", "--quiet", EVIDENCE_BRANCH], check=False).returncode == 0
    if local_branch_exists:
        run(["git", "-C", str(ROOT), "worktree", "add", str(worktree_dir), EVIDENCE_BRANCH])
        return
    run(["git", "-C", str(ROOT), "worktree", "add", "--detach", str(worktree_dir)])
    run(["git", "-C", str(worktree_dir), "checkout", "--orphan", EVIDENCE_BRANCH])
    run(["git", "-C", str(worktree_dir), "rm", "-rf", "--quiet", "."], check=False)
    readme = worktree_dir / "README.md"
    readme.write_text(
        "# Evaluation evidence\n\n"
        "Automated behavioral campaign evidence only, per "
        "docs/adr/0003-automated-behavioral-campaign.md. This branch has no "
        "shared history with the framework's development branches by design; "
        "each campaign folder's metadata records the exact source commit it "
        "tested. Every commit here touches only tests/governance/evaluations/.\n",
        encoding="utf-8", newline="\n",
    )
    run(["git", "-C", str(worktree_dir), "add", "README.md"])
    run(["git", "-C", str(worktree_dir), "-c", "user.email=automated-campaign@localhost", "-c", "user.name=Automated Behavioral Campaign",
         "commit", "-m", "chore: initialize evaluation-evidence branch"])


def _commit_subject(folder_name: str) -> str:
    return f"test: automated behavioral campaign evidence {folder_name}"


def _already_committed_locally(worktree_dir: Path, folder_name: str) -> bool:
    """True when this worktree already carries a local, not-yet-pushed
    commit for folder_name from a prior attempt whose `git push` itself
    failed (wrong credentials, network blip) -- so a retry should just
    re-push, not re-copy/re-commit (which would fail with "already
    exists" against the copy this same worktree already made). False for
    a genuine folder_name collision against history already fetched from
    origin, where HEAD lands exactly on origin's tip with nothing of ours
    on top yet."""
    head = run(["git", "-C", str(worktree_dir), "rev-parse", "HEAD"], check=False)
    if head.returncode != 0:
        return False
    origin_ref = run(["git", "-C", str(worktree_dir), "rev-parse", "--verify", "--quiet", f"origin/{EVIDENCE_BRANCH}"], check=False)
    if origin_ref.returncode == 0 and head.stdout.strip() == origin_ref.stdout.strip():
        return False
    subject = run(["git", "-C", str(worktree_dir), "log", "-1", "--format=%s"], check=False).stdout.strip()
    return subject == _commit_subject(folder_name)


def push_evidence(worktree_dir: Path, campaign_dir: Path, folder_name: str) -> None:
    target = worktree_dir / EVIDENCE_ROOT / folder_name
    if not _already_committed_locally(worktree_dir, folder_name):
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise Error(f"evidence folder already exists on the evidence branch: {target}")
        shutil.copytree(campaign_dir, target)
        run(["git", "-C", str(worktree_dir), "add", "--", f"{EVIDENCE_ROOT}/{folder_name}"])

        staged = run(["git", "-C", str(worktree_dir), "diff", "--cached", "--name-only"]).stdout.splitlines()
        outside = [path for path in staged if not path.startswith(f"{EVIDENCE_ROOT}/{folder_name}/")]
        if outside:
            run(["git", "-C", str(worktree_dir), "reset"], check=False)
            raise Error(f"refusing to commit: staged changes outside the dedicated evidence folder: {outside}")

        run(["git", "-C", str(worktree_dir), "-c", "user.email=automated-campaign@localhost", "-c", "user.name=Automated Behavioral Campaign",
             "commit", "-m", _commit_subject(folder_name)])

    push = run(["git", "-C", str(worktree_dir), "push", "origin", EVIDENCE_BRANCH], check=False)
    if push.returncode != 0:
        # Could be a rejected non-fast-forward (someone else pushed to the
        # evidence branch meanwhile) or a credential/network failure --
        # `check=False` here deliberately, so an auth failure on this fetch
        # surfaces as the same clear message below instead of a raw
        # "command failed" dump from run()'s default check=True.
        fetch = run(["git", "-C", str(worktree_dir), "fetch", "origin", EVIDENCE_BRANCH], check=False)
        if fetch.returncode == 0:
            rebase = run(["git", "-C", str(worktree_dir), "rebase", f"origin/{EVIDENCE_BRANCH}"], check=False)
            if rebase.returncode == 0:
                retry = run(["git", "-C", str(worktree_dir), "push", "origin", EVIDENCE_BRANCH], check=False)
                if retry.returncode == 0:
                    print(f"Pushed evidence: {EVIDENCE_ROOT}/{folder_name} -> origin/{EVIDENCE_BRANCH}")
                    return
                raise Error(f"evidence branch push failed after retry: {retry.stderr.strip()}")
            raise Error(f"evidence branch push rejected and could not be reconciled automatically: {push.stderr.strip()}")
        raise Error(f"evidence branch push failed (could not fetch origin either -- check git credentials/network): {push.stderr.strip()}")
    print(f"Pushed evidence: {EVIDENCE_ROOT}/{folder_name} -> origin/{EVIDENCE_BRANCH}")


def _push_retry_hint(workspace: Path, campaign_dir: Path, folder_name: str) -> str:
    return (
        f"captured responses are preserved at {campaign_dir} (not deleted); "
        f"fix the git credential/network problem, then retry with: "
        f"python3 {Path(__file__).name} --workspace {workspace} --push-existing {folder_name}"
    )


def push_existing(workspace: Path, folder_name: str) -> int:
    """Push an already-captured campaign directory without re-running any
    scenarios (no AI calls). For recovering from a push failure -- wrong git
    credentials, network blip, non-fast-forward conflict -- without
    re-paying for the whole campaign."""
    if "/" in folder_name or "\\" in folder_name:
        # `workspace / "campaign-runs" / folder_name` silently discards
        # `workspace` when folder_name is itself an absolute path --
        # pathlib's Path.__truediv__ behavior, not a bug in the join call
        # -- so a pasted full path (e.g. copied from an earlier error
        # message showing the evidence worktree's own internal path) would
        # otherwise resolve to some unrelated directory instead of failing
        # loudly. Correct it to the basename rather than trying every path
        # that could reach that directory.
        corrected = Path(folder_name).name
        print(f"--push-existing expects a bare folder name (see `ls {workspace / 'campaign-runs'}`), not a path; using '{corrected}'.")
        folder_name = corrected
    campaign_dir = workspace / "campaign-runs" / folder_name
    worktree_dir = workspace / "evaluation-evidence-worktree"
    have_local_copy = (campaign_dir / "EVALUATION-METADATA.json").is_file()
    # A prior attempt's failed push still leaves a local, not-yet-pushed
    # commit sitting in the evidence worktree even after campaign_dir is
    # gone (older script version, or the worktree survived a since-cleaned
    # workspace) -- push_evidence()'s own idempotency check already
    # recognizes that commit and skips needing campaign_dir to exist at
    # all, so accept that case here too instead of failing before even
    # trying.
    have_worktree_commit = worktree_dir.is_dir() and _already_committed_locally(worktree_dir, folder_name)
    if not have_local_copy and not have_worktree_commit:
        raise Error(
            f"{campaign_dir} does not look like a completed campaign run (no EVALUATION-METADATA.json), "
            f"and the evidence worktree at {worktree_dir} has no matching not-yet-pushed commit either"
        )
    try:
        ensure_git_remote_access(ROOT)
        ensure_evidence_worktree(worktree_dir)
        push_evidence(worktree_dir, campaign_dir, folder_name)
    except Error as exc:
        raise Error(f"{exc} -- {_push_retry_hint(workspace, campaign_dir, folder_name)}") from exc
    run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(worktree_dir)], check=False)
    if campaign_dir.is_dir():
        shutil.rmtree(campaign_dir)
    print(f"Pushed previously-captured campaign: {folder_name}")
    return 0


def run_one_model(kit, model_entry: dict, rows: list[dict], folders: dict, source, workspace: Path, worktree_dir: Path) -> bool:
    """Run every selected scenario against one model and push its evidence.
    Returns True iff the push succeeded (evidence safely recorded) -- a
    push failure does not raise, so a multi-model session can continue to
    the next model instead of aborting the whole session; the failed
    model's captured responses are preserved and the retry command is
    printed, same as a single-model run."""
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    folder_name = f"{stamp}-{model_entry['host']}-{model_entry['key']}"
    # Deliberately NOT a tempfile.TemporaryDirectory(): captured responses
    # are real AI-call output and must survive a failed push (git
    # credential issue, network blip, non-fast-forward conflict) so the
    # operator can retry the push with --push-existing instead of
    # re-running -- and re-paying for -- the whole campaign.
    campaign_dir = workspace / "campaign-runs" / folder_name
    campaign_dir.mkdir(parents=True)
    (campaign_dir / "responses").mkdir()
    (campaign_dir / "prompts").mkdir()

    records = []
    for row in rows:
        print(f"[{row['test_id']}] ({row['context']}) invoking {model_entry['host']}...")
        record = run_scenario(kit, row, model_entry, folders, campaign_dir)
        records.append(record)
        print(f"  -> {record['status']}" + (f" ({record['reason']})" if record["reason"] else ""))

    metadata = build_metadata(kit, model_entry, records, source)
    (campaign_dir / "EVALUATION-METADATA.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n"
    )

    try:
        push_evidence(worktree_dir, campaign_dir, folder_name)
    except Error as exc:
        print(f"FAILED to push {model_entry['label']}: {exc}")
        print(_push_retry_hint(workspace, campaign_dir, folder_name))
        return False
    shutil.rmtree(campaign_dir)

    failures = [r for r in records if r["status"] != "CAPTURED"]
    if failures:
        print(f"\n{len(failures)} scenario(s) did not execute cleanly for {model_entry['label']}:")
        for record in failures:
            print(f"  - {record['test_id']}: {record['reason']}")
    print(f"{model_entry['label']} complete: {len(records)} scenarios, {len(records) - len(failures)} captured.")
    return True


def run_automated(kit, workspace: Path, selection: str) -> int:
    folders_path = workspace / "folders.json"
    if not folders_path.is_file():
        raise Error(f"{folders_path} not found; run bootstrap-test-vm.py first")
    folders = json.loads(folders_path.read_text(encoding="utf-8"))

    # Verify evidence-branch fetch/push access *before* spending a single AI
    # call, and keep the worktree open for the whole session -- across
    # every model run, not just one -- instead of tearing it down and
    # re-creating it per model (one credential prompt total, not several).
    # Finding an access problem only after running the whole campaign
    # (previously: only at push time, with captured responses sitting in
    # an auto-deleted tempdir) meant a mistyped git password destroyed
    # every response the campaign had just paid for in AI calls and time.
    worktree_dir = workspace / "evaluation-evidence-worktree"
    print("Verifying evidence-branch access (fetch/push credentials)...")
    ensure_git_remote_access(ROOT)
    ensure_evidence_worktree(worktree_dir)
    print("Evidence-branch access OK.")

    rows = kit.selected_rows(kit.scenario_rows(), selection)
    source = kit.source_state()

    # One model at a time, but without leaving the session: once a model's
    # scenarios finish (successfully pushed, or failed-and-preserved), ask
    # whether to pick up right here with another model, rather than making
    # the operator exit and re-invoke the whole script -- re-verifying
    # access and re-answering the mode prompt -- just to run Codex after
    # Claude already succeeded.
    ran: list[dict] = []
    overall_ok = True
    while True:
        remaining = [m for m in MODELS if m not in ran]
        model_entry = choose_model(remaining)
        overall_ok = run_one_model(kit, model_entry, rows, folders, source, workspace, worktree_dir) and overall_ok
        ran.append(model_entry)
        remaining = [m for m in MODELS if m not in ran]
        if not remaining:
            print("\nAll available models have been run this session.")
            break
        answer = input(f"\nRun another model now ({', '.join(m['label'] for m in remaining)})? [y/N] ").strip().lower()
        if answer != "y":
            break

    run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(worktree_dir)], check=False)
    print(f"\nAutomated campaign session complete: {len(ran)} model(s) run.")
    return 0 if overall_ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path, help="the workspace bootstrap-test-vm.py created (contains folders.json and the three context directories)")
    parser.add_argument("--select", default="all", help="all, or a GOV-NNN[-GOV-MMM] range/list, same syntax as the manual conductor")
    parser.add_argument("--manual-args", nargs=argparse.REMAINDER, help="arguments forwarded to manual-behavioral-campaign.py conduct when manual mode is chosen")
    parser.add_argument("--push-existing", metavar="FOLDER_NAME", help="skip mode selection and scenario invocation; push a previously-captured campaign-runs/<FOLDER_NAME> that failed to push earlier (e.g. after a git credential problem), with no AI calls")
    args = parser.parse_args()

    try:
        if args.push_existing:
            return push_existing(args.workspace, args.push_existing)
        kit = load_campaign_kit()
        mode = choose_mode()
        if mode == "manual":
            print("Manual mode selected: hand off to `python3 scripts/manual-behavioral-campaign.py conduct ...` directly.")
            print("This script does not itself drive the manual VS Code conductor; see docs/evaluation-vm-bootstrap.md.")
            return 0
        return run_automated(kit, args.workspace, args.select)
    except Error as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
