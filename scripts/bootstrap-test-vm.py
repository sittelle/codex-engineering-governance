#!/usr/bin/env python3
"""Bootstrap the dedicated, isolated Ubuntu automated-behavioral-campaign test
VM (docs/adr/0003-automated-behavioral-campaign.md). Ubuntu only.

This is distinct from scripts/bootstrap-evaluation-vm.py's checksum-locked
route: it targets one dedicated, disposable-in-spirit test machine, resets
any pre-existing Codex/Claude configuration so it establishes known test
configuration itself, and hands off to run-behavioral-campaign-auto.py for
the actual campaign. It does not sign in on the operator's behalf, does not
make an AI call, and does not push to Git.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP_EVALUATION_VM = ROOT / "scripts" / "bootstrap-evaluation-vm.py"
CAMPAIGN_KIT = ROOT / "scripts" / "manual-behavioral-campaign.py"
SIGN_IN_RETRY_LIMIT = 3


class Error(RuntimeError):
    pass


def load_campaign_kit():
    spec = importlib.util.spec_from_file_location("manual_behavioral_campaign", CAMPAIGN_KIT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(argv, cwd=None, check=True):
    proc = subprocess.run(argv, cwd=cwd, text=True, capture_output=True)
    if check and proc.returncode != 0:
        raise Error(f"command failed ({' '.join(argv)}): {proc.stdout}\n{proc.stderr}")
    return proc


def require_linux() -> None:
    if platform.system() != "Linux":
        raise Error("bootstrap-test-vm.py targets the dedicated Ubuntu test VM only")


def check_framework_currency(root: Path) -> None:
    """Report, never silently pull: fetch the tracking remote and compare
    local HEAD against it. A behind/diverged checkout is the operator's
    decision to resolve (git pull, or explicit acknowledgment), not this
    script's to fix unattended."""
    fetch = run(["git", "-C", str(root), "fetch"], check=False)
    if fetch.returncode != 0:
        raise Error(f"could not fetch the framework's git remote: {fetch.stderr.strip()}")
    status = run(["git", "-C", str(root), "status", "--porcelain=v1", "--branch"], check=False)
    if status.returncode != 0:
        raise Error("could not read framework git status")
    header = status.stdout.splitlines()[0] if status.stdout.splitlines() else ""
    if "gone]" in header:
        raise Error(f"framework checkout's remote tracking branch is gone ({header.strip()}); resolve before continuing")
    if "behind" in header:
        raise Error(
            f"framework checkout is not current with its remote ({header.strip()}); "
            "run `git pull` (or otherwise reconcile) before bootstrapping the test VM"
        )
    print(f"Framework currency: OK ({header.strip() or 'up to date'})")


