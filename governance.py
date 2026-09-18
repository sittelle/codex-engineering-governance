#!/usr/bin/env python3
"""
Engineering Governance management entry point.

Interactive:
    python governance.py

Parameterized:
    python governance.py host status
    python governance.py host install --host codex
    python governance.py host install --host claude
    python governance.py host install --host all -y
    python governance.py host update --host all -y
    python governance.py host uninstall --host claude -y
    python governance.py host verify --host all

    python governance.py project status --project /path/to/project
    python governance.py project new --parent /path/to/projects --name demo
    python governance.py project adopt --project /path/to/existing
    python governance.py project update --project /path/to/project
    python governance.py project verify --project /path/to/project

Mutating commands always print a preview. Without -y/--yes, they ask:
    Apply these changes? [y/N]:

-y only confirms the displayed operation. It never bypasses ownership, dirty-worktree,
version, path, or verification checks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

FRAMEWORK_ID = "sittelle-engineering-governance"
LEGACY_FRAMEWORK_IDS = {"codex-engineering-governance"}
INTEGRITY_PATH = ".governance/integrity.json"
STATE_NAME = ".sittelle-engineering-governance.json"

HOST_BEGIN = "<!-- BEGIN SITTELLE-ENGINEERING-GOVERNANCE -->"
HOST_END = "<!-- END SITTELLE-ENGINEERING-GOVERNANCE -->"
HOST_RE = re.compile(re.escape(HOST_BEGIN) + r".*?" + re.escape(HOST_END), re.DOTALL)

PROJECT_BEGIN = "<!-- BEGIN ENGINEERING-GOVERNANCE-MANAGED -->"
PROJECT_END = "<!-- END ENGINEERING-GOVERNANCE-MANAGED -->"
PROJECT_RE = re.compile(re.escape(PROJECT_BEGIN) + r".*?" + re.escape(PROJECT_END), re.DOTALL)

OLD_PROJECT_BEGIN = "<!-- BEGIN CODEX-GOVERNANCE-MANAGED -->"
OLD_PROJECT_END = "<!-- END CODEX-GOVERNANCE-MANAGED -->"
OLD_PROJECT_RE = re.compile(
    re.escape(OLD_PROJECT_BEGIN) + r".*?" + re.escape(OLD_PROJECT_END), re.DOTALL
)

CLAUDE_PROJECT_BEGIN = "<!-- BEGIN SITTELLE-ENGINEERING-GOVERNANCE-CLAUDE -->"
CLAUDE_PROJECT_END = "<!-- END SITTELLE-ENGINEERING-GOVERNANCE-CLAUDE -->"
CLAUDE_PROJECT_RE = re.compile(
    re.escape(CLAUDE_PROJECT_BEGIN) + r".*?" + re.escape(CLAUDE_PROJECT_END), re.DOTALL
)


class GovernanceError(RuntimeError):
    pass


@dataclass(frozen=True)
class Host:
    key: str
    label: str
    home_env: str
    default_home: str
    instruction_name: str


HOSTS = {
    "codex": Host("codex", "Codex", "CODEX_HOME", ".codex", "AGENTS.md"),
    "claude": Host("claude", "Claude Code", "CLAUDE_CONFIG_DIR", ".claude", "CLAUDE.md"),
}


def fail(message: str) -> None:
    raise GovernanceError(message)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        text.replace("\r\n", "\n").replace("\r", "\n"),
        encoding="utf-8",
        newline="\n",
    )


def assert_plain_file_or_missing(path: Path) -> None:
    if path.is_symlink():
        fail(f"Refusing to manage symbolic link: {path}")
    if path.exists() and not path.is_file():
        fail(f"Expected a regular file or missing path: {path}")


def framework_root() -> Path:
    root = Path(__file__).resolve().parent
    required = (
        "VERSION",
        "host-adapters/operating-kernel.md",
        "host-adapters/operating-kernel.business-led.md",
        "templates/repository/AGENTS.md",
        "templates/repository/AGENTS.business-led.md",
        "templates/repository/CLAUDE.md",
        "templates/repository/project-governance.yml",
    )
    missing = [rel for rel in required if not (root / rel).is_file()]
    if missing:
        fail("Framework installation is incomplete: " + ", ".join(missing))
    return root


def version(root: Path) -> str:
    value = read_text(root / "VERSION").strip()
    if not value:
        fail("VERSION is empty")
    return value


def run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def git_worktree_is_dirty(path: Path) -> bool:
    if not (path / ".git").exists():
        return False
    result = run_git(["status", "--porcelain=v1", "--untracked-files=all"], path)
    if result.returncode != 0:
        fail(f"git status failed for {path}: {result.stderr.strip()}")
    return bool(result.stdout.strip())


def confirm(yes: bool) -> None:
    if yes:
        print("Confirmation: -y")
        return
    answer = input("Apply these changes? [y/N]: ").strip().lower()
    if answer not in {"y", "yes"}:
        print("No changes applied.")
        raise SystemExit(0)


def print_preview(title: str, lines: list[str]) -> None:
    print()
    print(title)
    print("-" * len(title))
    for line in lines:
        print(line)
    print()


def selected_hosts(name: str) -> list[Host]:
    return list(HOSTS.values()) if name == "all" else [HOSTS[name]]


def action_hosts(root: Path, action: str, requested: str) -> list[Host]:
    candidates = selected_hosts(requested)
    selected: list[Host] = []
    for host in candidates:
        status = host_status(root, host)
        installed = status.startswith("INSTALLED")
        legacy = status.startswith("LEGACY")
        unsafe_existing = status.startswith("MODIFIED") or status.startswith("BROKEN")
        if action == "install":
            applicable = status == "NOT INSTALLED"
        elif action == "update":
            applicable = installed or legacy or unsafe_existing
        elif action == "uninstall":
            applicable = installed or unsafe_existing
        elif action == "verify":
            applicable = installed
        else:
            applicable = True

        if applicable:
            selected.append(host)
        elif requested != "all":
            if legacy and action == "install":
                fail(f"{host.label}: legacy installation detected; use host update")
            if action == "uninstall" and legacy:
                fail(f"{host.label}: migrate the legacy installation with host update before uninstalling")
            fail(f"{host.label}: action {action} is not applicable ({status})")

    return selected


# ---------------------------------------------------------------------------
# Host adapter lifecycle
# ---------------------------------------------------------------------------

def host_home(host: Host) -> Path:
    configured = os.environ.get(host.home_env)
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / host.default_home).resolve()


def host_paths(host: Host) -> dict[str, Path]:
    home = host_home(host)
    return {
        "home": home,
        "instruction": home / host.instruction_name,
        "locator": home / "GOVERNANCE_ROOT",
        "state": home / STATE_NAME,
        "settings": home / "settings.json",
    }


def kernel_template_path(root: Path, kernel_mode: str) -> Path:
    if kernel_mode not in GOVERNANCE_MODES:
        fail(f"Unknown governance mode: {kernel_mode}")
    name = "operating-kernel.business-led.md" if kernel_mode == "business-led" else "operating-kernel.md"
    return root / "host-adapters" / name


def render_host_block(root: Path, host: Host, kernel_mode: str = "professional") -> str:
    template = read_text(kernel_template_path(root, kernel_mode))
    locator = (
        "$CODEX_HOME/GOVERNANCE_ROOT (default: $HOME/.codex/GOVERNANCE_ROOT)"
        if host.key == "codex"
        else "$CLAUDE_CONFIG_DIR/GOVERNANCE_ROOT (default: $HOME/.claude/GOVERNANCE_ROOT)"
    )
    body = template.replace("{{HOST_NAME}}", host.label).replace(
        "{{LOCATOR_DISPLAY}}", locator
    )
    if "{{" in body or "}}" in body:
        fail("Unresolved placeholder in host operating kernel")
    metadata = (
        f"<!-- framework={FRAMEWORK_ID}; host={host.key}; version={version(root)}; kernel_mode={kernel_mode} -->"
    )
    return f"{HOST_BEGIN}\n{metadata}\n{body.rstrip()}\n{HOST_END}"


def load_host_state(path: Path, host: Host) -> dict | None:
    assert_plain_file_or_missing(path)
    if not path.exists():
        return None
    try:
        data = json.loads(read_text(path))
    except Exception as exc:
        fail(f"Cannot parse installer state {path}: {exc}")
    for key, expected in (("schema_version", 1), ("host", host.key)):
        if data.get(key) != expected:
            fail(f"Unrecognized installer state in {path}: {key}")
    framework = data.get("framework")
    if framework != FRAMEWORK_ID and framework not in LEGACY_FRAMEWORK_IDS:
        fail(f"Unrecognized installer state in {path}: framework")
    return data


def save_host_state(path: Path, state: dict) -> None:
    write_text(path, json.dumps(state, indent=2, sort_keys=True) + "\n")


def current_host_block(path: Path) -> str | None:
    if not path.exists():
        return None
    matches = list(HOST_RE.finditer(read_text(path)))
    if len(matches) > 1:
        fail(f"Multiple framework-managed instruction blocks found: {path}")
    return matches[0].group(0) if matches else None


def legacy_codex_installation(paths: dict[str, Path]) -> bool:
    instruction = paths["instruction"]
    locator = paths["locator"]
    if not instruction.is_file() or not locator.is_file():
        return False
    try:
        old_root = Path(read_text(locator).strip()).expanduser().resolve()
    except Exception:
        return False
    old_kernel = old_root / "codex-home" / "AGENTS.md"
    return old_kernel.is_file() and old_kernel.read_bytes() == instruction.read_bytes()


def read_json_object(path: Path) -> dict:
    assert_plain_file_or_missing(path)
    if not path.exists():
        return {}
    try:
        data = json.loads(read_text(path))
    except Exception as exc:
        fail(f"Cannot parse JSON file {path}: {exc}")
    if not isinstance(data, dict):
        fail(f"Expected JSON object in {path}")
    return data


def claude_read_rule(root: Path) -> str:
    """Return the least-privilege Claude Read allow rule for the central governance root."""
    text = root.resolve().as_posix()
    if any(ch in text for ch in "*?[]"):
        fail(
            "Claude Code read permission cannot safely represent a governance root "
            "containing glob metacharacters (* ? [ ])"
        )
    if re.match(r"^[A-Za-z]:/", text):
        # Claude Code normalizes Windows paths to POSIX form: C:/x -> /c/x.
        text = "/" + text[0].lower() + text[2:]
    if not text.startswith("/"):
        fail(f"Cannot derive an absolute Claude Code permission path from {root}")
    return f"Read(/{text.rstrip('/')}/**)"


def claude_allow_rules(data: dict) -> list[str]:
    permissions = data.get("permissions")
    if permissions is None:
        return []
    if not isinstance(permissions, dict):
        fail("Claude settings permissions must be a JSON object")
    values = permissions.get("allow")
    if values is None:
        return []
    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
        fail("Claude settings permissions.allow must be a string array")
    return values


def add_claude_read_rule(settings_path: Path, root: Path) -> dict:
    """Add one exact read-only allow rule and return ownership facts for uninstall."""
    existed = settings_path.exists()
    data = read_json_object(settings_path)

    permissions_existed = "permissions" in data
    if permissions_existed and not isinstance(data["permissions"], dict):
        fail("Claude settings permissions must be a JSON object")
    permissions = data.setdefault("permissions", {})

    allow_existed = "allow" in permissions
    if allow_existed:
        values = permissions["allow"]
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            fail("Claude settings permissions.allow must be a string array")
    else:
        values = []
        permissions["allow"] = values

    rule = claude_read_rule(root)
    added = rule not in values
    if added:
        values.append(rule)
        write_text(settings_path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    return {
        "entry_added": added,
        "settings_created": not existed,
        "permissions_created": not permissions_existed,
        "allow_created": not allow_existed,
        "rule": rule,
    }


def remove_claude_read_rule(settings_path: Path, ownership: dict) -> None:
    """Remove only the exact allow-rule entry/containers created by this installation."""
    if not ownership.get("entry_added"):
        return
    if not settings_path.is_file():
        fail("Claude settings file is missing; refusing partial uninstall")

    rule = ownership.get("rule")
    if not isinstance(rule, str) or not rule:
        fail("Claude read-rule ownership state is invalid")

    data = read_json_object(settings_path)
    permissions = data.get("permissions")
    if not isinstance(permissions, dict):
        fail("Claude settings permissions changed; refusing partial uninstall")
    values = permissions.get("allow")
    if not isinstance(values, list) or rule not in values:
        fail("Claude governance Read allow rule changed; refusing partial uninstall")

    values.remove(rule)

    if ownership.get("allow_created") and not values:
        permissions.pop("allow", None)
    if ownership.get("permissions_created") and not permissions:
        data.pop("permissions", None)

    if ownership.get("settings_created") and not data:
        settings_path.unlink()
    else:
        write_text(settings_path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def host_status(root: Path, host: Host) -> str:
    paths = host_paths(host)
    state = load_host_state(paths["state"], host)

    if state:
        block = current_host_block(paths["instruction"])
        if block is None:
            return "BROKEN (managed instruction block missing)"
        if sha256_text(block) != state.get("managed_sha256"):
            return "MODIFIED (managed instruction block changed)"
        if not paths["locator"].is_file():
            return "BROKEN (GOVERNANCE_ROOT missing)"
        locator = read_text(paths["locator"]).strip()
        if locator != state.get("governance_root"):
            return "MODIFIED (GOVERNANCE_ROOT changed)"
        installed = str(state.get("version", "unknown"))
        current = version(root)
        if installed == current and Path(locator).resolve() == root:
            return f"INSTALLED {installed}"
        return f"INSTALLED {installed} (update available to {current})"

    if host.key == "codex" and legacy_codex_installation(paths):
        return "LEGACY CODEX INSTALLATION (migration available)"
    if current_host_block(paths["instruction"]):
        return "UNTRACKED MANAGED BLOCK (manual review required)"
    return "NOT INSTALLED"


def display_host_status(status: str) -> str:
    """Render governance-adapter state without implying host-software detection."""
    if status.startswith("INSTALLED "):
        return "adapter installed " + status[len("INSTALLED "):]
    if status == "NOT INSTALLED":
        return "adapter not configured"
    if status.startswith("LEGACY CODEX INSTALLATION"):
        return status.replace(
            "LEGACY CODEX INSTALLATION",
            "legacy Codex adapter",
            1,
        )
    if status.startswith("UNTRACKED MANAGED BLOCK"):
        return "adapter untracked (managed block; manual review required)"
    if status.startswith("MODIFIED "):
        return "adapter modified " + status[len("MODIFIED "):]
    if status.startswith("BROKEN "):
        return "adapter broken " + status[len("BROKEN "):]
    return "adapter " + status.lower()


def preflight_host_install(root: Path, host: Host) -> tuple[dict, bool]:
    paths = host_paths(host)
    for key in ("instruction", "locator", "state"):
        assert_plain_file_or_missing(paths[key])
    if host.key == "claude":
        assert_plain_file_or_missing(paths["settings"])
        data = read_json_object(paths["settings"])
        claude_allow_rules(data)

    state = load_host_state(paths["state"], host)
    legacy = host.key == "codex" and state is None and legacy_codex_installation(paths)

    if state:
        block = current_host_block(paths["instruction"])
        if block is None:
            fail(f"{host.label}: managed instruction block is missing")
        if sha256_text(block) != state.get("managed_sha256"):
            fail(
                f"{host.label}: managed instruction block was modified; "
                "refusing to overwrite user-modified content"
            )
        if not paths["locator"].is_file():
            fail(f"{host.label}: GOVERNANCE_ROOT is missing")
        if read_text(paths["locator"]).strip() != state.get("governance_root"):
            fail(
                f"{host.label}: GOVERNANCE_ROOT was modified; refusing to overwrite it"
            )
    else:
        if paths["instruction"].exists() and current_host_block(paths["instruction"]):
            fail(
                f"{host.label}: managed markers exist without trusted state; "
                "manual review is required"
            )
        if host.key == "codex" and paths["instruction"].exists() and paths["locator"].exists() and not legacy:
            fail(
                "Codex: existing AGENTS.md and GOVERNANCE_ROOT are not a provable "
                "legacy framework installation; manual review is required"
            )
        if paths["locator"].exists() and not legacy:
            value = read_text(paths["locator"]).strip()
            if value != str(root):
                fail(
                    f"{host.label}: pre-existing GOVERNANCE_ROOT points elsewhere: {value}"
                )

    return paths, legacy


def host_install_or_update(
    root: Path,
    host: Host,
    *,
    require_existing: bool,
    kernel_mode: str | None = None,
) -> None:
    paths, legacy = preflight_host_install(root, host)
    state = load_host_state(paths["state"], host)

    if require_existing and not state and not legacy:
        fail(f"{host.label}: no managed installation exists to update")

    # An explicit --kernel-mode always wins. Otherwise preserve whatever
    # mode this host was already installed with; only a fresh install
    # defaults to professional.
    effective_kernel_mode = kernel_mode or (state.get("kernel_mode") if state else None) or "professional"
    if effective_kernel_mode not in GOVERNANCE_MODES:
        fail(f"Unknown governance mode: {effective_kernel_mode}")

    block = render_host_block(root, host, effective_kernel_mode)

    if legacy:
        # Proven byte-for-byte legacy framework kernel: no distinguishable custom text.
        new_instruction = block + "\n"
        instruction_created = True
        locator_created = True
    else:
        old_instruction = read_text(paths["instruction"]) if paths["instruction"].exists() else ""
        old_block = current_host_block(paths["instruction"])
        if old_block:
            new_instruction = old_instruction.replace(old_block, block, 1)
        elif old_instruction:
            separator = "\n" if old_instruction.endswith("\n") else "\n\n"
            new_instruction = old_instruction + separator + block + "\n"
        else:
            new_instruction = block + "\n"
        instruction_created = (
            bool(state.get("instruction_created")) if state else not paths["instruction"].exists()
        )
        locator_created = (
            bool(state.get("locator_created")) if state else not paths["locator"].exists()
        )

    # Existing installer-owned locator can move with the framework. A pre-existing locator cannot.
    if state and not state.get("locator_created"):
        old_root = str(state.get("governance_root", ""))
        if old_root != str(root):
            fail(
                f"{host.label}: GOVERNANCE_ROOT pre-dated this installer; "
                "refusing to repoint user-owned locator during update"
            )

    paths["home"].mkdir(parents=True, exist_ok=True)
    write_text(paths["instruction"], new_instruction)

    if legacy or locator_created or (state and state.get("locator_created")):
        write_text(paths["locator"], str(root))

    claude_ownership = {
        "entry_added": False,
        "settings_created": False,
        "permissions_created": False,
        "allow_created": False,
        "rule": None,
    }
    if host.key == "claude":
        expected_rule = claude_read_rule(root)
        if state:
            previous = dict(state.get("claude_settings_ownership") or {})
            old_root = str(state.get("governance_root"))
            if old_root != str(root) and previous.get("entry_added"):
                remove_claude_read_rule(paths["settings"], previous)
                claude_ownership = add_claude_read_rule(paths["settings"], root)
            elif old_root == str(root):
                settings = read_json_object(paths["settings"])
                values = claude_allow_rules(settings)
                previous_rule = previous.get("rule") or expected_rule
                if previous.get("entry_added") and previous_rule not in values:
                    fail(
                        "Claude governance Read allow rule was modified; "
                        "refusing to overwrite settings"
                    )
                if previous.get("entry_added"):
                    previous["rule"] = previous_rule
                    claude_ownership = previous
                else:
                    claude_ownership = add_claude_read_rule(paths["settings"], root)
            else:
                claude_ownership = add_claude_read_rule(paths["settings"], root)
        else:
            claude_ownership = add_claude_read_rule(paths["settings"], root)

    new_state = {
        "schema_version": 1,
        "framework": FRAMEWORK_ID,
        "host": host.key,
        "version": version(root),
        "governance_root": str(root),
        "managed_sha256": sha256_text(block),
        "instruction_created": instruction_created,
        "locator_created": locator_created,
        "claude_settings_ownership": claude_ownership,
        "kernel_mode": effective_kernel_mode,
    }
    save_host_state(paths["state"], new_state)
    verify_host(root, host)


def preflight_host_uninstall(root: Path, host: Host) -> tuple[dict, dict, str]:
    paths = host_paths(host)
    for key in ("instruction", "locator", "state"):
        assert_plain_file_or_missing(paths[key])
    if host.key == "claude":
        assert_plain_file_or_missing(paths["settings"])

    state = load_host_state(paths["state"], host)
    if not state:
        fail(f"{host.label}: no trusted installation state exists; nothing will be removed")

    if host.key == "claude":
        ownership = dict(state.get("claude_settings_ownership") or {})
        if ownership.get("entry_added"):
            settings = read_json_object(paths["settings"])
            values = claude_allow_rules(settings)
            rule = ownership.get("rule") or claude_read_rule(
                Path(str(state.get("governance_root")))
            )
            if rule not in values:
                fail(
                    "Claude governance Read allow rule was modified; "
                    "refusing partial uninstall"
                )

    if not paths["instruction"].is_file():
        fail(f"{host.label}: managed instruction file is missing")
    block = current_host_block(paths["instruction"])
    if block is None:
        fail(f"{host.label}: managed instruction block is missing")
    if sha256_text(block) != state.get("managed_sha256"):
        fail(
            f"{host.label}: managed instruction block was modified; "
            "refusing to delete user-modified content"
        )

    if state.get("locator_created"):
        if not paths["locator"].is_file():
            fail(f"{host.label}: installer-owned GOVERNANCE_ROOT is missing")
        if read_text(paths["locator"]).strip() != state.get("governance_root"):
            fail(
                f"{host.label}: installer-owned GOVERNANCE_ROOT was modified; "
                "refusing partial uninstall"
            )

    return paths, state, block


def host_uninstall(root: Path, host: Host) -> None:
    paths, state, block = preflight_host_uninstall(root, host)

    text = read_text(paths["instruction"])
    remaining = text.replace(block, "", 1)
    remaining = re.sub(r"\n{3,}", "\n\n", remaining).strip("\n")

    if remaining.strip():
        write_text(paths["instruction"], remaining + "\n")
    elif state.get("instruction_created"):
        paths["instruction"].unlink()
    else:
        # Defensive: if a pre-existing file has become empty, leave an empty file rather than
        # claiming ownership of the whole file.
        write_text(paths["instruction"], "")

    if state.get("locator_created") and paths["locator"].exists():
        paths["locator"].unlink()

    if host.key == "claude":
        ownership = dict(state.get("claude_settings_ownership") or {})
        remove_claude_read_rule(paths["settings"], ownership)

    paths["state"].unlink()

    if current_host_block(paths["instruction"]):
        fail(f"{host.label}: verification failed; managed block still exists")
    if paths["state"].exists():
        fail(f"{host.label}: verification failed; state file still exists")


def verify_host(root: Path, host: Host) -> None:
    paths = host_paths(host)
    state = load_host_state(paths["state"], host)
    if not state:
        fail(f"{host.label}: installer state is missing")

    block = current_host_block(paths["instruction"])
    if block is None:
        fail(f"{host.label}: managed instruction block is missing")
    if sha256_text(block) != state.get("managed_sha256"):
        fail(f"{host.label}: managed instruction block hash mismatch")
    if state.get("version") != version(root):
        fail(f"{host.label}: installed version does not match framework VERSION")
    if not paths["locator"].is_file():
        fail(f"{host.label}: GOVERNANCE_ROOT is missing")
    if read_text(paths["locator"]).strip() != str(root):
        fail(f"{host.label}: GOVERNANCE_ROOT does not identify this framework root")

    if host.key == "claude":
        ownership = dict(state.get("claude_settings_ownership") or {})
        settings = read_json_object(paths["settings"])
        values = claude_allow_rules(settings)
        rule = ownership.get("rule") or claude_read_rule(root)
        if rule not in values:
            fail(
                "Claude Code: governance root is not covered by the expected "
                "permissions.allow Read rule"
            )


def claude_managed_settings_path() -> Path:
    system = platform.system()
    if system == "Darwin":
        return Path("/Library/Application Support/ClaudeCode/managed-settings.json")
    if system == "Windows":
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        return Path(program_files) / "ClaudeCode" / "managed-settings.json"
    return Path("/etc/claude-code/managed-settings.json")


def codex_managed_requirements_path() -> Path:
    if platform.system() == "Windows":
        program_data = os.environ.get("ProgramData", r"C:\ProgramData")
        return Path(program_data) / "OpenAI" / "Codex" / "requirements.toml"
    return Path("/etc/codex/requirements.toml")


def managed_policy_status(host: Host) -> dict:
    """Report whether the host's IT-managed policy layer is present and, if
    so, which enforcement mode it declares. Per the fail-closed rule: a
    present-but-invalid managed file means block; a missing file means
    inform, reported as ABSENT so IT Security can see clients that lack the
    policy rather than silently assuming coverage.
    """
    if host.key == "claude":
        path = claude_managed_settings_path()
        if not path.is_file():
            return {"source": "ABSENT", "mode": "inform", "path": str(path)}
        try:
            data = json.loads(read_text(path))
        except Exception as exc:
            return {
                "source": "MANAGED",
                "mode": "block",
                "path": str(path),
                "error": f"invalid managed settings: {exc}",
            }
        hooks = ((data.get("hooks") or {}).get("PreToolUse") or [{}])[0].get("hooks") or [{}]
        command = hooks[0].get("command", "")
        if "--enforce" in command:
            mode = "block"
        elif "--inform" in command:
            mode = "inform"
        else:
            mode = "block"
        return {"source": "MANAGED", "mode": mode, "path": str(path)}

    if host.key == "codex":
        path = codex_managed_requirements_path()
        if not path.is_file():
            return {"source": "ABSENT", "mode": "inform", "path": str(path)}
        # Codex requirements.toml templates are a WS2 follow-up; presence is
        # recorded without decoding TOML, since the framework adds no TOML
        # dependency. A present file with unknown content fails closed.
        return {"source": "MANAGED", "mode": "block", "path": str(path)}

    return {"source": "ABSENT", "mode": "inform", "path": None}


def preview_host_action(root: Path, action: str, hosts: list[Host]) -> None:
    lines: list[str] = []
    for host in hosts:
        status = host_status(root, host)
        lines.append(f"{host.label}: {display_host_status(status)}")
        if action in {"install", "update"}:
            paths, legacy = preflight_host_install(root, host)
            state = load_host_state(paths["state"], host)
            if action == "update" and not state and not legacy:
                fail(f"{host.label}: no managed installation exists to update")
            lines.append(f"  write managed block in {paths['instruction']}")
            lines.append(f"  set {paths['locator']} to {root}")
            if host.key == "claude":
                lines.append(
                    f"  ensure {claude_read_rule(root)} is in "
                    f"{paths['settings']} permissions.allow"
                )
            lines.append("  preserve unrelated user content")
        elif action == "uninstall":
            paths, state, _ = preflight_host_uninstall(root, host)
            lines.append(f"  remove only the recorded managed block from {paths['instruction']}")
            if state.get("locator_created"):
                lines.append(f"  remove installer-owned {paths['locator']}")
            else:
                lines.append(f"  preserve pre-existing {paths['locator']}")
            if host.key == "claude":
                if dict(state.get("claude_settings_ownership") or {}).get("entry_added"):
                    lines.append(
                        f"  remove only the recorded governance Read allow rule from {paths['settings']}"
                    )
            lines.append("  preserve unrelated user content")
    print_preview(f"Host {action} preview", lines)


# ---------------------------------------------------------------------------
# Project lifecycle
# ---------------------------------------------------------------------------

GOVERNANCE_MODES = ("professional", "business-led")


def template_paths(root: Path) -> dict[str, Path]:
    base = root / "templates" / "repository"
    return {
        "base": base,
        "agents": base / "AGENTS.md",
        "agents_business_led": base / "AGENTS.business-led.md",
        "claude": base / "CLAUDE.md",
        "manifest": base / "project-governance.yml",
        "verification": base / "verification-plan.json",
        "editorconfig": base / ".editorconfig",
        "gitignore": base / ".gitignore",
        "design": base / "docs" / "design.md",
    }


def agents_template_key(mode: str) -> str:
    return "agents_business_led" if mode == "business-led" else "agents"


def managed_project_block(root: Path, mode: str = "professional") -> str:
    text = read_text(template_paths(root)[agents_template_key(mode)])
    match = PROJECT_RE.search(text)
    if not match:
        fail("Project AGENTS template has no managed governance block")
    return match.group(0)


def managed_claude_project_block(root: Path) -> str:
    text = read_text(template_paths(root)["claude"])
    match = CLAUDE_PROJECT_RE.search(text)
    if not match:
        fail("Project CLAUDE template has no managed Claude adapter block")
    return match.group(0)


def replace_or_append_managed(
    original: str,
    new_block: str,
    *,
    current_pattern: re.Pattern,
    legacy_pattern: re.Pattern | None = None,
) -> str:
    if current_pattern.search(original):
        return current_pattern.sub(new_block, original, count=1).rstrip() + "\n"
    if legacy_pattern and legacy_pattern.search(original):
        return legacy_pattern.sub(new_block, original, count=1).rstrip() + "\n"
    return original.rstrip() + "\n\n" + new_block.rstrip() + "\n"


def set_project_name(text: str, name: str) -> str:
    updated, count = re.subn(
        r'(?m)^(\s*name:\s*).+$',
        lambda m: f'{m.group(1)}"{name}"',
        text,
        count=1,
    )
    if count != 1:
        fail("Could not set project name in project-governance.yml")
    return updated


def set_governance_mode(text: str, mode: str) -> str:
    if mode not in GOVERNANCE_MODES:
        fail(f"Unknown governance mode: {mode}")
    updated, count = re.subn(
        r'(?m)^(\s*mode:\s*)["\']?[A-Za-z-]+["\']?\s*$',
        lambda m: f'{m.group(1)}"{mode}"',
        text,
        count=1,
    )
    if count != 1:
        fail("Could not set governance mode in project-governance.yml")
    return updated


def set_governance_baseline(text: str, current_version: str) -> str:
    updated, count = re.subn(
        r'(?m)^(\s*baseline:\s*)["\']?[^"\']+["\']?\s*$',
        lambda m: f'{m.group(1)}"{current_version}"',
        text,
        count=1,
    )
    if count != 1:
        fail("Could not update governance baseline in project-governance.yml")

    source_line = '  source: "host-adapter-locator"'
    locator_line = '  locator: "GOVERNANCE_ROOT"'

    if re.search(r"(?m)^\s*source:\s*", updated):
        updated = re.sub(r"(?m)^(\s*source:\s*).+$", source_line, updated, count=1)
    else:
        updated = re.sub(
            r'(?m)^(\s*baseline:\s*["\'][^"\']+["\']\s*)$',
            lambda m: m.group(1) + "\n" + source_line,
            updated,
            count=1,
        )

    if re.search(r"(?m)^\s*locator:\s*", updated):
        updated = re.sub(r"(?m)^(\s*locator:\s*).+$", locator_line, updated, count=1)
    else:
        updated = re.sub(
            r"(?m)^(\s*source:\s*.+)$",
            lambda m: m.group(1) + "\n" + locator_line,
            updated,
            count=1,
        )
    return updated


def ensure_technology_baseline(text: str) -> tuple[str, bool]:
    if re.search(r"(?m)^technology_baseline:\s*$", text):
        return text, False

    block = """# Governed architecture-significant technology state.
