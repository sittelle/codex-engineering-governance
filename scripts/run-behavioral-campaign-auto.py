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
import platform
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_KIT = ROOT / "scripts" / "manual-behavioral-campaign.py"
EVIDENCE_BRANCH = "evaluation-evidence"
EVIDENCE_ROOT = "tests/governance/evaluations"
INVOCATION_TIMEOUT_SECONDS = 600

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


def choose_mode() -> str:
    while True:
        answer = input("Run this campaign (m)anually via the VS Code profile, or (a)utomated? [m/a] ").strip().lower()
        if answer in ("m", "manual"):
            return "manual"
        if answer in ("a", "auto", "automated"):
            return "automated"


def choose_model() -> dict:
    print("Select a model:")
    for index, entry in enumerate(MODELS, start=1):
        print(f"  {index}. {entry['label']}")
    while True:
        choice = input(f"Model [1-{len(MODELS)}]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(MODELS):
            return MODELS[int(choice) - 1]
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


def push_evidence(worktree_dir: Path, campaign_dir: Path, folder_name: str) -> None:
    target = worktree_dir / EVIDENCE_ROOT / folder_name
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
         "commit", "-m", f"test: automated behavioral campaign evidence {folder_name}"])

    push = run(["git", "-C", str(worktree_dir), "push", "origin", EVIDENCE_BRANCH], check=False)
    if push.returncode != 0:
        # Non-fast-forward: fetch and retry once. Never force-push.
        run(["git", "-C", str(worktree_dir), "fetch", "origin", EVIDENCE_BRANCH])
        rebase = run(["git", "-C", str(worktree_dir), "rebase", f"origin/{EVIDENCE_BRANCH}"], check=False)
        if rebase.returncode != 0:
            raise Error(f"evidence branch push rejected and could not be reconciled automatically: {push.stderr.strip()}")
        retry = run(["git", "-C", str(worktree_dir), "push", "origin", EVIDENCE_BRANCH], check=False)
        if retry.returncode != 0:
            raise Error(f"evidence branch push failed after retry: {retry.stderr.strip()}")
    print(f"Pushed evidence: {EVIDENCE_ROOT}/{folder_name} -> origin/{EVIDENCE_BRANCH}")


def run_automated(kit, workspace: Path, selection: str) -> int:
    folders_path = workspace / "folders.json"
    if not folders_path.is_file():
        raise Error(f"{folders_path} not found; run bootstrap-test-vm.py first")
    folders = json.loads(folders_path.read_text(encoding="utf-8"))

    model_entry = choose_model()
    rows = kit.selected_rows(kit.scenario_rows(), selection)
    source = kit.source_state()

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    folder_name = f"{stamp}-{model_entry['host']}-{model_entry['key']}"
    with tempfile.TemporaryDirectory() as tmp:
        campaign_dir = Path(tmp) / folder_name
        (campaign_dir / "responses").mkdir(parents=True)
        (campaign_dir / "prompts").mkdir(parents=True)

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

        worktree_dir = workspace / "evaluation-evidence-worktree"
        ensure_evidence_worktree(worktree_dir)
        push_evidence(worktree_dir, campaign_dir, folder_name)
        run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(worktree_dir)], check=False)

    failures = [r for r in records if r["status"] != "CAPTURED"]
    if failures:
        print(f"\n{len(failures)} scenario(s) did not execute cleanly:")
        for record in failures:
            print(f"  - {record['test_id']}: {record['reason']}")
    print(f"\nAutomated campaign complete: {len(records)} scenarios, {len(records) - len(failures)} captured.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path, help="the workspace bootstrap-test-vm.py created (contains folders.json and the three context directories)")
    parser.add_argument("--select", default="all", help="all, or a GOV-NNN[-GOV-MMM] range/list, same syntax as the manual conductor")
    parser.add_argument("--manual-args", nargs=argparse.REMAINDER, help="arguments forwarded to manual-behavioral-campaign.py conduct when manual mode is chosen")
    args = parser.parse_args()

    kit = load_campaign_kit()
    try:
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
