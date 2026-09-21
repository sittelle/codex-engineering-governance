#!/usr/bin/env python3
"""Bootstrap the dedicated, isolated Ubuntu behavioral-campaign test VM
(docs/adr/0003-automated-behavioral-campaign.md). Ubuntu only.

Asks the operator up front whether this VM is being set up for manual
testing (VS Code + a dedicated profile with the Codex/Claude extensions,
signed in through the IDE) or automated testing (native Codex/Claude CLI
binaries only, no VS Code, signed in through the terminal). The two setups
are mutually exclusive on purpose: manual testing drives the existing
`manual-behavioral-campaign.py conduct` VS Code conductor unchanged;
automated testing drives `run-behavioral-campaign-auto.py`'s direct,
non-interactive CLI invocations. This is distinct from
scripts/bootstrap-evaluation-vm.py's checksum-locked route: it targets one
dedicated, disposable-in-spirit test machine, resets any pre-existing
Codex/Claude configuration so it establishes known test configuration
itself. It does not sign in on the operator's behalf, does not make an AI
call, and does not push to Git.
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
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP_EVALUATION_VM = ROOT / "scripts" / "bootstrap-evaluation-vm.py"
CAMPAIGN_KIT = ROOT / "scripts" / "manual-behavioral-campaign.py"
GOVERNANCE_PY = ROOT / "governance.py"
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
        raise Error(f"command failed ({' '.join(str(a) for a in argv)}): {proc.stdout}\n{proc.stderr}")
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


def choose_test_mode(explicit: str | None) -> str:
    if explicit in ("manual", "automated"):
        return explicit
    while True:
        answer = input(
            "\nSet up this VM for (m)anual testing via VS Code, "
            "or (a)utomated testing via native CLI only (no VS Code)? [m/a] "
        ).strip().lower()
        if answer in ("m", "manual"):
            return "manual"
        if answer in ("a", "auto", "automated"):
            return "automated"


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
    """Manual mode only. Also installs the host adapter (governance.py host
    install) as part of scripts/bootstrap-evaluation-vm.py's bundled
    `latest --apply` route."""
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


def install_native_cli(name: str, npm_package: str, manual_install_hint: str) -> None:
    """Automated mode only. Installs via npm when available -- npm's
    registry provides package integrity/provenance the way apt/snap do,
    unlike piping a vendor's curl-hosted install script to a shell, which
    this script deliberately does not do unattended. If npm is
    unavailable, prints the vendor's own current install command and asks
    the operator to run it themselves rather than the script executing an
    unreviewed script on their behalf."""
    if shutil.which(name):
        return
    npm = shutil.which("npm")
    if npm:
        print(f"Installing {name} CLI via npm ({npm_package})...")
        proc = run([npm, "install", "-g", npm_package], check=False)
        if proc.returncode != 0:
            print(proc.stdout)
            print(proc.stderr, file=sys.stderr)
        if shutil.which(name):
            return
    print(f"\nCould not install '{name}' automatically (npm unavailable or the install failed).")
    print(f"Install it yourself, review the command first: {manual_install_hint}")
    input(f"Press Enter once '{name}' is installed and on PATH... ")
    if not shutil.which(name):
        raise Error(f"'{name}' is still not on PATH after prompting for manual install")


def install_native_clis(host: str) -> None:
    if host in ("codex", "all"):
        install_native_cli("codex", "@openai/codex", "curl -fsSL https://chatgpt.com/codex/install.sh | sh")
    if host in ("claude", "all"):
        install_native_cli("claude", "@anthropic-ai/claude-code", "curl -fsSL https://claude.ai/install.sh | bash")


def install_host_adapter(host: str) -> None:
    """Installs the framework's own kernel/governance instructions at the
    host level (the same step scripts/bootstrap-evaluation-vm.py bundles
    with VS Code setup for manual mode) so a scenario invocation actually
    loads the framework's instructions, not just the bare model."""
    proc = run([sys.executable, str(GOVERNANCE_PY), "host", "install", "--host", host, "-y"], check=False)
    print(proc.stdout)
    if proc.returncode != 0:
        raise Error(f"host-adapter install failed: {proc.stderr.strip()}")


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
    own CLI reference (https://developers.openai.com/codex/cli/reference).
    Codex also authenticates directly off OPENAI_API_KEY/CODEX_API_KEY when
    either is set, bypassing stored login state entirely, so treat those the
    same as a confirmed login rather than relying on the status subcommand
    alone."""
    if os.environ.get("OPENAI_API_KEY") or os.environ.get("CODEX_API_KEY"):
        return True
    proc = run(["codex", "login", "status"], check=False)
    return proc.returncode == 0


def _anthropic_profile_signed_in() -> bool:
    """Claude Code's Console "sign in without an API key" route (the
    recommended one, see
    https://code.claude.com/docs/en/authentication#sign-in-without-an-api-key)
    stores an OAuth profile under the Anthropic configuration directory --
    <config_dir>/credentials/<profile>.json -- not under
    ~/.claude/.credentials.json. See
    https://platform.claude.com/docs/en/manage-claude/wif-reference for the
    exact layout and the active_config/ANTHROPIC_PROFILE resolution order,
    which Claude Code also honors."""
    config_dir = Path(os.environ.get("ANTHROPIC_CONFIG_DIR", "")) if os.environ.get("ANTHROPIC_CONFIG_DIR") else Path.home() / ".config" / "anthropic"
    profile = os.environ.get("ANTHROPIC_PROFILE")
    if not profile:
        active_config = config_dir / "active_config"
        profile = active_config.read_text(encoding="utf-8").strip() if active_config.is_file() else ""
        profile = profile or "default"
    credentials = config_dir / "credentials" / f"{profile}.json"
    if not credentials.is_file():
        return False
    try:
        data = json.loads(credentials.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return bool(data)


def claude_signed_in(home: Path) -> bool:
    """Claude Code accepts several distinct credential sources beyond a
    claude.ai subscription login stored at ~/.claude/.credentials.json (mode
    0600, https://code.claude.com/docs/en/authentication): an
    ANTHROPIC_API_KEY/ANTHROPIC_AUTH_TOKEN environment variable, a
    CLAUDE_CODE_OAUTH_TOKEN, and an Anthropic Console sign-in stored as a
    profile (see _anthropic_profile_signed_in). Check all of them -- a
    Console sign-in that never touches .credentials.json is not a login
    failure."""
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN") or os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        return True
    config_dir_override = os.environ.get("CLAUDE_CONFIG_DIR")
    credentials = (Path(config_dir_override) if config_dir_override else home / ".claude") / ".credentials.json"
    if credentials.is_file():
        try:
            data = json.loads(credentials.read_text(encoding="utf-8"))
            if data:
                return True
        except (OSError, json.JSONDecodeError):
            pass
    return _anthropic_profile_signed_in()


def prompt_sign_in_vscode(profile: Path) -> None:
    code = shutil.which("code") or "/snap/bin/code"
    print("\nLaunching VS Code with the dedicated test profile for sign-in.")
    print("Sign in to both the Codex and Claude extensions, then return here.")
    subprocess.Popen([code, "--user-data-dir", str(profile), "--extensions-dir", str(profile / "extensions"), str(ROOT)])
    input("Press Enter once you have signed in to both Codex and Claude... ")


def prompt_sign_in_terminal() -> None:
    print("\nSign in to both CLIs in this terminal, then return here:")
    print("  codex login")
    print("  claude          # bare invocation opens the browser login on first launch; exit once signed in")
    input("Press Enter once you have signed in to both Codex and Claude... ")


def ensure_signed_in(home: Path, mode: str, profile: Path | None) -> None:
    if codex_signed_in() and claude_signed_in(home):
        print("Sign-in: both Codex and Claude already signed in.")
        return
    prompt = (lambda: prompt_sign_in_vscode(profile)) if mode == "manual" else prompt_sign_in_terminal
    prompt()
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
        prompt()


def create_project_folders(kit, workspace: Path) -> dict[str, str]:
    """Automated mode only. Reuse the manual campaign kit's own
    context-materialization logic (the same functions `prepare` uses),
    rather than a second implementation of the three GOV scenario
    contexts."""
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


def check_cli_executables_optional() -> dict[str, str | None]:
    """Manual mode: the native CLI binaries are not required (testing goes
    through the VS Code extensions), so their absence is informational,
    never fatal."""
    found = {}
    for name in ("codex", "claude"):
        found[name] = shutil.which(name)
    present = {k: v for k, v in found.items() if v}
    if present:
        print(f"Native CLI executables also present (not required for manual mode): {present}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=("codex", "claude", "all"), default="all")
    parser.add_argument("--mode", choices=("manual", "automated"), default=None, help="skip the interactive prompt")
    parser.add_argument("--vscode-user-data-dir", type=Path, help="manual mode: new directory outside the framework source for the dedicated test profile")
    parser.add_argument("--workspace", type=Path, help="automated mode: new or existing directory to hold the three scenario project folders")
    parser.add_argument("--skip-currency-check", action="store_true")
    args = parser.parse_args()

    try:
        require_linux()
        if not args.skip_currency_check:
            check_framework_currency(ROOT)

        mode = choose_test_mode(args.mode)
        print(f"Mode: {mode}")

        home = Path.home()
        backed_up = backup_existing_config(home)
        if backed_up:
            print("Reset pre-existing configuration (renamed, not deleted):")
            for path in backed_up:
                print(f"  - {path}")
        else:
            print("Reset: no pre-existing Codex/Claude configuration found.")

        if mode == "manual":
            if not args.vscode_user_data_dir:
                raise Error("manual mode requires --vscode-user-data-dir")
            ensure_vscode_and_profile(args.host, args.vscode_user_data_dir)
            executables = check_cli_executables_optional()
            ensure_signed_in(home, mode, args.vscode_user_data_dir)
            print("\nBootstrap complete (manual).")
            print(f"VS Code profile: {args.vscode_user_data_dir}")
            print("Continue with the existing manual campaign kit: "
                  "python3 scripts/manual-behavioral-campaign.py prepare <campaign-dir>, then `conduct`.")
            return 0

        if not args.workspace:
            raise Error("automated mode requires --workspace")
        install_native_clis(args.host)
        install_host_adapter(args.host)
        executables = check_cli_executables()
        versions = {name: cli_version(path) for name, path in executables.items()}
        print(f"CLI executables: codex={executables['codex']} ({versions.get('codex')}), claude={executables['claude']} ({versions.get('claude')})")
        ensure_signed_in(home, mode, None)

        kit = load_campaign_kit()
        folders = create_project_folders(kit, args.workspace)
        (args.workspace / "folders.json").write_text(json.dumps(folders, indent=2) + "\n", encoding="utf-8", newline="\n")

        print("\nBootstrap complete (automated).")
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