# Added during governance migration; reconcile before treating the historical stack as established.
technology_baseline:
  state: "RECONCILIATION_REQUIRED"
  record: "docs/design.md#technology-baseline"
"""
    if re.search(r"(?m)^platforms:\s*$", text):
        text = re.sub(
            r"(?m)^platforms:\s*$",
            block.rstrip() + "\n\nplatforms:",
            text,
            count=1,
        )
    else:
        text = text.rstrip() + "\n\n" + block
    return text, True


def set_adoption_state(text: str) -> str:
    updated, count = re.subn(
        r'(?m)^([ \t]*state:[ \t]*)"UNESTABLISHED"[ \t]*$',
        r'\1"RECONCILIATION_REQUIRED"',
        text,
        count=1,
    )
    if count == 0 and not re.search(
        r'(?m)^technology_baseline:\s*\n[ \t]+state:\s*"RECONCILIATION_REQUIRED"',
        updated,
    ):
        fail("Could not set adopted Technology Baseline to RECONCILIATION_REQUIRED")

    if not re.search(r"(?m)^adoption:\s*$", updated):
        updated = updated.rstrip() + """

adoption:
  state: "RECONCILIATION_REQUIRED"
  adopted_from_existing_project: true
  historical_governance_approval: false
  note: "Pre-existing requirements, design, implementation, dependencies, verification, and risks require governance reconciliation."