def backup_existing_config(home: Path) -> list[str]:
    """Rename (never delete) pre-existing Codex/Claude configuration so the
    bootstrapper establishes known test configuration itself. Timestamped,
    reversible -- matches this framework's general preference for
    reversible actions over destructive ones."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backed_up = []
    for name in (".codex", ".claude"):
        existing = home / name
        if existing.exists():
            backup = home / f"{name}.pre-test-backup-{stamp}"
            existing.rename(backup)
            backed_up.append(str(backup))
    return backed_up


def ensure_vscode_and_profile(host: str, profile: Path) -> None:
    if not BOOTSTRAP_EVALUATION_VM.is_file():
        raise Error("scripts/bootstrap-evaluation-vm.py is missing")
    plan = run([sys.executable, str(BOOTSTRAP_EVALUATION_VM), "latest", "--host", host], check=False)
    print(plan.stdout)
    apply = run(
        [sys.executable, str(BOOTSTRAP_EVALUATION_VM), "latest", "--host", host, "--apply", "--vscode-user-data-dir", str(profile)],
        check=False,
    )
    print(apply.stdout)
    if apply.returncode != 0:
        raise Error(f"VS Code/profile/extension/host-adapter bootstrap failed: {apply.stderr.strip()}")


def check_cli_executables() -> dict[str, str]:
    found = {}
    for name in ("codex", "claude"):
        path = shutil.which(name)
        if not path:
            raise Error(f"'{name}' executable is not on PATH; unable to proceed with the test")
        found[name] = path
    return found


def cli_version(executable: str) -> str | None:
    proc = run([executable, "--version"], check=False)
    return proc.stdout.strip() or None


def codex_signed_in() -> bool:
    """codex login status exits 0 when credentials are present, per OpenAI's
    own CLI reference (https://developers.openai.com/codex/cli/reference)."""
    proc = run(["codex", "login", "status"], check=False)
    return proc.returncode == 0


def claude_signed_in(home: Path) -> bool:
    """Claude Code's own docs (https://code.claude.com/docs/en/authentication)
    document credential storage at ~/.claude/.credentials.json (mode 0600)
    on Linux, not a documented non-interactive status subcommand; check for
    that file rather than relying on an undocumented CLI status command."""
    credentials = home / ".claude" / ".credentials.json"
    if not credentials.is_file():
        return False
    try:
        data = json.loads(credentials.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return bool(data)


def prompt_sign_in(profile: Path) -> None:
    code = shutil.which("code") or "/snap/bin/code"
    print("\nLaunching VS Code with the dedicated test profile for sign-in.")
    print("Sign in to both the Codex and Claude extensions, then return here.")
    subprocess.Popen([code, "--user-data-dir", str(profile), "--extensions-dir", str(profile / "extensions"), str(ROOT)])
    input("Press Enter once you have signed in to both Codex and Claude... ")


def ensure_signed_in(home: Path, profile: Path) -> None:
    if codex_signed_in() and claude_signed_in(home):
        print("Sign-in: both Codex and Claude already signed in.")
        return
    prompt_sign_in(profile)
    attempts = 0
    while True:
        attempts += 1
        codex_ok, claude_ok = codex_signed_in(), claude_signed_in(home)
        if codex_ok and claude_ok:
            print("Sign-in: confirmed for both Codex and Claude.")
            return
        missing = [name for name, ok in (("Codex", codex_ok), ("Claude", claude_ok)) if not ok]
        if attempts >= SIGN_IN_RETRY_LIMIT:
            raise Error(f"still not signed in after {SIGN_IN_RETRY_LIMIT} attempts ({', '.join(missing)}); unable to proceed with the test")
        answer = input(f"Not yet signed in to: {', '.join(missing)}. Try again? [y/N] ").strip().lower()
        if answer != "y":
            raise Error("sign-in declined; unable to proceed with the test")
        prompt_sign_in(profile)


def create_project_folders(kit, workspace: Path) -> dict[str, str]:
    """Reuse the manual campaign kit's own context-materialization logic
    (the same functions `prepare` uses), rather than a second
    implementation of the three GOV scenario contexts."""
    workspace.mkdir(parents=True, exist_ok=True)
    contexts = workspace / "contexts"
    contexts.mkdir(exist_ok=True)
    global_kernel = contexts / "global-kernel"
    global_kernel.mkdir(exist_ok=True)
    if not (contexts / "governed-project").exists():
        kit.create_governed_context(contexts)
    return {
        "GLOBAL_KERNEL": str(global_kernel),
        "GOVERNED_REPOSITORY": str(contexts / "governed-project"),
        "GOVERNANCE_FRAMEWORK_REPOSITORY": str(ROOT),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=("codex", "claude", "all"), default="all")
    parser.add_argument("--vscode-user-data-dir", required=True, type=Path, help="new directory outside the framework source for the dedicated test profile")
    parser.add_argument("--workspace", required=True, type=Path, help="new or existing directory to hold the three scenario project folders")
    parser.add_argument("--skip-currency-check", action="store_true")
    args = parser.parse_args()

    try:
        require_linux()
        if not args.skip_currency_check:
            check_framework_currency(ROOT)

        home = Path.home()
        backed_up = backup_existing_config(home)
        if backed_up:
            print("Reset pre-existing configuration (renamed, not deleted):")
            for path in backed_up:
                print(f"  - {path}")
        else:
            print("Reset: no pre-existing Codex/Claude configuration found.")

        ensure_vscode_and_profile(args.host, args.vscode_user_data_dir)

        executables = check_cli_executables()
        versions = {name: cli_version(path) for name, path in executables.items()}
        print(f"CLI executables: codex={executables['codex']} ({versions.get('codex')}), claude={executables['claude']} ({versions.get('claude')})")

        ensure_signed_in(home, args.vscode_user_data_dir)

        kit = load_campaign_kit()
        folders = create_project_folders(kit, args.workspace)
        (args.workspace / "folders.json").write_text(json.dumps(folders, indent=2) + "\n", encoding="utf-8", newline="\n")

        print("\nBootstrap complete.")
        print(f"VS Code profile: {args.vscode_user_data_dir}")
        print("Project folders:")
        for name, path in folders.items():
            print(f"  - {name}: {path}")
        print(f"Run the campaign with: python3 {ROOT / 'scripts' / 'run-behavioral-campaign-auto.py'} --workspace {args.workspace}")
        return 0
    except Error as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