"""
    return updated.rstrip() + "\n"


def project_status(root: Path, project: Path) -> str:
    if not project.exists():
        return "MISSING"
    manifest = project / "project-governance.yml"
    if not manifest.is_file():
        return "NOT GOVERNED"
    text = read_text(manifest)
    match = re.search(r'(?m)^\s*baseline:\s*["\']?([^"\']+)["\']?\s*$', text)
    baseline = match.group(1).strip() if match else "unknown"
    current = version(root)
    host_files = []
    if (project / "AGENTS.md").is_file():
        host_files.append("AGENTS")
    if (project / "CLAUDE.md").is_file():
        host_files.append("CLAUDE")
    suffix = "/".join(host_files) if host_files else "no host instruction files"
    if baseline == current:
        return f"GOVERNED {baseline} ({suffix})"
    return f"GOVERNED {baseline}; update available to {current} ({suffix})"


def governance_owned_yaml_block(text: str) -> str:
    """Return the top-level `governance:` block of project-governance.yml.

    This is the subset of the manifest that identifies the governance
    binding itself (baseline/source/locator); it is what an agent could
    edit to fake compliance with a different baseline, independent of the
    project-owned fields (maturity, profiles, platforms) that are not
    governance-owned.
    """
    match = re.search(r"(?m)^governance:[ \t]*\n(?:[ \t]+.*\n?|[ \t]*\n)*", text)
    if not match:
        fail("project-governance.yml has no top-level governance: block")
    return match.group(0).rstrip("\n") + "\n"


def verification_plan_assurance_json(path: Path) -> str:
    """Return a canonical JSON rendering of verification-plan.json's assurance object.

    Only `assurance` (facts plus capability decisions) is governance-owned in
    the sense that matters for integrity tracking; the `checks` array's argv
    commands are project-specific and are not covered here.
    """
    try:
        data = json.loads(read_text(path))
    except Exception as exc:
        fail(f"Cannot parse verification plan {path}: {exc}")
    assurance = data.get("assurance")
    if not isinstance(assurance, dict):
        fail(f"{path}: verification plan has no assurance object")
    return json.dumps(assurance, sort_keys=True, separators=(",", ":"))


def compute_integrity_entries(root: Path, project: Path) -> list[dict]:
    """Compute the governance-artifact integrity entries governance.py itself owns.

    The assurance-bootstrap baseline copy, copied runner, and CI workflow are
    separately hash-recorded by `scripts/bootstrap-assurance.py` in
    `.governance/assurance-bootstrap.json`; the verification-runner integrity
    preflight cross-checks those against live bytes directly rather than
    duplicating a second hash record for the same files here.
    """
    entries: list[dict] = []

    agents = project / "AGENTS.md"
    if agents.is_file():
        block = PROJECT_RE.search(read_text(agents))
        if block:
            entries.append(
                {"id": "agents_managed_block", "path": "AGENTS.md", "sha256": sha256_text(block.group(0))}
            )

    claude = project / "CLAUDE.md"
    if claude.is_file():
        block = CLAUDE_PROJECT_RE.search(read_text(claude))
        if block:
            entries.append(
                {"id": "claude_managed_block", "path": "CLAUDE.md", "sha256": sha256_text(block.group(0))}
            )

    manifest = project / "project-governance.yml"
    if manifest.is_file():
        entries.append(
            {
                "id": "project_governance_fields",
                "path": "project-governance.yml",
                "sha256": sha256_text(governance_owned_yaml_block(read_text(manifest))),
            }
        )

    verification_plan = project / "verification-plan.json"
    if verification_plan.is_file():
        entries.append(
            {
                "id": "verification_plan_assurance",
                "path": "verification-plan.json",
                "sha256": sha256_text(verification_plan_assurance_json(verification_plan)),
            }
        )

    registration = project / "registration.yml"
    if registration.is_file():
        entries.append(
            {
                "id": "registration",
                "path": "registration.yml",
                "sha256": sha256_text(read_text(registration)),
            }
        )

    return entries


def write_integrity_manifest(root: Path, project: Path) -> None:
    manifest = {
        "schema_version": "1",
        "governance_baseline": version(root),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "entries": compute_integrity_entries(root, project),
    }
    write_text(project / INTEGRITY_PATH, json.dumps(manifest, indent=2, sort_keys=True) + "\n")


# ---------------------------------------------------------------------------
# Business-led mode registration
# ---------------------------------------------------------------------------

REGISTRATION_CAPABILITY_KEYS = (
    "network_connections",
    "persistence",
    "authentication",
    "write_or_delete_actions",
    "cloud",
    "external_recipients",
    "elevated_access",
)


def registration_integrity_block(text: str) -> re.Match | None:
    return re.search(r"(?m)^integrity:[ \t]*\n(?:[ \t]+.*\n?|[ \t]*\n)*", text)


def registration_sealed_content(text: str) -> str:
    """Everything except the integrity: block itself, so sealing does not hash its own output."""
    match = registration_integrity_block(text)
    if match is None:
        fail("registration.yml has no top-level integrity: block")
    return text[: match.start()] + text[match.end() :]


def seal_registration_text(text: str, sealed_by: str, sealed_at: str) -> str:
    content_hash = sha256_text(registration_sealed_content(text))
    match = registration_integrity_block(text)
    if match is None:
        fail("registration.yml has no top-level integrity: block")
    block = match.group(0)
    block, n1 = re.subn(r'(?m)^(\s*sha256:\s*).*$', lambda m: f'{m.group(1)}"{content_hash}"', block, count=1)
    block, n2 = re.subn(r'(?m)^(\s*sealed_by:\s*).*$', lambda m: f'{m.group(1)}"{sealed_by}"', block, count=1)
    block, n3 = re.subn(r'(?m)^(\s*sealed_at:\s*).*$', lambda m: f'{m.group(1)}"{sealed_at}"', block, count=1)
    if (n1, n2, n3) != (1, 1, 1):
        fail("registration.yml integrity block is missing sha256/sealed_by/sealed_at fields")
    return text[: match.start()] + block + text[match.end() :]


def registration_seal_valid(text: str) -> bool:
    match = registration_integrity_block(text)
    if match is None:
        return False
    recorded = re.search(r'(?m)^\s*sha256:\s*["\']?([0-9a-f]{64})["\']?\s*$', match.group(0))
    if not recorded:
        return False
    return sha256_text(registration_sealed_content(text)) == recorded.group(1)


def parse_registration(text: str) -> dict:
    """Light-touch field extraction, not a general YAML parser, matching this
    codebase's existing pattern for project-governance.yml. Sufficient for the
    flat/shallow registration.yml shape; a project needing more expressive
    registration content is exactly what a future registration tool replaces
    this with.
    """
    result: dict = {}
    for key in ("schema_version", "registration_id", "purpose", "pathway", "business_owner", "approval_authority"):
        m = re.search(rf"(?m)^{key}:[ \t]*(.*)$", text)
        if not m:
            result[key] = None
            continue
        value = m.group(1).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        result[key] = value

    caps_match = re.search(r"(?m)^capabilities:[ \t]*\n((?:[ \t]+.*\n?)*)", text)
    capabilities: dict[str, bool] = {}
    caps_text = caps_match.group(1) if caps_match else ""
    for key in REGISTRATION_CAPABILITY_KEYS:
        m = re.search(rf"(?m)^\s*{key}:\s*(true|false)\s*$", caps_text)
        capabilities[key] = (m.group(1) == "true") if m else False
    result["capabilities"] = capabilities
    return result


def validate_registration(text: str) -> None:
    if not registration_seal_valid(text):
        fail("registration.yml integrity seal is missing or does not match its content; it was hand-edited or never sealed")
    data = parse_registration(text)
    if data.get("schema_version") != "1":
        fail("registration.yml is not schema_version 1")
    if data.get("pathway") not in ("green", "amber", "red"):
        fail("registration.yml pathway must be green, amber, or red")
    for field in ("registration_id", "purpose", "business_owner", "approval_authority"):
        if not data.get(field):
            fail(f"registration.yml is missing {field}")


def registration_assurance_facts(data: dict) -> dict:
    """Derive verification-plan.json assurance.facts entries from registration
    capabilities. Only facts genuinely implied by a capability flag are
    returned; other facts (has_dependencies, has_container_artifact, has_iac,
    ships_distributable_artifact) are not derivable from registration alone
    and are left for the project to declare.
    """
    caps = data.get("capabilities", {})
    return {
        "has_exposed_web_surface": bool(caps.get("network_connections") or caps.get("cloud")),
        "has_persisted_data": bool(caps.get("persistence")),
    }


def apply_registration_facts(plan_text: str, facts: dict) -> str:
    data = json.loads(plan_text)
    data.setdefault("assurance", {}).setdefault("facts", {}).update(facts)
    return json.dumps(data, indent=2) + "\n"


def pending_request_records(project: Path) -> list[dict]:
    requests_dir = project / "docs" / "governance" / "requests"
    if not requests_dir.is_dir():
        return []
    pending = []
    for path in sorted(requests_dir.glob("REQUEST-*.md")):
        text = read_text(path)
        status_match = re.search(r"(?m)^Status:\s*(.+?)\s*$", text)
        status = status_match.group(1).strip() if status_match else "unknown"
        if status.lower() == "open":
            routing_match = re.search(r"(?m)^Routing outcome:\s*(.+?)\s*$", text)
            pending.append(
                {
                    "path": path.relative_to(project).as_posix(),
                    "status": status,
                    "routing_outcome": routing_match.group(1).strip() if routing_match else None,
                }
            )
    return pending


CAPABILITY_CHECKLIST_ITEMS = {
    "network_connections": "It only connects to the services it's supposed to, and fails safely if one of them is unavailable.",
    "persistence": "The data it stores is what it should be, nothing more, and it doesn't keep data longer than needed.",
    "authentication": "Only the right people can log in, and losing a password or access doesn't lock out the business.",
    "write_or_delete_actions": "It only changes or deletes the specific things it's meant to, and a mistake doesn't destroy something you can't get back.",
    "cloud": "It only uses the cloud services it's registered for, and stops working safely if one becomes unavailable.",
    "external_recipients": "It only sends information to the people or systems it's supposed to, and not to anyone else.",
    "elevated_access": "It only uses the extra access it has for the specific task that needs it.",
}


def build_validation_checklist(project: Path) -> dict:
    """Generate the plain-language business validation checklist from the
    registration's purpose and approved capabilities.

    KNOWN LIMITATION: WS7 (not yet built) links this checklist to the same
    acceptance criteria the project's automated tests trace to, and shows
    per-item test coverage. Until WS7 exists, items are derived from the
    registration's purpose and capability flags only, not from acceptance
    criteria, since the registration schema has no acceptance-criteria field
    and none is recorded elsewhere in the framework yet.
    """
    manifest = project / "project-governance.yml"
    if not manifest.is_file():
        fail(f"Not a governed project: {project}")
    mode = project_governance_mode(read_text(manifest))
    registration_path = project / "registration.yml"
    if not registration_path.is_file():
        fail("No registration.yml found; the validation checklist needs a registration to generate from")
    reg_text = read_text(registration_path)
    validate_registration(reg_text)
    data = parse_registration(reg_text)

    items = [
        {
            "item": f"The software does what it's registered for: {data.get('purpose')}",
            "source": "purpose",
            "automated_test": None,
        }
    ]
    for key, description in CAPABILITY_CHECKLIST_ITEMS.items():
        if data.get("capabilities", {}).get(key):
            items.append({"item": description, "source": f"capability:{key}", "automated_test": None})

    return {
        "schema_version": "1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project": project.name,
        "governance_mode": mode,
        "registration_id": data.get("registration_id"),
        "items": items,
        "note": (
            "automated_test is always null today: WS7 will populate it once acceptance-criteria-to-test "
            "traceability exists. Check each item yourself before relying on this software for real work."
        ),
    }


def build_readiness_packet(root: Path, project: Path, report_path: Path | None) -> dict:
    manifest = project / "project-governance.yml"
    if not manifest.is_file():
        fail(f"Not a governed project: {project}")
    mode = project_governance_mode(read_text(manifest))

    registration_summary = None
    registration_path = project / "registration.yml"
    if registration_path.is_file():
        reg_text = read_text(registration_path)
        registration_summary = {
            "seal_valid": registration_seal_valid(reg_text),
            **{k: v for k, v in parse_registration(reg_text).items() if k != "capabilities"},
        }

    report = None
    if report_path is not None:
        if not report_path.is_file():
            fail(f"Verification report does not exist: {report_path}")
        try:
            report = json.loads(read_text(report_path))
        except Exception as exc:
            fail(f"Cannot parse verification report {report_path}: {exc}")

    governance_integrity = (report or {}).get("governance_integrity")
    instruction_surface = (report or {}).get("instruction_surface_audit")
    ci_enforcement = (report or {}).get("ci_enforcement")
    overall = (report or {}).get("overall")
    fail_count = sum(1 for r in (report or {}).get("results", []) if r.get("result") == "FAIL")

    requests = pending_request_records(project)

    pathway = (registration_summary or {}).get("pathway")
    blocking = (
        mode == "business-led"
        and (
            registration_summary is None
            or not registration_summary.get("seal_valid")
            or report is None
            or overall != "PASS"
            or fail_count > 0
            or (governance_integrity or {}).get("status") not in (None, "PASS")
            or (instruction_surface or {}).get("status") not in (None, "PASS")
        )
    )
    if mode != "business-led":
        disposition = "NOT_APPLICABLE"
    elif report is None:
        disposition = "INCOMPLETE_EVIDENCE"
    elif blocking:
        disposition = "NOT_READY"
    elif pathway == "red":
        disposition = "IT_OWNERSHIP_REQUIRED"
    elif requests:
        disposition = "PENDING_IT_SECURITY"
    elif pathway == "green":
        disposition = "READY_FOR_AUTOMATED_APPROVAL"
    else:
        disposition = "READY_FOR_MANUAL_REVIEW"

    return {
        "schema_version": "1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project": project.name,
        "governance_mode": mode,
        "git_commit": git_head(project),
        "registration": registration_summary,
        "full_report": (
            {
                "path": report_path.as_posix() if report_path else None,
                "overall": overall,
                "generated_at_utc": (report or {}).get("generated_at_utc"),
                "plan_sha256": (report or {}).get("plan_sha256"),
                "fail_count": fail_count,
            }
            if report is not None
            else None
        ),
        "governance_integrity": governance_integrity,
        "instruction_surface_audit": instruction_surface,
        "enforcement": ci_enforcement,
        "pending_requests": requests,
        "disposition": disposition,
    }


def git_head(project: Path) -> str | None:
    if not (project / ".git").exists():
        return None
    result = run_git(["rev-parse", "HEAD"], project)
    return result.stdout.strip() if result.returncode == 0 else None


def verify_project(root: Path, project: Path) -> None:
    manifest = project / "project-governance.yml"
    agents = project / "AGENTS.md"
    claude = project / "CLAUDE.md"
    for path in (manifest, agents, claude):
        if not path.is_file():
            fail(f"Governed project verification failed; missing {path.name}: {project}")

    manifest_text = read_text(manifest)
    expected_version = version(root)
    if not re.search(
        rf'(?m)^\s*baseline:\s*["\']?{re.escape(expected_version)}["\']?\s*$',
        manifest_text,
    ):
        fail("Project governance baseline does not match framework VERSION")
    if 'source: "host-adapter-locator"' not in manifest_text:
        fail("Project governance source is not host-adapter-locator")
    if 'locator: "GOVERNANCE_ROOT"' not in manifest_text:
        fail("Project governance locator is not host-neutral")

    mode = project_governance_mode(manifest_text)
    agents_text = read_text(agents)
    agents_block = PROJECT_RE.search(agents_text)
    if agents_block is None:
        fail("Project AGENTS.md has no current managed governance block")
    if agents_block.group(0) != managed_project_block(root, mode):
        fail(
            "Project AGENTS.md managed governance block does not match the "
            "pinned template for the current baseline and mode; it was "
            "edited or tampered with"
        )

    claude_text = read_text(claude)
    claude_block = CLAUDE_PROJECT_RE.search(claude_text)
    if claude_block is None:
        fail("Project CLAUDE.md has no managed Claude adapter block")
    if claude_block.group(0) != managed_claude_project_block(root):
        fail(
            "Project CLAUDE.md managed Claude adapter block does not match "
            "the pinned template for the current baseline; it was edited or "
            "tampered with"
        )
    if "@AGENTS.md" not in claude_text:
        fail("Project CLAUDE.md does not import AGENTS.md")

    if mode == "business-led":
        registration_path = project / "registration.yml"
        if not registration_path.is_file():
            fail("Business-led project has no registration.yml")
        validate_registration(read_text(registration_path))


def preview_project_new(
    root: Path,
    parent: Path,
    name: str,
    no_git_init: bool,
    mode: str = "professional",
    registration: Path | None = None,
) -> Path:
    if mode not in GOVERNANCE_MODES:
        fail(f"Unknown governance mode: {mode}")
    if mode == "business-led" and registration is None:
        fail("business-led mode requires --registration")
    if not parent.is_dir():
        fail(f"Parent folder does not exist: {parent}")
    if not name or any(ch in name for ch in '\\/:*?"<>|'):
        fail("Project name is empty or contains invalid path characters")
    target = parent / name
    if target.exists() and any(target.iterdir()):
        fail(f"Target exists and is not empty: {target}")
    print_preview(
        "New governed project preview",
        [
            f"Target: {target}",
            f"Governance baseline: {version(root)}",
            f"Governance mode: {mode}",
            "Create: AGENTS.md, CLAUDE.md, project-governance.yml, verification-plan.json",
            "Create: docs/, src/, tests/ and available repository templates",
            "Create: .governance/integrity.json (governance artifact integrity manifest)",
            (
                f"Registration: {registration}, derive assurance facts from its capabilities"
                if registration
                else "Registration: none"
            ),
            f"Git init: {'no' if no_git_init else 'yes'}",
            "Application code: none",
        ],
    )
    return target


def apply_registration(target: Path, registration: Path | None, mode: str) -> None:
    """Validate and copy the registration into a project, deriving assurance
    facts from its capability flags. Required in business-led mode.
    """
    if registration is None:
        if mode == "business-led":
            fail("business-led mode requires --registration")
        return
    reg_text = read_text(registration)
    validate_registration(reg_text)
    write_text(target / "registration.yml", reg_text)

    plan_path = target / "verification-plan.json"
    if plan_path.is_file():
        facts = registration_assurance_facts(parse_registration(reg_text))
        write_text(plan_path, apply_registration_facts(read_text(plan_path), facts))


def apply_project_new(
    root: Path,
    target: Path,
    name: str,
    no_git_init: bool,
    mode: str = "professional",
    registration: Path | None = None,
) -> None:
    if mode not in GOVERNANCE_MODES:
        fail(f"Unknown governance mode: {mode}")
    templates = template_paths(root)
    target.mkdir(parents=True, exist_ok=True)
    for directory in ("docs", "src", "tests"):
        (target / directory).mkdir(exist_ok=True)

    write_text(target / "AGENTS.md", read_text(templates[agents_template_key(mode)]))
    write_text(target / "CLAUDE.md", read_text(templates["claude"]))
    manifest = set_project_name(read_text(templates["manifest"]), name)
    manifest = set_governance_mode(manifest, mode)
    write_text(target / "project-governance.yml", manifest)

    for key, destination in (
        ("verification", "verification-plan.json"),
        ("editorconfig", ".editorconfig"),
        ("gitignore", ".gitignore"),
        ("design", "docs/design.md"),
    ):
        source = templates[key]
        if source.is_file():
            destination_path = target / destination
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination_path)

    apply_registration(target, registration, mode)

    if not no_git_init and not (target / ".git").exists():
        result = run_git(["init"], target)
        if result.returncode != 0:
            fail(f"Project created, but git init failed: {result.stderr.strip()}")

    write_integrity_manifest(root, target)
    verify_project(root, target)


def preview_project_adopt(
    root: Path, project: Path, mode: str = "professional", registration: Path | None = None
) -> None:
    if mode not in GOVERNANCE_MODES:
        fail(f"Unknown governance mode: {mode}")
    if mode == "business-led" and registration is None:
        fail("business-led mode requires --registration")
    if not project.is_dir():
        fail(f"Project root does not exist: {project}")
    if (project / "project-governance.yml").exists():
        fail("Project is already governed; use project update")
    if git_worktree_is_dirty(project):
        fail("Git worktree is dirty; commit or stash changes before adoption")

    lines = [
        f"Project: {project}",
        f"Governance baseline: {version(root)}",
        f"Governance mode: {mode}",
        "State: RECONCILIATION_REQUIRED",
        "Create project-governance.yml and governance adoption record",
        "Add/refresh only managed governance block in AGENTS.md",
        "Add/refresh only managed Claude adapter block in CLAUDE.md",
        "Preserve existing project content and custom host instructions",
        "Create/refresh .governance/integrity.json (governance artifact integrity manifest)",
        (
            f"Registration: {registration}, derive assurance facts from its capabilities"
            if registration
            else "Registration: none"
        ),
    ]
    print_preview("Adopt existing project preview", lines)


def apply_project_adopt(root: Path, project: Path, mode: str = "professional", registration: Path | None = None) -> None:
    if mode not in GOVERNANCE_MODES:
        fail(f"Unknown governance mode: {mode}")
    templates = template_paths(root)
    stamp = __import__("datetime").datetime.now().strftime("%Y%m%d-%H%M%S")

    agents = project / "AGENTS.md"
    claude = project / "CLAUDE.md"
    project_block = managed_project_block(root, mode)
    claude_block = managed_claude_project_block(root)

    if agents.exists():
        shutil.copy2(agents, project / f"AGENTS.md.governance-backup-{stamp}")
        new_agents = replace_or_append_managed(
            read_text(agents),
            project_block,
            current_pattern=PROJECT_RE,
            legacy_pattern=OLD_PROJECT_RE,
        )
    else:
        new_agents = read_text(templates[agents_template_key(mode)])

    if claude.exists():
        shutil.copy2(claude, project / f"CLAUDE.md.governance-backup-{stamp}")
        new_claude = replace_or_append_managed(
            read_text(claude),
            claude_block,
            current_pattern=CLAUDE_PROJECT_RE,
        )
    else:
        new_claude = read_text(templates["claude"])

    write_text(agents, new_agents)
    write_text(claude, new_claude)

    manifest = set_project_name(read_text(templates["manifest"]), project.name)
    manifest = set_governance_mode(manifest, mode)
    manifest = set_adoption_state(manifest)
    write_text(project / "project-governance.yml", manifest)

    (project / "docs").mkdir(exist_ok=True)
    adoption = f"""# Governance adoption

Governance baseline: {version(root)}
Status: RECONCILIATION_REQUIRED

This repository existed before governance adoption.

No pre-existing requirement, design decision, implementation behavior, dependency choice,
security posture, verification result, or risk acceptance is represented as historically
approved under this governance baseline.

Before substantial C2/C3, security-sensitive, or release work, perform governance
reconciliation and establish a truthful post-adoption evidence baseline.
"""
    write_text(project / "docs" / "governance-adoption.md", adoption)
    apply_registration(project, registration, mode)
    write_integrity_manifest(root, project)
    verify_project(root, project)


def build_project_update(root: Path, project: Path) -> dict:
    if not project.is_dir():
        fail(f"Project root does not exist: {project}")
    manifest_path = project / "project-governance.yml"
    agents_path = project / "AGENTS.md"
    claude_path = project / "CLAUDE.md"
    if not manifest_path.is_file() or not agents_path.is_file():
        fail("Not a governed project: project-governance.yml and AGENTS.md are required")
    if git_worktree_is_dirty(project):
        fail("Git worktree is dirty; commit or stash changes before governance update")

    manifest_old = read_text(manifest_path)
    mode = project_governance_mode(manifest_old)
    manifest_new = set_governance_baseline(manifest_old, version(root))
    manifest_new, technology_added = ensure_technology_baseline(manifest_new)

    agents_old = read_text(agents_path)
    agents_new = replace_or_append_managed(
        agents_old,
        managed_project_block(root, mode),
        current_pattern=PROJECT_RE,
        legacy_pattern=OLD_PROJECT_RE,
    )

    if claude_path.exists():
        claude_old = read_text(claude_path)
        claude_new = replace_or_append_managed(
            claude_old,
            managed_claude_project_block(root),
            current_pattern=CLAUDE_PROJECT_RE,
        )
    else:
        claude_old = None
        claude_new = read_text(template_paths(root)["claude"])

    return {
        "manifest_old": manifest_old,
        "manifest_new": manifest_new,
        "agents_old": agents_old,
        "agents_new": agents_new,
        "claude_old": claude_old,
        "claude_new": claude_new,
        "technology_added": technology_added,
    }


def preview_project_update(root: Path, project: Path, plan: dict) -> None:
    match = re.search(
        r'(?m)^\s*baseline:\s*["\']?([^"\']+)["\']?\s*$',
        plan["manifest_old"],
    )
    old_version = match.group(1).strip() if match else "unknown"
    lines = [
        f"Project: {project}",
        f"Baseline: {old_version} -> {version(root)}",
        f"Governance mode: {project_governance_mode(plan['manifest_old'])} (unchanged; mode is a governance decision, not a routine update)",
        "project-governance.yml: baseline/source/host-neutral locator",
        (
            "Technology Baseline: add RECONCILIATION_REQUIRED"
            if plan["technology_added"]
            else "Technology Baseline: preserve existing project-owned state"
        ),
        "AGENTS.md: replace/append managed governance block only",
        (
            "CLAUDE.md: create managed Claude adapter"
            if plan["claude_old"] is None
            else "CLAUDE.md: replace/append managed Claude adapter block only"
        ),
        "Preserve project-specific AGENTS.md and CLAUDE.md text",
        "Create backups before applying changed governed files",
        "Refresh .governance/integrity.json (governance artifact integrity manifest)",
    ]
    print_preview("Governed project update preview", lines)


def apply_project_update(root: Path, project: Path, plan: dict) -> None:
    stamp = __import__("datetime").datetime.now().strftime("%Y%m%d-%H%M%S")
    manifest = project / "project-governance.yml"
    agents = project / "AGENTS.md"
    claude = project / "CLAUDE.md"

    if plan["manifest_new"] != plan["manifest_old"]:
        shutil.copy2(manifest, project / f"project-governance.yml.governance-backup-{stamp}")
        write_text(manifest, plan["manifest_new"])

    if plan["agents_new"] != plan["agents_old"]:
        shutil.copy2(agents, project / f"AGENTS.md.governance-backup-{stamp}")
        write_text(agents, plan["agents_new"])

    if plan["claude_old"] is None:
        write_text(claude, plan["claude_new"])
    elif plan["claude_new"] != plan["claude_old"]:
        shutil.copy2(claude, project / f"CLAUDE.md.governance-backup-{stamp}")
        write_text(claude, plan["claude_new"])

    write_integrity_manifest(root, project)
    verify_project(root, project)


# ---------------------------------------------------------------------------
# Managed-client hook
# ---------------------------------------------------------------------------

# Names as used across the Claude Code and Codex PreToolUse hook contracts,
# which share the same hookSpecificOutput JSON shape. Only mutating tools are
# evaluated; Read/Grep/Glob/WebFetch/Task-style tools always pass through so
# inspection and planning are never slowed down by this hook.
MUTATING_TOOL_NAMES = {"Edit", "Write", "MultiEdit", "NotebookEdit", "Bash", "apply_patch"}


def project_governance_mode(manifest_text: str) -> str:
    match = re.search(r'(?m)^\s*mode:\s*["\']?([A-Za-z-]+)["\']?\s*$', manifest_text)
    return match.group(1) if match else "professional"


def registration_state(project: Path) -> tuple[bool, bool]:
    """Return (missing, highest_risk) for the project's registration.yml.

    This is a light-touch presence/field check, not the full WS4 schema
    validation; it exists so the hook can enforce "registration missing" and
    "Red pathway" without depending on assurance/registration.schema.json,
    which formalizes this contract separately.
    """
    path = project / "registration.yml"
    if not path.is_file():
        return True, False
    try:
        text = read_text(path)
    except Exception:
        return True, False
    highest_risk = bool(re.search(r'(?m)^\s*pathway:\s*["\']?red["\']?\s*$', text))
    return False, highest_risk


def load_run_verification_module(root: Path):
    """Dynamically load assurance/run-verification.py so the hook can reuse
    governance_integrity_preflight instead of duplicating it a third time
    (it is already duplicated once, intentionally, between governance.py and
    run-verification.py's own small helpers, for the standalone-distribution
    reason documented on that copy). governance.py only runs from within a
    full framework root (framework_root() already requires many sibling
    files), so depending on this sibling file here is not a new risk.
    """
    import importlib.util

    path = root / "assurance" / "run-verification.py"
    spec = importlib.util.spec_from_file_location("_governance_hook_run_verification", path)
    if spec is None or spec.loader is None:
        fail(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hook_pre_tool_decision(root: Path, data: dict, *, enforce: bool) -> dict | None:
    """Return a hookSpecificOutput payload, or None to allow silently."""
    tool_name = data.get("tool_name")
    if tool_name not in MUTATING_TOOL_NAMES:
        return None

    cwd = data.get("cwd")
    project = Path(cwd).resolve() if cwd else Path.cwd()
    manifest = project / "project-governance.yml"
    if not manifest.is_file():
        return None

    reasons: list[str] = []
    try:
        verify_project(root, project)
    except GovernanceError as exc:
        reasons.append(f"Governance artifact integrity check failed: {exc}")

    # verify_project (above) covers the manifest fields, both managed blocks,
    # and (in business-led mode) the registration seal. It does not cover
    # what only the verification runner's preflight checks: verification-plan.json's
    # assurance object, .governance/integrity.json's internal consistency,
    # and the .governance/assurance-bootstrap.json cross-check. Run that
    # here too so a hand-edit to one of those is denied live, not only at
    # the next quick/full run. Scoped to schema v3 projects, matching the
    # runner's own scope for this preflight.
    plan_path = project / "verification-plan.json"
    if plan_path.is_file():
        try:
            plan_schema = json.loads(read_text(plan_path)).get("schema_version")
        except Exception:
            plan_schema = None
        if plan_schema == "3":
            run_verification = load_run_verification_module(root)
            baseline_path = project / ".governance" / "assurance-baseline.json"
            preflight = run_verification.governance_integrity_preflight(
                project, baseline_path if baseline_path.is_file() else None
            )
            for issue in preflight.get("issues", []):
                reasons.append(issue["message"])

    mode = project_governance_mode(read_text(manifest))
    if mode == "business-led":
        missing, highest_risk = registration_state(project)
        if missing:
            reasons.append(
                "This project has no registration on file. Business-led mode requires "
                "IT Security's registration before development proceeds under full assurance."
            )
        elif highest_risk:
            reasons.append(
                "This project's registration is Red pathway. IT Security ownership is "
                "required before real use."
            )

    if not reasons:
        return None

    reason_text = " ".join(reasons)
    decision = "deny" if enforce else "allow"
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason_text,
        },
        "systemMessage": reason_text,
    }


def run_hook_pre_tool(root: Path, *, enforce: bool) -> int:
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except Exception as exc:
        print(f"governance hook: malformed input, allowing: {exc}", file=sys.stderr)
        return 0
    if not isinstance(data, dict):
        print("governance hook: malformed input (not an object), allowing", file=sys.stderr)
        return 0

    try:
        payload = hook_pre_tool_decision(root, data, enforce=enforce)
    except Exception as exc:
        # A hook bug must never itself become an unexplained block.
        print(f"governance hook: internal error, allowing: {exc}", file=sys.stderr)
        return 0

    if payload is not None:
        print(json.dumps(payload))
    return 0


# ---------------------------------------------------------------------------
# Interactive UI and CLI
# ---------------------------------------------------------------------------

def choose(prompt: str, options: list[str]) -> int:
    print()
    for index, option in enumerate(options, 1):
        print(f"{index}) {option}")
    while True:
        answer = input(f"{prompt} [1-{len(options)}]: ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return int(answer) - 1
        print("Please enter one of the listed numbers.")


def interactive(root: Path) -> int:
    print(f"Engineering Governance {version(root)}")
    print(f"Framework root: {root}")
    print()
    for host in HOSTS.values():
        print(f"{host.label:12} {display_host_status(host_status(root, host))}")

    area = choose(
        "Choose",
        [
            "Manage host adapters",
            "Manage governed projects",
            "Verify host adapters",
            "Exit",
        ],
    )
    if area == 3:
        return 0

    if area == 2:
        installed = [
            host for host in HOSTS.values()
            if host_status(root, host).startswith("INSTALLED")
        ]
        if not installed:
            print("No governance host adapters are configured.")
            return 0
        for host in installed:
            verify_host(root, host)
            print(f"{host.label}: verification PASS")
        return 0

    if area == 0:
        statuses = {key: host_status(root, host) for key, host in HOSTS.items()}
        actions = []
        if any(s == "NOT INSTALLED" for s in statuses.values()):
            actions.append("Install")
        if any(
            s.startswith(("INSTALLED", "LEGACY", "MODIFIED", "BROKEN"))
            for s in statuses.values()
        ):
            actions.append("Update")
        if any(
            s.startswith(("INSTALLED", "MODIFIED", "BROKEN"))
            for s in statuses.values()
        ):
            actions.append("Uninstall")
        actions.append("Back")
        pick = actions[choose("Host action", actions)].lower()
        if pick == "back":
            return 0

        candidates = action_hosts(root, pick, "all")
        labels = [h.label for h in candidates]
        if len(candidates) > 1:
            labels.append("All listed host adapters")
        idx = choose("Host", labels)
        targets = candidates if idx == len(candidates) else [candidates[idx]]
        preview_host_action(root, pick, targets)
        confirm(False)
        for host in targets:
            if pick == "install":
                host_install_or_update(root, host, require_existing=False)
            elif pick == "update":
                host_install_or_update(root, host, require_existing=True)
            else:
                host_uninstall(root, host)
            print(f"{host.label}: {pick} PASS")
        print("Verification: PASS")
        print("Done.")
        return 0

    project_action = ["New", "Adopt", "Status", "Update", "Verify", "Back"][
        choose("Project action", ["New", "Adopt", "Status", "Update", "Verify", "Back"])
    ].lower()
    if project_action == "back":
        return 0

    if project_action == "new":
        parent = Path(input("Parent folder: ").strip()).expanduser().resolve()
        name = input("Project name: ").strip()
        target = preview_project_new(root, parent, name, no_git_init=False)
        confirm(False)
        apply_project_new(root, target, name, no_git_init=False)
        print(f"Created governed project: {target}")
        print("Verification: PASS")
        return 0

    project = Path(input("Project root: ").strip()).expanduser().resolve()
    if project_action == "status":
        print(project_status(root, project))
        return 0
    if project_action == "verify":
        verify_project(root, project)
        print("Project verification: PASS")
        return 0
    if project_action == "adopt":
        preview_project_adopt(root, project)
        confirm(False)
        apply_project_adopt(root, project)
        print("Governance adoption: PASS")
        print("Verification: PASS")
        return 0
    if project_action == "update":
        plan = build_project_update(root, project)
        preview_project_update(root, project, plan)
        confirm(False)
        apply_project_update(root, project, plan)
        print("Governance update: PASS")
        print("Verification: PASS")
        return 0

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install/update/uninstall host adapters and manage governed projects.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="area")

    host = sub.add_parser("host", help="Manage Codex/Claude Code host adapters.")
    host_sub = host.add_subparsers(dest="action", required=True)
    for action in ("status", "verify", "install", "update", "uninstall"):
        command = host_sub.add_parser(action)
        command.add_argument("--host", choices=("codex", "claude", "all"), default="all")
        if action in {"install", "update"}:
            command.add_argument("--kernel-mode", choices=GOVERNANCE_MODES, default=None)
        if action in {"install", "update", "uninstall"}:
            command.add_argument("-y", "--yes", action="store_true")

    project = sub.add_parser("project", help="Manage governed projects.")
    project_sub = project.add_subparsers(dest="action", required=True)

    status = project_sub.add_parser("status")
    status.add_argument("--project", required=True)

    verify = project_sub.add_parser("verify")
    verify.add_argument("--project", required=True)

    readiness = project_sub.add_parser("readiness")
    readiness.add_argument("--project", required=True)
    readiness.add_argument("--report", default=None, help="Path to a canonical full verification report JSON.")
    readiness.add_argument("--output", default=None, help="Write the packet to this path instead of stdout.")

    checklist = project_sub.add_parser("validation-checklist")
    checklist.add_argument("--project", required=True)
    checklist.add_argument("--output", default=None, help="Write the checklist to this path instead of stdout.")

    new = project_sub.add_parser("new")
    new.add_argument("--parent", required=True)
    new.add_argument("--name", required=True)
    new.add_argument("--no-git-init", action="store_true")
    new.add_argument("--mode", choices=GOVERNANCE_MODES, default="professional")
    new.add_argument("--registration", default=None)
    new.add_argument("-y", "--yes", action="store_true")

    adopt = project_sub.add_parser("adopt")
    adopt.add_argument("--project", required=True)
    adopt.add_argument("--mode", choices=GOVERNANCE_MODES, default="professional")
    adopt.add_argument("--registration", default=None)
    adopt.add_argument("-y", "--yes", action="store_true")

    update = project_sub.add_parser("update")
    update.add_argument("--project", required=True)
    update.add_argument("-y", "--yes", action="store_true")

    hook = sub.add_parser("hook", help="Managed-client hook entry points.")
    hook_sub = hook.add_subparsers(dest="action", required=True)
    pre_tool = hook_sub.add_parser(
        "pre-tool",
        help="PreToolUse hook: reads the tool-call JSON on stdin, prints a hookSpecificOutput decision.",
    )
    mode_group = pre_tool.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--enforce", action="store_true")
    mode_group.add_argument("--inform", action="store_true")

    registration = sub.add_parser("registration", help="Business-led mode registration tooling.")
    registration_sub = registration.add_subparsers(dest="action", required=True)
    seal = registration_sub.add_parser("seal", help="Compute and write the integrity seal over a registration.yml.")
    seal.add_argument("--registration", required=True)
    seal.add_argument("--by", required=True, help="Identity of the sealer, recorded in integrity.sealed_by.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        root = framework_root()
        if args.area is None:
            return interactive(root)

        if args.area == "host":
            if args.action == "status":
                for host in selected_hosts(args.host):
                    print(f"{host.label}: {display_host_status(host_status(root, host))}")
                    state = load_host_state(host_paths(host)["state"], host)
                    print(f"  kernel mode: {(state or {}).get('kernel_mode', 'professional')}")
                    policy = managed_policy_status(host)
                    print(f"  managed policy: {policy['source']} (mode={policy['mode']})")
                return 0

            hosts = action_hosts(root, args.action, args.host)
            if not hosts:
                print(f"No host adapters require action: {args.action}.")
                return 0

            if args.action == "verify":
                for host in hosts:
                    verify_host(root, host)
                    print(f"{host.label}: verification PASS")
                    state = load_host_state(host_paths(host)["state"], host)
                    print(f"  kernel mode: {(state or {}).get('kernel_mode', 'professional')}")
                    policy = managed_policy_status(host)
                    print(f"  managed policy: {policy['source']} (mode={policy['mode']})")
                return 0

            preview_host_action(root, args.action, hosts)
            confirm(args.yes)
            for host in hosts:
                if args.action == "install":
                    host_install_or_update(
                        root, host, require_existing=False, kernel_mode=args.kernel_mode
                    )
                elif args.action == "update":
                    host_install_or_update(
                        root, host, require_existing=True, kernel_mode=args.kernel_mode
                    )
                else:
                    host_uninstall(root, host)
                print(f"{host.label}: {args.action} PASS")
            print("Verification: PASS")
            print("Done.")
            return 0

        if args.area == "project":
            if args.action == "status":
                project = Path(args.project).expanduser().resolve()
                print(project_status(root, project))
                return 0

            if args.action == "verify":
                project = Path(args.project).expanduser().resolve()
                verify_project(root, project)
                print("Project verification: PASS")
                return 0

            if args.action == "readiness":
                project = Path(args.project).expanduser().resolve()
                report_path = Path(args.report).expanduser().resolve() if args.report else None
                packet = build_readiness_packet(root, project, report_path)
                text = json.dumps(packet, indent=2) + "\n"
                if args.output:
                    write_text(Path(args.output).expanduser().resolve(), text)
                    print(f"Readiness packet written: {args.output}")
                else:
                    print(text, end="")
                return 0

            if args.action == "validation-checklist":
                project = Path(args.project).expanduser().resolve()
                checklist = build_validation_checklist(project)
                text = json.dumps(checklist, indent=2) + "\n"
                if args.output:
                    write_text(Path(args.output).expanduser().resolve(), text)
                    print(f"Validation checklist written: {args.output}")
                else:
                    print(text, end="")
                return 0

            if args.action == "new":
                parent = Path(args.parent).expanduser().resolve()
                registration = Path(args.registration).expanduser().resolve() if args.registration else None
                target = preview_project_new(root, parent, args.name, args.no_git_init, args.mode, registration)
                confirm(args.yes)
                apply_project_new(root, target, args.name, args.no_git_init, args.mode, registration)
                print(f"Created governed project: {target}")
                print("Verification: PASS")
                return 0

            project = Path(args.project).expanduser().resolve()
            if args.action == "adopt":
                registration = Path(args.registration).expanduser().resolve() if args.registration else None
                preview_project_adopt(root, project, args.mode, registration)
                confirm(args.yes)
                apply_project_adopt(root, project, args.mode, registration)
                print("Governance adoption: PASS")
                print("Verification: PASS")
                return 0

            if args.action == "update":
                plan = build_project_update(root, project)
                preview_project_update(root, project, plan)
                confirm(args.yes)
                apply_project_update(root, project, plan)
                print("Governance update: PASS")
                print("Verification: PASS")
                return 0

        if args.area == "hook" and args.action == "pre-tool":
            return run_hook_pre_tool(root, enforce=args.enforce)

        if args.area == "registration" and args.action == "seal":
            reg_path = Path(args.registration).expanduser().resolve()
            if not reg_path.is_file():
                fail(f"Registration file does not exist: {reg_path}")
            sealed_at = datetime.now(timezone.utc).isoformat()
            new_text = seal_registration_text(read_text(reg_path), args.by, sealed_at)
            write_text(reg_path, new_text)
            print(f"Sealed: {reg_path}")
            print(f"Sealed by: {args.by}")
            print(f"Sealed at: {sealed_at}")
            return 0

        parser.error("Unsupported operation")
        return 2
    except GovernanceError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
